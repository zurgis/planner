from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.database.base_class import Base


class Direction(Base):
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="direction")
