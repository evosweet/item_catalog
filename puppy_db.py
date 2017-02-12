import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BASE = declarative_base()


class Shelter(BASE):
    __tablename__ = "shelter"
    name = Column(String(80), nullable=False)
    address = Column(String(250))
    city = Column(String(80))
    state = Column(String(20))
    zipCode = Column(String(10))
    website = Column(String)
    id = Column(Integer, primary_key=True)


class Puppy(BASE):
    __tablename__ = "puppy"
    name = Column(String(250), nullable=False)
    dateOfBirth = Column(Date)
    gender = Column(String(6), nullable=False)
    weight = Column(Numeric(10))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    picture = Column(String)
    id = Column(Integer, primary_key=True)


ENGINE = create_engine('sqlite:///puppyshelter.db')
BASE.metadata.create_all(ENGINE)
