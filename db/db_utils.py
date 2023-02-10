from sqlalchemy import create_engine, Engine, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import Session
from utils import Config
from typing import Optional
import os

from db.db_map import *


def create_db_engine(config: Config) -> Engine:
    engine = create_engine(f"sqlite:///{config.db_filename}")
    if not os.path.isfile(f"./{config.db_filename}"):
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


def add_user_to_group(session: Session, group_id: int, user_id: int):
    if get_user_group_entry(session, group_id, user_id) is None:
        user_group = UserGroup(user_id=user_id, group_id=group_id)
        session.add(user_group)


def get_user_group_entry(session: Session, group_id: int, user_id: int) -> UserGroup:
    users = session.scalar(select(UserGroup)
                           .where((user_id == UserGroup.user_id) & (group_id == UserGroup.group_id)))
    return users


def get_user_by_id(session: Session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def get_group_by_id(session: Session, group_id: int) -> Optional[Group]:
    return session.get(Group, group_id)


def get_users_for_group(session: Session, group_id: int) -> list:
    users = session.scalars(select(User)
                            .join(UserGroup)
                            .where(UserGroup.group_id == group_id))
    return list(users)


def get_users_timezones_for_group(session: Session, group_id: int) -> list:
    # TODO: should select statements be created only once?
    timezones = session.scalars(select(User.timezone)
                                .join(UserGroup)
                                .where(UserGroup.group_id == group_id)
                                .group_by(User.timezone))
    return list(timezones)
