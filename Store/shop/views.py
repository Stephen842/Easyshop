from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect 
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
from .forms import CustomerForm, SigninForm, CommentForm, ContactForm, NewsletterForm # Import the form
from .models import Customer, Category, Products, Order, Post, Comment, Gallery, ContactMail  # and also Import the model

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
                    customer = Customer.objects.get(email=user.email)
                    request.session['customer'] = customer.id
                except Customer.DoesNotExist:
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
        product_id = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart', {})

        if product_id:
            quantity = cart.get(product_id, 0)
            if remove:
                if quantity <= 1:
                    cart.pop(product_id, None)
                else:
                    cart[product_id] = quantity - 1
            else:
                cart[product_id] = quantity + 1

        request.session['cart'] = cart
        print('cart', request.session['cart'])

        # I updated this below to render the same page with updated context instead of redirecting to the homepage
        return self.get(request)

    def get(self, request):
        return HttpResponseRedirect(f'/home{request.get_full_path()[1:]}')

# For the store homepage
def home(request):
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()
    context = {
        'title': 'Elvix Luxe – Fashion That Inspires Confidence',
        'newsletter': newsletter,
    }
    return render(request, 'pages/store.html', context)

# For the cart page 
@method_decorator(login_required, name='dispatch')
class Cart(View):
    def get(self, request):
        date = datetime.now()
        cart = request.session.get('cart', {})
        product_ids = list(cart.keys())
        products = Products.objects.filter(id__in=product_ids)

        cart_items = []
        for product in products:
            quantity = cart[str(product.id)]
            total_price = int(product.price.replace(',', '')) * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': total_price, 
            })

        context = {
                'title': 'Your Cart',
                'cart_items': cart_items,
                'date': date,
        }

        return render(request, 'pages/cart.html', context)

# For the order checkout page
@method_decorator(login_required, name='dispatch')
class CheckOut(View):
    def get(self, request):
        #If request is GET it should render the checkout form
        return render(request, 'pages/checkout.html')

    def post(self, request):
        #To process checkout form
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Get the customer_id from the session
        customer_id = request.session.get('customer')

        cart = request.session.get('cart')

        if not customer_id or not cart:
            return redirect('homepage') #Redirect user to homepage if user is not logged in or there nothing is in the cart

        products = Products.get_products_by_id(list(cart.keys()))
        customer = Customer.objects.get(id=customer_id)

        for product in products:
            quantity = cart.get(str(product.id))
            total_price = int(product.price.replace(',', '')) * quantity

            order = Order(
                        customer = customer,
                        products = product,
                        price = total_price,
                        address = address,
                        phone = phone,
                        quantity = quantity
                    )
            order.save()
        request.session['cart'] = {}

        return redirect('order-confirm')

# For the viewing of all orders that have been placed successfully by a user
@method_decorator(login_required, name='dispatch')
class OrderView(View):
    def get(self, request):
        date = datetime.now()
        customer_id = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer_id)
        print(orders)
        context = {
                'orders': orders,
                'title': 'Your Purchase Summary',
                'date': date,
        }
        return render(request, 'pages/orders.html', context)

@login_required
def order_confirm(request):
    shop_url = reverse('home')
    context = {
        'title': 'Order Placed Successfully',
        'shop_url': shop_url
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
    categories = Category.objects.filter(name__icontains=query)
    
    context = {
        'query': query,
        'products': products,
        'categories': categories,
        'date': date,
    }
    return render(request, 'pages/search_results.html', context)

# For the message sent page
def message_sent(request):
    context = {
        'title': 'Message Sent Successfully!'
    }
    return render(request, 'pages/success.html', context)

def error_404(request):
    context ={
            'title': 'Oops! Page Not Found'
    }
    return render(request, 'pages/404.html', context)
