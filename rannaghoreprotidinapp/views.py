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
from .models import Products, Order

# Create your views here.

def home(request):
    products=Products.objects.all()
    context={
        'products' : products,
    }
    return render(request, template_name='shop/home.html', context=context)

def product_details(request, p_id):
    product = get_object_or_404(Products, p_id=p_id)
    return render(request, 'shop/product_details.html', {'p': product})


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

def add_to_cart(request):
    return render(request, template_name='shop/cart.html')
# Logout View
@login_required
def sing_out_view(request):
    logout(request)
    return redirect('sing_in')  # Redirect to login page after logout

@login_required
def order_page(request, p_id):
    try:
        product = Products.objects.get(id=p_id)
    except Products.DoesNotExist:
        return redirect('home')  # Redirect if product doesn't exist

    # Generate Order Number (Example: RP-0001)
    order_number = f"RP-{Order.objects.count() + 1:04d}"

    # Pass data to the template
    context = {
        'user_name': request.user.username,
        'order_number': order_number,
        'product_name': product.name,
        'quantity': 1,  # Default quantity
        'status': 'Ordered'  # Default status
    }

    return render(request, 'shop/order.html', context)


@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    unique_product_count = cart_items.count()  # Counting unique products

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'unique_product_count': unique_product_count
    })


@login_required
def add_to_cart(request, p_id):
    product = Products.objects.get(id=p_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, p=product)

    if not created:
        cart_item.quantity += 1  # Increase quantity if already exists
        cart_item.save()

    return redirect('cart')


@login_required
def remove_from_cart(request, cart_id):
    cart_item = Cart.objects.get(id=cart_id, user=request.user)
    cart_item.delete()
    return redirect('cart')

