from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Role(Base):
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("Role_Permission", back_populates="role")
