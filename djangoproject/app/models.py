from django.db import models

# Create your models here.
from django.contrib.auth.models import User


# Apartment Model
class Apartment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # here we use foreign key to create a one-to-many relationship
    #  on_delete=models.CASCADE ensures that when a user is deleted, the related 
    # information would be also deleted automatically
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField()
    size = models.IntegerField(help_text="Size in square meters")
    amenities = models.TextField(help_text="Comma-separated list of amenities")
    available_from = models.DateField()
    available_to = models.DateField()
    image = models.ImageField(upload_to='apartments/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.location}"



class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='apartments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.apartment.title}"


# Swap Request Model
class SwapRequest(models.Model):
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_requests")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_requests")
    apartment_requested = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="requests")
    status_choices = [('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Declined', 'Declined')]
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

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
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

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


