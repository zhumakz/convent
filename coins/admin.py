from django.contrib import admin
from .models import DoscointBalance, Transaction


class DoscointBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance')


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp', 'description')
    readonly_fields = ('sender', 'recipient', 'amount', 'timestamp', 'description')


admin.site.register(DoscointBalance, DoscointBalanceAdmin)
admin.site.register(Transaction, TransactionAdmin)
