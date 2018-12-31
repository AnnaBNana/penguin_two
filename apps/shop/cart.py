from django.conf import settings
from django.db.models import Sum

from models import Product

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
        items = self.session.get(settings.CART_SESSION_ID)
        if not items:
            items = self.session[settings.CART_SESSION_ID] = []
        self.items = items

    def add(self, product_id):
        '''
        add id to items list
        raise ValueError if product_id is not int
        '''
        if not isinstance(product_id, int):
            raise ValueError
        if product_id not in self.items:
            self.items.append(product_id)
            self.save()

    def save(self):
        '''
        updates session with obj values
        flags session as modified
        '''
        self.session[settings.CART_SESSION_ID] = self.items
        self.session.modified = True

    def remove(self, product_ids):
        '''
        product_ids: [int]
        removes product ids from items array
        '''
        for product_id in product_ids:
            if not isinstance(product_id, int):
                raise ValueError
            if product_id in self.items:
                self.items.remove(product_id)
                self.save()
        print self.items

    def total(self):
        '''
        get total price of items in items list
        '''
        items = Product.objects.filter(id__in=(self.items))
        return items.aggregate(Sum('price'))['price__sum']

    def get_items(self):
        '''
        get available and sold items, return tuple
        '''
        items = Product.objects.filter(
                id__in=(self.items)).prefetch_related('image')
        sold_items = items.filter(status='S')
        avail_items = items.filter(status='A')

        return avail_items, sold_items

    def create_cart_context(self):
        '''
        get items, remove sold items, return context dict for views
        shared functionality between show cart and checkout
        '''
        avail_items, sold_items = self.get_items()

        if sold_items:
            sold_ids = [x for x in sold_items.values_list('id', flat=True)]
            self.remove(sold_ids)

        context = {
            'items': avail_items,
            'total': self.total(),
            'sold_items': sold_items
        }

        return context 







