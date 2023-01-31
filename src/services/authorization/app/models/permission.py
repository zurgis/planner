from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Permission(Base):
    name = Column(String, unique=True, index=True, nullable=False)

    roles = relationship("Role_Permission", back_populates="permission")
