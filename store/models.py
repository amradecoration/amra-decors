import os
import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ckeditor.fields import RichTextField
    
GENDER = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

class Categories(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    active = models.BooleanField(default=True)
    menu = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        # ordering = ['id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Automatically generate slug if not set
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Coupons(models.Model):
    COUPON_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    coupon_type = models.CharField(max_length=20, choices=COUPON_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True, help_text="Maximum times coupon can be used")
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Coupons'
        ordering = ['id']

    def is_valid(self):
        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and (self.usage_limit is None or self.used_count < self.usage_limit)

    def increment_usage(self):
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            raise ValueError("Coupon usage limit reached")
        self.used_count += 1
        self.save()

    def __str__(self):
        return self.code

class Roles(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Roles'
        ordering = ['id']

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Roles, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.FileField(upload_to='profile_images/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER, blank=True, null=True)
    address_line1 = models.CharField(max_length=255, blank=True, null=True)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Profiles'
        ordering = ['id']

    def __str__(self):
        return str(self.user)

class Products(models.Model):
    code = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    categories = models.ManyToManyField(Categories, related_name='products')
    description = RichTextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.FileField(upload_to='products/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def is_new(self):
        return self.created_at >= timezone.now() - timedelta(days=7)

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['id']

class Banner(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Banners'
        ordering = ['created_at']

    def __str__(self):
        return self.title or "Banner #{}".format(self.id)

class Slide(models.Model):
    TYPES = [
        # ('default', 'Default'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    def get_unique_filename(instance, filename):
        # Generate a unique filename for uploaded files
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        return unique_name
    
    def validate_image_size(file):
        max_size_mb = 1
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Maximum file size is {max_size_mb}MB")
    
    def validate_video_size(file):
        max_size_mb = 5
        if file.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Maximum file size is {max_size_mb}MB")
    
    banner = models.ForeignKey(Banner, related_name='slides', on_delete=models.CASCADE)
    slide_type = models.CharField(max_length=255, choices=TYPES, default="image")
    title = models.CharField(max_length=255, blank=True, null=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    button_text = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, blank=True, null=True)
    order = models.PositiveIntegerField(default=0)  # To order the slides
    image = models.FileField(upload_to=get_unique_filename, blank=True, null=True, validators=[validate_image_size])  # Image field
    video = models.FileField(upload_to=get_unique_filename, blank=True, null=True, validators=[validate_video_size]) # Video field
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Slides'

    def __str__(self):
        return self.title or "Slide #{}".format(self.id)

class Testimonial(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    profession = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Testimonials'
        ordering = ['created_at']

    def __str__(self):
        return self.name or "Testimonial #{}".format(self.id)