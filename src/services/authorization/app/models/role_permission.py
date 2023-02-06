from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class RolePermissionAssociation(Base):
    __tablename__ = "role_permission"

    id = None
    role_id = Column(ForeignKey("role.id"), primary_key=True)
    permission_id = Column(ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role", back_populates="role_permission_associations")
    permission = relationship("Permission")

    def __init__(self, permission) -> None:
        self.permission = permission
