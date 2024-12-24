from django import forms
from .models import MyCustomer, Order, ContactMail, Comment, Newsletter

class CustomerForm(forms.ModelForm):
    class Meta:
        model = MyCustomer
        fields = '__all__'

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 8:
            raise forms.ValidationError('Name must be 8 characters long or more')
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if len(email) < 8:
            raise forms.ValidationError('Email address must be 8 characters long')
        if MyCustomer.objects.filter(email=email).exists():
            raise forms.ValidationError('Email Address Already Registered...')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if len(phone) < 8:
            raise forms.ValidationError('Phone number is too short')
        return phone

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError('Password is too short')
        return password
    
class SigninForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'

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