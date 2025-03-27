from django.contrib import admin
from .models import Apartment, SwapRequest, Match, Message, Review, Report


class ApartmentAdmin(admin.ModelAdmin):
    list_display = ["location", "size", "user", "approved"]
    search_fields = ["location", "user__username"]
    list_filter = ["approved"]


class SwapRequestAdmin(admin.ModelAdmin):
    list_display = ["requester", "requested", "apartment", "status"]
    list_filter = ["status"]


class MessageAdmin(admin.ModelAdmin):
    list_display = ["sender", "receiver", "timestamp"]
    search_fields = ["sender__username", "receiver__username"]


class ReviewAdmin(admin.ModelAdmin):
    list_display = ["reviewer", "reviewee", "rating", "timestamp"]
    search_fields = ["reviewer__username", "reviewee__username"]


class ReportAdmin(admin.ModelAdmin):
    list_display = ["reporter", "reported_user", "timestamp", "resolved"]
    search_fields = ["reporter__username", "reported_user__username"]
    list_filter = ["resolved"]


admin.site.register(Apartment)
admin.site.register(SwapRequest)
admin.site.register(Match)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Report)
