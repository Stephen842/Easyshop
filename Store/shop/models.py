from django.db import models
from django.utils import timezone

# Create your models here.

# For products and post category
class Category(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

# For Post Creation
class Post(models.Model):
    title = models.CharField(max_length=300)
    body = models.TextField()
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField('Category', related_name='posts')

    def __str__(self):
        return self.title

# For commenting on post
class Comment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"{self.author} on '{self.created_on}'"
    
class Gallery(models.Model):
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    caption = models.CharField(max_length=60, null=True, blank=True, default="")

    class Meta:
        verbose_name_plural = 'Galleries'

    def __str__(self):
        return self.caption if self.caption else "No Caption"
# For the contact us details
class ContactMail(models.Model):
    name = models.CharField(max_length = 100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)  # this is to automatically store the submission time

    def __str__(self):
        return f'Message from {self.name}'

class Newsletter(models.Model):
    email = models.EmailField(blank=True)

    def __str__(self):
        if self.email:
            return self.email
        else:
            return 'No email provided'
