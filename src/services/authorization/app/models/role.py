from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Role(Base):
    name = Column(String, unique=True, index=True, nullable=False)
    permission_id = Column(Integer, ForeignKey("permission.id"))

    user = relationship("User", back_populates="role", uselist=False)
    permission = relationship("Permission")
