import attr

from django.conf import settings
from django.db.models import Sum

from models import Product
from fixtures import SHIPPING_OPTIONS


LOCALES = {
    'domestic': 'US',
    'canada': 'CA'
}


@attr.s
class ShippingOptions(object):
    locale = attr.ib(kw_only=True)
    order_size = attr.ib(kw_only=True)
    order_size_cat = attr.ib(init=False)
    options = attr.ib(init=False)

    all_shipping_options = SHIPPING_OPTIONS

    def __attrs_post_init__(self):
        self.order_size_cat = self._set_order_size_cat()
        self.options = self._set_options()

    def _set_order_size_cat(self):
        if self.order_size <= 5:
            return 'lte5'
        else:
            return 'gt5'

    def _set_options(self):
        locale_options = self.all_shipping_options.get(self.locale)
        if locale_options:
            return locale_options.get(self.order_size_cat)
        else:
            return None


@attr.s
class Address(object):
    phone_number = attr.ib()
    email = attr.ib()
    street = attr.ib()
    apt = attr.ib()
    city = attr.ib()
    state = attr.ib()
    zip_code = attr.ib()
    country = attr.ib()

    def get_shipping_options(self, cart):
        locale_name = LOCALES.get(self.country, 'international')
        return ShippingOptions(locale=locale_name, order_size=len(cart.item_ids))


class Cart:
    '''
    class representing the cart objects
    items: [int] of product ids
    session: django session obj
    '''
    def __init__(self, request):
        '''
        establish session
        get cart or assign empty list to cart if key does not exist
        '''
        self.session = request.session
        self.item_ids = self.session.get(settings.CART_SESSION_ID)
        if not self.item_ids:
            self.item_ids = self.session[settings.CART_SESSION_ID] = []

        all_items = self._get_items(self.item_ids)
        self.sold_items = all_items.filter(status='S')
        items = all_items.filter(status='A')

        if self.sold_items:
            sold_ids = [x for x in self.sold_items.values_list('id', flat=True)]
            self.remove(sold_ids)

        self.total = self._get_total()
        self.special_packaging = self._req_special_packaging(items)
        self.context = {'items': items, 'total': self.total}

    def _get_items(self, item_ids):
        '''
        get all items in cart
        '''
        return Product.objects.filter(
            id__in=(item_ids)
        ).prefetch_related('image')

    def _get_total(self):
        '''
        get total price of items in items list
        '''
        items = Product.objects.filter(id__in=(self.item_ids))
        return items.aggregate(Sum('price'))['price__sum']

    def _req_special_packaging(self, items):
        '''
        returns boolean to indicate whether package requires special shipping
        '''
        if len(self.item_ids) > 5:
            return True
        for item in items:
            if item.special_packaging:
                return True
        return False

    def _save(self):
        '''
        updates session with obj values
        flags session as modified
        '''
        self.session[settings.CART_SESSION_ID] = self.item_ids
        self.session.modified = True

    def add(self, product_id):
        '''
        add id to items list
        raise ValueError if product_id is not int
        '''
        if not isinstance(product_id, int):
            raise ValueError
        if product_id not in self.item_ids:
            self.item_ids.append(product_id)
            self._save()

    def remove(self, product_ids):
        '''
        product_ids: [int]
        removes product ids from items array
        '''
        for product_id in product_ids:
            if not isinstance(product_id, int):
                raise ValueError
            if product_id in self.item_ids:
                self.item_ids.remove(product_id)
                self._save()
