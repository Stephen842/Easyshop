from django import forms
from .models import ContactMail

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMail
        fields = '__all__'