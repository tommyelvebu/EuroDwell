from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home, name="home"),
    path('register/', views.register, name = 'register'),
    path('login/', views.user_login, name = 'login'),
    path('logout/', views.user_logout, name = 'logout'),
    path('profile/', views.update_profile, name = 'profile'),

    # Apartment-related views
    path('apartment/<int:apartment_id>/', views.apartment_details, name='apartment_details'),
    path('apartment/create/', views.create_apartment, name='create_apartment'),

    # Swap requests
    path('apartment/<int:apartment_id>/request_swap/', views.request_swap, name='request_swap'),
    path('swap_requests/', views.swap_requests, name='swap_requests'),
    path('swap_request/<int:swap_id>/accept/', views.accept_swap, name='accept_swap'),

    # Messaging system
    path('messages/', views.user_messages, name='messages'),
    path('message/<int:recipient_id>/send/', views.send_message, name='send_message'),

    # Reviews
    path('review/<int:user_id>/submit/', views.submit_review, name='submit_review'),
]
