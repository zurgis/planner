import pytest
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Session, close_all_sessions, relationship

from app import crud
from app.crud.permission import PermissionCreate
from app.crud.role import RoleCreate, RoleUpdate


@pytest.fixture(scope="module")
def Role(Base):
    class Role(Base):
        name = Column(String, unique=True, index=True, nullable=False)

        role_permission_associations = relationship(
            "RolePermissionAssociation", back_populates="role"
        )

        permissions = association_proxy("role_permission_associations", "permission")

    return Role


# FIXME: temp solution
@pytest.fixture(scope="module")
def Permission(Base):
    class Permission(Base):
        name = Column(String, unique=True, index=True, nullable=False)

    return Permission


# FIXME: temp solution
@pytest.fixture(scope="module")
def RolePermissionAssociation(Base):
    class RolePermissionAssociation(Base):
        __tablename__ = "role_permission"

        id = None
        role_id = Column(ForeignKey("role.id"), primary_key=True)
        permission_id = Column(ForeignKey("permission.id"), primary_key=True)

        role = relationship("Role", back_populates="role_permission_associations")
        permission = relationship("Permission")

        def __init__(self, permission) -> None:
            self.permission = permission

    return RolePermissionAssociation


@pytest.fixture(autouse=True)
def init_database(
    request, connection, Base, Role, Permission, RolePermissionAssociation
):
    Base.metadata.create_all(connection)

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


def test_create(db: Session):
    role_in = RoleCreate(name="admin")

    role = crud.role.create(db, obj_in=role_in)

    assert role.name == "admin"


def test_create_with_permissions(db: Session):
    permission_in_one = PermissionCreate(name="create_user")
    permission_in_two = PermissionCreate(name="read_user")
    permission_in_three = PermissionCreate(name="remove_user")

    crud.permission.create(db, obj_in=permission_in_one)
    crud.permission.create(db, obj_in=permission_in_two)
    crud.permission.create(db, obj_in=permission_in_three)

    permissions = ["create_user", "read_user", "remove_user"]

    permissions_db = crud.permission.get_multi_where_in(db, list_=permissions)

    role_in = RoleCreate(name="admin", permissions=permissions_db)
    role = crud.role.create(db, obj_in=role_in)

    get_role = crud.role.get(db, id=role.id)

    assert get_role
    assert get_role.name == "admin"
    assert get_role.permissions[0].name in permissions
    assert get_role.permissions[1].name in permissions
    assert get_role.permissions[2].name in permissions


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
