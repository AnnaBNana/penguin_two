import attr

from django.conf import settings
from django.db.models import Sum

from models import Product


@attr.s
class Cart(object):
    '''
    class representing the cart objects
    items: [int] of product ids
    session: django session obj
    '''
    request = attr.ib()
    session = attr.ib(init=False)
    item_ids = attr.ib(init=False)
    items = attr.ib(init=False)
    sold_items = attr.ib(init=False)
    total = attr.ib(init=False)
    special_packaging = attr.ib(init=False)

    def __attrs_post_init__(self):
        '''
        establish session
        get cart or assign empty list to cart if key does not exist
        '''
        self.session = self.request.session
        self.item_ids = self.session.get(settings.CART_SESSION_ID)
        if not self.item_ids:
            self.item_ids = self.session[settings.CART_SESSION_ID] = []

        all_items = self._get_items(self.item_ids)
        self.sold_items = all_items.filter(status='S')
        self.items = all_items.filter(status='A')

        if self.sold_items:
            sold_ids = [x for x in self.sold_items.values_list('id', flat=True)]
            self.remove(sold_ids)

        self.total = self._get_total()
        self.special_packaging = self._req_special_shipping(self.items)

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

    def _req_special_shipping(self, items):
        '''
        returns boolean to indicate whether package requires special shipping
        '''
        if len(self.item_ids) > 5:
            return True
        for item in items:
            if item.special_shipping:
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
