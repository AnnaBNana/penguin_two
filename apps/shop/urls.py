from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^show/product/(?P<model>\w+)/(?P<id>\d+)$', views.product, name='show_product')
]
