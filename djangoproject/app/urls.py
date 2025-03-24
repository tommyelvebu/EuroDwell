from django.urls import path
from . import views 
from .views import register, user_login, user_logout, update_profile

urlpatterns = [
    path("", views.home, name="home"),
    path('register/', register, name = 'register'),
    path('login/', user_login, name = 'login'),
    path('logout/', user_logout, name = 'logout'),
    path('profile/', update_profile, name = 'profile'),

]