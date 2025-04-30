from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Apartment, SwapRequest, Message, Review, Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address is already registered.')
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 1:
            raise forms.ValidationError('Enter your first name.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise forms.ValidationError('Enter your last name.')
        return last_name

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

UserLoginForm = AuthenticationForm

class UserUpdateForm(UserChangeForm):
    password = None
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

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 1:
            raise forms.ValidationError('FEnter your first name.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 1:
            raise forms.ValidationError('Enter your last name.')
        return last_name
    
# We need to make an extention of this user update form above, since these variables are not in the standard django user form:
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Profile
        fields = ['bio', 'phone_number', 'sms_notifications', 'email_notifications', 'avatar']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ApartmentForm(forms.ModelForm):
    images = forms.ImageField(
        widget=MultipleFileInput(),
        required=False
    )

    class Meta:
        model = Apartment
        fields = ['title', 'description', 'location', 'bedrooms', 'bathrooms', 'available_from', 'available_until']

    def clean_size(self):
        size = self.cleaned_data.get('size')
        if size <= 0:
            raise forms.ValidationError('Size must be a positive number.')
        return size

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if len(location.strip()) < 1:
            raise forms.ValidationError('Enter a valid location.')
        return location

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 1:
            raise forms.ValidationError('Enter a valid description')
        return description

class SwapRequestForm(forms.ModelForm):
    class Meta:
        model = SwapRequest
        fields = ['message']

    def clean_apartment_requested(self):
        apartment = self.cleaned_data.get('apartment_requested')
        if self.instance.requester == apartment.user:
            raise forms.ValidationError('You cannot request your own apartment.')
        return apartment

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]

    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 1:
            raise forms.ValidationError('Message cannot be empty.')
        return content

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError('Rating must be between 1 and 5.')
        return rating

    def clean_comment(self):
        comment = self.cleaned_data.get('comment')
        if len(comment.strip()) < 1:
            raise forms.ValidationError('Enter a comment.')
        return comment