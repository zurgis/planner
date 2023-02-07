from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base
from app.models.permission import Permission


class RolePermissionAssociation(Base):
    __tablename__ = "role_permission"  # type: ignore

    id = None
    role_id = Column(ForeignKey("role.id"), primary_key=True)
    permission_id = Column(ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role", back_populates="role_permission_associations")
    permission = relationship("Permission")

    def __init__(self, permission: Permission) -> None:
        self.permission = permission
