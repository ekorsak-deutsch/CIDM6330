from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from sqlmodel import SQLModel, Field, create_engine, Session, select
import csv
import os
import json
from datetime import datetime


# SQLModel definitions
class AutoForwardingBase(SQLModel):
    """Base SQLModel for Auto Forwarding rules"""
    email: str = Field(unique=True, index=True)
    name: str
    forwarding_email: Optional[str] = None
    disposition: Optional[str] = None
    has_forwarding_filters: bool = False
    error: Optional[str] = None
    investigation_note: Optional[str] = None


class AutoForwarding(AutoForwardingBase, table=True):
    """SQLModel for Auto Forwarding rules with table configuration"""
    id: Optional[int] = Field(default=None, primary_key=True)


class ForwardingFilterBase(SQLModel):
    """Base SQLModel for Forwarding Filters"""
    forwarding_id: int = Field(foreign_key="autoforwarding.id")
    email_address: str
    created_at: Optional[str] = None


class ForwardingFilter(ForwardingFilterBase, table=True):
    """SQLModel for Forwarding Filters with table configuration"""
    id: Optional[int] = Field(default=None, primary_key=True)


# BaseRepository Interface
class BaseAutoForwardingRepository(ABC):
    """Base repository interface for Auto Forwarding rules"""
    
    @abstractmethod
    def create_rule(self, rule: AutoForwardingBase) -> AutoForwarding:
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
    def create_filter(self, filter: ForwardingFilterBase) -> ForwardingFilter:
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


# SQLModel Implementation
class SQLModelAutoForwardingRepository(BaseAutoForwardingRepository):
    """SQLModel implementation of Auto Forwarding repository"""
    
    def __init__(self, connection_string: str = "sqlite:///email_forwarding.db"):
        """Initialize the repository with a connection string"""
        self.engine = create_engine(connection_string)
        SQLModel.metadata.create_all(self.engine)
    
    def create_rule(self, rule: AutoForwardingBase) -> AutoForwarding:
        """Create a new forwarding rule"""
        with Session(self.engine) as session:
            db_rule = AutoForwarding.from_orm(rule)
            session.add(db_rule)
            session.commit()
            session.refresh(db_rule)
            return db_rule
    
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AutoForwarding]:
        """Get all forwarding rules with pagination"""
        with Session(self.engine) as session:
            statement = select(AutoForwarding).offset(skip).limit(limit)
            return list(session.exec(statement))
    
    def get_rule_by_id(self, rule_id: int) -> Optional[AutoForwarding]:
        """Get a forwarding rule by ID"""
        with Session(self.engine) as session:
            statement = select(AutoForwarding).where(AutoForwarding.id == rule_id)
            return session.exec(statement).first()
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AutoForwarding]:
        """Update a forwarding rule"""
        with Session(self.engine) as session:
            db_rule = session.get(AutoForwarding, rule_id)
            if not db_rule:
                return None
            
            for key, value in updates.items():
                setattr(db_rule, key, value)
            
            session.add(db_rule)
            session.commit()
            session.refresh(db_rule)
            return db_rule
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a forwarding rule"""
        with Session(self.engine) as session:
            db_rule = session.get(AutoForwarding, rule_id)
            if not db_rule:
                return False
            
            session.delete(db_rule)
            session.commit()
            return True
    
    def search_rules(self, email: Optional[str] = None, has_filters: Optional[bool] = None) -> List[AutoForwarding]:
        """Search for forwarding rules"""
        with Session(self.engine) as session:
            statement = select(AutoForwarding)
            
            if email:
                statement = statement.where(AutoForwarding.email.contains(email))
            
            if has_filters is not None:
                statement = statement.where(AutoForwarding.has_forwarding_filters == has_filters)
            
            return list(session.exec(statement))
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about forwarding rules"""
        with Session(self.engine) as session:
            # Update count queries to work with SQLAlchemy 2.0
            total_rules = len(list(session.exec(select(AutoForwarding))))
            active_forwarding = len(list(session.exec(
                select(AutoForwarding).where(AutoForwarding.forwarding_email != None)
            )))
            with_filters = len(list(session.exec(
                select(AutoForwarding).where(AutoForwarding.has_forwarding_filters == True)
            )))
            with_errors = len(list(session.exec(
                select(AutoForwarding).where(AutoForwarding.error != None)
            )))
            
            # For total filters, we need the filter repository
            filter_repo = SQLModelForwardingFilterRepository(self.engine)
            total_filters = filter_repo.get_total_filters()
            
            return {
                "total_rules": total_rules,
                "active_forwarding": active_forwarding,
                "rules_with_filters": with_filters,
                "rules_with_errors": with_errors,
                "total_filters": total_filters
            }


class SQLModelForwardingFilterRepository(BaseForwardingFilterRepository):
    """SQLModel implementation of Forwarding Filter repository"""
    
    def __init__(self, engine=None, connection_string: str = "sqlite:///email_forwarding.db"):
        """Initialize the repository with a connection string or existing engine"""
        if engine:
            self.engine = engine
        else:
            self.engine = create_engine(connection_string)
            SQLModel.metadata.create_all(self.engine)
    
    def create_filter(self, filter: ForwardingFilterBase) -> ForwardingFilter:
        """Create a new forwarding filter"""
        with Session(self.engine) as session:
            db_filter = ForwardingFilter.from_orm(filter)
            session.add(db_filter)
            session.commit()
            session.refresh(db_filter)
            return db_filter
    
    def get_filters_for_rule(self, rule_id: int) -> List[ForwardingFilter]:
        """Get all filters for a forwarding rule"""
        with Session(self.engine) as session:
            statement = select(ForwardingFilter).where(ForwardingFilter.forwarding_id == rule_id)
            return list(session.exec(statement))
    
    def delete_filters_for_rule(self, rule_id: int) -> bool:
        """Delete all filters for a forwarding rule"""
        with Session(self.engine) as session:
            filters = session.exec(
                select(ForwardingFilter).where(ForwardingFilter.forwarding_id == rule_id)
            ).all()
            
            for filter in filters:
                session.delete(filter)
            
            session.commit()
            return True
    
    def get_total_filters(self) -> int:
        """Get the total number of filters"""
        with Session(self.engine) as session:
            # Update to work with SQLAlchemy 2.0
            return len(list(session.exec(select(ForwardingFilter))))


# CSV Implementation
class CSVAutoForwardingRepository(BaseAutoForwardingRepository):
    """CSV implementation of Auto Forwarding repository"""
    
    def __init__(self, rules_file: str = "autoforwarding_rules.csv"):
        """Initialize the repository with a CSV file"""
        self.rules_file = rules_file
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure that the CSV files exist"""
        if not os.path.exists(self.rules_file):
            with open(self.rules_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'email', 'name', 'forwarding_email', 'disposition',
                    'has_forwarding_filters', 'error', 'investigation_note'
                ])
                writer.writeheader()
    
    def load_rules(self) -> List[Dict[str, Any]]:
        """Load rules from the CSV file"""
        rules = []
        with open(self.rules_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string values to appropriate types
                row['id'] = int(row['id']) if row['id'] else None
                row['has_forwarding_filters'] = row['has_forwarding_filters'].lower() == 'true'
                rules.append(row)
        return rules
    
    def save_rules(self, rules: List[Dict[str, Any]]):
        """Save rules to the CSV file"""
        with open(self.rules_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'email', 'name', 'forwarding_email', 'disposition',
                'has_forwarding_filters', 'error', 'investigation_note'
            ])
            writer.writeheader()
            for rule in rules:
                writer.writerow(rule)
    
    def create_rule(self, rule: AutoForwardingBase) -> AutoForwarding:
        """Create a new forwarding rule"""
        rules = self.load_rules()
        
        # Generate a new ID
        new_id = 1
        if rules:
            new_id = max(r['id'] for r in rules if r['id'] is not None) + 1
        
        # Create the new rule
        rule_dict = rule.dict()
        rule_dict['id'] = new_id
        rules.append(rule_dict)
        
        self.save_rules(rules)
        return AutoForwarding(**rule_dict)
    
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AutoForwarding]:
        """Get all forwarding rules with pagination"""
        rules = self.load_rules()
        paginated_rules = rules[skip:skip + limit]
        return [AutoForwarding(**rule) for rule in paginated_rules]
    
    def get_rule_by_id(self, rule_id: int) -> Optional[AutoForwarding]:
        """Get a forwarding rule by ID"""
        rules = self.load_rules()
        for rule in rules:
            if rule['id'] == rule_id:
                return AutoForwarding(**rule)
        return None
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AutoForwarding]:
        """Update a forwarding rule"""
        rules = self.load_rules()
        
        for i, rule in enumerate(rules):
            if rule['id'] == rule_id:
                for key, value in updates.items():
                    rule[key] = value
                
                self.save_rules(rules)
                return AutoForwarding(**rule)
        
        return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a forwarding rule"""
        rules = self.load_rules()
        initial_count = len(rules)
        
        rules = [rule for rule in rules if rule['id'] != rule_id]
        
        if len(rules) < initial_count:
            self.save_rules(rules)
            
            # Also delete associated filters
            filter_repo = CSVForwardingFilterRepository()
            filter_repo.delete_filters_for_rule(rule_id)
            
            return True
        
        return False
    
    def search_rules(self, email: Optional[str] = None, has_filters: Optional[bool] = None) -> List[AutoForwarding]:
        """Search for forwarding rules"""
        rules = self.load_rules()
        filtered_rules = []
        
        for rule in rules:
            matches = True
            
            if email and email.lower() not in rule['email'].lower():
                matches = False
            
            if has_filters is not None and rule['has_forwarding_filters'] != has_filters:
                matches = False
            
            if matches:
                filtered_rules.append(rule)
        
        return [AutoForwarding(**rule) for rule in filtered_rules]
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about forwarding rules"""
        rules = self.load_rules()
        
        total_rules = len(rules)
        active_forwarding = sum(1 for rule in rules if rule['forwarding_email'])
        with_filters = sum(1 for rule in rules if rule['has_forwarding_filters'])
        with_errors = sum(1 for rule in rules if rule['error'])
        
        # For total filters, we need the filter repository
        filter_repo = CSVForwardingFilterRepository()
        total_filters = filter_repo.get_total_filters()
        
        return {
            "total_rules": total_rules,
            "active_forwarding": active_forwarding,
            "rules_with_filters": with_filters,
            "rules_with_errors": with_errors,
            "total_filters": total_filters
        }


class CSVForwardingFilterRepository(BaseForwardingFilterRepository):
    """CSV implementation of Forwarding Filter repository"""
    
    def __init__(self, filters_file: str = "forwarding_filters.csv"):
        """Initialize the repository with a CSV file"""
        self.filters_file = filters_file
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure that the CSV files exist"""
        if not os.path.exists(self.filters_file):
            with open(self.filters_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'id', 'forwarding_id', 'email_address', 'created_at'
                ])
                writer.writeheader()
    
    def load_filters(self) -> List[Dict[str, Any]]:
        """Load filters from the CSV file"""
        filters = []
        with open(self.filters_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert string values to appropriate types
                row['id'] = int(row['id']) if row['id'] else None
                row['forwarding_id'] = int(row['forwarding_id']) if row['forwarding_id'] else None
                filters.append(row)
        return filters
    
    def save_filters(self, filters: List[Dict[str, Any]]):
        """Save filters to the CSV file"""
        with open(self.filters_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'forwarding_id', 'email_address', 'created_at'
            ])
            writer.writeheader()
            for filter in filters:
                writer.writerow(filter)
    
    def create_filter(self, filter: ForwardingFilterBase) -> ForwardingFilter:
        """Create a new forwarding filter"""
        filters = self.load_filters()
        
        # Generate a new ID
        new_id = 1
        if filters:
            new_id = max(f['id'] for f in filters if f['id'] is not None) + 1
        
        # Create the new filter
        filter_dict = filter.dict()
        filter_dict['id'] = new_id
        filters.append(filter_dict)
        
        self.save_filters(filters)
        return ForwardingFilter(**filter_dict)
    
    def get_filters_for_rule(self, rule_id: int) -> List[ForwardingFilter]:
        """Get all filters for a forwarding rule"""
        filters = self.load_filters()
        rule_filters = [f for f in filters if f['forwarding_id'] == rule_id]
        return [ForwardingFilter(**f) for f in rule_filters]
    
    def delete_filters_for_rule(self, rule_id: int) -> bool:
        """Delete all filters for a forwarding rule"""
        filters = self.load_filters()
        initial_count = len(filters)
        
        filters = [f for f in filters if f['forwarding_id'] != rule_id]
        
        if len(filters) < initial_count:
            self.save_filters(filters)
            return True
        
        return False
    
    def get_total_filters(self) -> int:
        """Get the total number of filters"""
        filters = self.load_filters()
        return len(filters)


# In-Memory Implementation
class InMemoryAutoForwardingRepository(BaseAutoForwardingRepository):
    """In-memory implementation of Auto Forwarding repository"""
    
    def __init__(self):
        """Initialize the repository with empty lists"""
        self.rules = []
        self.next_rule_id = 1
    
    def create_rule(self, rule: AutoForwardingBase) -> AutoForwarding:
        """Create a new forwarding rule"""
        rule_dict = rule.dict()
        rule_dict['id'] = self.next_rule_id
        
        db_rule = AutoForwarding(**rule_dict)
        self.rules.append(db_rule)
        self.next_rule_id += 1
        
        return db_rule
    
    def get_all_rules(self, skip: int = 0, limit: int = 100) -> List[AutoForwarding]:
        """Get all forwarding rules with pagination"""
        return self.rules[skip:skip + limit]
    
    def get_rule_by_id(self, rule_id: int) -> Optional[AutoForwarding]:
        """Get a forwarding rule by ID"""
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def update_rule(self, rule_id: int, updates: Dict[str, Any]) -> Optional[AutoForwarding]:
        """Update a forwarding rule"""
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                for key, value in updates.items():
                    setattr(rule, key, value)
                return rule
        return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a forwarding rule"""
        initial_count = len(self.rules)
        self.rules = [rule for rule in self.rules if rule.id != rule_id]
        
        if len(self.rules) < initial_count:
            # Also delete associated filters
            if hasattr(self, 'filter_repo') and self.filter_repo:
                self.filter_repo.delete_filters_for_rule(rule_id)
            return True
        
        return False
    
    def search_rules(self, email: Optional[str] = None, has_filters: Optional[bool] = None) -> List[AutoForwarding]:
        """Search for forwarding rules"""
        filtered_rules = []
        
        for rule in self.rules:
            matches = True
            
            if email and email.lower() not in rule.email.lower():
                matches = False
            
            if has_filters is not None and rule.has_forwarding_filters != has_filters:
                matches = False
            
            if matches:
                filtered_rules.append(rule)
        
        return filtered_rules
    
    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about forwarding rules"""
        total_rules = len(self.rules)
        active_forwarding = sum(1 for rule in self.rules if rule.forwarding_email)
        with_filters = sum(1 for rule in self.rules if rule.has_forwarding_filters)
        with_errors = sum(1 for rule in self.rules if rule.error)
        
        # For total filters, we need the filter repository
        total_filters = 0
        if hasattr(self, 'filter_repo') and self.filter_repo:
            total_filters = self.filter_repo.get_total_filters()
        
        return {
            "total_rules": total_rules,
            "active_forwarding": active_forwarding,
            "rules_with_filters": with_filters,
            "rules_with_errors": with_errors,
            "total_filters": total_filters
        }


class InMemoryForwardingFilterRepository(BaseForwardingFilterRepository):
    """In-memory implementation of Forwarding Filter repository"""
    
    def __init__(self):
        """Initialize the repository with empty lists"""
        self.filters = []
        self.next_filter_id = 1
    
    def create_filter(self, filter: ForwardingFilterBase) -> ForwardingFilter:
        """Create a new forwarding filter"""
        filter_dict = filter.dict()
        filter_dict['id'] = self.next_filter_id
        
        db_filter = ForwardingFilter(**filter_dict)
        self.filters.append(db_filter)
        self.next_filter_id += 1
        
        return db_filter
    
    def get_filters_for_rule(self, rule_id: int) -> List[ForwardingFilter]:
        """Get all filters for a forwarding rule"""
        return [f for f in self.filters if f.forwarding_id == rule_id]
    
    def delete_filters_for_rule(self, rule_id: int) -> bool:
        """Delete all filters for a forwarding rule"""
        initial_count = len(self.filters)
        self.filters = [f for f in self.filters if f.forwarding_id != rule_id]
        return len(self.filters) < initial_count
    
    def get_total_filters(self) -> int:
        """Get the total number of filters"""
        return len(self.filters)


# Factory function to create repositories
def create_repositories(repo_type: str = "sqlmodel", **kwargs):
    """
    Create and return repositories based on the specified type
    
    Args:
        repo_type: Type of repository to create ("sqlmodel", "csv", or "memory")
        **kwargs: Additional arguments to pass to the repository constructors
    
    Returns:
        Tuple of (rule_repo, filter_repo)
    """
    if repo_type.lower() == "sqlmodel":
        connection_string = kwargs.get("connection_string", "sqlite:///email_forwarding.db")
        rule_repo = SQLModelAutoForwardingRepository(connection_string)
        filter_repo = SQLModelForwardingFilterRepository(rule_repo.engine)
        return rule_repo, filter_repo
    
    elif repo_type.lower() == "csv":
        rules_file = kwargs.get("rules_file", "autoforwarding_rules.csv")
        filters_file = kwargs.get("filters_file", "forwarding_filters.csv")
        rule_repo = CSVAutoForwardingRepository(rules_file)
        filter_repo = CSVForwardingFilterRepository(filters_file)
        return rule_repo, filter_repo
    
    elif repo_type.lower() == "memory":
        rule_repo = InMemoryAutoForwardingRepository()
        filter_repo = InMemoryForwardingFilterRepository()
        # Set up circular reference for statistics
        rule_repo.filter_repo = filter_repo
        return rule_repo, filter_repo
    
    else:
        raise ValueError(f"Unknown repository type: {repo_type}") 