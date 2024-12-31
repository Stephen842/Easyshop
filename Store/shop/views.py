from django.shortcuts import render, redirect, get_object_or_404 
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.http import HttpResponse
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
import random
import string
from .forms import CustomerForm, CartItemForm, SigninForm, CommentForm, ContactForm, NewsletterForm # Import the form
from .models import MyCustomer, Category, ProductCategory, Products, Order, CartItem, Post, Comment, Gallery, ContactMail  # and also Import the model

# Create your views here.

# To handle user's registration processes
class Signup(View):
    def get(self, request):
        form = CustomerForm()
        return render(request, 'pages/signup.html', {'form': form})

    def post(self, request):
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.password = make_password(customer.password)
            customer.save()
            return redirect('homepage')
        else:
            return render(request, 'pages/signup.html', {'form': form})

# To handle user's authentication process with error handling capabilities
def Signin(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('homepage')
        form = SigninForm()
        return render(request, 'pages/signin.html', {'form': form})

    if request.method == 'POST':
        form = SigninForm(request.POST)

        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                try:
                    customer = MyCustomer.objects.get(email=user.email)
                    request.session['customer'] = customer.id
                except MyCustomer.DoesNotExist:
                    return HttpResponse('Customer does not exist for this user')
                return redirect('homepage')
            else:
                return HttpResponse('Invalid login')
        return render(request, 'pages/signin.html', {'form': form})


# Handles user logout while keeping session data intact.
def logout(request):
    auth_logout(request)  # Logs out the user without clearing session data.
    return redirect('homepage') 

class Index(View):
    def post(self, request):
        user = request.user
        product_id = request.POST.get('product')
        remove = request.POST.get('remove')

        if not user.is_authenticated:
            # Redirect to login if user is not authenticated
            return redirect(f"{reverse('login')}?next={request.path}")
        
        # Get the product
        product = get_object_or_404(Products, id=product_id)

        # Check if the product is already in the cart for the user
        cart_item, created = CartItem.objects.get_or_create(user=user, product=product)

        if remove:
            if cart_item.quantity <= 1:
                cart_item.delete()
            else:
                cart_item.quantity -= 1
                cart_item.save()
        else:
            cart_item.quantity += 1
            cart_item.save()

        # Optionally, synchronize the session cart data (e.g., product IDs and quantities) for future reference
        cart_items = CartItem.objects.filter(user=user)
        session_cart = {}
        for item in cart_items:
            session_cart[item.product.id] = item.quantity

        request.session['cart'] = session_cart  # Update session with the current cart state
        
        return redirect('Store/')
        
    def get(self, request):
        # Redirect to the store or render a response as per your application
        return HttpResponseRedirect(f'/Store{request.get_full_path()[1:]}')

# For the store homepage
def home(request):

    date = datetime.now()
    posts = Post.objects.all().order_by('-created_on')[:5]

    # Fetch the user's cart items directly from CartItem model
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
    else:
        cart_items = []
        
    products = None
    categories = ProductCategory.get_all_categories()
    categoryID = request.GET.get('category')

    if categoryID:
        #This is to ensure that categoryID is a valid integer
        try:
            categoryId = int(categoryID)
            products = Products.get_all_products_by_categoryid(categoryID)
        except ValueError:
            products = Products.get_all_products() #If the CategoryId is invalid, it should display all products
    else:
        products = Products.get_all_products()

    data = {
        'products': products,
        'categories': categories,
        'cart': cart_items, # Pass the cart items fetched from the database
    }

    # Newsletter subscription form
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'title': 'Elvix Luxe – Fashion That Inspires Confidence',
        'posts': posts,
        'data': data,
        'date': date,
        'newsletter': newsletter,
    }
    return render(request, 'pages/store.html', context)

# For the cart page 
@method_decorator(login_required, name='dispatch')
class Cart(View):
    def get(self, request):
        date = datetime.now()

        # Fetch cart items from the database
        cart_items = CartItem.objects.filter(user=request.user)

        # Initialize total_product
        subtotal = 0

        shipping_cost = 1 

        total = 0

        # Prepare cart items
        cart_details = []
        for item in cart_items:
            total_price = int(item.product.price.replace(',', '')) * item.quantity
            subtotal += total_price  # Accumulate the total value of all products
            total = subtotal + shipping_cost
            cart_details.append({
                'product': item.product,
                'quantity': item.quantity,
                'total_price': total_price,
                'subtotal': subtotal,
                'total': total,
            })

        context = {
                'title': 'Your Shopping Cart',
                'cart_items': cart_details,
                'subtotal': subtotal,
                'total': total,
                'date': date,
                'form': CartItemForm(),
                'newsletter': NewsletterForm()
        }

        return render(request, 'pages/cart.html', context)
    
    def post(self, request):
        # Handle form submission
        form = CartItemForm(request.POST)
        if form.is_valid():
            # Save the cart item to the database
            cart_item = form.save(commit=False)
            cart_item.user = request.user  # Associate the cart item with the logged-in user
            cart_item.save()

        cart_items = CartItem.objects.filter(user=request.user)

        # Initialize total_product
        total_product = 0

        # Prepare cart items
        cart_details = []
        for item in cart_items:
            total_price = int(item.product.price.replace(',', '')) * item.quantity
            total_product += total_price  # Accumulate the total value of all products
            cart_details.append({
                'product': item.product,
                'quantity': item.quantity,
                'total_price': total_price,
                'total_product': total_product,
            })


        # This part is for user's to subscribe to the newsletter found in the footer
        if request.method  == 'POST':
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'pages/success.html')
        newsletter = NewsletterForm()


        context = {
            'title': 'Your Shopping Cart',
            'cart_items': cart_details,
            'total_product': total_product,
            #'final_product_price': final_product_price,
            'date': datetime.now(),
            'form': form,
            'newsletter': newsletter,
        }
        return render(request, 'pages/cart.html', context)

# For the order checkout page
@method_decorator(login_required, name='dispatch')
class CheckOut(View):
    def get(self, request):
        context={
            'title': 'Order Confirmation',
            'newsletter': NewsletterForm(),
        }
        # If request is GET it should render the checkout form
        return render(request, 'pages/checkout.html')

    def post(self, request):
        # To process checkout form
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        if not address or not phone:
            messages.error(request, "Address and phone are required.")
            return redirect('checkout')  # Redirect back to checkout if inputs are invalid

        # Get the authenticated user
        customer = request.user

        # Get cart data from the database
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty.")
            return redirect('homepage')


        try:
           with transaction.atomic():
                # Prepare orders for bulk creation
                orders = [
                    Order(
                        customer=customer,
                        products=cart_item.product,
                        price=cart_item.total_price(),
                        address=address,
                        phone=phone,
                        quantity=cart_item.quantity,
                    )
                    for cart_item in cart_items
                ]
                # Save all orders
                Order.objects.bulk_create(orders)

                # Clear cart items
                cart_items.delete()

                messages.success(request, "Order placed successfully!")
                return redirect('order-confirm')
        except Exception as e:
            # Log the error for debugging
            print(f"Error during checkout: {e}")
            messages.error(request, "Something went wrong during checkout. Please try again.")
            return redirect('checkout')
        

# For the viewing of all orders that have been placed successfully by a user
@method_decorator(login_required, name='dispatch')
class OrderView(View):
    def get(self, request):

        # Get orders directly from the database linked to the logged-in user
        orders = Order.objects.filter(customer=request.user).order_by('-id')

        if not orders.exists():
            messages.info(request, "You have no orders yet.")

        # Calculate subtotal by summing all the prices
        subtotal = sum(order.price for order in orders)

        shipping_cost = 1 
        total = subtotal + shipping_cost

        # This part is for user's to subscribe to the newsletter found in the footer
        if request.method  == 'POST':
            form = NewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'pages/success.html')
        newsletter = NewsletterForm()


        context = {
                'orders': orders,
                'title': 'Your Purchase Summary',
                'newsletter': newsletter,
                'subtotal': subtotal,
                'shipping_cost': shipping_cost,
                'total': total,

        }
        return render(request, 'pages/orders.html', context)

@login_required
def order_confirm(request):
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'title': 'Order Placed Successfully',
        'newsletter': newsletter,
    }
    return render(request, 'pages/order_confirm.html', context)

# For the blog page
def blog(request):
    posts = Post.objects.all().order_by('-created_on')

    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'posts': posts,
        'title': 'Your Style Destination for Fashion Trends and Inspiration',
        'newsletter': newsletter,
    }
    return render(request, 'pages/blog.html', context)

# For the blog category
def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
        ).order_by('-created_on')

    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        "category": category,
        'posts': posts,
        'title': 'Discover Your Perfect Style',
        'newsletter': newsletter,
    }
    return render(request, 'pages/category.html', context)

# For the blog details
def blog_details(request, pk):
    post = Post.objects.get(pk=pk)

    # Logic for related posts: Get other posts from the same category
    related_posts = Post.objects.filter(categories__in=post.categories.all()).exclude(id=post.pk)
    
    # Handle comment form submission
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post  # Associate the comment with the current post
            comment.save()
            return redirect(request.path_info)
    else:
        form = CommentForm()

    comments = Comment.objects.filter(post=post)
    
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
        'newsletter': newsletter,
    }
    return render(request, 'pages/blog_detail.html', context)

def gallery(request):
    media = Gallery.objects.all().order_by('-id')

    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'media': media,
        'title': 'The Luxe Wardrobe Showcase',
        'newsletter': newsletter,
    }
    return render(request, 'pages/gallery.html', context)
    

# For the contact page
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            #This is to save the message to the database
            contact_message = ContactMail.objects.create(
                    name = form.cleaned_data['name'],
                    email = form.cleaned_data['email'],
                    message = form.cleaned_data['message'],
            )

            #To send message to our preferred SMTP Provider(Gmail)
            send_mail(
                    f'New message submitted via the contact form by {contact_message.name}', # This will serve as the subject of the message upon recieving
                    contact_message.message, # The body of the message
                    contact_message.email, # From the email that sent the message
                    [settings.EMAIL_HOST_USER], # To the Email that will be recieving. (set at the settings.py file(Your email))
            )
            return redirect('message_sent') #Redirect to the success page
    else:
        form = ContactForm()

    context = {
        'title': 'We Would Love to Hear From You!',
        'form': form,
    }

    return render(request, 'pages/contact.html', context)

# For retrieving of data
def search(request):
    date = datetime.now()
    query = request.GET.get('q')
    products = Products.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    categories = ProductCategory.objects.filter(name__icontains=query)

    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()
    
    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'date': date,
        'newsletter': newsletter,
    }
    return render(request, 'pages/search_results.html', context)

# For the message sent page
def message_sent(request):
    context = {
        'title': 'Message Sent Successfully!'
    }
    return render(request, 'pages/success.html', context)

def error_404(request):
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'title': 'Oops! Page Not Found',
        'newsletter': newsletter,
    }
    return render(request, 'pages/404.html', context)
