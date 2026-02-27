from django import forms
from django.contrib import admin
from django.db.models import Case, When

from .models import *

# -----------------------------
# Categories Admin
# -----------------------------
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('indented_name', 'active', 'menu', 'created_at')
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('active',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Fetch all categories
        categories = list(qs)
        # Build a mapping of parent_id -> children
        children_map = {}
        for cat in categories:
            parent_id = cat.parent_id or 0
            children_map.setdefault(parent_id, []).append(cat)

        # Recursive function to flatten categories in hierarchy
        def build_order(parent_id=0):
            ordered = []
            for cat in children_map.get(parent_id, []):
                ordered.append(cat)
                ordered.extend(build_order(cat.id))
            return ordered

        # Return queryset in hierarchical order
        ordered_categories = build_order()
        # Using list for display, so return qs filtered by ids in order
        ordered_ids = [c.id for c in ordered_categories]
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ordered_ids)])
        return qs.filter(pk__in=ordered_ids).order_by(preserved_order)

    def indented_name(self, obj):
        level = 0
        parent = obj.parent
        while parent:
            level += 1
            parent = parent.parent
        return f"{'— ' * level}{obj.name}"

    indented_name.short_description = "Name"

# -----------------------------
# Coupons Admin
# -----------------------------
class CouponsAdmin(admin.ModelAdmin):
    list_display = ('code', 'coupon_type', 'discount_value', 'active', 'valid_from', 'valid_to', 'usage_limit', 'used_count')
    list_filter = ('active', 'coupon_type', 'valid_from', 'valid_to')
    search_fields = ('code', 'description')
    readonly_fields = ('used_count', 'created_at', 'updated_at')

# -----------------------------
# Roles Admin
# -----------------------------
class RolesAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('name',)

# -----------------------------
# Profile Admin
# -----------------------------
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

# -----------------------------
# Helper: Category Choices (Lazy)
# -----------------------------
def get_category_choices(categories, level=0):
    """
    Recursively builds (id, name) tuples for ModelMultipleChoiceField.
    Assumes children are prefetched.
    """
    choices = []
    indent = "— " * level
    for cat in categories:
        choices.append((cat.id, f"{indent}{cat.name}"))
        children = getattr(cat, 'children_prefetch', None)
        if children:
            choices += get_category_choices(children, level + 1)
    return choices

# -----------------------------
# Product Form (Lazy-Safe)
# -----------------------------
class ProductAdminForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Categories.objects.none(),  # start empty
        widget=forms.SelectMultiple(attrs={'size': '15', 'style': 'width: 775px;'})
    )

    class Meta:
        model = Products
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Prefetch top-level categories with children
        top_categories = Categories.objects.filter(parent__isnull=True).prefetch_related('children')
        for cat in top_categories:
            cat.children_prefetch = list(cat.children.all())

        # Set queryset and choices at runtime
        self.fields['categories'].queryset = Categories.objects.all()
        self.fields['categories'].choices = get_category_choices(top_categories)

# -----------------------------
# Products Admin
# -----------------------------
class ProductsAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('code', 'name', 'get_categories', 'price', 'discount_price', 'active', 'created_at')
    list_filter = ('active', 'categories')
    search_fields = ('code', 'name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')

    def get_queryset(self, request):
        # Prefetch categories to avoid N+1
        qs = super().get_queryset(request)
        return qs.prefetch_related('categories')

    def get_categories(self, obj):
        return ", ".join(category.name for category in obj.categories.all())
    get_categories.short_description = 'Categories'

# -----------------------------
# Slide Inline + Banner Admin
# -----------------------------
class SlideInline(admin.TabularInline):
    model = Slide
    extra = 1
    fields = ['title', 'subtitle', 'description', 'button_text', 'link', 'order', 'image']

class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    inlines = [SlideInline]

# -----------------------------
# Slide Admin
# -----------------------------
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'slide_type', 'order', 'created_at')
    search_fields = ('title', 'slide_type')

    def get_fieldsets(self, request, obj=None):
        common_fields = ('slide_type', 'title', 'order')
        if obj:
            if obj.slide_type == 'default':
                return ((None, {'fields': common_fields + ('subtitle','description','button_text','link','image')}),)
            elif obj.slide_type == 'image':
                return ((None, {'fields': common_fields + ('image','link')}),)
            elif obj.slide_type == 'video':
                return ((None, {'fields': common_fields + ('video',)}),)
        return ((None, {'fields': common_fields}),)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'image' in form.base_fields:
            form.base_fields['image'].label = "Image (Max 1MB)"
        if 'video' in form.base_fields:
            form.base_fields['video'].label = "Video (Max 5MB)"
        if obj:
            if obj.slide_type == 'image':
                form.base_fields.pop('video', None)
            elif obj.slide_type == 'video':
                form.base_fields.pop('image', None)
        return form

    def save_model(self, request, obj, form, change):
        if not obj.banner_id:
            obj.banner_id = 1
        super().save_model(request, obj, form, change)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'profession', 'created_at')
    search_fields = ('name',)

# -----------------------------
# Settings Admin
# -----------------------------
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'facebook', 'twitter', 'instagram', 'linkedin', 'pinterest', 'phone1', 'phone2', 'phone3', 'email1', 'email2', 'email3')

    fieldsets = (
        (None, {'fields': ('time',)}),
        ('Social Media', {'fields': ('facebook', 'twitter', 'instagram', 'linkedin', 'pinterest')}),
        ('Address', {'fields': ('address',)}),
        ('Contact', {'fields': ('phone1', 'phone2', 'phone3')}),
        ('Email', {'fields': ('email1', 'email2', 'email3')}),
    )

    def has_add_permission(self, request):
        return False

# -----------------------------
# Register Admins
# -----------------------------
# admin.site.register(Banner, BannerAdmin)
admin.site.register(Categories, CategoriesAdmin)
# admin.site.register(Coupons, CouponsAdmin)  # optional
# admin.site.register(Roles, RolesAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Settings, SettingsAdmin)
