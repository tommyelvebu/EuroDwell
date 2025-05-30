from .models import Message, SwapRequest

def unread_message_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(receiver=request.user, is_read=False).count()
        return {'unread_message_count': count}
    return {}

def pending_swap_requests_count(request):
    if request.user.is_authenticated:
        count = SwapRequest.objects.filter(
            apartment_requested__user=request.user,
            status='Pending'
        ).count()
        return {'pending_swap_requests_count': count}
    return {}
