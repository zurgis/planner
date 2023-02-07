from collections.abc import Callable, Sequence
from typing import NamedTuple

from psycopg2.extras import register_composite
from sqlalchemy import MetaData, event
from sqlalchemy.engine import Connection, Dialect
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import _CreateDropBase
from sqlalchemy.sql.compiler import DDLCompiler
from sqlalchemy.types import UserDefinedType

from app.database.connection import engine


class CreateCompositeType(_CreateDropBase):
    """Represent a CREATE TYPE statement."""

    __visit_name__ = "create_composite_type"


class DropCompositeType(_CreateDropBase):
    """Represent a DROP TYPE statement."""

    __visit_name__ = "drop_composite_type"


# TODO: add filter by composite type
# TODO: add creation of composite type in composite type
# TODO: add checks composite type in other tables
# FIXME: add column nullable check
class CompositeType(UserDefinedType):
    """
    :param name:
        Name of the composite type.
    :param columns:
        List of columns that this composite type consists of
    """

    def __init__(self, name: str, columns: list | tuple) -> None:
        if engine.dialect.driver != "psycopg2":
            raise InterfaceError(
                None,
                None,
                "'psycopg2' driver is required in order to use CompositeType.",
            )

        self.name = name
        self.columns = columns

        event.listen(MetaData, "before_create", self.before_create)
        event.listen(MetaData, "after_drop", self.after_drop)

    @property
    def python_type(self) -> type:
        return tuple

    def get_col_spec(self) -> str:
        return self.name

    def bind_processor(self, dialect: Dialect) -> Callable[[Sequence], tuple]:
        def process(value: Sequence) -> tuple:
            if value is None:
                return None

            if isinstance(value, dict):
                value = tuple(value[column.name] for column in self.columns)
            else:
                value = tuple(value[index] for index in range(len(self.columns)))

            return value

        return process

    def result_processor(
        self, dialect: Dialect, coltype: int
    ) -> Callable[[NamedTuple], NamedTuple]:
        def process(value: NamedTuple) -> NamedTuple:
            if value is None:
                return None

            return value

        return process

    def create(self, bind: Connection, checkfirst: bool = True) -> None:
        if checkfirst and not bind.dialect.has_type(bind, self.name):
            bind.execute(CreateCompositeType(self))

    def before_create(
        self, target: MetaData, connection: Connection, **kwargs: dict
    ) -> None:
        self.create(connection)

        register_composite(
            name=self.name, conn_or_curs=connection.connection.connection, globally=True
        )

    def drop(self, bind: Connection, checkfirst: bool = True) -> None:
        if checkfirst and bind.dialect.has_type(bind, self.name):
            bind.execute(DropCompositeType(self))

    def after_drop(
        self, target: MetaData, connection: Connection, **kwargs: dict
    ) -> None:
        self.drop(connection)

    @compiles(CreateCompositeType)
    def visit_create_composite_type(
        create, compiler: DDLCompiler, **kwargs: dict
    ) -> str:
        type_ = create.element

        fields = ", ".join(
            f"{compiler.preparer.quote(column.name)} {compiler.type_compiler.process(column.type)}"  # noqa: E501, W505
            for column in type_.columns
        )

        return f"CREATE TYPE {compiler.preparer.quote(type_.name)} AS ({fields})"

    @compiles(DropCompositeType)
    def visit_drop_composite_type(drop, compiler: DDLCompiler, **kwargs: dict) -> str:
        type_ = drop.element

        return f"DROP TYPE {compiler.preparer.quote(type_.name)}"
