from pydantic import BaseModel

from app.crud.base import CRUDBase
from app.models.role import Role


class RoleCreate(BaseModel):
    name: str


class RoleUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    ...


role = CRUDRole(Role)
