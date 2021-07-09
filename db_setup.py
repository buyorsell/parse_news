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
from sqlalchemy.orm import sessionmaker


engine = create_engine(os.environ.get('PostgresDB'))

Base = declarative_base()


class Meduza(Base):
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


class Kommersant(Base):
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

Base.metadata.bind = engine
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()