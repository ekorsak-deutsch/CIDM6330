from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ForwardingFilterBase(BaseModel):
    """Base schema for Forwarding Filters"""
    criteria: Dict[str, Any]
    action: Dict[str, Any]
    created_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ForwardingFilterCreate(ForwardingFilterBase):
    """Schema for creating Forwarding Filters"""
    forwarding_id: int


class ForwardingFilter(ForwardingFilterBase):
    """Schema for Forwarding Filters with ID"""
    id: int
    forwarding_id: int
    
    model_config = ConfigDict(from_attributes=True)


class ForwardingRuleBase(BaseModel):
    """Base schema for Auto Forwarding rules"""
    email: str
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool = False
    error: Optional[str] = None
    investigation_note: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ForwardingRuleCreate(ForwardingRuleBase):
    """Schema for creating Auto Forwarding rules"""
    pass


class ForwardingRuleUpdate(BaseModel):
    """Schema for updating Auto Forwarding rules"""
    investigation_note: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ForwardingRule(ForwardingRuleBase):
    """Schema for Auto Forwarding rules with ID and filter"""
    id: int
    filter: Optional[ForwardingFilter] = None
    
    model_config = ConfigDict(from_attributes=True)


class Error(BaseModel):
    """Schema for error responses"""
    detail: str 