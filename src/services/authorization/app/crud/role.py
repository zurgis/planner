from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.models.role import Role


class RoleCreate(BaseModel):
    id: int | None
    name: str
    permissions: list[Permission] | None

    class Config:
        arbitrary_types_allowed = True


class RoleUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def create(self, db: Session, *, obj_in: RoleCreate) -> Role:
        obj_in_data = obj_in.dict()

        if obj_in_data["permissions"] is None:
            del obj_in_data["permissions"]

        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj


role = CRUDRole(Role)
