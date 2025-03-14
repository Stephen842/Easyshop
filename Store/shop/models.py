from django.db import models
from django.conf import settings
from PIL import Image
import datetime
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField

# Change the Product category to ManyToManyField for the product categories - categories = models.ManyToManyField(ProductCategory, related_name="products")

# Create your models here.

class CustomerManager(BaseUserManager):
    def create_user(self, email, name, phone, country, password=None):
        if not email:
            raise ValueError('Enter Email address')
        if not name:
            raise ValueError('Enter Full name')
        if not phone:
            raise ValueError('Enter Phone Number')
        if not country:
            raise ValueError('Enter Country')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone=phone,
            country=country,
        )
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, phone, country, password=None):
        user = self.create_user(
            email=email,
            name=name,
            phone=phone,
            country=country,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class MyCustomer(AbstractBaseUser, PermissionsMixin):  # Add PermissionsMixin here
    name = models.CharField(max_length=100, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone = PhoneNumberField(region='US')
    country = CountryField(blank_label='Select Country',)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Add this field
    is_superuser = models.BooleanField(default=False)  # Add this field

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'phone']

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the customer's full name"""
        return self.name  # Assuming 'name' is the full name

    def get_short_name(self):
        """Return the short name (same as full name in this case)"""
        return self.name

# For products and post category
class Category(models.Model):
    name = models.CharField(max_length=50, db_index=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    
class ProductCategory(models.Model):
    name = models.CharField(max_length=50, db_index=True)

    class Meta:
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return self.name
    
    @staticmethod
    def get_all_categories():
        return ProductCategory.objects.all()

# For uploading of product
class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=20, blank=True)
    size = models.CharField(max_length=20, blank=True)
    price = models.CharField(max_length=20, default=0)
    old_price = models.CharField(max_length=20, default=0)
    category = models.ManyToManyField(ProductCategory, related_name='products')
    image_0 = models.ImageField(upload_to='media/')

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Products'

    #To retrieve product by its ID
    @staticmethod
    def get_products_by_id(ids):
        return Products.objects.filter(id__in=ids)

    #To get retrieve product stored in the database
    @staticmethod
    def get_all_products():
        return Products.objects.all()

    #To retrieve product using category ID
    @staticmethod
    def get_all_products_by_categoryid(category_id=None):
        if category_id:
            return Products.objects.filter(category=category_id)
        return Products.get_all_products()

class CartItem(models.Model):
    user = models.ForeignKey(MyCustomer, on_delete=models.CASCADE, null=True, blank=True, related_name="cart_items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    shipping = models.CharField(
        max_length=100,
        choices=[
            ('standard', 'Standard Delivery - $1 (3-5 business days)'),
        ],
        default='standard'
    )

    def total_price(self):
        # Assuming product price is stored as a string with commas
        return int(self.product.price.replace(',', '')) * self.quantity

    def __str__(self):
        return f"Cart for {self.user} {self.product} (x{self.quantity}) - {self.get_shipping_display() if self.user else 'No user'}"
    
#This is for the order model, where users fill the neccessary products they are ordering for and then the orders are been submitted
class Order(models.Model):
    customer = models.ForeignKey(MyCustomer, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Products, related_name="orders")
    order_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField()
    state = models.CharField(max_length=50, default='unknown')
    phone = PhoneNumberField(region='US', default='+11234567890')
    country = CountryField(blank_label='Select Country', default='US')
    name = models.CharField(max_length=50, default='Anonymous User')
    email = models.EmailField(default='unknown@example.com')
    city = models.CharField(max_length=50, default='Unknown City')
    zipcode = models.CharField(max_length=20, blank=True, default='000000')
    date = models.DateField(default=datetime.datetime.today)
    paid = models.BooleanField(default=False)



    def placeOrder(self):
        self.save()

    #To retrieve an order using customer ID
    @staticmethod
    def get_orders_by_customer(customer_id):
        return Order.objects.filter(customer=customer_id).order_by('-date')

class OrderItem(models.Model):  # Through Model
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey('Products', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()  # Store quantity per product

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) in Order {self.order.order_id}"

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
