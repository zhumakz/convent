from django.contrib import admin
from .models import DoscointBalance, Transaction
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class DoscointBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp', 'description')
    readonly_fields = ('sender', 'recipient', 'amount', 'timestamp', 'description')

admin.site.register(DoscointBalance, DoscointBalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)

# Создаем группы и разрешения
content_type = ContentType.objects.get_for_model(Transaction)
permissions = [
    Permission.objects.get_or_create(codename='can_add_coins', name='Can add coins', content_type=content_type)[0],
    Permission.objects.get_or_create(codename='can_remove_coins', name='Can remove coins', content_type=content_type)[0],
]

# Группа модераторов, которые могут добавлять коинов
add_coins_group, created = Group.objects.get_or_create(name='AddCoinsModerators')
add_coins_group.permissions.add(permissions[0])

# Группа модераторов, которые могут убавлять коины
remove_coins_group, created = Group.objects.get_or_create(name='RemoveCoinsModerators')
remove_coins_group.permissions.add(permissions[1])
