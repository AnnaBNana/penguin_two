from django.contrib import admin
from .models import Image, Pen, Make, Nib, Knife, Bulletin
from django.contrib.contenttypes.admin import GenericTabularInline
from django_summernote.admin import SummernoteModelAdmin

class ImageInline(GenericTabularInline):
    model = Image
    fields = ('file', 'image_thumb')
    readonly_fields = ('image_thumb',)

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
admin.site.register(Nib)
admin.site.register(Knife, KnifeAdmin)
admin.site.register(Bulletin, BulletinAdmin)
