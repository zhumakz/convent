from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('phone_number', 'name', 'surname', 'age', 'is_admin', 'is_superuser')
    search_fields = ('phone_number', 'name', 'surname')
    readonly_fields = ('last_login',)

    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('name', 'surname', 'age')}),
        ('Permissions', {'fields': ('is_admin', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'surname', 'age', 'password1', 'password2'),
        }),
    )
    ordering = ('phone_number',)

admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
