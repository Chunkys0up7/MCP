from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import MCPConfiguration, MCPChain, ChainSession, MCPPermission, AuditLog

class DatabaseOperations:
    def __init__(self, db: Session):
        self.db = db

    # MCP Configuration operations
    def create_configuration(self, name: str, type: str, config: Dict[str, Any], dependencies: Optional[Dict[str, Any]] = None) -> MCPConfiguration:
        """Create a new MCP configuration."""
        config = MCPConfiguration(
            name=name,
            type=type,
            config=config,
            dependencies=dependencies
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_configuration(self, config_id: int) -> Optional[MCPConfiguration]:
        """Get an MCP configuration by ID."""
        return self.db.query(MCPConfiguration).filter(MCPConfiguration.id == config_id).first()

    def update_configuration(self, config_id: int, **kwargs) -> Optional[MCPConfiguration]:
        """Update an MCP configuration."""
        config = self.get_configuration(config_id)
        if config:
            for key, value in kwargs.items():
                setattr(config, key, value)
            config.last_modified = datetime.utcnow()
            self.db.commit()
            self.db.refresh(config)
        return config

    def delete_configuration(self, config_id: int) -> bool:
        """Delete an MCP configuration."""
        config = self.get_configuration(config_id)
        if config:
            self.db.delete(config)
            self.db.commit()
            return True
        return False

    # MCP Chain operations
    def create_chain(self, name: str, workflow: Dict[str, Any], parent_chain: Optional[int] = None) -> MCPChain:
        """Create a new MCP chain."""
        # Get the latest version number for this chain
        latest_version = self.db.query(MCPChain).filter(
            MCPChain.name == name
        ).order_by(desc(MCPChain.version)).first()
        
        version = 1 if not latest_version else latest_version.version + 1
        
        chain = MCPChain(
            name=name,
            workflow=workflow,
            version=version,
            parent_chain=parent_chain
        )
        self.db.add(chain)
        self.db.commit()
        self.db.refresh(chain)
        return chain

    def get_chain(self, chain_id: int) -> Optional[MCPChain]:
        """Get an MCP chain by ID."""
        return self.db.query(MCPChain).filter(MCPChain.id == chain_id).first()

    def get_chain_versions(self, name: str) -> List[MCPChain]:
        """Get all versions of a chain by name."""
        return self.db.query(MCPChain).filter(
            MCPChain.name == name
        ).order_by(desc(MCPChain.version)).all()

    def update_chain(self, chain_id: int, **kwargs) -> Optional[MCPChain]:
        """Update an MCP chain by creating a new version."""
        old_chain = self.get_chain(chain_id)
        if old_chain:
            # Create a new version
            new_chain = MCPChain(
                name=old_chain.name,
                workflow=kwargs.get('workflow', old_chain.workflow),
                version=old_chain.version + 1,
                parent_chain=chain_id
            )
            self.db.add(new_chain)
            self.db.commit()
            self.db.refresh(new_chain)
            return new_chain
        return None

    # Chain Session operations
    def create_session(self, session_id: str, chain_data: Dict[str, Any]) -> ChainSession:
        """Create a new chain session."""
        session = ChainSession(
            session_id=session_id,
            chain_data=chain_data
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[ChainSession]:
        """Get a chain session by session ID."""
        return self.db.query(ChainSession).filter(ChainSession.session_id == session_id).first()

    def update_session(self, session_id: str, chain_data: Dict[str, Any]) -> Optional[ChainSession]:
        """Update a chain session."""
        session = self.get_session(session_id)
        if session:
            session.chain_data = chain_data
            session.last_activity = datetime.utcnow()
            self.db.commit()
            self.db.refresh(session)
        return session

    # Permission operations
    def set_permission(self, user_id: str, chain_id: int, access_level: str) -> MCPPermission:
        """Set or update a user's permission for a chain."""
        permission = self.db.query(MCPPermission).filter(
            MCPPermission.user_id == user_id,
            MCPPermission.chain_id == chain_id
        ).first()

        if permission:
            permission.access_level = access_level
        else:
            permission = MCPPermission(
                user_id=user_id,
                chain_id=chain_id,
                access_level=access_level
            )
            self.db.add(permission)

        self.db.commit()
        self.db.refresh(permission)
        return permission

    def get_permission(self, user_id: str, chain_id: int) -> Optional[MCPPermission]:
        """Get a user's permission for a chain."""
        return self.db.query(MCPPermission).filter(
            MCPPermission.user_id == user_id,
            MCPPermission.chain_id == chain_id
        ).first()

    def remove_permission(self, user_id: str, chain_id: int) -> bool:
        """Remove a user's permission for a chain."""
        permission = self.get_permission(user_id, chain_id)
        if permission:
            self.db.delete(permission)
            self.db.commit()
            return True
        return False

    # Audit log operations
    def log_action(self, user_id: str, action_type: str, target_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None) -> AuditLog:
        """Log an action in the audit log."""
        log = AuditLog(
            user_id=user_id,
            action_type=action_type,
            target_id=target_id,
            details=details
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_audit_logs(self, user_id: Optional[str] = None, action_type: Optional[str] = None) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if action_type:
            query = query.filter(AuditLog.action_type == action_type)
            
        return query.order_by(desc(AuditLog.created_at)).all() 