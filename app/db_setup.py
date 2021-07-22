from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ARRAY,
    DateTime,
    REAL,
    Float,
    ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship


engine = create_engine(
    "postgresql://postgres:Misha_Yarikoff_Loves_You@146.185.208.198:5432/news")

Base = declarative_base()


class AllNews(Base):
    __tablename__ = 'all_news'
    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    rubric = Column(ARRAY(String))
    link = Column(String, unique=True)
    title = Column(String)
    text = Column(String)
    locs = Column(ARRAY(String))
    pers = Column(ARRAY(String))
    orgs = Column(ARRAY(String))
    x = Column(Float)
    y = Column(Float)
    highlights = Column(String)
    tokens = Column(ARRAY(String))
    recommendations = relationship("Recommendation", backref="about")


class Recommendation(Base):
    __tablename__ = 'recommendation'
    id = Column(Integer, primary_key=True)
    quote = Column(String)
    bos = Column(Float)
    bos_positive = Column(Float)
    bos_negative = Column(Float)
    datetime = Column(DateTime)
    news_id = Column(Integer, ForeignKey("all_news.id"))


Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
