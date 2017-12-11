from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^show/blog/(?P<id>\d+)$', views.index, name="blog")
]
