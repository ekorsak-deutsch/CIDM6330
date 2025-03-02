from sqlalchemy import Column, Integer, String, Boolean, create_engine, Text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic import BaseModel, ConfigDict
from typing import Optional

# SQLAlchemy setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./email_forwarding.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy Models
class Base(DeclarativeBase):
    pass

class AutoForwarding(Base):
    __tablename__ = "AutoForwarding"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    forwarding_email = Column(String)
    disposition = Column(String)
    has_forwarding_filters = Column(Boolean)
    error = Column(String)
    review_note = Column(Text, nullable=True)
    investigation_note = Column(Text, nullable=True)

# Pydantic Models for API
class ForwardingRuleBase(BaseModel):
    email: str
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool
    error: Optional[str] = None
    review_note: Optional[str] = None
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ForwardingRuleCreate(ForwardingRuleBase):
    pass

class ForwardingRule(ForwardingRuleBase):
    id: int

class ForwardingRuleUpdate(BaseModel):
    review_note: Optional[str] = None
    investigation_note: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# Create tables
Base.metadata.create_all(bind=engine) 