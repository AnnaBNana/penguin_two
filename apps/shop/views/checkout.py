import json
import logging
import urlparse

import easypost
import stripe
import requests

from django.shortcuts import redirect, render
from django.urls import reverse
from django.db.models import Sum
from django.http import JsonResponse
from django.conf import settings

from ..models import (
    Product,
    Order,
    Address
)
from ..forms import (
    BillingAddressForm,
    AddressForm
)
from ..helpers import Helpers
from ..cart import Cart

logger = logging.getLogger(__name__)
easypost.api_key = settings.EASYPOST_PRODUCTION_KEY
stripe.api_key = settings.STRIPE_TEST_PRIVATE_KEY


def checkout(request):
    '''
    get cart contents
    remove any sold items
    redirect back to show cart if empty
    render checkout if cart contains items
    '''
    cart = Cart(request)
    context = cart.create_cart_context()

    if not cart.items:
        return redirect(reverse("shop:show_cart"))

    context['address_form'] = AddressForm()

    return render(request, 'shop/nuevo_checkout.html', context)

def shipping(request):
    cart = Cart(request)
    context = cart.create_cart_context()

    if not cart.items:
        return redirect(reverse("shop:show_cart"))
    # get shipping
    # put shipping in session?
    return redirect(reverse("shop:payments"))

def payments(request):
    cart = Cart(request)
    context = cart.create_cart_context()

    if not cart.items:
        return redirect(reverse("shop:show_cart"))
    # shipping and order info in session
    # use to display order info
    context['billing_form'] = BillingAddressForm()
    return render(request, 'shop/payments.html', context)


def shipping_cost(request):
    try:
        item_ids = request.session['cart']
        items = Product.objects.filter(pk__in=item_ids)
    except KeyError:
        request.session['cart'] = []
        return JsonResponse({'cart_empty': True})
    messages = []
    order_subtotal = items.aggregate(Sum('price'))['price__sum']
    # make global in deployment
    from_address = easypost.Address.create(
        verify=["delivery"],
        name="Rick Propas",
        street1="43739 Montrose Ave.",
        city="Fremont",
        state="CA",
        zip="94538",
        country="US",
        phone="510-754-3278"
    )
    address = add_address(request, messages)
    if 'shipping_address' in address:
        to_address = address['to_address']
        address_id = address['shipping_address'].id
    else:
        # return errors?
        return JsonResponse(address)
    data = {
        "item_ids": item_ids,
        "items": items,
        "to_address": to_address,
        "from_address": from_address,
        "order_subtotal": order_subtotal
    }
    shipping_choices = get_shipping(request, data)
    context = {
        "total_cost": order_subtotal,
        "usps_shipment": shipping_choices["usps_shipment"],
        "fedex_shipment": shipping_choices["fedex_shipment"],
        "all_options": shipping_choices["shipment"],
        "address_id": address_id,
        "usps_insurance": Helpers.generate_insurance(order_subtotal),
        "usps_express_insurance": Helpers.generate_insurance_express(order_subtotal)
    }
    return JsonResponse(context)


def complete(request):
    order = Order.objects.get(id=1)
    context = {
        "order": order
    }
    return render(request, 'shop/success.html', context)


def add_address(request, messages):
    flag = False
    response = requests.get(
        "https://api.mailgun.net/v3/address/validate",
        params={'address': request.POST["email"],
                "mailbox_verification": True},
        auth=('api', settings.MAILGUN_PUBLIC_KEY)
    )
    if response.status_code == 200:
        if not response.json().get("is_valid"):
            message = "Email invalid"
            if response.json().get("did_you_mean"):
                message += "; did you mean: {}".format(
                    response.json().get("did_you_mean"))
            messages.append({"message": message, "field": "email"})
            flag = True
    try:
        to_address = easypost.Address.create(
            verify=["delivery"],
            name=request.POST["addressee"],
            email=request.POST["email"],
            street1=request.POST["street"],
            street2=request.POST["apt"],
            city=request.POST["city"],
            state=request.POST["state"],
            zip=request.POST["zip_code"],
            country=request.POST["country"],
            phone=request.POST["phone"]
        )
        #errors when creating address should be returned to the client for error display
        if to_address.verifications.delivery.errors:
            errors = to_address.verifications.delivery.errors
            #we're sending back this thing bc the object doesn't want to be serialized, should pickle?
            for err in errors:
                messages.append({
                    "message": err.message,
                    "field": err.field,
                })
            flag = True
        else:
            shipping_address = Address.objects.create(
                addressee=to_address.name,
                street=to_address.street1,
                apt=to_address.street2,
                city=to_address.city,
                state=to_address.state,
                zip_code=to_address.zip,
                country=to_address.country,
                phone=to_address.phone,
                email=to_address.email,
            )
    except easypost.Error as e:
        to_address = None
        messages.append({"message": "Error validating your address"})
        flag = True
    if flag:
        return {"errors": messages}
    return {"shipping_address": shipping_address, "to_address": to_address}


def get_shipping(request, data):
    item_ids = data["item_ids"]
    items = data["items"]
    to_address = data["to_address"]
    from_address = data["from_address"]
    weight = items.aggregate(Sum('weight'))['weight__sum']
    special_shipping = items.filter(special_shipping=True).count()
    knives = items.exclude(knife__isnull=True)
    # TODO: knives should only have 3/package
    if len(item_ids) < 6 and special_shipping == 0\
            or len(knives) == len(items):
        usps_parcel = easypost.Parcel.create(
            weight=weight,
            carrier_accounts="USPS",
            predefined_package="SmallFlatRateBox"
        )
        usps_shipment = easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=usps_parcel
        )
        fedex_parcel = easypost.Parcel.create(
            weight=weight,
            carrier_accounts="FedEx",
            predefined_package="FedExEnvelope"
        )
        fedex_shipment = easypost.Shipment.create(
            to_address=to_address,
            from_address=from_address,
            parcel=fedex_parcel
        )
        length = 8.625
        height = 5.375
        width = 1.625
    else:
        usps_shipment = None
        fedex_shipment = None
        if len(items) == 1:
            width = items[0].width
            height = items[0].depth
            length = items[0].length
        else:
            all_dimensions = [[i.width, i.depth, i.length] for i in items]
            height = 0
            # length should be set to highest value dimension
            length = max(max(all_dimensions))
            for item_dimension in all_dimensions:
                min_val = min(item_dimension)
                max_val = max(item_dimension)
                # remove max and min from each array
                # the max of the remaining value for each will be the width
                item_dimension.remove(min_val)
                item_dimension.remove(max_val)
                # height should be the combined smallest dimensions of each item
                height += min_val
            width = max(max(all_dimensions))
    # create parcel via easypost
    parcel = easypost.Parcel.create(
        weight=weight,
        length=length,
        height=height,
        width=width
    )
    shipment = easypost.Shipment.create(
        to_address=to_address,
        from_address=from_address,
        parcel=parcel
    )
    return {
        "shipment": shipment.to_json(),
        "usps_shipment": usps_shipment.to_json() if usps_shipment else None,
        "fedex_shipment": fedex_shipment.to_json() if fedex_shipment else None
    }


def order_handler(request):
    #kick user out of checkout if cart is empty
    try:
        cart = request.session['cart']
    except KeyError:
        request.session['cart'] = []
        logger.error('there was a cart error')
        return JsonResponse({"cart_empty": True})
    # payment must be handled differently if sent by paypal vs stripe
    try:
        parsed_payment = json.loads(request.POST["payment"])
    except ValueError:
        logger.error('there was an error retrieving payment')
        parsed_payment = urlparse.parse_qs(request.POST["payment"])

    msg = 'the parsed payment: {}'.format(parsed_payment)
    logger.error(msg)
    # get all cart items as queryset
    items = Product.objects.filter(pk__in=cart)
    # get items total
    items_total = items.aggregate(Sum('price'))['price__sum']
    parsed_address = urlparse.parse_qs(request.POST['address'])
    parsed_shipping = urlparse.parse_qs(request.POST['shipping'])
    # the charge still remains to be completed if customer went through stripe
    if "address_id" not in parsed_address or not parsed_address["address_id"]:
        return JsonResponse({"error": "There was a problem with your address, please contact <a href='mailto:rickpropas@comcast.net'>rickpropas@comcast.net</a>"})
    if request.POST["method"] == "card":
        charge_cents = int(100 * (float(items_total) +
                                  float(parsed_shipping["shipping"][0])))
        # catch exceptions returned by stripe API
        try:
            charge = stripe.Charge.create(
                amount=charge_cents,
                currency="usd",
                source=parsed_payment['stripeToken'][0],
                description="Charge for order to {}".format(
                    parsed_address['email'])
            )
            order_id = charge.id
        except stripe.InvalidRequestError as e:
            logger.error('there was a problem with stripe: {}'.format(e))
            logger.error(
                'there was a problem with stripe: {}'.format(e.message))
            return JsonResponse({"error": "There was a problem with your order, please contact <a href='mailto:rickpropas@comcast.net'>rickpropas@comcast.net</a>"})
    else:
        order_id = parsed_payment["id"]
    # this is the data we need to complete the order
    data = {
        "method": request.POST['method'],
        "order_id": order_id,
        "subtotal": items_total,
        "shipping": parsed_shipping["shipping"],
        "address_id": parsed_address["address_id"],
        "status": "pending",
        "items": items,
        "carrier": parsed_shipping["carrier"],
        "service": parsed_shipping["service"]
    }
    order = create_order(data)
    if not order:
        return JsonResponse({"error": "There was a problem with your order, please contact <a href='mailto:rickpropas@comcast.net'>rickpropas@comcast.net</a>"})
    request.session["order_id"] = order.id
    # send emails to owner and client
    email_res = send_emails(request, order)
    context = {
        "order": order,
        "message": "success!"
    }
    request.session["cart"] = []
    return render(request, "shop/success.html", context)


def create_order(data):
    address_id = data["address_id"][0]
    try:
        shipping_address = Address.objects.get(id=address_id)
    except Address.DoesNotExist:
        return None
    orderData = {
        "order_method": data["method"],
        "order_id": data["order_id"],
        "subtotal": data["subtotal"],
        "shipping": data["shipping"][0],
        "shipping_address": shipping_address,
        "status": "pending",
        "shipping_carrier": data["carrier"][0],
        "shipping_service": data["service"][0]
    }
    if not Order.objects.validate_create(orderData):
        return None
    order = Order.objects.create(**orderData)
    # add order id to each item just sold
    order.products.set(data["items"])
    Order.objects.update_sold_items(data['items'])
    return order


def send_emails(request, order):
    response = {}
    receiver = order.shipping_address.email
    subject = "Thank You for Your Penguin Pen Purchase"
    text = email_text(request, order, False)
    # send receipt
    receipt = requests.post(
        settings.MAILGUN_BASE_URL + "messages",
        auth=("api", settings.MAILGUN_PRIVATE_KEY),
        data={
            "from": settings.MAILGUN_SENDER,
            "to": [receiver],
            "subject": subject,
            "html": text
        }
    )
    order_subject = "You Made a Sale"
    order_text = email_text(request, order, True)
    if receipt.status_code != 200:
        response["error"] = "receipt"
        response["error_code"] = receipt.status_code
    # send email to owner notifying that package needs to be shipped.
    order_notification = requests.post(
        settings.MAILGUN_BASE_URL + "messages",
        auth=("api", settings.MAILGUN_PRIVATE_KEY),
        data={
            "from": settings.MAILGUN_SENDER,
            "to": ['Rick Propas <rickpropas@gmail.com>'],
            "subject": order_subject,
            "html": order_text
        }
    )
    if order_notification.status_code != 200:
        response["error"] = "order notification"
        response["error_code"] = order_notification.status_code
        order_notification = requests.post(
            settings.MAILGUN_BASE_URL + "messages",
            auth=("api", settings.MAILGUN_PRIVATE_KEY),
            data={
                "from": settings.MAILGUN_SENDER,
                "to": ["Anna Propas <apropas@gmail.com>"],
                "subject": "[urgent] Error!",
                "html": "Owner delivery email was not sent for order number {}. Please investigate further".format(order.id)
            }
        )
    # TODO: return success or error
    if "error" not in response:
        response["success"] = "all emails sent"
    return response


def email_text(request, order, seller):
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
    return render(request, "shop/email.html", context)
