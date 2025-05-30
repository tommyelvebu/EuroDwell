from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("explore", views.explore, name="explore"),
    path('register/', views.register, name = 'register'),
    path('login/', views.user_login, name = 'login'),
    path('logout/', views.user_logout, name = 'logout'),
    path('profile/', views.profile, name = 'profile'),
    path('apartment/edit/<int:apartment_id>/', views.edit_apartment, name='edit_apartment'),


    # Password reset URLs (Django built-in)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Apartment-related views
    path('apartment/<int:apartment_id>/', views.apartment_details, name='apartment_details'),
    path('apartment/create/', views.create_apartment, name='create_apartment'),

    # Swap requests
    path('apartment/<int:apartment_id>/request_swap/', views.request_swap, name='request_swap'),
    path('swap_requests/', views.swap_requests, name='swap_requests'),
    path('swap_request/<int:swap_id>/accept/', views.accept_swap, name='accept_swap'),

    # Messaging system
    path('messages/', views.user_messages, name='user_messages'),
    path('message/<int:recipient_id>/send/', views.send_message, name='send_message'),

    # Reviews
    path('review/<int:user_id>/submit/', views.submit_review, name='submit_review'),

    # User profile view (viewing others)
    path('user/<int:user_id>/', views.user_profile_view, name='user_profile'),
]
