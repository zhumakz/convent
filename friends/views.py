from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import FriendRequest, Friendship
from .forms import FriendRequestForm, ConfirmFriendRequestForm
from accounts.models import User

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        form = FriendRequestForm(request.POST, user=request.user)
        if form.is_valid():
            friend_request = form.save(commit=False)
            friend_request.from_user = request.user
            friend_request.save()
            messages.success(request, 'Запрос на добавление в друзья отправлен!')
            return redirect('friend_requests')
    else:
        form = FriendRequestForm(user=request.user)
    return render(request, 'friends/send_friend_request.html', {'form': form})

@login_required
def confirm_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    if request.method == 'POST':
        form = ConfirmFriendRequestForm(request.POST, instance=friend_request)
        if form.is_valid():
            Friendship.objects.create(user1=friend_request.from_user, user2=friend_request.to_user)
            friend_request.delete()
            messages.success(request, 'Запрос в друзья подтвержден!')
            return redirect('friend_requests')
    else:
        form = ConfirmFriendRequestForm(instance=friend_request)
    return render(request, 'friends/confirm_friend_request.html', {'form': form})

@login_required
def friend_requests(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user)
    sent_requests = FriendRequest.objects.filter(from_user=request.user)
    return render(request, 'friends/friend_requests.html', {'received_requests': received_requests, 'sent_requests': sent_requests})

@login_required
def friends_list(request):
    friendships1 = request.user.friendships1.all()
    friendships2 = request.user.friendships2.all()
    friends = [f.user2 for f in friendships1] + [f.user1 for f in friendships2]
    return render(request, 'friends/friends_list.html', {'friends': friends})
