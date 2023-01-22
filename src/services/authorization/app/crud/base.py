from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.base_class import Base


Model = TypeVar("Model", bound=Base)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class CRUDBase:
    def __init__(self, model: type[Model]) -> None:
        self.model = model

    def get(self, db: Session, *, id: int | UUID) -> Model:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, *, skip=0, limit=100) -> Model:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchema) -> Model:
        obj_in_data = obj_in.dict()
        db_obj = self.model(**obj_in_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(self, db: Session, *, db_obj: Model, obj_in: UpdateSchema) -> Model:
        if isinstance(obj_in, dict):
            updated_data = obj_in
        else:
            updated_data = obj_in.dict(exclude_unset=True)

        for field in db_obj._fields:
            if field in updated_data:
                setattr(db_obj, field, updated_data[field])

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def remove(self, db: Session, *, id: int | UUID) -> Model:
        obj = db.query(self.model).get(id)

        db.delete(obj)
        db.commit()

        return obj
