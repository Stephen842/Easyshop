from django.urls import path
from . import views
from .views import Signup, Index, Cart, CheckOut, OrderView 

urlpatterns = [
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', views.Signin, name='login'), 
    path('logout/', views.logout, name='logout'),
    path('', Index.as_view(), name='homepage'), 
    path('Store/', views.home, name='Store'),
    path('product-details/<int:id>', views.Product_details, name='product-details'),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path('cart/', Cart.as_view(), name='cart'),
    path('checkout/', CheckOut.as_view(), name='checkout'),
    path('webhook/flutterwave/', views.flutterwave_webhook, name='flutterwave-webhook'),
    path('order-confirm/<str:order_id>/', views.order_confirm, name='order-confirm'),
    path('Payment-Failed/', views.Payment_failed, name='payment-failed'),
    path('orders/', OrderView.as_view(), name='orders'),
    path('blog/', views.blog, name='blog'),
    path('post/<int:pk>/', views.blog_details, name='blog_details'),
    path('category/<category>/', views.blog_category, name='blog_category'),
    path('gallery/', views.gallery, name='gallery'),
    path('contact_us/', views.contact, name='contact_us'),
    path('search/', views.search, name='search'),
    path('message_sent/', views.message_sent, name='message_sent'),
    path('email/', views.email, name='email'),
]
