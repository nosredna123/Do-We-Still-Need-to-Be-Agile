from django.contrib import admin

from foodguard.core.models import Anamnese, Chat, Message, UserContext

# O registro do User fica em foodguard/users/admin.py (convenção Django).

@admin.register(Anamnese)
class AnamneseAdmin(admin.ModelAdmin):
    list_display = ('user', 'previous_consultation', 'alcohol_intake', 'smoking')
    search_fields = ('user__email', 'user__name')
    list_filter = ('previous_consultation', 'alcohol_intake', 'smoking')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('created_at',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'role', 'created_at')
    search_fields = ['chat__user__email', 'chat__user__name']
    list_filter = ('created_at',)

@admin.register(UserContext)
class UserContextAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated_at')
    search_fields = ('user__email', 'user__name')
    list_filter = ('updated_at',)
    readonly_fields = ('created_at', 'updated_at')