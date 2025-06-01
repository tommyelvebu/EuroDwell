from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import messages as msg_system
from django.db.models import Q
from django.utils.timezone import now

from datetime import date, timedelta
from itertools import chain

from .models import Apartment, SwapRequest, Match, Message, Review, ApartmentImage, Profile
from .forms import (
    UserRegistrationForm, UserLoginForm, UserUpdateForm, ApartmentForm, 
    SwapRequestForm, MessageForm, ReviewForm, ReportForm, ProfileUpdateForm,
    EUROPEAN_COUNTRIES
)


def homepage(request):
    destinations = [
        {"name": "Poland", "image": "destinations/Poland.jpeg"},
        {"name": "Italy", "image": "destinations/Italy.jpeg"},
        {"name": "Latvia", "image": "destinations/Latvia.jpeg"},
        {"name": "Norway", "image": "destinations/Norway.jpeg"},
        {"name": "Netherlands", "image": "destinations/Netherlands.jpeg"},
        {"name": "Spain", "image": "destinations/Spain.jpeg"},
    ]
    return render(request, "homepage.html", {"destinations": destinations, "destinations": destinations,
        "countries": EUROPEAN_COUNTRIES,
})

# explore page: List all available apartments
def explore(request):
    country = request.GET.get("country")

    if country:
        apartments = Apartment.objects.filter(
            country__icontains=country
        ).order_by('-available_until')
    else:
        apartments = Apartment.objects.all().order_by('-available_until')

    return render(request, "explore.html", {
        "apartments": apartments,
        "country": country,
        "countries": EUROPEAN_COUNTRIES,
    })





def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in automatically after registration
            return redirect('explore')
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
                remember_me = request.POST.get('remember_me')
                if remember_me:
                    request.session.set_expiry(1209600) ##1209600 seconds = 2 weeks
                else:
                    request.session.set_expiry(0)
                login(request, user)
                return redirect('explore')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def profile(request):
    user_apartments = Apartment.objects.filter(user=request.user)

    # Check if the user has any completed swaps they haven't reviewed yet
    eligible_swaps = SwapRequest.objects.filter(
    status="Accepted",
    swap_end_date__lt=now().date()
).filter(
    Q(requester=request.user) | Q(recipient=request.user)
)

    users_to_review = []
    for swap in eligible_swaps:
        other_user = swap.recipient if swap.requester == request.user else swap.requester
        already_reviewed = Review.objects.filter(
            reviewer=request.user,
            reviewee=other_user,
            created_at__date__gte=swap.swap_end_date
        ).exists()
        if not already_reviewed and other_user not in users_to_review:
            users_to_review.append(other_user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if form.is_valid():
            request.user.email = form.cleaned_data.get('email')
            request.user.first_name = form.cleaned_data.get('first_name')
            request.user.last_name = form.cleaned_data.get('last_name')
            request.user.save()
            form.save()

            from django.contrib import messages
            messages.success(request, 'Your profile has been successfully updated!')
            
            return redirect('profile')

    else:
        form = ProfileUpdateForm(instance=request.user.profile, initial={
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })

    return render(request, 'profile.html', {
        'form': form,
        'user_apartments': user_apartments,
        'users_to_review': users_to_review,
    })






@login_required
def edit_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id, user=request.user)

    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES, instance=apartment)
        if form.is_valid():
            form.save()

            # Handle new images (optional: clear old ones first)
            images = request.FILES.getlist('images')
            if images:
                # Optionally clear old images
                ApartmentImage.objects.filter(apartment=apartment).delete()

                for image in images:
                    ApartmentImage.objects.create(apartment=apartment, image=image)

            return redirect('profile')
    else:
        form = ApartmentForm(instance=apartment)

    return render(request, 'edit_apartment.html', {'form': form, 'apartment': apartment})


@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

# Apartment Details Page
def apartment_details(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)
    images = apartment.images.all() 
    profile, created = Profile.objects.get_or_create(user=apartment.user)
    return render(request, "apartment_details.html", {"apartment": apartment,  'images': images})

@login_required
def create_apartment(request):
    if request.method == "POST":
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.user = request.user
            if not apartment.available_until:
                apartment.available_until = date.today() + timedelta(days=365)
            apartment.save()
            
            images = request.FILES.getlist('images')
            for image in images:
                ApartmentImage.objects.create(
                    apartment=apartment,
                    image=image
                )
            return redirect("explore")
    else:
        form = ApartmentForm()
    return render(request, "create_apartment.html", {"form": form})


# Send a swap request
def request_swap(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id)

    # Prevent self-swap
    if apartment.user == request.user:
        messages.error(request, "You cannot request a swap with your own apartment.")
        return redirect('apartment_details', apartment_id=apartment.id)

    user_apartments = Apartment.objects.filter(user=request.user)

    if not user_apartments.exists():
        return redirect('create_apartment')

    if request.method == "POST":
        form = SwapRequestForm(
            request.POST,
            available_from=apartment.available_from,
            available_until=apartment.available_until
        )
        selected_apartment_id = request.POST.get('selected_apartment')

        if form.is_valid() and selected_apartment_id:
            swap_request = form.save(commit=False)
            swap_request.requester = request.user
            swap_request.recipient = apartment.user
            swap_request.apartment_requested = apartment
            swap_request.apartment_offered = get_object_or_404(
                Apartment, id=selected_apartment_id, user=request.user
            )
            swap_request.swap_start_date = form.cleaned_data['swap_start_date']
            swap_request.swap_end_date = form.cleaned_data['swap_end_date']
            swap_request.message = form.cleaned_data.get('message')
            swap_request.save()

            messages.success(request, "Your request has been sent to the owner!")
            return redirect("chat_with_user", recipient_id=apartment.user.id)

    else:
        form = SwapRequestForm(
            available_from=apartment.available_from,
            available_until=apartment.available_until
        )

    return render(request, "request_swap.html", {
        "form": form,
        "apartment": apartment,
        "user_apartments": user_apartments,
    })






# View swap requests
@login_required
def swap_requests(request):
    requests_sent = SwapRequest.objects.filter(requester=request.user).order_by('-created_at')
    requests_received = SwapRequest.objects.filter(apartment_requested__user=request.user).order_by('-created_at')
    return render(request, "swap_requests.html", {"sent_requests": requests_sent, "received_requests": requests_received})

# Accept a swap request
@login_required
def accept_swap(request, swap_id):
    swap_request = get_object_or_404(SwapRequest, id=swap_id, recipient=request.user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            swap_request.status = "Accepted"
            swap_request.save()

            from datetime import date
            if swap_request.swap_end_date and swap_request.swap_end_date <= date.today():
                return redirect('submit_review', user_id=swap_request.requester.id)

            
            messages.success(request, "Swap accepted! Please come back to review after the swap ends.")
            return redirect('swap_requests')

        elif action == "reject":
            swap_request.status = "Declined"
            swap_request.save()
            messages.warning(request, "You declined the swap request.")
            return redirect('swap_requests')

    return redirect('swap_requests')



# Messaging system between users
@login_required
def chat_with_user(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    if recipient == request.user:
        messages.error(request, "You cannot send a message to yourself.")
        return redirect("chat_inbox")


    messages_sent = Message.objects.filter(sender=request.user, receiver=recipient)
    messages_received = Message.objects.filter(sender=recipient, receiver=request.user)
    messages_received.filter(is_read=False).update(is_read=True)

    all_messages = sorted(
        chain(messages_sent, messages_received),
        key=lambda m: m.created_at
    )

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = recipient
            msg.save()
            return redirect('chat_with_user', recipient_id=recipient.id)
    else:
        form = MessageForm()

    return render(request, "chat_with_user.html", {
        "all_messages": all_messages,
        "recipient": recipient,
        "form": form,
    })



# View messages
@login_required
def chat_inbox(request):
    messages = Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
    conversation_partners = {}

    for msg in messages.order_by('-created_at'):
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user not in conversation_partners:
            unread_count = Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).count()
            conversation_partners[other_user] = {
                'last_message': msg,
                'unread_count': unread_count
            }

    return render(request, "chat_inbox.html", {
        'conversations': conversation_partners
    })

 

# Submit a review after swap
@login_required
def submit_review(request, user_id):
    today = now().date()
    other_user = get_object_or_404(User, id=user_id)

    # Find an accepted swap between the current user and the other person
    valid_swap = SwapRequest.objects.filter(
        status='Accepted',
        swap_end_date__lt=today
    ).filter(
        Q(requester=request.user, recipient=other_user) |
        Q(recipient=request.user, requester=other_user)
    ).first()

    if not valid_swap:
        return render(request, "review_permission_denied.html")


    # Prevent duplicate reviews for the same swap and same user
    already_reviewed = Review.objects.filter(
        reviewer=request.user,
        reviewee=other_user,
        created_at__date__gte=valid_swap.swap_end_date  # Only count reviews after swap
    ).exists()

    if already_reviewed:
        messages.info(request, "You have already submitted a review for this user.")
        return redirect("user_profile", user_id=other_user.id)


    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("review_text")

        if rating and comment:
            Review.objects.create(
                reviewer=request.user,
                reviewee=other_user,
                rating=int(rating),
                comment=comment,
            )
            return redirect("user_profile", user_id=other_user.id)

        else:
            return HttpResponseForbidden("All fields are required.")

    return render(request, "submit_review.html", {
        "apartment": valid_swap.apartment_requested,
        "stay_period": {
            "start_date": valid_swap.swap_start_date,
            "end_date": valid_swap.swap_end_date,
        },
        "reviewee": other_user,  # Add the reviewee user object
        "reviewee_profile": other_user.profile,  # Add the reviewee's profile
    })





# page for viewing other profiles 
def user_profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile, created = Profile.objects.get_or_create(user=profile_user)
    user_apartments = Apartment.objects.filter(user=profile_user)
    reviews = Review.objects.filter(reviewee=profile_user).order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'user_apartments': user_apartments,
        'reviews': reviews,
    }
    return render(request, 'user_profile.html', context)

@login_required
def delete_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id, user=request.user)

    if request.method == "POST":
        apartment.delete()
        messages.success(request, "Apartment deleted successfully.")
        return redirect("profile")  

    messages.error(request, "Invalid request.")
    return redirect("profile")

@login_required
def report_user(request, user_id):
    reported_user = get_object_or_404(User, id=user_id)
    
    has_interaction = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=reported_user)) |
        (Q(sender=reported_user) & Q(receiver=request.user))
    ).exists() or SwapRequest.objects.filter(
        (Q(requester=request.user) & Q(recipient=reported_user)) |
        (Q(requester=reported_user) & Q(recipient=request.user))
    ).exists()

    if not has_interaction:
        messages.error(request, "You can only report users you've interacted with through messages or swap requests.")
        return redirect('user_profile', user_id=user_id)

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = reported_user
            report.save()
            messages.success(request, "Your report has been submitted and will be reviewed by our team.")
            return redirect('user_profile', user_id=user_id)
    else:
        form = ReportForm()

    context = {
        'form': form,
        'reported_user': reported_user,
        'messages': Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=reported_user)) |
            (Q(sender=reported_user) & Q(receiver=request.user))
        ).order_by('-created_at'),
        'swap_requests': SwapRequest.objects.filter(
            (Q(requester=request.user) & Q(recipient=reported_user)) |
            (Q(requester=reported_user) & Q(recipient=request.user))
        ).order_by('-created_at')
    }
    return render(request, 'report_user.html', context)