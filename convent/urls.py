from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('friends/', include('friends.urls')),
    path('coins/', include('coins.urls')),
    path('qr/', include('qrcode_generator.urls')),
    path('campaigns/', include('campaigns.urls')),
    path('leaderboard/', include('leaderboard.urls')),
    path('lectures/', include('lectures.urls')),
    path('shop/', include('shop.urls')),
    path('sms/', include('sms.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
