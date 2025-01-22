from itertools import product

from django.shortcuts import render
from django.template import Context
from .models import *

# Create your views here.

def home(request):
    products=Products.objects.all()
    context={
        'products' : products,
    }
    return render(request, template_name='shop/home.html', context=context)

def product_details(request,id):
    products = Products.objects.get(pk = id)
    context = {
        'product':product,
    }
    return render(request,template_name = 'shop\product_details.html',context = context)


def about_us(request):
    return render(request, template_name='shop/about_us.html')

def sing_in(request):
    return render(request, template_name='SingIn_SingUp/sing_in.html')

def sing_up(request):
    return render(request, template_name='SingIn_SingUp/sing_up.html')
