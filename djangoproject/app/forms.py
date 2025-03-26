from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Apartment, SwapRequest, Message, Review

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email address is already in use.')
        return email
    
# Apartment Form - For users to create/edit apartment listings
class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ["location", "size", "description", "image"]  # Include all necessary fields

# Swap Request Form - For users to request a swap
class SwapRequestForm(forms.ModelForm):
    class Meta:
        model = SwapRequest
        fields = ['apartment_requested']  # Users can send a message with their swap request

# Message Form - For users to send messages
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]  # Message content only

# Review Form - For users to submit reviews
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]  # Users rate and leave a comment