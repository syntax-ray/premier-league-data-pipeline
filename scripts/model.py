from sqlalchemy import (
    Column, Integer, String, Boolean,
    ForeignKey, DECIMAL, TIMESTAMP, BigInteger
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class AvailableLeague(Base):
    __tablename__ = 'available_league'

    id = Column(Integer, primary_key=True)
    league_id = Column(BigInteger, unique=True)
    name = Column(String, nullable=False)
    type = Column(String)
    country = Column(String)
