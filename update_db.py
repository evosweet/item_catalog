from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import BASE, Restaurant, MenuItem

ENGINE = create_engine('sqlite:///restaurantmenu.db')


BASE.metadata.bind = ENGINE
DBS = sessionmaker(bind=ENGINE)

SESS = DBS()


# create restaurant
# myRestaurant = Restaurant(name="Pizza Palace")
# SESS.add(myRestaurant)
# SESS.commit()

# print SESS.query(Restaurant).all()


# create menu item
# cheesepizza = MenuItem(
#     name="cheese pizza",
#     description="Made all natural ingredients and fresh mozzarella",
#     course="Entree",
#     price="$8.99",
#     restaurant=myRestaurant
# )
# SESS.add(cheesepizza)
# SESS.commit()

# print SESS.query(MenuItem).all()


# firstResult = SESS.query(MenuItem).all()
# for item in firstResult:
#     print item.name, item.restaurant.name



# bugger = SESS.query(MenuItem).filter_by(id= 8).one()
# print bugger.price
# bugger.price = '$2.99'
# SESS.add(bugger)
# SESS.commit()


# spinach = SESS.query(MenuItem).filter_by(name= 'Spinach Ice Cream').one()
# SESS.delete(spinach)
# SESS.commit()
# spinach = SESS.query(MenuItem).filter_by(name= 'Spinach Ice Cream').one()
# print spinach