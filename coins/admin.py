from django.contrib import admin
from .models import DoscointBalance, Transaction, TransactionCategory


@admin.register(TransactionCategory)
class TransactionCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    readonly_fields = ('name',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'amount', 'timestamp', 'category', 'is_positive')
    search_fields = ('sender__username', 'recipient__username', 'category__name')
    list_filter = ('category', 'is_positive')


@admin.register(DoscointBalance)
class DoscointBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'total_earned', 'total_spent')
    search_fields = ('user__username',)
    list_filter = ('balance', 'total_earned', 'total_spent')
