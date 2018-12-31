import operator
from datetime import datetime

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.postgres.search import SearchVector
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)

from ..models import (
    Product,
    Pen,
    Knife,
    VacationSettings,
    Image
)


def product(request, id):
    vacation_settings = VacationSettings.load()
    product = Product.objects.get(id=id)
    images = Image.objects.filter(product=product)
    end = vacation_settings.end_date
    begin = datetime.now().date()
    weeks = (end-begin).days//7
    vacation_message = 'Expect a minimum shipping delay of {} weeks.'.format(
        weeks)
    context = {
        "product": product,
        "images": images,
        "vacation_message": vacation_message
    }
    return render(request, 'shop/product.html', context)


# perform filter and render products page
def search(request):
    field = request.GET.get('filter')
    value = request.GET.get('value')
    page = request.GET.get('page')
    # TODO: datetime handling will need changing in production
    if field == 'recent':
        all_products = Product.objects.filter(status='A').order_by(
            '-created_at').prefetch_related('image')
        headline = 'All Products'
    elif field == 'all':
        all_products = Product.objects.filter(status='A', knife__isnull=True).order_by(
            '-updated_at').prefetch_related('image')
        headline = 'All Pens'
    elif field == 'shop':
        if value == 'other':
            make_list = ['pelikan', 'parker', 'montblanc', "waterman's"]
            query = reduce(operator.or_, (Q(make__iexact=x)
                                          for x in make_list))
            all_products = Product.objects.filter(status="A", knife__isnull=True).exclude(query).exclude(
                pen__country__iexact="it").exclude(pen__country__iexact="de").prefetch_related('image')
            headline = "Other Pens"
        elif value == "italian":
            all_products = Product.objects.filter(
                pen__country__iexact="it", status="A", knife__isnull=True).prefetch_related('image')
            headline = "Italian Pens"
        elif value == "german":
            germans = ["montblanc", "pelikan"]
            query = reduce(operator.or_, (Q(make__iexact=x) for x in germans))
            all_products = Product.objects.filter(
                pen__country__iexact="de", status="A", knife__isnull=True).exclude(query).prefetch_related("image")
            headline = "Other German Pens"
        else:
            all_products = Product.objects.filter(make__iexact=value, status="A", knife__isnull=True).order_by(
                '-updated_at').prefetch_related('image').prefetch_related('image')
            headline = "Pens Manufactured by {}".format(value.capitalize())
    elif field == "price":
        if value == "high":
            all_products = Product.objects.filter(price__gt=600, status="A", knife__isnull=True).order_by(
                '-updated_at').prefetch_related('image')
            phrase = "over $600"
        elif value == "low":
            all_products = Product.objects.filter(price__lt=200, status="A", knife__isnull=True).order_by(
                '-updated_at').prefetch_related('image')
            phrase = "under $200"
        else:
            all_products = Product.objects.filter(price__lt=int(value), price__gt=int(
                value)-200, status="A", knife__isnull=True).order_by('-updated_at').prefetch_related('image')
            phrase = "between ${} and ${}".format(str(int(value)-200), value)
        headline = "Pens {}".format(phrase)
    elif field == "other":
        if value == "knife":
            all_products = Product.objects.filter(status="A").exclude(
                knife__isnull=True).order_by('-updated_at').prefetch_related('image')
            headline = "Knives"
        if value == "sold":
            all_products = Product.objects.filter(
                status="S").order_by('-updated_at')
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


def get_all_search_fields():
    product_fields = Product._meta.get_fields()
    product_field_names = [field.name for field in product_fields if field.get_internal_type(
    ) == "CharField" or field.get_internal_type() == "TextField"]
    pen_fields = Pen._meta.get_fields()
    pen_field_names = ["pen__" + field.name for field in pen_fields if field.get_internal_type(
    ) == "CharField" or field.get_internal_type() == "TextField"]
    knife_fields = Knife._meta.get_fields()
    knife_field_names = ["knife__" + field.name for field in knife_fields if field.get_internal_type(
    ) == "CharField" or field.get_internal_type() == "TextField"]
    return product_field_names + pen_field_names + knife_field_names
