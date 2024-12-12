from django import forms
from .models import ContactMail, Comment, Newsletter

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMail
        fields = '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'body',)

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']