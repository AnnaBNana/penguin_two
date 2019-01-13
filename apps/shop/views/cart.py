from django.shortcuts import redirect, render
from django.urls import reverse
from django.http import JsonResponse

from ..cart import Cart


def add_cart(request, product_id):
    '''
    view method to add an item to user's cart
    '''
    cart = Cart(request)
    cart.add(int(product_id))
    return redirect(reverse('shop:show_cart'))

def remove_cart(request, product_id):
    '''
    remove item from shopping cart
    '''
    cart = Cart(request)
    cart.remove([int(product_id)])
    return redirect(reverse('shop:show_cart'))

def get_cart_total(request):
    '''
    view method to get total shopping cart items' value
    '''
    cart = Cart(request)
    context = {
        "total_cost": cart.total()
    }
    return JsonResponse(context)


def show_cart(request):
    '''
    get cart contents
    remove any sold items
    render cart
    '''
    cart = Cart(request)
    context = cart.create_cart_context()
    return render(request, 'shop/cart.html', context)
