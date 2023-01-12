import uuid

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.base_class import Base
from app.database.custom_types import CompositeType


regex_email = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"


class User(Base):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(
        CompositeType(
            "full_name",
            [
                Column("first_name", String),
                Column("last_name", String),
                Column("middle_name", String),
            ],
        ),
        nullable=False,
    )
    role_id = Column(Integer, ForeignKey("role.id"), nullable=False)
    direction_id = Column(Integer, ForeignKey("direction.id"))
    is_active = Column(Boolean, nullable=False, default=True)

    role = relationship("Role", back_populates="user")              # TODO: check this field
    direction = relationship("Direction", back_populates="user")    # TODO: check this field

    __table_args__ = (CheckConstraint(f"email ~ '{regex_email}'", name="email"),)
