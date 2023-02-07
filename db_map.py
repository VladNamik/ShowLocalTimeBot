from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'Users'

    user_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    timezone = Column(String(100), nullable=True)

    def __repr__(self):
        return f'{self.first_name} {self.last_name} {self.user_id}'


class Group(Base):
    __tablename__ = 'Groups'

    group_id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=True)


class UserGroup(Base):
    __tablename__ = 'UserGroups'

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey(f'{User.__tablename__}.id', ondelete='CASCADE'), nullable=False, index=True)
    group_id = Column(ForeignKey(f'{Group.__tablename__}.id', ondelete='CASCADE'), nullable=False, index=True)
