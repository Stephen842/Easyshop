from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.db import models
from django.db.models import Q
from .models import MyCustomer, Category, ProductCategory, Products, CartItem, Order, Post, Comment, Gallery, ContactMail, Newsletter

# Register your models here.

class CustomerAdmin(admin.ModelAdmin):
    # Specify the fields to be displayed in the list view
    list_display = ('id','email', 'name', 'phone', 'is_active', 'is_staff')
    
    # Add filters in the right sidebar
    list_filter = ('is_active', 'is_staff')
    
    # Add a search bar at the top of the list view
    search_fields = ('email', 'name', 'phone')
    
    # Add fields to be displayed in the detail view
    fieldsets = (
        (None, {'fields': ('email', 'name', 'phone', 'is_active', 'is_staff')}),
        ('Permissions', {'fields': ('is_superuser',)}),
    )


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

    pass

class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

    pass

class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category')
    search_fields = ('name', 'price')

    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            search_term_as_int = int(search_term)
            queryset |= self.model.objects.filter(Q(category__name__icontains=search_term))
        except ValueError:
            queryset |= self.model.objects.filter(Q(category__name__icontains=search_term))
        return queryset, use_distinct

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'shipping')  # Fields to display in the list view
    search_fields = ('user__name', 'product__name')  # Enable searching by user name or product name
    list_filter = ('shipping',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'products')
    search_fields = ('id',)  # Only include fields directly on the Order model

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        # Filter based on the related model's fields
        queryset |= self.model.objects.filter(Q(products__name__icontains=search_term))
        return queryset, use_distinct

class PostAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

    pass

class CommentAdmin(admin.ModelAdmin):
    pass

class GalleryAdmin(admin.ModelAdmin):
    pass
class ContactAdmin(admin.ModelAdmin):
    pass

admin.site.register(MyCustomer, CustomerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(Products, ProductsAdmin)
#admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(ContactMail, ContactAdmin)
admin.site.register(Newsletter)