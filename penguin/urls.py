from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles import views
import os
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('apps.shop.urls', namespace='shop')),
    url(r'^learn/', include('apps.learn.urls', namespace='learn')),
    url(r'^blog/', include('apps.blog.urls', namespace='blog')),
    url(r'^summernote/', include('django_summernote.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)