from collections.abc import Generator

import pytest
from sqlalchemy import Column, Integer, MetaData, create_engine
from sqlalchemy.orm import (
    as_declarative,
    close_all_sessions,
    declared_attr,
    sessionmaker,
)


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(
        "postgresql://planner_user:planner_password@127.0.0.1:5432/planner_users",
        future=True,
    )
    # engine.echo = True

    return engine


@pytest.fixture(scope="session")
def connection(engine) -> Generator:
    yield engine.connect()


@pytest.fixture(scope="module")
def Base():
    metadata_obj = MetaData(schema="dev")

    @as_declarative(metadata=metadata_obj)
    class Base:
        __name__: str

        id = Column(Integer, primary_key=True)

        @declared_attr
        def __tablename__(cls) -> str:
            return cls.__name__.lower()

    yield Base


@pytest.fixture
def init_database(request, connection, Base):
    Base.metadata.create_all(connection)

    def teardown():
        close_all_sessions()
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


@pytest.fixture(scope="session")
def db(connection) -> Generator:
    Session = sessionmaker(bind=connection)

    yield Session(future=True)
