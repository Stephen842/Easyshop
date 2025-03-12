from django.shortcuts import render, redirect, get_object_or_404 
from django.conf import settings
from datetime import datetime
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
import uuid
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.utils.html import strip_tags
from django.templatetags.static import static
from django.db.models import Count, Q
import logging
from .forms import CustomerForm, CartItemForm, SigninForm, CommentForm, ContactForm, NewsletterForm # Import the form
from .models import MyCustomer, Category, ProductCategory, Products, Order, OrderItem, CartItem, Post, Comment, Gallery, ContactMail  # and also Import the model

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
    if request.method == 'GET':
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
                    messages.error(request, 'Customer does not exist for this user.')
                    return render(request, 'pages/signin.html', {'form': form})
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid email or password.')
        return render(request, 'pages/signin.html', {'form': form})


# Handles user logout while keeping session data intact.
def logout(request):
    auth_logout(request)  # Logs out the user without clearing session data.
    return redirect('homepage') 


# Function to add to Cart via AJAX API endpoint
@csrf_exempt
def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You must be logged in to add items to the cart.'}, status=401)

    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=405)
    
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    if not product_id:
        return JsonResponse({'success': False, 'message': 'Missing product ID.'}, status=400)

    if action not in ['add', 'remove']:
        return JsonResponse({'success': False, 'message': 'Invalid action.'}, status=400)

    # Get the product (handle the case if the product does not exist)
    user = request.user
    product = get_object_or_404(Products, id=product_id)

    # Retrieve or create a cart item
    cart_item, created = CartItem.objects.get_or_create(user=user, product=product)

    if action == 'add':
        cart_item.quantity += 1
        cart_item.save()
        message = 'Product added to cart!'

    elif action == 'remove':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            message = 'Product quantity decreased!'
            
        else:
            cart_item.delete()
            message = 'Product removed from cart!'

    cart_count = CartItem.objects.filter(user=user).count()

    return JsonResponse({'success': True, 'message': message,  'cart_count': cart_count})


class Index(View):
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


# For rendering a detailed description about a product
def Product_details(request, id):
    all_product = Products.objects.get(id=id)

    # Logic for related products: Get other products that shares two or categories
    related_products = Products.objects.filter(category__in=all_product.category.all()).exclude(id=all_product.id).annotate(matching_categories=Count('category', filter=Q(category__in=all_product.category.all()))).filter(matching_categories__gt=1).distinct()
    
    #This below is for the comment section of each product
    #form = CommentForm()
    #if request.method == 'POST':
        #form = CommentForm(request.POST)
        #if form.is_valid():
            #customer = Customer.objects.get(name=request.user.name)  # Get the Customer instance
            #comment = Comment(
                        #author = customer,  # Assign the Customer instance
                        #body = form.cleaned_data['body'],
                        #post = all_product,
                    #)
            #comment.save()
            #return redirect(request.path_info)

    #comments = Comment.objects.filter(post=all_product)

    # Newsletter subscription form
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'all_product': all_product,
        'related_products': related_products,
        #'comments': comments,
        'newsletter': newsletter,
        
    }
    return render(request, 'pages/product_details.html', context)

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
        # Handle Adding item to cart
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

        # Get cart data from the database from an authenticated user
        cart_items = CartItem.objects.filter(user=request.user)

        subtotal = 0 

        shipping_cost = 1

        cart_details = [] # Store processed cart items

        for item in cart_items: 
            product_price = int(item.product.price.replace(',', '')) * item.quantity  # Multiply product price by it quantity
            subtotal += product_price # To Accumulate subtotal

            cart_details.append({
                'product': item.product,
                'quantity': item.quantity,
                'product_price': product_price, 
            })

        total = subtotal + shipping_cost
        
        context={
            'cart_items': cart_details,
            'subtotal': subtotal,
            'shipping_cost': shipping_cost,
            'total': total,
            'title': 'Order Confirmation',
            'newsletter': NewsletterForm(),
        }
        # If request is GET it should render the checkout form
        return render(request, 'pages/checkout.html', context)

    def post(self, request):
        # To process checkout form
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')

        if not state or not phone:
            messages.error(request, 'State and phone are required.')
            return redirect('checkout')  # Redirect back to checkout if inputs are invalid

        # Get the authenticated user
        customer = request.user

        shipping_cost = 1

        # Get cart data from the database
        cart_items = CartItem.objects.filter(user=customer)
        if not cart_items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('homepage')
        
        order_price = sum(item.total_price() for item in cart_items)

        # Create an order but mark it as unpaid
        order = Order.objects.create(
            customer=customer,
            price=order_price,
            state=state,
            phone=phone,
            country=country,
            city=city,
            name=name,
            email=email,
            zipcode=zipcode,

            order_id=uuid.uuid4().hex[:10].upper(), # Generate a unique order_id for each order
            paid=False
        )

        # Correctly store products and their quantity using OrderItem
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        order.flutterwave_tx_ref = order.order_id # To save the unique transaction ID
        order.save()

        # Flutterwave Payment Data
        payload = {
            'tx_ref': order.flutterwave_tx_ref,
            'amount': order_price + shipping_cost,
            'currency': 'USD',
            'redirect_url': request.build_absolute_uri(reverse('order-confirm', args=[order.order_id])), # Redirect here after successful payment
            'payment_options': 'card, ussd, banktransfer',
            'customer': {
                'email': customer.email,
                'phonenumber': phone,
                'name': customer.get_full_name()
            },
            'customizations':{
                'title': 'Elvix Luxe Checkout',
                'description': 'Secure Payment for Your Luxury Items',
                'logo': request.build_absolute_uri(static('elvix.png'))
            }
        }

        headers = {
            'Authorization': f'Bearer {settings.FLUTTERWAVE_SECRET_KEY}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                'https://api.flutterwave.com/v3/payments',
                json=payload,
                headers=headers,
                timeout=10  # Add timeout to avoid infinite waiting
            )
            response.raise_for_status()  # Raise an error for HTTP 4xx/5xx

            res_data = response.json()  # Convert response to JSON

            if res_data.get('status') == 'success':
                return redirect(res_data['data']['link'])  # Redirect to payment page
            else:
                messages.error(request, 'Payment failed. Try again.')
                return redirect('payment-failed')

        except requests.exceptions.Timeout:
            messages.error(request, 'Payment request timed out. Please try again.')
            return redirect('checkout')

        except requests.exceptions.ConnectionError:
            messages.error(request, 'Network error. Please check your internet connection.')
            return redirect('checkout')

        except requests.exceptions.HTTPError as e:
            messages.error(request, f'Payment gateway error: {e}')
            return redirect('checkout')

        except requests.exceptions.RequestException as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return redirect('checkout')
        

# FlutterWave Webhook
@csrf_exempt
def flutterwave_webhook(request):

    logger = logging.getLogger('webhook')

    try:
        # Verify the request signature
        secret_hash = settings.FLUTTERWAVE_SECRET_HASH
        signature = request.headers.get("verif-hash")

        logger.info(f"Expected Secret Hash: {secret_hash}")
        logger.info(f"Received Signature: {signature}")

        if not secret_hash or signature != secret_hash:
            logger.error("Invalid webhook signature")
            return JsonResponse({"error": "Invalid webhook signature"}, status=403)

        # To ensure the request is JSON
        try:
            event = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        logger.info(f"Received Webhook: {event}")

        # Extract data correctly
        status = event.get("data", {}).get("status")
        tx_ref = event.get("data", {}).get("tx_ref")

        # Process successful payment
        if status == "successful":
            order = Order.objects.filter(order_id=tx_ref, paid=False).first()
            if order:
                order.paid = True
                order.save()

                # Clear cart after successful payment
                CartItem.objects.filter(user=order.customer).delete()

                # Send confirmation email
                send_order_confirmation_email(order)

                 # Log only necessary details
                logger.info(f"Order {tx_ref} marked as paid and email sent.")

        return JsonResponse({"status": "success"})

    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
    
# This feature is for the sending of order confirmation email to user containing list of product bought
def send_order_confirmation_email(order):
    subject = 'Order Confirmation – Thank You for Your Purchase!'
    sender_email = settings.EMAIL_HOST_USER
    recipient =  order.customer.email

    # To render the HTML email template
    message = render_to_string('pages/order_confirmation_email.html', {'order':order})

    # Convert HTML to plain text for email clients that don't support HTML
    text_content = strip_tags(message)

    # Create an email message with both plain text anf HTML
    email = EmailMultiAlternatives(subject, text_content, sender_email, [recipient])
    email.attach_alternative(message, 'text/html')

    # Send the email
    email.send()

# For the viewing of all orders that have been placed successfully by a user
@method_decorator(login_required, name='dispatch')
class OrderView(View):
    def get(self, request):

        # Get orders directly from the database linked to the logged-in user
        orders = OrderItem.objects.filter(order__customer=request.user).order_by('-id')

        if not orders.exists():
            messages.info(request, 'You have no orders yet.')

        # Calculate subtotal by summing all the prices
        subtotal = sum(float(order.product.price) * order.quantity for order in orders)

        shipping_cost = 1 
        total = subtotal + shipping_cost

         # Attach computed total price to each order item
        for order in orders:
            order.total_price = float(order.product.price) * order.quantity


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
def order_confirm(request, order_id):
    status = request.GET.get('status')  # Get the status from the URL
    tx_ref = request.GET.get('tx_ref')  # Get transaction reference

    # Retrieve the order details from the database
    order = Order.objects.filter(order_id=order_id).first()

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
        'order_id': order_id,
        'status': status,  # Pass payment status
        'tx_ref': tx_ref,  # Pass transaction reference
        'order': order  # Pass the order object if needed
    }

    if status == 'cancelled':
        return redirect('payment-failed')  # Redirect to a payment cancelled page

    # Proceed with normal order confirmation if not cancelled
    return render(request, 'pages/order_confirm.html', context)

@login_required
def Payment_failed(request):
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'title': 'Order Placement Failed.',
        'newsletter': newsletter,
    }
    return render(request, 'pages/payment-cancel.html', context)

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
        'category': category,
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

def error_404(request, exception):
    # This part is for user's to subscribe to the newsletter found in the footer
    if request.method  == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/success.html')
    newsletter = NewsletterForm()

    context = {
        'status_code': 404,
        'error_message': 'Page Not Found',
        'newsletter': newsletter,
        'title': 'Oops! Page Not Found',
    }
    return render(request, 'pages/404.html', context, status=404)

def error_500(request):
    context = {
        'status_code': 500,
        'error_message': 'Internal Server Error',
        'title': '500 - Server Error',
    }
    return render(request, 'pages/500.html', context, status=500)

