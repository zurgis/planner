from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.permission import Permission


class PermissionCreate(BaseModel):
    name: str


class PermissionUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):
    def get_multi_where_in(self, db: Session, *, list_: list[str]):
        return db.query(self.model).where(self.model.name.in_(list_)).all()


permission = CRUDPermission(Permission)
