from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    "postgresql://planner_user:planner_password@127.0.0.1:5432/planner_users",
    echo=True,
    echo_pool=True,
    pool_pre_ping=True,
    future=True,
)

Session = sessionmaker(engine, future=True)
