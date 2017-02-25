import sys
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

BASE = declarative_base()

class Restaurant(BASE):
    __tablename__ = 'restaurant'

    name = Column(
        String(80), nullable=False
    )
    id = Column(
        Integer, primary_key=True
    )


class MenuItem(BASE):
    __tablename__ = 'menu_item'

    id = Column(
        Integer, primary_key=True
    )
    name = Column(
        String(80), nullable=False
    )
    course = Column(String(250))
    description = Column(
        String(250)
    )
    price = Column(String(8))
    restaurant_id = Column(
        Integer, ForeignKey('restaurant.id')
    )
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'price': self.price,
            'course': self.course,
        }


ENGINE = create_engine('sqlite:///restaurantmenu.db')

BASE.metadata.create_all(ENGINE)

