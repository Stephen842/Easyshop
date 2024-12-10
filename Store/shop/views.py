from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .forms import CommentForm, ContactForm # Import the form
from .models import Category, Post, Comment, ContactMail  # and also Import the model


# Create your views here.

# For the store homepage
def home(request):
    context = {
        'title': 'Elvix Luxe – Fashion That Inspires Confidence',
    }
    return render(request, 'pages/store.html', context)

# For the blog page
def blog(request):
    posts = Post.objects.all().order_by('-created_on')
    context = {
        'posts': posts,
        'title': 'Your Style Destination for Fashion Trends and Inspiration',
    }
    return render(request, 'pages/blog.html', context)

# For the blog category
def blog_category(request, category):
    posts = Post.objects.filter(
        categories__name__contains=category
        ).order_by('-created_on')
    context = {
        "category": category,
        'posts': posts,
        'title': 'Discover Your Perfect Style',
    }
    return render(request, 'pages/category.html', context)

# For the blog details
def blog_details(request, pk):
    post = Post.objects.get(pk=pk)
    
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
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'pages/blog_detail.html', context)



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

# For the message sent page
def message_sent(request):
    context = {
        'title': 'Message Sent Successfully!'
    }
    return render(request, 'pages/success.html', context)
