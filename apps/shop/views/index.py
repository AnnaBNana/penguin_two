from datetime import (
    datetime,
    timedelta
)

from django.shortcuts import (
    render,
    redirect
)
from django.urls import reverse

from ..models import (
    Bulletin,
    Product,
    VacationSettings
)
from django.core.paginator import Paginator


def index(request):
    vacation_settings = VacationSettings.load()

    if 'cart' not in request.session:
        request.session['cart'] = []

    if vacation_settings.active:
        return redirect(reverse('shop:vacation'))
    else:
        return redirect(reverse('shop:main'))


def vacation_index(request):
    return render(request, 'shop/temp_index.html')


def main_index(request):
    today = datetime.now()
    month_ago = today - timedelta(days=int(30))
    all_products = Product.objects.filter(status='A').order_by('-created_at').prefetch_related('pen').prefetch_related('image')
    paginator = Paginator(all_products, 24)
    products = paginator.page(1)
    context = {
        'products': products,
        'bulletins': Bulletin.objects.filter(updated_at__range=(month_ago, today), active=True).order_by('-updated_at')[:1]
    }

    return render(request, 'shop/index.html', context)


def news(request):
    bulletins = Bulletin.objects.filter(active=True).order_by('-updated_at')
    context = {
        "bulletins": bulletins,
    }
    return render(request, 'shop/news.html', context)


def not_found(request):
    return render(request, 'shop/404.html')
