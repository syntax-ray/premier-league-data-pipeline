from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, DECIMAL, TIMESTAMP, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class League(Base):
    __tablename__ = 'league'

    id = Column(Integer, primary_key=True)
    league_id = Column(BigInteger, unique=True)
    name = Column(String, nullable=False)
    type = Column(String)
    country = Column(String)


class Team(Base):
    __tablename__ = 'team'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String)
    national = Column(Boolean)


class Match(Base):
    __tablename__ = 'match'

    id = Column(Integer, primary_key=True)
    date = Column(TIMESTAMP, nullable=False)
    home_id = Column(Integer, ForeignKey("team.id"))
    away_id = Column(Integer, ForeignKey("team.id"))
    season = Column(Integer)
    home_score = Column(Integer)
    away_score = Column(Integer)

    

