from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import Apartment, SwapRequest, Message, Review, Profile, Report
import re

EUROPEAN_PHONE_CODES = [
    ("+43", "Austria (+43)"),
    ("+32", "Belgium (+32)"),
    ("+385", "Croatia (+385)"),
    ("+420", "Czech Republic (+420)"),
    ("+45", "Denmark (+45)"),
    ("+372", "Estonia (+372)"),
    ("+358", "Finland (+358)"),
    ("+33", "France (+33)"),
    ("+49", "Germany (+49)"),
    ("+30", "Greece (+30)"),
    ("+36", "Hungary (+36)"),
    ("+354", "Iceland (+354)"),
    ("+353", "Ireland (+353)"),
    ("+39", "Italy (+39)"),
    ("+371", "Latvia (+371)"),
    ("+370", "Lithuania (+370)"),
    ("+31", "Netherlands (+31)"),
    ("+47", "Norway (+47)"),
    ("+48", "Poland (+48)"),
    ("+351", "Portugal (+351)"),
    ("+421", "Slovakia (+421)"),
    ("+386", "Slovenia (+386)"),
    ("+34", "Spain (+34)"),
    ("+46", "Sweden (+46)"),
    ("+41", "Switzerland (+41)"),
]

PHONE_VALIDATION_RULES = {
    "+43": (10, 13), "+32": (9, 10), "+385": (8, 9), "+420": (9, 9),
    "+45": (8, 8), "+372": (7, 8), "+358": (9, 10), "+33": (10, 10),
    "+49": (10, 12), "+30": (10, 10), "+36": (8, 9), "+354": (7, 7),
    "+353": (9, 9), "+39": (10, 11), "+371": (8, 8), "+370": (8, 8),
    "+31": (9, 9), "+47": (8, 8), "+48": (9, 9), "+351": (9, 9),
    "+421": (9, 9), "+386": (8, 8), "+34": (9, 9), "+46": (9, 10), "+41": (9, 10),
}

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
            raise forms.ValidationError(
                'An account with this email already exists. '
                'If you forgot your password, you can reset it on the login page.'
            )
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
            raise forms.ValidationError('Enter your first name.')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 1:
            raise forms.ValidationError('Enter your last name.')
        return last_name
    
# We need an extention of the user update form above, since these variables are not in the standard django user form:
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=255, required=True)
    last_name = forms.CharField(max_length=255, required=True)
    
    phone_country_code = forms.ChoiceField(
        choices=[("", "Select Country")] + EUROPEAN_PHONE_CODES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'phone_country_code'})
    )
    phone_local_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'phone_local_number',
            'placeholder': 'Enter phone number',
            'pattern': '[0-9\s]*',
            'inputmode': 'numeric'
        })
    )

    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.phone_number:
            phone = self.instance.phone_number.strip()
            for code, _ in EUROPEAN_PHONE_CODES:
                if phone.startswith(code):
                    self.fields['phone_country_code'].initial = code
                    self.fields['phone_local_number'].initial = phone[len(code):].strip()
                    break

    def clean(self):
        cleaned_data = super().clean()
        country_code = cleaned_data.get('phone_country_code')
        local_number = cleaned_data.get('phone_local_number')
        
        if country_code and local_number:
            clean_number = re.sub(r'[^\d]', '', local_number)

            if country_code in PHONE_VALIDATION_RULES:
                min_len, max_len = PHONE_VALIDATION_RULES[country_code]
                if not (min_len <= len(clean_number) <= max_len):
                    raise forms.ValidationError(
                        f'Phone number for {dict(EUROPEAN_PHONE_CODES)[country_code]} '
                        f'should be {min_len}-{max_len} digits long.'
                    )

            cleaned_data['phone_number'] = f"{country_code} {clean_number}"
        elif country_code or local_number:
            raise forms.ValidationError('Please provide both country code and phone number, or leave both empty.')
        else:
            cleaned_data['phone_number'] = ''
            
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        phone_number = self.cleaned_data.get('phone_number', '')
        instance.phone_number = phone_number
        if commit:
            instance.save()
        return instance
        
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result
    
EUROPEAN_COUNTRIES = [
    ("Austria", "Austria"),
    ("Belgium", "Belgium"),
    ("Croatia", "Croatia"),
    ("Czech Republic", "Czech Republic"),
    ("Denmark", "Denmark"),
    ("Estonia", "Estonia"),
    ("Finland", "Finland"),
    ("France", "France"),
    ("Germany", "Germany"),
    ("Greece", "Greece"),
    ("Hungary", "Hungary"),
    ("Iceland", "Iceland"),
    ("Ireland", "Ireland"),
    ("Italy", "Italy"),
    ("Latvia", "Latvia"),
    ("Lithuania", "Lithuania"),
    ("Netherlands", "Netherlands"),
    ("Norway", "Norway"),
    ("Poland", "Poland"),
    ("Portugal", "Portugal"),
    ("Slovakia", "Slovakia"),
    ("Slovenia", "Slovenia"),
    ("Spain", "Spain"),
    ("Sweden", "Sweden"),
    ("Switzerland", "Switzerland"),
]


class ApartmentForm(forms.ModelForm):
    images = MultipleImageField(
        required=False,
        help_text="Select multiple images for your apartment listing."
    )

    country = forms.ChoiceField(
        choices=EUROPEAN_COUNTRIES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the city (e.g., Oslo, Rome)."
    )
    shared_bathroom = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    shared_kitchen = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Apartment
        fields = [
            'title', 'description', 'country', 'city',
            'bedrooms', 'bathrooms', 'shared_bathroom', 'shared_kitchen',
            'available_from', 'available_until','images'
        ]

        widgets = {
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_from': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'available_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shared_bathroom': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'shared_kitchen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description.strip()) < 10:
            raise forms.ValidationError('Please provide a more detailed description (at least 10 characters).')
        return description

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if len(city.strip()) < 2:
            raise forms.ValidationError('Enter a valid city.')
        return city

 
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Type your message...'
            }),
        }


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
    

class SwapRequestForm(forms.ModelForm):
    swap_start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    swap_end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = SwapRequest
        fields = ['message', 'swap_start_date', 'swap_end_date']

    def __init__(self, *args, **kwargs):
        self.available_from = kwargs.pop('available_from', None)
        self.available_until = kwargs.pop('available_until', None)
        super().__init__(*args, **kwargs)

        if self.available_from:
            self.fields['swap_start_date'].widget.attrs['min'] = self.available_from.strftime('%Y-%m-%d')
            self.fields['swap_end_date'].widget.attrs['min'] = self.available_from.strftime('%Y-%m-%d')
        if self.available_until:
            self.fields['swap_start_date'].widget.attrs['max'] = self.available_until.strftime('%Y-%m-%d')
            self.fields['swap_end_date'].widget.attrs['max'] = self.available_until.strftime('%Y-%m-%d')

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('swap_start_date')
        end = cleaned_data.get('swap_end_date')

        if start and end:
            if start > end:
                raise forms.ValidationError("End date must be after start date.")
            if self.available_from and start < self.available_from:
                raise forms.ValidationError("Start date is before availability.")
            if self.available_until and end > self.available_until:
                raise forms.ValidationError("End date is after availability.")

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['report_type', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Please provide details about your report...'}),
            'report_type': forms.Select(attrs={'class': 'form-control'})
        }

