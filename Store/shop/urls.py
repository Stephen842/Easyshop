from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    #path('blog/', views.blog, name='blog'),
    #path('gallery/', views.gallery, name='gallery'),
    #path('contact_us/', views.contact, name='contact_us'),
    
]