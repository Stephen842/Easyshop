from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import Category, Post, Comment, Gallery, ContactMail, Newsletter

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    pass

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

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Gallery, GalleryAdmin)
admin.site.register(ContactMail, ContactAdmin)
admin.site.register(Newsletter)