from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Sum, Count, Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.search import SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

from .forms import BillingAddressForm, AddressForm
from models import Pen, Knife, Image, Bulletin, Product, Order, Sale, Address

import stripe
import ssl
import easypost

import uuid
import os
from datetime import datetime, timedelta
import json
import operator
import requests
import urlparse

import logging


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, complex):
            return [obj.real, obj.imag]
        return json.JSONEncoder.default(self, obj)

# remind me why we need a UUID? Session stored locally????
# TODO: uncommment for production:
# SESSION_ID = str(uuid.uuid4())

# remove for production
# SESSION_ID = os.environ['TEST_ONLY_UUID']

stripe.api_key = os.environ['STRIPE_PRIVATE_KEY']
easypost.api_key = os.environ['EASYPOST_PRODUCTION_KEY']
MAILGUN_DOMAIN = "https://api.mailgun.net/v3/sandbox0586d32429d14009806d4cd0efa6313b.mailgun.org/messages"
MAILGUN_SENDER = "Rick Propas <rickpropas@comcast.net>"
MAILGUN_PRIVATE_KEY = os.environ['MAILGUN_PRIVATE_KEY']
MAILGUN_PUBLIC_KEY = os.environ['MAILGUN_PUBLIC_KEY']

# TODO: every time you select products, must check if they are sold or not

# ALL GET ROUTES

def index(request):
    if 'cart' not in request.session:
        request.session['cart'] = []
    today = datetime.now()
    month_ago = today - timedelta(days=int(30))
    all_products = Product.objects.filter(status='A').order_by('-created_at').prefetch_related('pen').prefetch_related('image')
    paginator = Paginator(all_products, 24)
    products = paginator.page(1)

    context = {
        'products': products,
        'bulletins': Bulletin.objects.filter(updated_at__range=(month_ago, today), active=True).order_by('-updated_at')[:3]
    }

    return render(request, 'shop/index.html', context)

def search(request):
    field = request.GET.get('filter')
    value = request.GET.get('value')
    page = request.GET.get('page')
    # TODO: datetime handling will need changing in production
    if field == 'recent':
        all_products = Product.objects.filter(status='A').order_by('-created_at').prefetch_related('image')
        headline = 'All Products'
    elif field == 'all':
        all_products = Product.objects.filter(status='A', knife__isnull=True).order_by('-updated_at').prefetch_related('image')
        headline = 'All Pens'
    elif field == 'shop':
        if value == 'other':
            make_list = ['pelikan', 'parker', 'montblanc', "waterman's"]
            query = reduce(operator.or_, (Q(make__iexact=x) for x in make_list))
            all_products = Product.objects.filter(status="A", knife__isnull=True).exclude(query).exclude(pen__country__iexact="it").exclude(pen__country__iexact="de").prefetch_related('image')
            headline = "Other Pens"
        elif value == "italian":
            all_products = Product.objects.filter(pen__country__iexact="it", status="A", knife__isnull=True).prefetch_related('image')
            headline = "Italian Pens"
        elif value == "german":
            germans = ["montblanc", "pelikan"]
            query = reduce(operator.or_, (Q(make__iexact=x) for x in germans))
            all_products = Product.objects.filter(pen__country__iexact="de", status="A", knife__isnull=True).exclude(query).prefetch_related("image")
            headline = "Other German Pens"
        else:
            print(value)
            all_products = Product.objects.filter(make__iexact=value, status="A", knife__isnull=True).order_by('-updated_at').prefetch_related('image').prefetch_related('image')
            headline = "Pens Manufactured by {}".format(value.capitalize())
    elif field == "price":
        if value == "high":
            all_products = Product.objects.filter(price__gt=600, status="A", knife__isnull=True).order_by('-updated_at').prefetch_related('image')
            phrase = "over $600"
        elif value == "low":
            all_products = Product.objects.filter(price__lt=200, status="A", knife__isnull=True).order_by('-updated_at').prefetch_related('image')
            phrase = "under $200"
        else:
            all_products = Product.objects.filter(price__lt=int(value), price__gt=int(value)-200, status="A", knife__isnull=True ).order_by('-updated_at').prefetch_related('image')
            phrase = "between ${} and ${}".format(str(int(value)-200), value)
        headline = "Pens {}".format(phrase)
    elif field == "other":
        if value == "knife":
            all_products = Product.objects.filter(status="A").exclude(knife__isnull=True).order_by('-updated_at').prefetch_related('image')
            headline = "Knives"
        if value == "sold":
            all_products = Product.objects.filter(status="S").order_by('-updated_at')
            headline = "Sold Items"
    elif field == "search":
        all_fields = get_all_search_fields()
        all_products = Product.objects.annotate(
           search=SearchVector(*all_fields),
          ).filter(search=value, status="A").order_by('-updated_at').prefetch_related('image')
        headline = "Search Results For: '{}'".format(value)
    paginator = Paginator(all_products, 24)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)
    context = {
        "products": products,
        "headline": headline,
        "filter": field, 
        "value": value
    }
    return render(request, 'shop/products.html', context)

def product(request,id):
    product = Product.objects.get(id=id)
    images = Image.objects.filter(product=product)
    context = {
        "product": product,
        "images": images,
    }
    return render(request, 'shop/product.html', context)


def news(request):
    bulletins = Bulletin.objects.filter(active=True)
    context = {
        "bulletins": bulletins,
    }
    return render(request, 'shop/news.html', context)

def show_cart(request):
    try:
        cart = request.session["cart"]
    except KeyError:
        request.session["cart"] = []
        cart = []
    items = Product.objects.filter(id__in=(cart)).prefetch_related("image")
    sold_items = items.filter(status="S")
    available = items.filter(status="A")
    sold_ids = [str(x) for x in sold_items.values_list("id", flat=True)]
    price = items.aggregate(Sum("price"))["price__sum"]
    context = {}
    if sold_items:
        context["error"] = "You waited too long! The following items were sold:"
        context["sold_items"] = sold_items
        for i in request.session["cart"]:
            if i in sold_ids:
                request.session["cart"].remove(i)
        request.session.modified = True
    context["items"] = available
    context["total"] = price
    return render(request, 'shop/cart.html', context)


def checkout(request):
    try:
        cart = request.session["cart"]
    except KeyError:
        request.session["cart"] = []
        cart = []
    if not cart:
        return redirect(reverse("shop:show_cart"))
    items = Product.objects.filter(id__in=(cart)).prefetch_related("image")
    sold_items = items.filter(status="S")
    available = items.filter(status="A")
    sold_ids = [str(x) for x in sold_items.values_list("id", flat=True)]
    price = items.aggregate(Sum("price"))["price__sum"]
    context = {}
    if sold_items:
        context["error"] = "You waited too long! The following items were sold:"
        context["sold_items"] = sold_items
        for i in request.session["cart"]:
            if i in sold_ids:
                request.session["cart"].remove(i)
        request.session.modified = True
    context["items"] = available
    context["total"] = price
    context["address_form"] = AddressForm()
    context["billing_form"] = BillingAddressForm()
    return render(request, 'shop/checkout.html', context)


def complete(request):
    order = Order.objects.get(id=17)
    context = {
        "order": order
    }
    return render(request, 'shop/success.html', context)

# REDIRECTS

def add_cart(request,id):
    if 'cart' in request.session and id not in request.session['cart']:
        request.session['cart'].append(id)
        request.session.modified = True
    elif 'cart' not in request.session:
        request.session['cart'] = [id]
    return redirect(reverse('shop:show_cart'))


def remove_cart(request,id):
    cart = request.session.get('cart', [])
    if id in cart:
        request.session['cart'].remove(id)
        request.session.modified = True
    return redirect(reverse('shop:show_cart'))

# JSON ROUTES

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
        name = "Rick Propas",
        street1 = "43739 Montrose Ave.",
        city = "Fremont",
        state = "CA",
        zip = "94538",
        country = "US",
        phone = "510-754-3278"
    )
    address = add_address(request, messages)
    # print "address after validation", address
    if 'shipping_address' in address:
        to_address = address['to_address']
        address_id = address['shipping_address'].id
    else:
        # return errors?
        # print "return errors"
        # print address
        return JsonResponse(address)
    data = {
        "item_ids": item_ids,
        "items": items,
        "to_address": to_address,
        "from_address": from_address
    }
    shipping_choices = get_shipping(request, data)
    context = {
        "total_cost": order_subtotal,
        "usps_shipment": shipping_choices["usps_shipment"], 
        "fedex_shipment": shipping_choices["fedex_shipment"],
        "all_options": shipping_choices["shipment"],
        "address_id": address_id,
        }
    return JsonResponse(context)

def order_handler(request):
    #kick user out of checkout if cart is empty
    logging.warn('the logging works!')
    try:
        cart = request.session['cart']
    except KeyError:
        request.session['cart'] = []
        return JsonResponse({"cart_empty":True})
    # payment must be handled differently if sent by paypal vs stripe
    try:
        parsed_payment = json.loads(request.POST["payment"])
    except ValueError:
        parsed_payment = urlparse.parse_qs(request.POST["payment"])
    # get all cart items as queryset
    items = Product.objects.filter(pk__in=cart)
    # get items total
    items_total = items.aggregate(Sum('price'))['price__sum']
    parsed_address = urlparse.parse_qs(request.POST['address'])
    parsed_shipping = urlparse.parse_qs(request.POST['shipping'])
    # the charge still remains to be completed if customer went through stripe
    if "address_id" not in parsed_address\
    or not parsed_address["address_id"]:
        return JsonResponse({"error": "There was a problem with your address, please contact <a href='mailto:rpropas@thepenguinpen.com'>rpropas@thepenguinpen.com</a>"})
    if request.POST["method"] == "card":
        charge_cents = int(100 * (float(items_total) + float(parsed_shipping["shipping"][0])))
        # catch exceptions returned by stripe API
        try:
            charge = stripe.Charge.create(
                amount=charge_cents,
                currency="usd",
                source=parsed_payment['stripeToken'][0],
                description="Charge for order to {}".format(parsed_address['email'])
            )
            order_id = charge.id
        except stripe.InvalidRequestError:
            return JsonResponse({"error": "There was a problem with your order, please contact <a href='mailto:rpropas@thepenguinpen.com'>rpropas@thepenguinpen.com</a>"})
    else:
        order_id = parsed_payment["id"]
    # this is the data we need to complete the order
    # print request.POST
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
    # print order
    # send emails to owner and client
    email_res = send_emails(request, order)
    context = {
        "order": order,
        "message": "success!"
    }
    request.session["cart"] = []
    return render(request, "shop/success.html", context)
    
def get_cart_total(request):
    try:
        cart = request.session['cart']
    except KeyError:
        request.session['cart'] = []
        return JsonResponse({'cart_empty': True})
    item_ids = request.session['cart']
    items = Product.objects.filter(pk__in=item_ids)
    context = {
        "total_cost": items.aggregate(Sum('price'))['price__sum']
    }
    return JsonResponse(context)

# helper functions
# helpers should be moved to model manager
def add_address(request, messages):
    flag = False
    response = requests.get(
        "https://api.mailgun.net/v3/address/validate", 
        params={'address': request.POST["email"],"mailbox_verification": True},
        auth=('api', MAILGUN_PUBLIC_KEY)
        )
    if response.status_code == 200:
        if not response.json().get("is_valid"):
            # print "failed validation"
            message = "Email invalid"
            if response.json().get("did_you_mean"):
                message += "; did you mean: {}".format(response.json().get("did_you_mean"))
            messages.append({"message": message, "field": "email"})
            flag = True
    try:
        to_address = easypost.Address.create(
            verify=["delivery"],
            name=request.POST["addressee"],
            email=request.POST["email"],
            street1 = request.POST["street"],
            street2 = request.POST["apt"],
            city = request.POST["city"],
            state = request.POST["state"],
            zip = request.POST["zip_code"],
            country = request.POST["country"],
            phone = request.POST["phone"]
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
                addressee = to_address.name,
                street = to_address.street1,
                apt = to_address.street2,
                city = to_address.city,
                state = to_address.state,
                zip_code = to_address.zip,
                country = to_address.country,
                phone = to_address.phone,
                email = to_address.email,
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
            weight = weight,
            carrier_accounts = "USPS",
            predefined_package = "SmallFlatRateBox"
        )
        usps_shipment = easypost.Shipment.create(
            to_address = to_address,
            from_address = from_address,
            parcel = usps_parcel
        )
        fedex_parcel =  easypost.Parcel.create(
            weight = weight,
            carrier_accounts = "FedEx",
            predefined_package = "FedExEnvelope"
        )
        fedex_shipment = easypost.Shipment.create(
            to_address = to_address,
            from_address = from_address,
            parcel = fedex_parcel
        )
        length = 8.625
        height = 5.375
        width = 1.625
    else:
        # print "irregular items present"
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
    parcel =  easypost.Parcel.create(
        weight = weight,
        length = length,
        height = height,
        width = width
    )
    shipment = easypost.Shipment.create(
        to_address = to_address,
        from_address = from_address,
        parcel = parcel
    )
    return {
        "shipment": shipment.to_json(), 
        "usps_shipment": usps_shipment.to_json() if usps_shipment else None,
        "fedex_shipment": fedex_shipment.to_json() if fedex_shipment else None
        }

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
        MAILGUN_DOMAIN,
        auth=("api", MAILGUN_PRIVATE_KEY),
        data={
            "from": MAILGUN_SENDER,
            "to": [receiver],
            "subject": subject,
            "html": text
        }
    )
    order_subject = "You Made a Sale"
    order_text = email_text(request, order, True)
    if receipt.status_code != 200:
        response["error"] = "receipt"
        response["error_code"] == receipt.status_code
    # send email to owner notifying that package needs to be shipped.
    order_notification = requests.post(
        MAILGUN_DOMAIN,
        auth=("api", MAILGUN_PRIVATE_KEY),
        data={
            "from": MAILGUN_SENDER,
            "to": [MAILGUN_SENDER],
            "subject": order_subject,
            "html": order_text
        }
    )
    if order_notification.status_code != 200:
        response["error"] = "order notification"
        response["error_code"] = order_notification.status_code
        order_notification = requests.post(
            MAILGUN_DOMAIN,
            auth=("api", MAILGUN_PRIVATE_KEY),
            data={
                "from": "Anna Propas <apropas@gmail.com>",
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
        thank_you = "These are great {} and this is a fine example.".format(item_type)
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


def get_all_search_fields():
    product_fields = Product._meta.get_fields()
    product_field_names = [field.name for field in product_fields if field.get_internal_type() == "CharField" or field.get_internal_type() == "TextField"]
    pen_fields = Pen._meta.get_fields()
    pen_field_names = ["pen__" + field.name for field in pen_fields if field.get_internal_type() == "CharField" or field.get_internal_type() == "TextField"]
    knife_fields = Knife._meta.get_fields()
    knife_field_names = ["knife__" + field.name for field in knife_fields if field.get_internal_type() == "CharField" or field.get_internal_type() == "TextField"]
    return product_field_names + pen_field_names + knife_field_names
