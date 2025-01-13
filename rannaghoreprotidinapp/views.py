from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, template_name='shop/home.html')
def about_us(request):
    return render(request, template_name='shop/about_us.html')

def sing_in(request):
    return render(request, template_name='SingIn_SingUp/sing_in.html')

def sing_up(request):
    return render(request, template_name='SingIn_SingUp/sing_up.html')
