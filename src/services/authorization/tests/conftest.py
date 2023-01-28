from collections.abc import Generator

import pytest
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import as_declarative, declared_attr, sessionmaker


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
    @as_declarative()
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
        Base.metadata.drop_all(connection)

    request.addfinalizer(teardown)


@pytest.fixture(scope="session")
def db(connection) -> Generator:
    Session = sessionmaker(bind=connection)

    yield Session(future=True)
