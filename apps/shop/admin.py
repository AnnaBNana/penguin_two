import unicodedata
from django.contrib import admin
from django.utils import timezone
from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.contrib.admin.views.main import ChangeList

from .models import (
    Product,
    Image,
    Pen,
    Knife,
    Bulletin,
    Order,
    Sale,
    Address,
    VacationSettings,
    SalesSummaryPanel,
    ShippingOptions
)
from django.contrib.contenttypes.admin import GenericTabularInline
from django_summernote.admin import SummernoteModelAdmin
from sorl.thumbnail.admin import AdminImageMixin
from .forms import SaleAdminForm, ProductAdminForm, PenAdminForm
from .list_filters import MonthFilter

# helper functions 
def product(obj):
    return "#{}: {} {}".format(
        obj.id, 
        unicodedata.normalize('NFKD', obj.make).encode('ascii', 'ignore'),
        unicodedata.normalize('NFKD', obj.model).encode('ascii', 'ignore')
    )

def net_revenue(obj):
    return obj.price - obj.cost

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
        "status",
        "purchase_date",
        "make"
    ]
    list_display = (product, 'sold_date', 'cost', 'price', net_revenue)
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
    readonly_fields = ['id']
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


class VacationSettingsAdmin(admin.ModelAdmin):
    actions = None
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SalesSummaryPanelAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sales_summary_panel_change_list.html'
    ordering = ('-sold_date', 'id')
    list_filter = [
        MonthFilter
        ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super(SalesSummaryPanelAdmin, self).changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        sold_products = qs.filter(status="S").annotate(net_rev=F('price') - F('cost'))
        month_summary = (sold_products
            .annotate(sold_month=ExtractMonth('sold_date'))
            .annotate(sold_year=ExtractYear('sold_date'))
            .values('sold_month', 'sold_year')
            .annotate(total_revenue=Sum(F('price') - F('cost')))
            .order_by()
        )
        totals = sold_products.aggregate(total_revenue=Sum(F('price') - F('cost')), total_cost=Sum('cost'), total_price=Sum('price'))
        response.context_data['sold_products'] = sold_products
        response.context_data['totals'] = totals
        response.context_data['month_summary'] = month_summary

        return response


class ShippingOptionsAdmin(SummernoteModelAdmin):
    model = ShippingOptions


class AddressAdmin(SummernoteModelAdmin):
    model = Address


admin.site.register(Bulletin, BulletinAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Sale, SaleAdmin)
admin.site.register(VacationSettings, VacationSettingsAdmin)
admin.site.register(SalesSummaryPanel, SalesSummaryPanelAdmin)
admin.site.register(ShippingOptions, ShippingOptionsAdmin)
admin.site.register(Address, AddressAdmin)
