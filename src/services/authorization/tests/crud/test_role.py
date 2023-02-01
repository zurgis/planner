import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, relationship

from app import crud
from app.crud.role import RoleCreate, RoleUpdate


@pytest.fixture(scope="module")
def Role(Base):
    class Role(Base):
        name = Column(String, unique=True, index=True, nullable=False)

        users = relationship("User", back_populates="role")
        permissions = relationship("Role_Permission", back_populates="role")

    return Role


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, Role):
    Base.metadata.create_all(connection)

    def teardown():
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


def test_create(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    assert role.name == "admin"


def test_get(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)
    get_role = crud.role.get(db, id=role.id)

    assert get_role
    assert get_role.name == "admin"


def test_get_multi(db: Session):
    role_in_one = RoleCreate(name="admin")
    role_in_two = RoleCreate(name="user")

    crud.role.create(db, obj_in=role_in_one)
    crud.role.create(db, obj_in=role_in_two)

    roles = crud.role.get_multi(db)

    assert roles
    assert roles[0].name == "admin"
    assert roles[1].name == "user"


def test_update(db: Session):
    role_in = RoleCreate(name="admin")

    role_db = crud.role.create(db, obj_in=role_in)

    role_in = RoleUpdate.from_orm(role_db)
    role_in.name = "user"

    role = crud.role.update(db, db_obj=role_db, obj_in=role_in)

    assert role.name == "user"


def test_remove(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)
    remove_role = crud.role.remove(db, id=role.id)
    get_role = crud.role.get(db, id=role.id)

    assert remove_role.id == role.id
    assert get_role is None
