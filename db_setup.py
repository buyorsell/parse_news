import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ARRAY,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


engine = create_engine(os.environ.get('PostgresDB'))

base = declarative_base()


class Meduza(base):
    __tablename__ = 'meduza'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    source = Column(DateTime)
    link = Column(String, unique=True)
    title = Column(String)
    text = Column(String)
    locs = Column(ARRAY(String))
    pers = Column(ARRAY(String))
    orgs = Column(ARRAY(String))


class Commersant(base):
    __tablename__ = 'commersant'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    rubric = Column(String)
    link = Column(String, unique=True)
    title = Column(String)
    text = Column(String)
    locs = Column(ARRAY(String))
    pers = Column(ARRAY(String))
    orgs = Column(ARRAY(String))


base.metadata.create_all(engine)

session = Session(bind=engine)