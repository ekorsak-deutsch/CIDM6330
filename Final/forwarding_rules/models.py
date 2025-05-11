from django.db import models


class AutoForwarding(models.Model):
    """
    Django model for Auto Forwarding rules
    Stores information about email forwarding rules for users
    """
    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=255)
    forwarding_email = models.EmailField(null=True, blank=True)
    disposition = models.CharField(max_length=50, null=True, blank=True)
    has_forwarding_filters = models.BooleanField(default=False)
    error = models.TextField(null=True, blank=True)
    investigation_note = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.email} ({self.name})"
    
    class Meta:
        db_table = 'autoforwarding'
        verbose_name = 'Auto Forwarding Rule'
        verbose_name_plural = 'Auto Forwarding Rules'


class ForwardingFilter(models.Model):
    """
    Django model for Forwarding Filters
    Stores filter details for email forwarding rules
    
    Each rule can have at most one filter with:
    - criteria: JSON object with filter conditions (e.g. {"from": "example@example.com", "subject": "invoice"})
    - action: JSON object with actions to take (e.g. {"forward": "backup@example.com", "addLabels": "TRASH"})
    """
    forwarding = models.OneToOneField(
        AutoForwarding, 
        on_delete=models.CASCADE, 
        related_name='filter',
        db_column='forwarding_id'
    )
    criteria = models.JSONField(help_text="Filter criteria (e.g. from, subject)")
    action = models.JSONField(help_text="Actions to take (e.g. forward, addLabels)")
    created_at = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        criteria_str = ", ".join([f"{k}: {v}" for k, v in self.criteria.items()])
        return f"Filter for {self.forwarding.email}: {criteria_str}"
    
    class Meta:
        db_table = 'forwardingfilter'
        verbose_name = 'Forwarding Filter'
        verbose_name_plural = 'Forwarding Filters' 