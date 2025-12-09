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
from django.views.generic import RedirectView
from django.urls import path, include
from rannaghoreprotidinapp import views as s_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Home and About
    path('', s_views.home, name='home'),
    path('about_us/', s_views.about_us, name='about_us'),

    # Authentication
    path('sing_in/', s_views.sing_in, name='sing_in'),
    path('sing_up/', s_views.sing_up, name='sing_up'),
    path('logout/', s_views.sing_out_view, name='logout'),

    # Products
    path('all_products/', s_views.all_products, name='all_products'),
    path('product/<uuid:p_id>/', s_views.product_details, name='product_details'),

    # Cart and Orders (FIXED - using UUID for product IDs)
    path('cart/', s_views.cart_view, name='cart'),
    path('cart/add/<uuid:p_id>/', s_views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_id>/', s_views.remove_from_cart, name='remove_from_cart'),
    path('buy_now/<uuid:p_id>/', s_views.buy_now, name='buy_now'),
    path('process-order/', s_views.process_order, name='process_order'),
    path('order-confirmation/<int:order_id>/', s_views.order_confirmation, name='order_confirmation'),

    # Help & Support
    path('help_support/', s_views.help_support, name='help_support'),
    path('submit-support-ticket/', s_views.submit_support_ticket, name='submit_support_ticket'),
    path('track-ticket/', s_views.track_ticket, name='track_ticket'),
    path('close-ticket/<int:ticket_id>/', s_views.close_ticket, name='close_ticket'),
    path('rate-support/<int:ticket_id>/', s_views.rate_support, name='rate_support'),

    # AJAX endpoints
    path('search-faqs/', s_views.search_faqs, name='search_faqs'),
    path('get-faqs-by-category/', s_views.get_faqs_by_category, name='get_faqs_by_category'),

    # Favicon
    path("favicon.ico", RedirectView.as_view(url="/static/assets/favicon.ico")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)