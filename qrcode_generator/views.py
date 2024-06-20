from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404
from accounts.models import User

def user_qr_code_view(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'qrcode_generator/user_qr_code.html', {'user': user})
