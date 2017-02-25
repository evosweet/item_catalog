from flask import Flask, render_template, request, \
    redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import BASE, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
BASE.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/new/<int:restaurant_id>/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'], restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here


@app.route('/restaurants/edit/<int:restaurant_id>/<int:menu_id>/', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    editItem = session.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id).filter(MenuItem.id == menu_id).one()
    if request.method == 'POST':
        req = request.form
        editItem.name = req['name']
        editItem.course = req['course']
        editItem.price = req['price']
        editItem.description = req['description']
        flash("item updated!")
        return render_template('menuitem.html', editItem=editItem)
    else:
        return render_template('menuitem.html', editItem=editItem)
    # return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here


@app.route('/restaurants/delete/<int:restaurant_id>/<int:menu_id>/', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    dItem = session.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id).filter(MenuItem.id == menu_id).one()
    if request.method == 'POST':
        session.delete(dItem)
        session.commit()
        flash("Item Deleted!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', item=dItem)
    #return "page to delete a menu item. Task 3 complete!"

@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJson(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuJsonOne(restaurant_id, menu_id):
    OneItem = session.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id).filter(MenuItem.id == menu_id).one()
    return jsonify(MenuItems=OneItem.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
