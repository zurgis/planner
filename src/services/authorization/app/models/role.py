from sqlalchemy import Column, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Role(Base):
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="role")
    role_permission_associations = relationship(
        "RolePermissionAssociation", back_populates="role"
    )

    permissions = association_proxy("role_permission_associations", "permission")
