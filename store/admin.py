from django import forms
from django.db import models
from django.contrib import admin

# Register your models here.
from .models import Categories, Coupons, Roles, Profile, Products, Slide, Banner

class CategoriesAdmin(admin.ModelAdmin):
	list_display = ('name', 'parent', 'active', 'menu', 'created_at')
	prepopulated_fields = {"slug": ("name",)}
	list_filter = ('active', 'parent')
	search_fields = ('name',)

class CouponsAdmin(admin.ModelAdmin):
    list_display = ('code', 'coupon_type', 'discount_value', 'active', 'valid_from', 'valid_to', 'usage_limit', 'used_count')
    list_filter = ('active', 'coupon_type', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')

class RolesAdmin(admin.ModelAdmin):
	list_display = ('name', 'active', 'created_at')
	list_filter = ('active',)
	search_fields = ('name',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone_number', 'city', 'state', 'country', 'email_verified', 'phone_verified')
    list_filter = ('role', 'email_verified', 'phone_verified', 'city', 'state', 'country')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city', 'state', 'country')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('user', 'role', 'phone_number', 'profile_image')
        }),
        ('Personal Info', {
            'fields': ('date_of_birth', 'gender')
        }),
        ('Address', {
            'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Verification', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

def get_category_choices(categories, level=0):
    choices = []
    indent = "— " * level
    for category in categories:
        choices.append((category.id, f"{indent}{category.name}"))
        children = category.children.all()
        if children.exists():
            choices += get_category_choices(children, level + 1)
    return choices

class CategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        # Flat queryset for validation — all categories
        queryset = kwargs.pop('queryset', Categories.objects.all())
        
        # Choices with indentation — only top-level parents to start recursion
        choices = get_category_choices(Categories.objects.filter(parent__isnull=True))
        
        super().__init__(queryset=queryset, *args, **kwargs)
        self.choices = choices

class ProductAdminForm(forms.ModelForm):
    categories = CategoryMultipleChoiceField(
        queryset=Categories.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'size': '15',
            'style': 'width: 775px;'  # increase width here
        })
    )

    class Meta:
        model = Products
        fields = '__all__'

class ProductsAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('code', 'name', 'get_categories', 'price', 'discount_price', 'active', 'created_at')
    list_filter = ('active', 'categories')
    search_fields = ('code', 'name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # filter_horizontal = ('categories',)  # makes multi-select nicer in admin

    readonly_fields = ('created_at', 'updated_at')
    
    def get_categories(self, obj):
        return ", ".join(category.name for category in obj.categories.all())
    get_categories.short_description = 'Categories'  # This sets the column header

class SlideInline(admin.TabularInline):
    model = Slide
    extra = 1  # Number of empty slides to show by default
    fields = ['title', 'subtitle', 'description', 'button_text', 'link', 'order', 'image']

class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    inlines = [SlideInline]

class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'slide_type', 'order', 'created_at')
    search_fields = ('title', 'slide_type')

    formfield_overrides = {
        models.ImageField: {'label': 'Image (Max 1MB)'},
        models.FileField: {'label': 'Video (Max 5MB)'},
    }

    def get_fieldsets(self, request, obj=None):
        common_fields = ('slide_type', 'title', 'order')

        if obj:
            if obj.slide_type == 'default':
                return (
                    (None, {'fields': common_fields + (
                        'subtitle', 'description', 'button_text', 'link', 'image'
                    )}),
                )
            elif obj.slide_type == 'image':
                return (
                    (None, {'fields': common_fields + ('image', 'link')}),
                )
            elif obj.slide_type == 'video':
                return (
                    (None, {'fields': common_fields + ('video',)}),
                )

        # Fallback during creation
        return (
            (None, {'fields': ('slide_type', 'title', 'order')}),
        )

    def save_model(self, request, obj, form, change):
        if not obj.banner_id:
            obj.banner_id = 1
        super().save_model(request, obj, form, change)


admin.site.register(Banner, BannerAdmin)
admin.site.register(Categories, CategoriesAdmin)
# admin.site.register(Coupons, CouponsAdmin)
admin.site.register(Roles, RolesAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Slide, SlideAdmin)