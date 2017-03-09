from django.contrib import admin
from .models import Image, Pen, Make, Knife, Bulletin
from django.contrib.contenttypes.admin import GenericTabularInline
from django_summernote.admin import SummernoteModelAdmin
from sorl.thumbnail.admin import AdminImageMixin

class ImageInline(AdminImageMixin, GenericTabularInline):
    model = Image

class PenAdmin(SummernoteModelAdmin):
    inlines = [
        ImageInline,
    ]

class BulletinAdmin(SummernoteModelAdmin):
    pass

class KnifeAdmin(SummernoteModelAdmin):
    pass

admin.site.register(Pen, PenAdmin)
admin.site.register(Make)
admin.site.register(Knife, KnifeAdmin)
admin.site.register(Bulletin, BulletinAdmin)
