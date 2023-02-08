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


def add_user(session: Session, user: User):
    db_user = get_user_by_id(session, user.user_id)
    if db_user is None:
        session.add(user)


def add_group(session: Session, group: Group):
    db_group = get_group_by_id(session, group.group_id)
    if db_group is None:
        session.add(group)


def add_user_to_group(session: Session, group_id: str, user_id: str):
    if session.query(UserGroup).filter(
            (user_id == UserGroup.user_id) & (group_id == UserGroup.group_id)).scalar() is None:
        user_group = UserGroup(user_id=user_id, group_id=group_id)
        session.add(user_group)


def get_user_by_id(session: Session, user_id: str) -> User or None:
    return session.get(User, user_id)


def get_group_by_id(session: Session, group_id: str) -> Group or None:
    return session.get(Group, group_id)


def get_users_timezones_in_group(session: Session, group_id: str) -> list:
    users = session.query(User).join(UserGroup, User.user_id == UserGroup.user_id)\
        .filter(UserGroup.group_id == group_id).all()
    return users
