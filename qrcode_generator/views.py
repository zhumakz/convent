from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import User
from friends.models import FriendRequest
from django.conf import settings
from cryptography.fernet import Fernet
from .utils import generate_qr_code


@login_required
def process_qr_code(request, encrypted_id):
    """
    Обрабатывает QR-код, дешифрует ID пользователя и отправляет запрос на добавление в друзья.

    :param request: HTTP запрос.
    :param encrypted_id: Зашифрованный ID пользователя.
    :return: HTTP ответ с результатом обработки QR-кода.
    """
    method = settings.ENCRYPTION_METHOD
    try:
        if method == 'simple':
            decrypted_id = User.decrypt_id(encrypted_id)
            user = get_object_or_404(User, id=decrypted_id)
        elif method == 'cryptography':
            f = Fernet(settings.QR_CODE_KEY)
            user_id = f.decrypt(encrypted_id.encode()).decode()
            user = get_object_or_404(User, id=user_id)
        else:
            raise ValueError("Invalid encryption method")

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


@login_required
def user_qr_code_view(request, user_id):
    """
    Отображает страницу с QR-кодом пользователя.

    :param request: HTTP запрос.
    :param user_id: ID пользователя.
    :return: HTTP ответ с отображением страницы QR-кода.
    """
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'qrcode_generator/user_qr_code.html', {'user': user})
