from django.contrib import admin
from .models import AutoForwarding, ForwardingFilter

class ForwardingFilterInline(admin.TabularInline):
    model = ForwardingFilter
    extra = 1

@admin.register(AutoForwarding)
class AutoForwardingAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'forwarding_email', 'disposition', 'has_forwarding_filters')
    search_fields = ('email', 'name', 'forwarding_email')
    list_filter = ('has_forwarding_filters', 'disposition')
    inlines = [ForwardingFilterInline]

@admin.register(ForwardingFilter)
class ForwardingFilterAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'forwarding', 'created_at')
    search_fields = ('email_address', 'forwarding__email')
    list_filter = ('created_at',) 