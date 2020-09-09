from django.contrib import admin
from .models import EmailToken


class TokensAdmin(admin.ModelAdmin):
    list_display = ('token', 'email', 'created', 'entered', 'last_visited', 'active')
    fields = ['email', 'active']
    readonly_fields = ['token', 'created', 'entered', 'last_visited']


admin.site.register(EmailToken, TokensAdmin)
