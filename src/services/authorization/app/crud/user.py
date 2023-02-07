from pydantic import BaseModel

from app.crud.base import CRUDBase
from app.models.user import User


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: dict[str, str] | tuple
    role_id: int
    direction_id: int | None


class UserUpdate(BaseModel):
    email: str
    password: str
    full_name: dict[str, str] | tuple
    role_id: int
    direction_id: int | None

    class Config:
        orm_mode = True


# TODO: add create method with hashable password
class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    ...


user = CRUDUser(User)
