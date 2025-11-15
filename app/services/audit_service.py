from __future__ import annotations
from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.AuditLog import AuditLog
from app.models.AuditAction import AuditAction

async def log_action(
        db: AsyncSession, 
        user_id:Optional[int], 
        action_type: AuditAction, 
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
        ) -> None:
    try:
        log = AuditLog(
            user_id=user_id,
            action_type = action_type,
            metadata=metadata or {},
            ip_address= ip_address,
            user_agent=user_agent
        )

        db.add(log)
        await db.flush()
        
    except Exception:
        pass
