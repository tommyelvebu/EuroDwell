from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Apartment, SwapRequest, Match, Message, Review, ApartmentImage
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ApartmentForm, SwapRequestForm, MessageForm, ReviewForm

# Home page: List all available apartments
def home(request):
    apartments = Apartment.objects.all()
    return render(request, "home.html", {"apartments": apartments})



def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in automatically after registration
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form' : form})



def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})



@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserUpdateForm(instance = request.user)
    return render(request, 'update_profile.html', {'form' : form})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# Apartment Details Page
def apartment_details(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    return render(request, "apartment_details.html", {"apartment": apartment})

# Create a new apartment Listing
@login_required
def create_apartment(request):
    if request.method == "POST":
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            apartment.save()
            
            #To handle multiple images to be uploaded
            for image in request.FILES.getlist('images'):
                ApartmentImage.objects.create(
                    apartment=apartment,
                    image=image
                )
            return redirect("home")
    else:
        form = ApartmentForm()
    return render(request, "create_apartment.html", {"form": form})

# Send a swap request
@login_required
def request_swap(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    if request.method == "POST":
        form = SwapRequestForm(request.POST)
        if form.is_valid():
            swap_request = form.save(commit=False)
            swap_request.requester = request.user
            swap_request.apartment_requested  = apartment
            swap_request.save()
            return redirect("swap_requests")
    else:
        form = SwapRequestForm()
    return render(request, "request_swap.html", {"form": form, "apartment": apartment})

# View swap requests
@login_required
def swap_requests(request):
    requests_sent = SwapRequest.objects.filter(requester=request.user)
    requests_received = SwapRequest.objects.filter(apartment__user=request.user)
    return render(request, "swap_requests.html", {"requests_sent": requests_sent, "requests_received": requests_received})

# Accept a swap request
@login_required
def accept_swap(request, swap_id):
    swap = get_object_or_404(SwapRequest, id=swap_id, apartment__user=request.user)
    swap.status = "Accepted"
    swap.save()
    return redirect("swap_requests")

# Messaging system between users
@login_required
def send_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect("messages")
    else:
        form = MessageForm()
    return render(request, "send_message.html", {"form": form, "recipient": recipient})

# View messages
@login_required
def messages(request):
    received_messages = Message.objects.filter(recipient=request.user)
    sent_messages = Message.objects.filter(sender=request.user)
    return render(request, "messages.html", {"received_messages": received_messages, "sent_messages": sent_messages})

# Submit a review after swap
@login_required
def submit_review(request, user_id):
    reviewed_user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewee = reviewed_user
            review.save()
            return redirect("home")
    else:
        form = ReviewForm()
    return render(request, "submit_review.html", {"form": form, "reviewed_user": reviewed_user})



