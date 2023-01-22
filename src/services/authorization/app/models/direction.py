from sqlalchemy import Column, String

from app.database.base_class import Base


class Direction(Base):
    name = Column(String, unique=True, index=True, nullable=False)
