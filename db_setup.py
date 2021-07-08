from sqlalchemy import (
	create_engine,

	Column,

	INTEGER,
	TEXT,
	ARRAY,
	DATE,

	UniqueConstraint
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


# dialect://username:password@host:port/database
engine = create_engine('postgresql://postgres:iQLKz7Go@localhost:5432/postgres')

base = declarative_base()


class Meduza(base):

	__tablename__ = 'meduza'

	id = Column(INTEGER(), primary_key=True)

	datetime = Column(DATE())
	source = Column(TEXT())
	link = Column(TEXT())

	title = Column(TEXT())
	text = Column(TEXT())

	locs = Column('locs', ARRAY(TEXT))
	pers = Column('pers', ARRAY(TEXT))
	orgs = Column('orgs', ARRAY(TEXT))

	__table_args__ = (
		UniqueConstraint('link'),
	)


class Commersant(base):

	__tablename__ = 'commersant'

	id = Column(INTEGER(), primary_key=True)

	datetime = Column(DATE())
	rubric = Column(TEXT())
	link = Column(TEXT())

	title = Column(TEXT())
	text = Column(TEXT())

	locs = Column('locs', ARRAY(TEXT))
	pers = Column('pers', ARRAY(TEXT))
	orgs = Column('orgs', ARRAY(TEXT))

	__table_args__ = (
		UniqueConstraint('link'),
	)


base.metadata.create_all(engine)

session = Session(bind=engine)