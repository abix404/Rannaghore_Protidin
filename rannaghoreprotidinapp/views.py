from django.shortcuts import render

# Create your views here.

def home(request):
    return render(request, template_name='home.html')
def about_us(request):
    return render(request, template_name='about_us.html')
