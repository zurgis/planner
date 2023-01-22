import pytest
from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from app.database.custom_types import CompositeType


class TestCompositeType:
    @pytest.fixture(scope="class")
    def User(self, Base):
        class User(Base):
            full_name = Column(
                CompositeType(
                    "full_name",
                    [
                        Column("first_name", String),
                        Column("last_name", String),
                        Column("middle_name", String),
                    ],
                ),
                nullable=False,
            )

        return User

    @pytest.fixture(scope="class", autouse=True)
    def init_database(self, request, connection, Base, User):
        Base.metadata.create_all(connection)

        def teardown():
            Base.metadata.drop_all(connection)

        request.addfinalizer(teardown)

    def test_composite_type_tuple(self, db: Session, User):
        user = User(full_name=("FirstTest", "LastTest", "MiddleTest"))

        db.add(user)
        db.commit()

        user = db.query(User).get(1)

        assert user.full_name.first_name == "FirstTest"
        assert user.full_name.last_name == "LastTest"
        assert user.full_name.middle_name == "MiddleTest"

    def test_composite_type_dict(self, db: Session, User):
        user = User(
            full_name={
                "first_name": "FirstTest",
                "last_name": "LastTest",
                "middle_name": "MiddleTest",
            }
        )

        db.add(user)
        db.commit()

        user = db.query(User).get(2)

        assert user.full_name.first_name == "FirstTest"
