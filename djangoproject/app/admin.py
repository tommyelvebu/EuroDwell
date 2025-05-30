from django.contrib import admin
from .models import (
    Apartment,
    SwapRequest,
    Match,
    Message,
    Review,
    Report,
    Profile,
    ApartmentImage,
)


class ApartmentAdmin(admin.ModelAdmin):
    list_display = ["location", "user"]  
    search_fields = ["location", "user__username"]
    list_filter = [] 


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ["requester", "recipient", "apartment_requested", "status"]
    list_filter = ["status"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "created_at"]
    search_fields = ["sender__username", "receiver__username"]


class ReviewAdmin(admin.ModelAdmin):
    list_display = ["reviewer", "reviewee", "rating", "created_at"]
    search_fields = ["reviewer__username", "reviewee__username"]


class ReportAdmin(admin.ModelAdmin):
    list_display = ["reporter", "reported_user", "created_at"]
    search_fields = ["reporter__username", "reported_user__username"]
    list_filter = [] 


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "phone_number",
        "email_notifications",
        "sms_notifications",
    ]
    search_fields = ["user__username", "phone_number"]


class ApartmentImageAdmin(admin.ModelAdmin):
    list_display = ["apartment", "uploaded_at"]
    search_fields = ["apartment__title"]


admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(SwapRequest, SwapRequestAdmin)
admin.site.register(Match)
admin.site.register(Message, MessageAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ApartmentImage, ApartmentImageAdmin)
