import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, relationship

from app import crud
from app.crud.permission import PermissionCreate, PermissionUpdate


@pytest.fixture(scope="module")
def Permission(Base):
    class Permission(Base):
        name = Column(String, unique=True, index=True, nullable=False)

        roles = relationship("Role_Permission", back_populates="permission")

    return Permission


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, Permission):
    Base.metadata.create_all(connection)

    def teardown():
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


def test_create(db: Session):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.permission.create(db, obj_in=permission_in)

    assert permission.name == "view_users"


def test_get(db: Session):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.permission.create(db, obj_in=permission_in)
    get_permission = crud.permission.get(db, id=permission.id)

    assert get_permission
    assert get_permission.name == "view_users"


def test_get_multi(db: Session):
    permission_in_one = PermissionCreate(name="view_users")
    permission_in_two = PermissionCreate(name="create_users")

    crud.permission.create(db, obj_in=permission_in_one)
    crud.permission.create(db, obj_in=permission_in_two)

    permissions = crud.permission.get_multi(db)

    assert permissions
    assert permissions[0].name == "view_users"
    assert permissions[1].name == "create_users"


def test_update(db: Session):
    permission_in = PermissionCreate(name="view_users")

    permission_db = crud.permission.create(db, obj_in=permission_in)

    permission_in = PermissionUpdate.from_orm(permission_db)
    permission_in.name = "create_users"

    permission = crud.permission.update(db, db_obj=permission_db, obj_in=permission_in)

    assert permission.name == "create_users"


def test_remove(db: Session):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.permission.create(db, obj_in=permission_in)
    remove_permission = crud.permission.remove(db, id=permission.id)
    get_permission = crud.permission.get(db, id=permission.id)

    assert remove_permission.id == permission.id
    assert get_permission is None
