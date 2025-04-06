"""
Legacy models file for compatibility.
Import schemas from the new location.

This file exists only for backward compatibility with any code
that might still import from the original location.
"""
from forwarding_rules.schemas import (
    ForwardingRule,
    ForwardingRuleBase,
    ForwardingRuleUpdate,
    ForwardingFilter,
    ForwardingFilterCreate
)
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

# Pydantic Models for API
class ForwardingFilter(BaseModel):
    id: Optional[int] = None
    forwarding_id: int
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingFilterCreate(BaseModel):
    email_address: str
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleBase(BaseModel):
    email: str
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool
    error: Optional[str] = None
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleCreate(ForwardingRuleBase):
    pass

class ForwardingRule(ForwardingRuleBase):
    id: int
    filters: Optional[List[ForwardingFilter]] = None

class ForwardingRuleUpdate(BaseModel):
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True) 