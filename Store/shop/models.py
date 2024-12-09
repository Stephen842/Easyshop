from django.db import models

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

    def __str__(self):
        return f"{self.author} on '{self.created_on}'"

# For the contact us details
class ContactMail(models.Model):
    name = models.CharField(max_length = 100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)  # this is to automatically store the submission time

    def __str__(self):
        return f'Message from {self.name}'
