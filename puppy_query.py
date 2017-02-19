from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from puppy_db import BASE, Shelter, Puppy
import datetime

ENGINE = create_engine('sqlite:///puppyshelter.db')

BASE.metadata.bind = ENGINE
DBS = sessionmaker(bind=ENGINE)

SESS = DBS()

def get_puppyAlpha():
    puppies = SESS.query(Puppy).order_by(asc(Puppy.name)).all()
    return puppies

def less_six():
    six_m = (datetime.date.today() - datetime.timedelta(6*365/12))
    puppies = SESS.query(Puppy).order_by(asc(Puppy.dateOfBirth)).all()
    filter_list = []
    for puppy in puppies:
        if puppy.dateOfBirth >= six_m:
            filter_list.append(puppy.dateOfBirth, six_m)
    return filter_list

def weight():
    puppies = SESS.query(Puppy).order_by(asc(Puppy.weight)).all()
    return puppies

def group():
    puppies = SESS.query(Puppy).group_by(Puppy.shelter_id).all()
    return puppies

#less_six()
#get_puppyAlpha()
group()