"""
URL configuration for RannaghoreProtidin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path
from rannaghoreprotidinapp import views as s_views
from django.urls import include,path
from . import settings

urlpatterns = [
    path('admin/',admin.site.urls),
    path('', s_views.home, name='home'),
    path('about_us/',s_views.about_us, name='about_us'),

    path('sing_in/',s_views.sing_in, name='sing_in'),

    path('sing_up/',s_views.sing_up, name='sing_up'),

    path('<str:id>',s_views.product_details, name = 'product_details'),

    path('product/<uuid:p_id>/', s_views.product_details, name='product_details'),


]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
