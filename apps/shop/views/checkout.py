import json
import logging
import urlparse
import attr

import stripe
import requests
from tenacity import (
    retry,
    wait_exponential,
    RetryError,
    stop_after_attempt,
    retry_if_exception_message
)
from paypalcheckoutsdk.core import (
    PayPalHttpClient,
    SandboxEnvironment,
    LiveEnvironment
)
from paypalcheckoutsdk.orders import OrdersCreateRequest
from paypalcheckoutsdk.payments import AuthorizationsCaptureRequest
from paypalhttp import HttpError

from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models import Sum
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ValidationError

from ..models import (
    Product,
    Order,
    Address,
    ShippingOptions,
    LOCALES
)
from ..forms import (
    BillingAddressForm,
    AddressForm
)
from ..helpers import Helpers
from ..cart import Cart


logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_PRIVATE_KEY


def get_paypal_client():
    # Creating Access Token for Sandbox
    if settings.ENV == 'LOCAL':
        initializer = SandboxEnvironment
    else:
        initializer = LiveEnvironment

    environment = initializer(
        client_id=settings.PAYPAL_CLIENT_ID,
        client_secret=settings.PAYPAL_SECRET
    )

    return PayPalHttpClient(environment)


def checkout(request):
    '''
    get cart contents
    remove any sold items
    redirect back to show cart if empty
    render checkout if cart contains items
    '''
    cart = Cart(request)

    if not cart.item_ids:
        return redirect(reverse("shop:show_cart"))

    context = attr.asdict(cart)
    context['address_form'] = AddressForm()

    return render(request, 'shop/checkout.html', context)


def shipping(request):
    '''
    get shipping options for address from client
    '''
    cart = Cart(request)
    if not cart.item_ids:
        return redirect(reverse("shop:show_cart"))

    locales = (i[0] for i in LOCALES)
    if request.POST['country'] in locales:
        locale = request.POST['country']
    else:
        locale = 'INTER'

    order_size_cat = 'lte5' if len(cart.item_ids) <= 5 else 'gt5'

    shipping_options = ShippingOptions.objects.filter(
        locale=locale,
        order_size_cat=order_size_cat
    )

    shipping_options_dicts = [item.display_dict() for item in shipping_options]
    try:
        shipping_address = get_or_create_address(request.POST)
    except ValidationError as e:
        logger.info(e)
        return JsonResponse({'errors': e.message_dict})

    context = {
        'cartEmpty': len(cart.items) == 0,
        'shippingOptions': shipping_options_dicts,
        'addressId': shipping_address.id
    }

    return JsonResponse(context)


def payments(request):
    cart = Cart(request)

    if not cart.item_ids:
        return redirect(reverse("shop:show_cart"))
    # shipping and order info in session
    # use to display order info
    context = attr.asdict(cart)
    context['billing_form'] = BillingAddressForm()

    return render(request, 'shop/payments.html', context)


def get_or_create_address(form_data):
    if form_data.get('phone') and form_data.get('phone_prefix'):
        full_phone = form_data['phone_prefix'] + form_data['phone']
    else:
        full_phone = None

    data = {
        "addressee": form_data.get("addressee") if form_data.get("addressee") else None,
        "street": form_data.get("street") if form_data.get("street") else None,
        "apt": form_data.get("apt") if form_data.get("apt") else None,
        "city": form_data.get("city") if form_data.get("city") else None,
        "state": form_data.get("state") if form_data.get("state") else None,
        "zip_code": form_data.get("zip_code") if form_data.get("zip_code") else None,
        "country": form_data.get("country") if form_data.get("country") else None,
        "phone": full_phone,
        "email": form_data.get("email") if form_data.get("email") else None
    }
    try:
        address = Address.objects.get(**data)
    except Address.DoesNotExist:
        address = Address(**data)
        # validate
        address.full_clean()
        address.save()

    return address


def create_order(data):
    items = data.pop('items')
    order = Order(**data)
    order.full_clean()
    order.save()
    # add order id to each item just sold
    order.products.set(items)
    # wat?!?! this should be on the product model
    Order.objects.update_sold_items(items)
    return order


def order_handler(request):
    #kick user out of checkout if cart is empty
    try:
        cart = request.session['cart']
    except KeyError:
        request.session['cart'] = []
        logger.error('there was a cart error')
        return JsonResponse({"cart_empty": True})

    items = Product.objects.filter(pk__in=cart)
    items_total = items.aggregate(Sum('price'))['price__sum']

    form_data = json.loads(request.body)
    purchase_method = form_data.get('method')

    parsed_payment = urlparse.parse_qs(form_data.get('payment'))
    parsed_address = urlparse.parse_qs(form_data.get('address'))
    parsed_shipping = urlparse.parse_qs(form_data.get('shipping'))
    
    order_address = Address.objects.get(id=parsed_address.get('address_id', [None])[0])

    order_id = None
    stripe_charge = None
    if purchase_method == "card":
        charge_cents = int(100 * (float(items_total) + float(parsed_shipping["cost"][0])))
        try:
            stripe_charge = setup_stripe_charge(
                charge_cents,
                parsed_payment['stripeToken'][0],
                order_address.email
            )
            if 'error' in stripe_charge:
                return JsonResponse(stripe_charge)
            else:
                order_id = stripe_charge['charge'].id
        except RetryError as e:
            return JsonResponse({'error': e.message.exception_info()[0].message})

    # this is the data we need to complete the order
    data = {
        "order_method": purchase_method,
        "order_id": order_id,
        "subtotal": items_total,
        "shipping": parsed_shipping["cost"][0],
        "shipping_address": order_address,
        "status": "pending",
        "items": items,
        "shipping_carrier": parsed_shipping["carrier"][0],
        "shipping_service": parsed_shipping["service"][0]
    }
    order = create_order(data)
    # if there is a problem creating the order, return an error
    if not order:
        return JsonResponse({"error": "There was a problem with your order, please contact <a href='mailto:rickpropas@comcast.net'>rickpropas@comcast.net</a> Please note that you have not been charged for your order."})

    request.session["order_id"] = order.id
    if purchase_method == 'paypal':
        paypal_order = create_paypal_order(order)
        return JsonResponse(paypal_order.result.dict())

    #  capture the order here using the order id (if paid with stripe)
    if stripe_charge:
        stripe.Charge.capture(stripe_charge.get('charge'))

    context = {
        "order": order,
        "message": "success!"
    }
    request.session["cart"] = []
    # send emails to owner and client
    send_all_emails(order)
    return render(request, "shop/success.html", context)


def create_paypal_order(order):
    req = OrdersCreateRequest()
    req.prefer('return=representation')
    req_body = create_paypal_order_body(order)
    req.request_body(req_body)
    return get_paypal_client().execute(req)


def send_all_emails(order):
    # email buyer first so that seller can be notified if there is an error
    buyer_recipient = order.shipping_address.email
    buyer_subject = "Thank You for Your Penguin Pen Purchase"
    buyer_email_text = email_text(order, False)

    seller_subject = "You Made a Sale"
    seller_email_text = email_text(order, True)

    valid = True

    try:
        send_email(buyer_recipient, buyer_subject, buyer_email_text)
    except (ValueError, RetryError) as e:
        error_subject = "There was an error emailing client at {}".format(
            order.shipping_address.email
        )
        logger.error(error_subject)
        context = {"order": order, "message": e.message}
        error_email_text = render_to_string("shop/error_email.html", context=context)
        try:
            send_email(settings.ADMIN_EMAIL, error_subject, error_email_text)
        except (ValueError, RetryError) as e:
            logger.error('There was an error emailing the seller.')

    try:
        send_email(settings.ADMIN_EMAIL, seller_subject, seller_email_text)
    except:
        logger.error('There was an error emailing the seller.')


def email_text(order, seller):
    products = order.products.all()
    pens = order.products.filter(pen__isnull=False)
    knives = order.products.filter(knife__isnull=False)
    if len(pens) == len(products):
        item_type = "pens"
    elif len(knives) == len(products):
        item_type = "knives"
    else:
        item_type = "items"
    prep = "them"
    if len(products) == 1:
        prep = "it"
        thank_you = "These are great {} and this is a fine example.".format(
            item_type)
        if item_type == "pens":
            item_type = "pen"
        elif item_type == "knives":
            item_type = "knife"
    else:
        thank_you = ""
    context = {
        "order": order,
        "thank_you": thank_you,
        "item_type": item_type,
        "prep": prep
    }
    if seller:
        context["seller"] = True
    return render_to_string("shop/email.html", context=context)


@retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(4))
def setup_stripe_charge(amount, stripe_token, email):
    # some exceptions are caught as they will not benefit from retries, others result in retries and raise RetryException exception when retry limit expires
    error_msg = ''
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            capture=False,
            source=stripe_token,
            description="Charge for order to {}".format(email)
        )
        return {'charge': charge}
    except stripe.error.CardError as e:
        error_msg = e.message
    except stripe.error.InvalidRequestError as e:
        error_msg = e.message
    except stripe.error.AuthenticationError as e:
        error_msg = e.message
    return {'error': error_msg}


@retry(
    wait=wait_exponential(multiplier=1, min=4, max=10),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_message(message='RETRY')
)
def send_email(recipient, subject, text):
    response = requests.post(
        settings.MAILGUN_BASE_URL + "messages",
        auth=("api", settings.MAILGUN_PRIVATE_KEY),
        data={
            "from": settings.MAILGUN_SENDER,
            "to": [recipient],
            "subject": subject,
            "html": text
        }
    )
    if response.status_code == 200:
        return {'status': response.status_code}
    elif response.status_code == 400:
        message = response.json().get('message', '')
        logger.error('Parameter error from stripe API:: %s', message)
        raise ValueError(message)
    elif response.status_code == 401:
        message = 'Auth error from stripe API, check API key'
        logger.error(message)
        raise ValueError(message)
    else:
        logger.error('Mailgun API error:: [%s] %s', response.status_code, response.text)
        raise ValueError('RETRY')


def create_paypal_order_body(order):
    items = order.products.all()
    paypal_items = []
    for item in items:
        paypal_items.append(create_paypal_item(item))

    return {
        "intent": "AUTHORIZE",
        "application_context": {
            "brand_name": "Penguin Pens",
            "landing_page": "BILLING",
            "shipping_preference": "SET_PROVIDED_ADDRESS",
            "user_action": "CONTINUE"
        },
        "purchase_units": [
            {
                "reference_id": order.id,
                "description": "Fine writing instruments and collectible knives",
                "amount": {
                    "currency_code": "USD",
                    "value": str(order.subtotal + order.shipping),
                    "breakdown": {
                        "item_total": {
                            "currency_code": "USD",
                            "value": str(order.subtotal)
                        },
                        "shipping": {
                            "currency_code": "USD",
                            "value": str(order.shipping)
                        },
                    }
                },
                "items": paypal_items,
                "shipping": {
                    "method": order.shipping_carrier,
                    "address": {
                        "name": {
                            "full_name": order.shipping_address.addressee
                        },
                        "address_line_1": order.shipping_address.street,
                        "address_line_2": order.shipping_address.apt,
                        "admin_area_2": order.shipping_address.city,
                        "admin_area_1": order.shipping_address.state,
                        "postal_code": order.shipping_address.zip_code,
                        "country_code": str(order.shipping_address.country)
                    }
                }
            }
        ]
    }


def create_paypal_item(item):
    return {
        "name": str(item),
        "description": item.description,
        "sku": item.id,
        "unit_amount": {
            "currency_code": "USD",
            "value": str(item.price)
        },
        "quantity": "1",
        "category": "PHYSICAL_GOODS"
    }


def create_paypal_capture(order):
    return {
        "invoice_id": order.id,
        "note_to_payer": "Thank you for your purchase with the PENguin!",
        "amount": {
            "currency_code": "USD",
            "value": str(order.subtotal + order.shipping),
            },
        "final_capture": True
    }


def capture_paypal(request):
    ids = json.loads(request.body)
    order = Order.objects.get(id=request.session.get('order_id'))

    req = AuthorizationsCaptureRequest(ids['authorizationID'])
    req.request_body(create_paypal_capture(order))
    get_paypal_client().execute(req)

    context = {
        "order": order,
        "message": "success!"
    }
    request.session["cart"] = []
    # send emails to owner and client
    send_all_emails(order)
    return render(request, "shop/success.html", context)
