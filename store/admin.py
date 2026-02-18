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
        (None, {'fields': ('user', 'role', 'phone_number', 'profile_image')}),
        ('Personal Info', {'fields': ('date_of_birth', 'gender')}),
        ('Address', {'fields': ('address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country')}),
        ('Verification', {'fields': ('email_verified', 'phone_verified')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

def get_category_choices(categories, level=0):
    """
    Recursively generates (id, name) choices for categories with indentation.
    Uses prefetch_related to minimize queries.
    """
    choices = []
    indent = "— " * level
    for category in categories:
        choices.append((category.id, f"{indent}{category.name}"))
        # children are already prefetched in queryset
        children = getattr(category, 'children_prefetch', category.children.all())
        if children:
            choices += get_category_choices(children, level + 1)
    return choices

class CategoryMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Lazy ManyToMany field for categories — avoids DB query on import.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("queryset", Categories.objects.none())
        super().__init__(*args, **kwargs)

class ProductAdminForm(forms.ModelForm):
    categories = CategoryMultipleChoiceField(
        widget=forms.SelectMultiple(attrs={'size': '15', 'style': 'width: 775px;'})
    )

    class Meta:
        model = Products
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prefetch categories for choices
        top_categories = Categories.objects.filter(parent__isnull=True).prefetch_related('children')
        for cat in top_categories:
            # attach prefetched children for recursion
            cat.children_prefetch = list(cat.children.all())
        self.fields["categories"].queryset = Categories.objects.all()
        self.fields["categories"].choices = get_category_choices(top_categories)

class ProductsAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('code', 'name', 'get_categories', 'price', 'discount_price', 'active', 'created_at')
    list_filter = ('active', 'categories')
    search_fields = ('code', 'name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # filter_horizontal = ('categories',)  # makes multi-select nicer in admin

    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        # Prefetch categories to avoid N+1 queries in get_categories
        qs = super().get_queryset(request)
        return qs.prefetch_related('categories')

    def get_categories(self, obj):
        return ", ".join(category.name for category in obj.categories.all())
    get_categories.short_description = 'Categories'

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

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically return fieldsets based on slide_type.
        """
        common_fields = ('slide_type', 'title', 'order')

        if obj:
            if obj.slide_type == 'default':
                return ((None, {'fields': common_fields + ('subtitle','description','button_text','link','image')}),)
            elif obj.slide_type == 'image':
                return ((None, {'fields': common_fields + ('image','link')}),)
            elif obj.slide_type == 'video':
                return ((None, {'fields': common_fields + ('video',)}),)

        # Fallback during creation
        return ((None, {'fields': common_fields}),)

    def get_form(self, request, obj=None, **kwargs):
        """
        Dynamically set labels for FileFields depending on slide_type.
        """
        form = super().get_form(request, obj, **kwargs)

        # Set default labels
        if 'image' in form.base_fields:
            form.base_fields['image'].label = "Image (Max 1MB)"
        if 'video' in form.base_fields:
            form.base_fields['video'].label = "Video (Max 5MB)"

        # Optionally hide irrelevant fields on existing object
        if obj:
            if obj.slide_type == 'image':
                form.base_fields.pop('video', None)
            elif obj.slide_type == 'video':
                form.base_fields.pop('image', None)
            # default shows image + other fields
        return form

    def save_model(self, request, obj, form, change):
        # Optional: assign default banner if missing
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