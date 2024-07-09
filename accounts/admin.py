from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from modeltranslation.admin import TranslationAdmin

from .models import User, City


@admin.action(description='Generate QR codes for selected users')
def generate_qr_codes(modeladmin, request, queryset):
    for user in queryset:
        user.generate_qr_code()
        user.save()


class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'name', 'surname', 'age', 'city', 'is_admin', 'is_superuser', 'is_moderator', 'profile_picture','is_active')
    search_fields = ('phone_number', 'name', 'surname')
    readonly_fields = ('last_login',)
    actions = [generate_qr_codes]

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'age', 'city', 'profile_picture','is_active')}),
        ('Important dates', {'fields': ('last_login',)}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser', 'groups', 'user_permissions', 'is_moderator')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'surname', 'age', 'city', 'profile_picture', 'password1', 'password2', 'is_moderator','is_active'),
        }),
    )
    ordering = ('phone_number',)

admin.site.register(User, UserAdmin)


@admin.register(City)
class CityAdmin(TranslationAdmin):
    list_display = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
    )
    search_fields = ('name',)
    list_filter = ('name',)
