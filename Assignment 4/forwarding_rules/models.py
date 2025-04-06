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
    """
    forwarding = models.ForeignKey(
        AutoForwarding, 
        on_delete=models.CASCADE, 
        related_name='filters',
        db_column='forwarding_id'
    )
    email_address = models.EmailField()
    created_at = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return f"Filter: {self.email_address} for {self.forwarding.email}"
    
    class Meta:
        db_table = 'forwardingfilter'
        verbose_name = 'Forwarding Filter'
        verbose_name_plural = 'Forwarding Filters' 