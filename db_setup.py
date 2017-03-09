import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BASE = declarative_base()

class User(BASE):
    __tablename__ = 'user'
    id = Column(
        Integer, primary_key=True
    )
    name = Column(
        String(250), nullable=False
    )
    email = Column(
        String(250), nullable=False
    )
    picture = Column(
        String(240)
    )

class Category(BASE):
    __tablename__ = 'catgory'
    id = Column(
        Integer, primary_key=True
    )
    name = Column(
        String(250), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    user = relationship(User)
    property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(BASE):
    __tablename__ = 'item'

    id = Column(
        Integer, primary_key=True
    )
    name = Column(
        String(80), nullable=False
    )
    description = Column(
        String(250)
    )
    catgory_id = Column(
        Integer, ForeignKey('catgory.id')
    )
    user_id = Column(
        Integer, ForeignKey('user.id')
    )
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
        }



ENGINE = create_engine('sqlite:///category.db')

BASE.metadata.create_all(ENGINE)