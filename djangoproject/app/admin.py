from django.contrib import admin
from .models import Apartment, SwapRequest, Match, Message, Review, Report

admin.site.register(Apartment)
admin.site.register(SwapRequest)
admin.site.register(Match)
admin.site.register(Message)
admin.site.register(Review)
admin.site.register(Report)
