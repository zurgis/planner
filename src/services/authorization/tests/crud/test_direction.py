import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session, close_all_sessions

from app.crud.direction import CRUDDirection, DirectionCreate, DirectionUpdate


@pytest.fixture(scope="module")
def Direction(Base):
    class Direction(Base):
        name = Column(String, unique=True, index=True, nullable=False)

    return Direction


@pytest.fixture(autouse=True)
def init_database(request, connection, Base, Direction):
    Base.metadata.create_all(connection)

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


@pytest.fixture
def crud(Direction):
    return CRUDDirection(model=Direction)


def test_create(db: Session, crud: CRUDDirection):
    direction_in = DirectionCreate(name="Отдел Web-разработки")

    direction = crud.create(db, obj_in=direction_in)

    assert direction.name == "Отдел Web-разработки"


def test_get(db: Session, crud: CRUDDirection):
    direction_in = DirectionCreate(name="Отдел Web-разработки")

    direction = crud.create(db, obj_in=direction_in)
    get_direction = crud.get(db, id=direction.id)

    assert get_direction
    assert get_direction.name == "Отдел Web-разработки"


def test_get_multi(db: Session, crud: CRUDDirection):
    direction_in_one = DirectionCreate(name="Отдел Web-разработки")
    direction_in_two = DirectionCreate(name="Отдел контроля качества")

    crud.create(db, obj_in=direction_in_one)
    crud.create(db, obj_in=direction_in_two)

    directions = crud.get_multi(db)

    assert directions
    assert directions[0].name == "Отдел Web-разработки"
    assert directions[1].name == "Отдел контроля качества"


def test_update(db: Session, crud: CRUDDirection):
    direction_in = DirectionCreate(name="Отдел Web-разработки")

    direction_db = crud.create(db, obj_in=direction_in)

    direction_in = DirectionUpdate.from_orm(direction_db)
    direction_in.name = "Отдел контроля качества"

    direction = crud.update(db, db_obj=direction_db, obj_in=direction_in)

    assert direction.name == "Отдел контроля качества"


def test_remove(db: Session, crud: CRUDDirection):
    direction_in = DirectionCreate(name="Отдел Web-разработки")

    direction = crud.create(db, obj_in=direction_in)
    remove_direction = crud.remove(db, id=direction.id)
    get_direction = crud.get(db, id=direction.id)

    assert remove_direction.id == direction.id
    assert get_direction is None
