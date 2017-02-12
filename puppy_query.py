from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from puppy_db import BASE, Shelter, Puppy

ENGINE = create_engine('sqlite:///puppyshelter.db')

BASE.metadata.bind = ENGINE
DBS = sessionmaker(bind=ENGINE)

SESS = DBS()

def get_puppyAlpha():
    puppies = SESS.query(Puppy).order_by(asc(Puppy.name)).all()
    for puppy in puppies:
        print puppy.name + "\n"
        print puppy.dateOfBirth

def less_six():
    puppies = SESS.query(Puppy).order_by(asc(Puppy.name)).all()


get_puppyAlpha()