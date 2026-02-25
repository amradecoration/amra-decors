from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect


# Create your views here.
from .models import *

def get_active_categories():
    return Categories.objects.filter(active=True)

def home_view(request):
    all_products = Products.objects.filter(active=True).order_by('-id')
    categories = Categories.objects.filter(active=True).prefetch_related(
        Prefetch('products', queryset=all_products, to_attr='ordered_products')
    )
    banner = Banner.objects.first()
    testimonials = Testimonial.objects.all()

    page_data = {
        'page_name': 'home',
        'page_title': 'Amra Decoration | Transforming Ideas into Timeless Decor',
        'categories': categories,
        'all_products': all_products,
        'banner': banner,
        'testimonials': testimonials,
    }

    return render(request, 'home.html', page_data)

def about_view(request):
    categories = get_active_categories()

    page_data = {
        'page_name': 'about',
        'categories': categories,
    }
    
    return render(request, 'about.html', page_data)

def services_view(request):
    categories = get_active_categories()

    page_data = {
        'page_name': 'services',
        'page_title': 'Services',
        'categories': categories,
    }
    
    return render(request, 'services.html', page_data)

def products_view(request, slug=''):
    if slug:
        category = Categories.objects.filter(slug=slug).first()
        if category:
            products = Products.objects.filter(categories__in=[category], active=True).order_by('-id')
            page_title = f'{category.name} | Amra Decorations'
        else:
            return redirect('products')
    else:
        products = Products.objects.filter(active=True).order_by('-id')
        page_title = 'Products | Amra Decorations'
    
    categories = get_active_categories()

    page_data = {
        'page_name': 'products',
        'page_title': page_title,
        'products': products,
        'categories': categories,
    }
    
    return render(request, 'products.html', page_data)

def product_detail_view(request, id=''):
    categories = get_active_categories()

    if id:
        product = Products.objects.get(id=id)
        page_title = f'{product.name} | Amra Decorations'
    else:
        return redirect('home')

    page_data = {
        'page_name': 'product-detail',
        'page_title': page_title,
        'product': product,
        'categories': categories,
    }
    
    return render(request, 'product-detail.html', page_data)

def contact_view(request):
    categories = get_active_categories()

    page_data = {
        'page_name': 'contact',
        'page_title': 'Contact | Amra Decorations',
        'categories': categories,
    }
    
    return render(request, 'contact.html', page_data)

def login_view(request):
    categories = get_active_categories()

    page_data = {
        'page_name': 'login',
        'page_title': 'Login | Amra Decorations',
        'categories': categories,
    }
    
    return render(request, 'login.html', page_data)

def custom_404_view(request, exception):
    categories = get_active_categories()
    
    page_data = {
        'page_name': '404',
        'page_title': 'Page not found | Amra Decorations',
        'categories': categories,
    }
    
    return render(request, '404.html', page_data, status=404)
