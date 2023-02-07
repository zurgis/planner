import uuid

import pytest
from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session, close_all_sessions, relationship

from app import crud
from app.crud.role import RoleCreate
from app.crud.user import UserCreate, UserUpdate
from app.database.custom_types import CompositeType


@pytest.fixture(scope="module")
def User(Base):
    regex_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+$"

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

        role = relationship("Role", back_populates="users")
        direction = relationship("Direction", back_populates="users")

        __table_args__ = (CheckConstraint(f"email ~ '{regex_email}'", name="email"),)

    return User


# FIXME: temp solution
@pytest.fixture(scope="module")
def Role(Base):
    class Role(Base):
        name = Column(String, unique=True, index=True, nullable=False)

        users = relationship("User", back_populates="role")

    return Role


# FIXME: temp solution
@pytest.fixture(scope="module")
def Direction(Base):
    class Direction(Base):
        name = Column(String, unique=True, index=True, nullable=False)

        users = relationship("User", back_populates="direction")

    return Direction


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, User, Role, Direction):
    Base.metadata.create_all(connection)

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


def test_create(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    user_in = UserCreate(
        email="test@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )

    user = crud.user.create(db, obj_in=user_in)

    assert user.email == "test@planner.planner"
    assert user.password == "planner"
    assert user.full_name.first_name == "FirstTest"
    assert user.full_name.last_name == "LastTest"
    assert user.full_name.middle_name == "MiddleTest"
    assert user.role.name == "admin"


def test_get(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    user_in = UserCreate(
        email="test@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )

    user = crud.user.create(db, obj_in=user_in)
    get_user = crud.user.get(db, id=user.id)

    assert get_user
    assert get_user.email == "test@planner.planner"


def test_get_multi(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    user_in_one = UserCreate(
        email="test@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )
    user_in_two = UserCreate(
        email="test_two@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )

    crud.user.create(db, obj_in=user_in_one)
    crud.user.create(db, obj_in=user_in_two)

    users = crud.user.get_multi(db)

    assert users
    assert users[0].email == "test@planner.planner"
    assert users[1].email == "test_two@planner.planner"


def test_update(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    user_in = UserCreate(
        email="test@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )

    user_db = crud.user.create(db, obj_in=user_in)

    user_in = UserUpdate.from_orm(user_db)
    user_in.email = "update@planner.planner"

    user = crud.user.update(db, db_obj=user_db, obj_in=user_in)

    assert user.email == "update@planner.planner"


def test_remove(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    user_in = UserCreate(
        email="test@planner.planner",
        password="planner",
        full_name=("FirstTest", "LastTest", "MiddleTest"),
        role_id=role.id,
    )

    user = crud.user.create(db, obj_in=user_in)
    remove_user = crud.user.remove(db, id=user.id)
    get_user = crud.user.get(db, id=user.id)

    assert remove_user.id == user.id
    assert get_user is None
