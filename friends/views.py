from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import FriendRequest
from .forms import FriendRequestForm, ConfirmFriendRequestForm
from .services import FriendService
from accounts.models import User

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        form = FriendRequestForm(request.POST, user=request.user)
        if form.is_valid():
            to_user = form.cleaned_data['to_user']
            success, message = FriendService.send_friend_request(request.user, to_user)
            messages.success(request, message)
            return redirect('friends_list' if success else 'friend_requests')
    else:
        form = FriendRequestForm(user=request.user)
    return render(request, 'friends/send_friend_request.html', {'form': form})

@login_required
def confirm_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        form = ConfirmFriendRequestForm(request.POST, instance=friend_request)
        if form.is_valid():
            message = FriendService.confirm_friend_request(friend_request)
            messages.success(request, message)
            return redirect('friend_requests')
        else:
            return render(request, 'friends/confirm_friend_request.html', {'form': form})
    else:
        form = ConfirmFriendRequestForm(instance=friend_request)
    return render(request, 'friends/confirm_friend_request.html', {'form': form})

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        friend_request.delete()
        messages.success(request, 'Friend request rejected.')
        return redirect('friend_requests')

@login_required
def friend_requests(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user)
    sent_requests = FriendRequest.objects.filter(from_user=request.user)
    return render(request, 'friends/friend_requests.html', {'received_requests': received_requests, 'sent_requests': sent_requests})

@login_required
def friends_list(request):
    friends = FriendService.get_friends(request.user)
    users = User.objects.exclude(id=request.user.id)
    received_requests = FriendRequest.objects.filter(to_user=request.user)
    return render(request, 'friends/friends_list.html', {'friends': friends, 'users': users, 'received_requests': received_requests})
