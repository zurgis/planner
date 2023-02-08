import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, close_all_sessions

from app.crud.permission import CRUDPermission, PermissionCreate, PermissionUpdate


@pytest.fixture(scope="module")
def Permission(Base):
    class Permission(Base):
        name = Column(String, unique=True, index=True, nullable=False)

    return Permission


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, Permission):
    Base.metadata.create_all(connection)

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


@pytest.fixture
def crud(Permission):
    return CRUDPermission(model=Permission)


def test_create(db: Session, crud: CRUDPermission):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.create(db, obj_in=permission_in)

    assert permission.name == "view_users"


def test_get(db: Session, crud: CRUDPermission):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.create(db, obj_in=permission_in)
    get_permission = crud.get(db, id=permission.id)

    assert get_permission
    assert get_permission.name == "view_users"


def test_get_multi(db: Session, crud: CRUDPermission):
    permission_in_one = PermissionCreate(name="view_users")
    permission_in_two = PermissionCreate(name="create_users")

    crud.create(db, obj_in=permission_in_one)
    crud.create(db, obj_in=permission_in_two)

    permissions = crud.get_multi(db)

    assert permissions
    assert permissions[0].name == "view_users"
    assert permissions[1].name == "create_users"


def test_get_multi_where_in(db: Session, crud: CRUDPermission):
    permission_in_one = PermissionCreate(name="view_users")
    permission_in_two = PermissionCreate(name="create_users")

    crud.create(db, obj_in=permission_in_one)
    crud.create(db, obj_in=permission_in_two)

    permissions = ["view_users", "create_users"]

    permissions_db = crud.get_multi_where_in(db, list_=permissions)

    assert permissions_db
    assert permissions_db[0].name in permissions
    assert permissions_db[1].name in permissions


def test_update(db: Session, crud: CRUDPermission):
    permission_in = PermissionCreate(name="view_users")

    permission_db = crud.create(db, obj_in=permission_in)

    permission_in = PermissionUpdate.from_orm(permission_db)
    permission_in.name = "create_users"

    permission = crud.update(db, db_obj=permission_db, obj_in=permission_in)

    assert permission.name == "create_users"


def test_remove(db: Session, crud: CRUDPermission):
    permission_in = PermissionCreate(name="view_users")

    permission = crud.create(db, obj_in=permission_in)
    remove_permission = crud.remove(db, id=permission.id)
    get_permission = crud.get(db, id=permission.id)

    assert remove_permission.id == permission.id
    assert get_permission is None
