from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import Apartment, SwapRequest, Match, Message, Review, ApartmentImage
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ApartmentForm, SwapRequestForm, MessageForm, ReviewForm
from datetime import date, timedelta
from .forms import ProfileUpdateForm

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
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            request.user.email = form.cleaned_data.get('email')
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.save()
            form.save()

            return redirect('profile')
    else:
        # To pre-fill data
        form = ProfileUpdateForm(instance=request.user.profile, initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })

    return render(request, 'update_profile.html', {'form': form})


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
            # Set a default available_until if it's not provided
            if not apartment.available_until:
                apartment.available_until = date.today() + timedelta(days=365)
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

    # Get all apartments owned by the user
    user_apartments = Apartment.objects.filter(user=request.user)

    if not user_apartments.exists():
        return redirect('create_apartment')

    if request.method == "POST":
        form = SwapRequestForm(request.POST)
        selected_apartment_id = request.POST.get('selected_apartment')

        if form.is_valid() and selected_apartment_id:
            swap_request = form.save(commit=False)
            swap_request.requester = request.user
            swap_request.apartment_requested = apartment
            swap_request.apartment_offered = get_object_or_404(Apartment, id=selected_apartment_id, user=request.user)
            swap_request.save()
            return redirect("swap_requests")
    else:
        form = SwapRequestForm()

    return render(request, "request_swap.html", {
        "form": form,
        "apartment": apartment,
        "user_apartments": user_apartments,  # pass all apartments
    })



# View swap requests
@login_required
def swap_requests(request):
    requests_sent = SwapRequest.objects.filter(requester=request.user)
    requests_received = SwapRequest.objects.filter(apartment_requested__user=request.user)
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
            message.receiver = recipient
            message.save()
            return redirect("messages")
    else:
        form = MessageForm()
    return render(request, "send_message.html", {"form": form, "recipient": recipient})

# View messages
@login_required
def user_messages(request):
    received_messages = Message.objects.filter(receiver=request.user)
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