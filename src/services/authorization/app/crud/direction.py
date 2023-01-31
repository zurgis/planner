from pydantic import BaseModel

from app.crud.base import CRUDBase
from app.models.direction import Direction


class DirectionCreate(BaseModel):
    name: str


class DirectionUpdate(BaseModel):
    name: str

    class Config:
        orm_mode = True


class CRUDDirection(CRUDBase[Direction, DirectionCreate, DirectionUpdate]):
    ...


direction = CRUDDirection(Direction)
