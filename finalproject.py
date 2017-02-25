from flask import Flask, render_template,\
    request, redirect, url_for, flash, jsonify

app = Flask(__name__)



from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker
from database_setup import BASE, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#restaurants = [{'name':'franks','id':0},{'name':'mark','id':1}]
#menu = [{}]

#Show all Restaurants
@app.route('/')
@app.route('/restaurant')
def showRestaurants():
    """ Show All Restaurants """
    restaurants = session.query(Restaurant).order_by(desc(Restaurant.id)).all()
    return render_template('index.html', restaurants=restaurants)


#Create new restrant 
@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    """ show new Restaurant form """
    if request.method == 'POST':
        req = request.form
        restaurant = Restaurant(name=req['name'])
        session.add(restaurant)
        session.commit()
        flash("New Restaurant Created")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')

#edit Restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    """ edit Restaurant"""
    restaurant = session.query(Restaurant).get(restaurant_id)
    if request.method == 'POST':
        req = request.form
        restaurant.name = req['name']
        session.commit()
        flash("Record Updated")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)

#delete Restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    """ Delete Restaurant """
    restaurant = session.query(Restaurant).get(restaurant_id)
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        flash("Record Deleted")
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleterestaurant.html', restaurant=restaurant)

# Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    """ show menu """
    restaurant = session.query(Restaurant).get(restaurant_id)
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return render_template('showmenu.html', items=items, restaurant=restaurant)

# Create a new menu item
@app.route(
    '/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """ New Menu Item"""
    if request.method == 'POST':
        req = request.form
        item = MenuItem(name=req['name'], course=req['course'],
                        description=req['description'], price=req['price'],
                        restaurant_id=restaurant_id)
        session.add(item)
        session.commit()
        flash("Item Created")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)

# Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    """ Edit Menu Item """
    item = session.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id).filter(MenuItem.id == menu_id).one()
    if request.method == 'POST':
        req = request.form
        item.name = req['name']
        item.course = req['course']
        item.description = req['description']
        session.commit()
        flash("Item Updated")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', item=item)

# Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """ Delete Menu Item """
    if request.method == 'POST':
        item = session.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id).filter(MenuItem.id == menu_id).one()
        session.delete(item)
        session.commit()
        flash("Item Deleted")
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
