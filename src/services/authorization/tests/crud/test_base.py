import uuid

import pytest
from pydantic import BaseModel
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase


@pytest.fixture(scope="module")
def User(Base):
    class User(Base):
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        email = Column(String, nullable=False)

    return User


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, User):
    Base.metadata.create_all(connection)

    def teardown():
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


@pytest.fixture
def base(User):
    return CRUDBase(model=User)


class UserCreate(BaseModel):
    id: uuid.UUID | None
    email: str


class UserUpdate(UserCreate):
    class Config:
        orm_mode = True


def test_create(db: Session, base: CRUDBase):
    id = uuid.uuid4()

    user_in = UserCreate(id=id, email="test@planner.planner")

    user = base.create(db, obj_in=user_in)

    assert user.id == id
    assert user.email == "test@planner.planner"


def test_get(db: Session, base: CRUDBase):
    user_in = UserCreate(email="test@planner.planner")

    user = base.create(db, obj_in=user_in)
    get_user = base.get(db, id=user.id)

    assert get_user
    assert get_user.email == "test@planner.planner"


def test_get_multi(db: Session, base: CRUDBase):
    user_in_one = UserCreate(email="test@planner.planner")
    user_in_two = UserCreate(email="test@planner.planner")

    base.create(db, obj_in=user_in_one)
    base.create(db, obj_in=user_in_two)

    users = base.get_multi(db)

    assert users
    assert users[0].email == "test@planner.planner"


def test_update_dict(db: Session, base: CRUDBase):
    user_in = UserCreate(email="test@planner.planner")

    user_db = base.create(db, obj_in=user_in)
    user = base.update(db, db_obj=user_db, obj_in={"email": "update@planner.planner"})

    assert user.email == "update@planner.planner"


def test_update_schema(db: Session, base: CRUDBase):
    user_in = UserCreate(email="test@planner.planner")

    user_db = base.create(db, obj_in=user_in)

    user_in = UserUpdate.from_orm(user_db)
    user_in.email = "update@planner.planner"

    user = base.update(db, db_obj=user_db, obj_in=user_in)

    assert user.email == "update@planner.planner"


def test_remove(db: Session, base: CRUDBase):
    id = uuid.uuid4()

    user_in = UserCreate(id=id, email="test@planner.planner")

    user = base.create(db, obj_in=user_in)
    remove_user = base.remove(db, id=id)
    get_user = base.get(db, id=id)

    assert remove_user.id == user.id
    assert get_user is None
