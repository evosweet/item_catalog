import json
import requests
import httplib2
import random
import string

from flask import Flask, render_template,\
    request, redirect, url_for, flash, jsonify,\
    session as login_session, make_response


from sqlalchemy import create_engine, and_, desc
from sqlalchemy.orm import sessionmaker
from db_setup import BASE, User, Category, Item


from flask import session as login_session


app = Flask(__name__)

ENGINE = create_engine('sqlite:///category.db')
BASE.metadata.bind = ENGINE

DBSESSION = sessionmaker(bind=ENGINE)
SESSION = DBSESSION()


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    SESSION.add(newUser)
    SESSION.commit()
    user = SESSION.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = SESSION.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = SESSION.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant'\
        '_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("Now logged in as %s" % login_session['username'])
    return "Processing"


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    resp = make_response("you have been logged out")
    resp.set_cookie('session', '', expires=0)  # add session cookie expiration
    return resp


@app.route('/')
@app.route('/category')
def showCategory():
    """ show all categories """
    catquery = SESSION.query(Category).order_by(desc(Category.id)).all()
    status = False
    if 'username' in login_session:
        status = True
    return render_template('index.html', category=catquery, status=status, image_url=login_session['picture'])


@app.route('/category/new/', methods=['GET', 'POST'])
def showNewCategory():
    catquery = SESSION.query(Category).order_by(desc(Category.id)).all()
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            req = request.form
            newCategory = Category(
                name=req['name'], user_id=login_session['user_id'])
            SESSION.add(newCategory)
            catquery = SESSION.query(Category).order_by(
                desc(Category.id)).all()
            flash("New Record Added !!!!!")
        return render_template('newcategory.html', category=catquery)


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    pass


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    pass


@app.route('/item/<int:category_id>/')
@app.route('/item/<int:category_id>/item/')
def showItems(category_id):
    catquery = SESSION.query(Category).get(category_id)
    items = SESSION.query(Item).filter_by(category_id=category_id).order_by('id desc').all()
    status = False
    if 'username' not in login_session:
        return render_template('publicitems.html', category_one=catquery, items=items)
    else:
        status = True
        return render_template('showitems.html', category_one=catquery, items=items, status=status)


@app.route('/item/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        catquery = SESSION.query(Category).get(category_id)
        if request.method == 'POST':
            req = request.form
            itemNew = Item(name=req['name'], description=req['description'],
                           user_id=login_session['user_id'], category_id=category_id)
            SESSION.add(itemNew)
            SESSION.commit()
            flash("New Record Added !!!!!")
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('newitem.html', category_one=catquery)


@app.route('/login')
def login():
    catquery = SESSION.query(Category).order_by(desc(Category.id)).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, category=catquery)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
