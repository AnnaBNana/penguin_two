from django.shortcuts import render
from models import Pen, Knife, Image
from django.contrib.contenttypes.models import ContentType

# Create your views here.
def index(request):
    context = {
        "products": Pen.objects.all().order_by('created_at')[:24].prefetch_related('images')
    }
    return render(request, 'shop/index.html', context)

def product(request,model,id):
    product = eval(model).objects.get(id=id)
    images = Image.objects.filter(object_id=product.id, content_type=ContentType.objects.get_for_model(eval(model)))
    context = {
        "product": product,
        "images": images,
    }
    return render(request, 'shop/pen.html', context)
