from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('blog/', views.blog, name='blog'),
    path('post/<int:pk>/', views.blog_details, name='blog_details'),
    path('category/<category>/', views.blog_category, name='blog_category'),
    #path('gallery/', views.gallery, name='gallery'),
    path('contact_us/', views.contact, name='contact_us'),
    path('message_sent/', views.message_sent, name='message_sent'),
    
]
