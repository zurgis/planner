from database import Base, engine


# TODO: https://docs.sqlalchemy.org/en/14/tutorial/data.html


def main() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
