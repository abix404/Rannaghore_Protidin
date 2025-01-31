from itertools import product
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from django.template import Context
from .models import *

# Create your views here.

def home(request):
    products=Products.objects.all()
    context={
        'products' : products,
    }
    return render(request, template_name='shop/home.html', context=context)

def product_details(request, p_id):
    products = get_object_or_404(Products, p_id=p_id)
    return render(request, "shop/product_details.html", {"product": product})


def about_us(request):
    return render(request, template_name='shop/about_us.html')

def sing_in(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to homepage after login
    else:
        form = AuthenticationForm()
    return render(request, 'SingIn_SingUp/sing_in.html', {'form': form})

def sing_up(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sing_in')  # Redirect to login page after successful signup
    else:
        form = SignupForm()
    return render(request, 'SingIn_SingUp/sing_up.html', {'form': form})


# Logout View
@login_required
def sing_out_view(request):
    logout(request)
    return redirect('sing_in')  # Redirect to login page after logout
