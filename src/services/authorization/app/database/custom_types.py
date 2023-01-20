from typing import List, Tuple

from psycopg2.extras import register_composite
from sqlalchemy import MetaData, event
from sqlalchemy.exc import InterfaceError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import _CreateDropBase
from sqlalchemy.types import UserDefinedType

from app.database.connection import engine


# TODO: https://pganalyze.com/blog/custom-postgres-data-types-django-python
# TODO: https://schinckel.net/2014/09/24/using-postgres-composite-types-in-django/
# TODO: https://docs.sqlalchemy.org/en/14/core/ddl.html#sqlalchemy.schema.DDLElement


class CompositeType(UserDefinedType):
    """
    :param name:
        Name of the composite type.
    :param columns:
        List of columns that this composite type consists of
    """

    def __init__(self, name: str, columns: List | Tuple) -> None:
        if engine.dialect.driver != "psycopg2":
            raise InterfaceError(
                None,
                None,
                "'psycopg2' driver is required in order to use CompositeType.",
            )

        self.name = name
        self.columns = columns

        event.listen(MetaData, "before_create", self.before_create)
        # event.listen(MetaData, "after_drop", self.after_drop)

    @property
    def python_type(self):
        return tuple

    def get_col_spec(self):
        return self.name

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None

            if isinstance(value, dict):
                value = tuple(value[column.name] for column in self.columns)
            else:
                value = tuple(value[index] for index in range(len(self.columns)))

            return value

        return process

    def result_processor(self, dialect, coltype):
        def process(value):
            if value is None:
                return None

            return value

        return process

    def create(self, bind=None, checkfirst=False):
        bind.execute(CreateCompositeType(self))

    def before_create(self, target, connection, **kwargs):
        self.create(connection)

        register_composite(
            name=self.name, conn_or_curs=connection.connection.connection, globally=True
        )

        # from collections import namedtuple
        # tuple_ = namedtuple(self.name, [column.name for column in self.columns])

        # type_ = register_composite(name=self.name, conn_or_curs=connection.connection.connection, globally=True).type

        # def adapt_composite(composite_type):
        #     adapted = [adapt(getattr(composite_type, column.name)) for column in composite_type.columns]

        #     # return AsIs(f"({', '.join(values)})::{composite_type.name}")
        #     return AsIs("(%s)::full_name" % (
        #         ", ".join([
        #                     adapt(getattr(composite_type, field)).getquoted() for field in composite_type._fields
        #                 ])
        #     ))

        # register_adapter(type_, adapt_composite)

    def drop(self, bind=None, checkfirst=False):
        bind.execute(DropCompositeType(self))

    def after_drop(self, target, connection, **kwargs):
        self.drop(connection)


class CreateCompositeType(_CreateDropBase):
    """Represent a CREATE TYPE statement."""

    __visit_name__ = "create_composite_type"


class DropCompositeType(_CreateDropBase):
    """Represent a DROP TYPE statement."""

    __visit_name__ = "drop_composite_type"


@compiles(CreateCompositeType)
def visit_create_composite_type(create, compiler, **kwargs):
    type_ = create.element

    fields = ", ".join(
        f"{compiler.preparer.quote(column.name)} {compiler.type_compiler.process(column.type)}"
        for column in type_.columns
    )

    return f"CREATE TYPE {compiler.preparer.quote(type_.name)} AS ({fields})"


@compiles(DropCompositeType)
def visit_drop_composite_type(drop, compiler, **kwargs):
    type_ = drop.element

    return f"DROP TYPE {compiler.preparer.quote(type_.name)}"


# TODO: IdentifierPreparer: https://github.com/sqlalchemy/sqlalchemy/blob/main/lib/sqlalchemy/sql/compiler.py
