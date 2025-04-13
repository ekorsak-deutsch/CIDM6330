from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from django.db.models import Count
from django.conf import settings

from .models import AutoForwarding, ForwardingFilter


# BaseRepository Interface
class BaseAutoForwardingRepository(ABC):
    """Base repository interface for Auto Forwarding rules"""
    
    @abstractmethod
    def create_rule(self, rule_data: Dict[str, Any]) -> AutoForwarding:
        """Create a new forwarding rule"""
        pass
    
    @abstractmethod
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AutoForwarding]:
        """Get all forwarding rules with pagination"""
        pass
    
    @abstractmethod
    def get_rule_by_id(self, rule_id: int) -> Optional[AutoForwarding]:
        """Get a forwarding rule by ID"""
        pass
    
    @abstractmethod
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AutoForwarding]:
        """Update a forwarding rule"""
        pass
    
    @abstractmethod
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a forwarding rule"""
        pass
    
    @abstractmethod
    def search_rules(self, email: Optional[str] = None, has_filters: Optional[bool] = None) -> List[AutoForwarding]:
        """Search for forwarding rules"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about forwarding rules"""
        pass


class BaseForwardingFilterRepository(ABC):
    """Base repository interface for Forwarding Filters"""
    
    @abstractmethod
    def create_filter(self, filter_data: Dict[str, Any]) -> ForwardingFilter:
        """Create a new forwarding filter"""
        pass
    
    @abstractmethod
    def get_filters_for_rule(self, rule_id: int) -> List[ForwardingFilter]:
        """Get all filters for a forwarding rule"""
        pass
    
    @abstractmethod
    def delete_filters_for_rule(self, rule_id: int) -> bool:
        """Delete all filters for a forwarding rule"""
        pass


# Django Implementation
class DjangoAutoForwardingRepository(BaseAutoForwardingRepository):
    """Django implementation of Auto Forwarding repository"""
    
    def create_rule(self, rule_data: Dict[str, Any]) -> AutoForwarding:
        """Create a new forwarding rule"""
        rule = AutoForwarding.objects.create(**rule_data)
        return rule
    
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AutoForwarding]:
        """Get all forwarding rules with pagination"""
        return list(AutoForwarding.objects.all()[skip:skip + limit])
    
    def get_rule_by_id(self, rule_id: int) -> Optional[AutoForwarding]:
        """Get a forwarding rule by ID"""
        try:
            return AutoForwarding.objects.get(id=rule_id)
        except AutoForwarding.DoesNotExist:
            return None
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AutoForwarding]:
        """Update a forwarding rule"""
        try:
            rule = AutoForwarding.objects.get(id=rule_id)
            for key, value in updates.items():
                setattr(rule, key, value)
            rule.save()
            return rule
        except AutoForwarding.DoesNotExist:
            return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a forwarding rule"""
        try:
            rule = AutoForwarding.objects.get(id=rule_id)
            rule.delete()
            return True
        except AutoForwarding.DoesNotExist:
            return False
    
    def search_rules(self, email: Optional[str] = None, has_filters: Optional[bool] = None) -> List[AutoForwarding]:
        """Search for forwarding rules"""
        queryset = AutoForwarding.objects.all()
        
        if email:
            queryset = queryset.filter(email__icontains=email)
        
        if has_filters is not None:
            queryset = queryset.filter(has_forwarding_filters=has_filters)
        
        return list(queryset)
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about forwarding rules"""
        total_rules = AutoForwarding.objects.count()
        active_forwarding = AutoForwarding.objects.exclude(forwarding_email__isnull=True).count()
        with_filters = AutoForwarding.objects.filter(has_forwarding_filters=True).count()
        with_errors = AutoForwarding.objects.exclude(error__isnull=True).count()
        
        # Get total filters
        total_filters = ForwardingFilter.objects.count()
        
        return {
            "total_rules": total_rules,
            "active_forwarding": active_forwarding,
            "rules_with_filters": with_filters,
            "rules_with_errors": with_errors,
            "total_filters": total_filters
        }


class DjangoForwardingFilterRepository(BaseForwardingFilterRepository):
    """Django implementation of Forwarding Filter repository"""
    
    def create_filter(self, filter_data: Dict[str, Any]) -> ForwardingFilter:
        """Create a new forwarding filter"""
        forwarding_id = filter_data.pop('forwarding_id', None)
        
        if forwarding_id:
            try:
                forwarding = AutoForwarding.objects.get(id=forwarding_id)
                filter_data['forwarding'] = forwarding
            except AutoForwarding.DoesNotExist:
                raise ValueError(f"Forwarding rule with ID {forwarding_id} does not exist")
        
        filter = ForwardingFilter.objects.create(**filter_data)
        
        # Update the has_forwarding_filters field on the related rule
        if filter.forwarding:
            filter.forwarding.has_forwarding_filters = True
            filter.forwarding.save()
            
        return filter
    
    def get_filters_for_rule(self, rule_id: int) -> List[ForwardingFilter]:
        """Get all filters for a forwarding rule"""
        return list(ForwardingFilter.objects.filter(forwarding_id=rule_id))
    
    def delete_filters_for_rule(self, rule_id: int) -> bool:
        """Delete all filters for a forwarding rule"""
        filters = ForwardingFilter.objects.filter(forwarding_id=rule_id)
        count = filters.count()
        filters.delete()
        
        # Update the has_forwarding_filters field on the related rule
        try:
            forwarding = AutoForwarding.objects.get(id=rule_id)
            forwarding.has_forwarding_filters = False
            forwarding.save()
        except AutoForwarding.DoesNotExist:
            pass
            
        return count > 0


# Factory function to create repositories
def create_repositories(repo_type: str = "django", **kwargs):
    """
    Create and return repositories
    
    Returns:
        Tuple of (rule_repo, filter_repo)
    """
    # Django is now the only repository type
    rule_repo = DjangoAutoForwardingRepository()
    filter_repo = DjangoForwardingFilterRepository()
    return rule_repo, filter_repo 