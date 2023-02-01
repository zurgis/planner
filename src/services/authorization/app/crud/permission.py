from pydantic import BaseModel

from app.crud.base import CRUDBase
from app.models.permission import Permission


class PermissionCreate(BaseModel):
    name: str


class PermissionUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    ...


permission = CRUDPermission(Permission)
