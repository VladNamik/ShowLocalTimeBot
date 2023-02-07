from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.sql import exists
from utils import Config
import os

from db_map import *


def create_db_engine(config: Config) -> Engine:
    engine = create_engine(f'sqlite:///{config.db_filename}')
    if not os.path.isfile(f'./{config.db_filename}'):
        Base.metadata.create_all(engine)

    return engine


def get_scoped_session(engine: Engine) -> scoped_session:
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


def add_user_if_needed(session: Session, user: User):
    session.add(user)


def add_user_in_group(session: Session, group_id: str, user_id: str):
    # TODO
    # if (session.query(UserGroup).filter(user_id == User.id))
    user_group = UserGroup(user_id=user_id, group_id=group_id)
    session.add(user_group)


def is_user_exists(session: Session, user_id: str) -> bool:
    return session.query(exists().where(User.user_id == user_id)).scalar()


def get_registered_user_by_group(session: Session, group_id: str) -> list:
    # TODO return list of users in group
    pass


def get_users_timezones_by_group(session: Session, group_id: str) -> list:
    # TODO return list of tuples in format (timezone: str, users:
    pass
