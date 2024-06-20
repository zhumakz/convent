

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from friends.models import FriendRequest
from cryptography.fernet import Fernet
from django.conf import settings

KEY = settings.QR_CODE_KEY


def user_qr_code_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'qrcode_generator/user_qr_code.html', {'user': user})
@login_required
def process_qr_code(request, encrypted_id):
    f = Fernet(KEY)
    try:
        user_id = f.decrypt(encrypted_id.encode()).decode()
        user = get_object_or_404(User, id=user_id)
        if user != request.user:
            # Проверим, есть ли уже запрос на дружбу
            if not FriendRequest.objects.filter(from_user=request.user, to_user=user).exists():
                FriendRequest.objects.create(from_user=request.user, to_user=user)
                message = f'Friend request sent to {user.name} {user.surname}.'
            else:
                message = f'You have already sent a friend request to {user.name} {user.surname}.'
        else:
            message = "You cannot send a friend request to yourself."
    except Exception as e:
        message = "Invalid QR code."
    return render(request, 'qrcode_generator/qr_code_result.html', {'message': message})



