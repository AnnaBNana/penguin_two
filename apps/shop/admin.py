from django.contrib import admin
from .models import Product, Image, Pen, Knife, Bulletin, Order, Sale, Address
from django.contrib.contenttypes.admin import GenericTabularInline
from django_summernote.admin import SummernoteModelAdmin
from sorl.thumbnail.admin import AdminImageMixin
from .forms import SaleAdminForm, ProductAdminForm, PenAdminForm

# helper functions 
def obj_display(obj):
    return "#{}: {} {}".format(obj.id, obj.make, obj.model)

def mark_sold(modeladmin, request, queryset):
    queryset.update(status="S")
mark_sold.short_description = "Mark selected products sold"

def mark_for_sale(modeladmin, request, queryset):
    queryset.update(status="A")
mark_for_sale.short_description = "Mark selected products for sale"

# product inlines
class ImageInline(AdminImageMixin, admin.TabularInline):
    model = Image


class PenInline(admin.StackedInline):
    form = PenAdminForm
    model = Pen
    verbose_name_plural = "Pen Details"
    max_num = 1


class KnifeInline(admin.StackedInline):
    classes = ['collapse']
    model = Knife
    verbose_name_plural = "Knife Details"
    max_num = 1


class ProductAdmin(SummernoteModelAdmin):
    form = ProductAdminForm
    ordering = ('-updated_at',)
    fieldsets = (
        (None, {
            'fields': ('make', 'model', 'condition', 'flaws', 'special_shipping', 'length', 'width', 'depth', 'weight', 'price', 'description')
        }),
        ('Purchase Information', {
            'fields': ('purchase_source', 'purchase_date', 'cost')
        }),
        ('Stocking Information', {
            'fields': ('in_stock', 'status', 'sold_date', 'sale')
        }),
    )
    inlines = [
        PenInline,
        ImageInline,
        KnifeInline, 
    ]
    exclude = ('order',)
    search_fields = [
        "id",
        "^make", 
        "^model", 
        "^condition", 
        "flaws",
        "purchase_source",
        "^purchase_date",
        "^status",
        "description",
        "sale__headline",
        "order__id",
        "pen__year",
        "pen__id",
        "pen__country",
        "pen__cap_color",
        "pen__body_color",
        "pen__nib_description",
        "pen__nib_make",
        "pen__nib_grade",
        "pen__nib_material",
        "pen__nib_flexibility",
    ]
    list_filter = [
        "make",
        "status",
        "pen__year",
    ]
    list_display = (obj_display,)
    actions = [
        mark_for_sale,
        mark_sold
    ]

# order inline
class AddressInline(admin.StackedInline):
    model = Address
    verbose_name_plural = "Address Details"
    min_num = 1
    max_num = 1


class ProductInline(admin.TabularInline):
    model = Product
    fields = ['id','make','model']
    readonly_fields = ['id','make','model']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    ordering = ('-created_at',)
    inlines = [
        ProductInline
    ]
    search_fields = [
        "order_method",
        "order_id",
        "subtotal",
        "shipping",
        "shipping_address__addressee",
        "shipping_address__street",
        "shipping_address__apt",
        "shipping_address__city",
        "shipping_address__state",
        "shipping_address__zip_code",
        "shipping_address__country",
        "shipping_address__phone",
        "shipping_address__email",
        "status",
        "created_at"
    ]
    list_filter = [
        "created_at",
        "order_method",
        "status",
    ]


class SaleAdmin(admin.ModelAdmin):
    form = SaleAdminForm
    search_fields = [
        "headline"
    ]


class BulletinAdmin(SummernoteModelAdmin):
    search_fields = [
        "headline",
        "text"
    ]

admin.site.register(Bulletin, BulletinAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Sale, SaleAdmin)
