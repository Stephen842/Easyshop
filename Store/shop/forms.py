from django import forms
from .models import Comment, ContactMail

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMail
        fields = '__all__'

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('author', 'body',)