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
    list_display = ('get_criteria_display', 'forwarding', 'created_at')
    search_fields = ('forwarding__email',)
    list_filter = ('created_at',)
    
    def get_criteria_display(self, obj):
        """Display the criteria field in a readable format"""
        if not obj.criteria:
            return "No criteria"
        
        parts = []
        for key, value in obj.criteria.items():
            parts.append(f"{key}: {value}")
        
        return ", ".join(parts)
    
    get_criteria_display.short_description = "Criteria" 