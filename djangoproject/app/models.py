from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from PIL import Image

def default_available_until():
    return date.today() + timedelta(days=365)
class Apartment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    country = models.CharField(max_length=100,default='Norway')
    city = models.CharField(max_length=100,default='Oslo')
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    shared_bathroom = models.BooleanField(default=False) 
    shared_kitchen = models.BooleanField(default=False)
    available_from = models.DateField(default=date.today)
    available_until = models.DateField(default=default_available_until)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def location(self):
        return f"{self.city}, {self.country}"

def validate_image_extension(image):
    valid_formats = ['JPEG', 'JPG', 'PNG']
    try:
        img = Image.open(image)
        if img.format.upper() not in valid_formats:
            raise ValidationError(_("Only JPEG and PNG formats are supported."))
    except Exception:
        raise ValidationError(_("Invalid image format."))

class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.apartment.title}"
        
    def clean(self):
        # Size check
        max_size_mb = 5
        if self.image and self.image.size > max_size_mb * 1024 * 1024:
            raise ValidationError(_(f"Image file too large ( > {max_size_mb}MB )"))

        # Format check using Pillow
        validate_image_extension(self.image)


# Swap Request Model
class SwapRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    apartment_requested = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="requests")
    apartment_offered = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="offers", null=True, blank=True)
    status_choices = [('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined')]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)
    swap_start_date = models.DateField(null=True, blank=True)
    swap_end_date = models.DateField(null=True, blank=True)
    def __str__(self):
        return f"Request from {self.requester} to {self.recipient} for {self.apartment_requested}"

# Match Model (Confirmed Swaps)
class Match(models.Model):
    swap_request = models.OneToOneField(SwapRequest, on_delete=models.CASCADE)
    confirmed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Match: {self.swap_request.requester} ↔ {self.swap_request.recipient}"

# Messaging Model
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)  #  Add this line
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

# Review Model
class Review(models.Model):
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    reviewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewee} - {self.rating} stars"

# Report Model (For handling complaints)
class Report(models.Model):
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_made")
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reports_received")
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report by {self.reporter} against {self.reported_user}"



# New model - profile - extention of previous update profile which is built on djangos user model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} Profile"
    
    def average_rating(self):
        reviews = Review.objects.filter(reviewee=self.user)
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    def total_reviews(self):
        return Review.objects.filter(reviewee=self.user).count()