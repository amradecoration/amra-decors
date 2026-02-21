"""
URL configuration for api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.contrib import admin
from django.conf.urls import handler404
from django.conf.urls.static import static


from store.views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('about/', about_view, name='about'),
    path('services/', services_view, name='services'),
    path('products/', products_view, name='products'),
    path('products/<str:slug>', products_view, name='products'),
    path('product-detail/', product_detail_view, name='product-detail'),
    path('product-detail/<int:id>', product_detail_view, name='product-detail'),
    path('contact/', contact_view, name='contact'),
    path('admin', admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'store.views.custom_404_view'
