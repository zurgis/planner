import pytest
from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Session, close_all_sessions, relationship

from app.crud.permission import CRUDPermission, PermissionCreate
from app.crud.role import CRUDRole, RoleUpdate


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


@pytest.fixture
def crud(Role):
    return CRUDRole(model=Role)


@pytest.fixture
def crud_permission(Permission):
    return CRUDPermission(Permission)


class RoleCreate(BaseModel):
    id: int | None
    name: str
    permissions: list | None


def test_create(db: Session, crud: CRUDRole):
    role_in = RoleCreate(name="admin")

    role = crud.create(db, obj_in=role_in)

    assert role.name == "admin"


def test_create_with_permissions(
    db: Session, crud: CRUDRole, crud_permission: CRUDPermission
):
    permission_in_one = PermissionCreate(name="create_user")
    permission_in_two = PermissionCreate(name="read_user")
    permission_in_three = PermissionCreate(name="remove_user")

    crud_permission.create(db, obj_in=permission_in_one)
    crud_permission.create(db, obj_in=permission_in_two)
    crud_permission.create(db, obj_in=permission_in_three)

    permissions = ["create_user", "read_user", "remove_user"]

    permissions_db = crud_permission.get_multi_where_in(db, list_=permissions)

    role_in = RoleCreate(name="admin", permissions=permissions_db)
    role = crud.create(db, obj_in=role_in)

    get_role = crud.get(db, id=role.id)

    assert get_role
    assert get_role.name == "admin"
    assert get_role.permissions[0].name in permissions
    assert get_role.permissions[1].name in permissions
    assert get_role.permissions[2].name in permissions


def test_get(db: Session, crud: CRUDRole):
    role_in = RoleCreate(name="admin")

    role = crud.create(db, obj_in=role_in)
    get_role = crud.get(db, id=role.id)

    assert get_role
    assert get_role.name == "admin"


def test_get_multi(db: Session, crud: CRUDRole):
    role_in_one = RoleCreate(name="admin")
    role_in_two = RoleCreate(name="user")

    crud.create(db, obj_in=role_in_one)
    crud.create(db, obj_in=role_in_two)

    roles = crud.get_multi(db)

    assert roles
    assert roles[0].name == "admin"
    assert roles[1].name == "user"


def test_update(db: Session, crud: CRUDRole):
    role_in = RoleCreate(name="admin")

    role_db = crud.create(db, obj_in=role_in)

    role_in = RoleUpdate.from_orm(role_db)
    role_in.name = "user"

    role = crud.update(db, db_obj=role_db, obj_in=role_in)

    assert role.name == "user"


def test_remove(db: Session, crud: CRUDRole):
    role_in = RoleCreate(name="admin")

    role = crud.create(db, obj_in=role_in)
    remove_role = crud.remove(db, id=role.id)
    get_role = crud.get(db, id=role.id)

    assert remove_role.id == role.id
    assert get_role is None
