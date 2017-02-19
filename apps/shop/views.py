from django.shortcuts import render
from models import Pen, Knife, Image
from django.contrib.contenttypes.models import ContentType

# Create your views here.
def index(request):
    context = {
        "products": Pen.objects.all().order_by('created_at')[:24]
    }
    return render(request, 'shop/index.html', context)
