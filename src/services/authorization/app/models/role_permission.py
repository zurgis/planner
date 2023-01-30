from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Role_Permission(Base):
    id = None
    role_id = Column(ForeignKey("role.id"), primary_key=True)
    permission_id = Column(ForeignKey("permission.id"), primary_key=True)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
