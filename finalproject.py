import json
import requests
import httplib2
import random
import string
import os

from werkzeug.utils import secure_filename

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

# upload settings
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def createUser(login_session):
    """ add new user to DB """
    newuser = User(name=login_session['username'], email=login_session['email'],
                   picture=login_session['picture'])
    SESSION.add(newuser)
    SESSION.commit()
    user = SESSION.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """ get user data for exiting users """
    user = SESSION.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """ get user email address """
    user = SESSION.query(User).filter_by(email=email).one()
    return user.id


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ connect and authenticate users with FB """
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
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
    #token = result.split("&")[0]
    data = json.loads(result)
    token = 'access_token=' + data['access_token']
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
    output = """
            <div class="alert alert-success" role="alert">You Are now Logged out</div>
            <a href="/">Main Page</a>
    """
    resp = make_response(output)
    resp.set_cookie('session', '', expires=0)  # add session cookie expiration
    return resp


@app.route('/itemsJson/<int:category_id>/items/JSON')
def itemsJSON(category_id):
    """ return list of items in JSON """
    items = SESSION.query(Item).filter_by(
        category_id=category_id).order_by('id desc').all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/itemJson/<int:category_id>/<int:item_id>/item/JSON')
def itemJson(category_id, item_id):
    item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
        Item.id == item_id).one()
    return jsonify(Item=item.serialize)


@app.route('/')
@app.route('/category')
def showCategory():
    """ show all categories """
    catquery = SESSION.query(Category).order_by(desc(Category.id)).all()
    itemquery = SESSION.query(Item).order_by(desc(Item.id)).all()
    status = False
    if 'username' in login_session:
        status = True
        return render_template('index.html', category=catquery, itemquery=itemquery, status=status,
                               image_url=login_session['picture'])
    else:
        return render_template('index.html', category=catquery, status=status, itemquery=itemquery)


@app.route('/category/new/', methods=['GET', 'POST'])
def showNewCategory():
    """ add new Category """
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
    """ edit category """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        catquery = SESSION.query(Category).get(category_id)
        if catquery.user_id != login_session['user_id']:
            flash(" You don't have access to this record ")
            return redirect(url_for('showCategory'))
        if request.method == 'POST':
            req = request.form
            catquery.name = req['name']
            SESSION.commit()
            flash("Record Updated !!")
            return redirect(url_for('showCategory'))
        else:
            return render_template('editcategory.html', category_one=catquery)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    """ delete category """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        category = SESSION.query(Category).get(category_id)
        if category.user_id != login_session['user_id']:
            flash(" You don't have access to this record ")
            return redirect(url_for('showCategory'))
        if request.method == 'POST':
            SESSION.delete(category)
            SESSION.commit()
            flash("Record Deleted !!")
            return redirect(url_for('showCategory'))
        else:
            return render_template('deletecategory.html', category=category)


@app.route('/item/<int:category_id>/')
@app.route('/item/<int:category_id>/item/')
def showItems(category_id):
    """ show all items """
    catquery = SESSION.query(Category).get(category_id)
    items = SESSION.query(Item).filter_by(
        category_id=category_id).order_by('id desc').all()
    status = False
    if 'username' not in login_session:
        return render_template('publicitems.html', category_one=catquery, items=items)
    else:
        status = True
        return render_template('showitems.html', category_one=catquery, items=items, status=status)


@app.route('/item/<int:category_id>/new/', methods=['GET', 'POST'])
def newItem(category_id):
    """ create new item """
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


@app.route('/item/<int:category_id>/item/<int:item_id>/show')
def showItem(category_id, item_id):
    """ show single item """
    item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
        Item.id == item_id).one()
    return render_template('showitem.html', item=item)


@app.route('/item/<int:category_id>/item/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """ edit item """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
            Item.id == item_id).one()
        if item.user_id != login_session['user_id']:
            flash(" You don't have access to edit this record !!")
            return render_template('showitem.html', item=item)
        else:
            if request.method == 'POST':
                req = request.form
                item.name = req['name']
                item.description = req['description']
                SESSION.add(item)
                SESSION.commit()
                flash("record updated")
                return render_template('showitem.html', item=item)
            else:
                return render_template('edititem.html', item=item)


@app.route('/item/<int:category_id>/item/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """ delete item """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
            Item.id == item_id).one()
        if item.user_id != login_session['user_id']:
            flash(" You don't have access to edit this record !!")
            return render_template('showitems.html', category_id=category_id)
        else:
            if request.method == 'POST':
                SESSION.delete(item)
                SESSION.commit()
                flash("record deleted")
                return redirect(url_for('showItems', category_id=category_id))
            else:
                return render_template('deleteitem.html', item=item)


def allowed_file(filename):
    """ validate file types """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/item/<int:category_id>/item/<int:item_id>/image', methods=['GET', 'POST'])
def imageUpload(category_id, item_id):
    """" upload images """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
            Item.id == item_id).one()
        if item.user_id != login_session['user_id']:
            flash(" You don't have access to add images to this record !!")
            return render_template('showitems.html', category_id=category_id)
        else:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file part')
                    return redirect(request.url)
                upload_file = request.files['file']
                if upload_file.filename == '':
                    flash('No file selected')
                    return redirect(request.url)
                if upload_file and allowed_file(upload_file.filename):
                    filename = secure_filename(upload_file.filename)
                    upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(
                        item.id) + "_" + str(item.category_id) + "_" + filename))
                    item.image_path = 'static/uploads/' + str(item.id) + "_" + \
                        str(item.category_id) + "_" + filename
                    SESSION.add(item)
                    SESSION.commit()
                    return redirect(url_for('editItem', category_id=category_id, item_id=item_id))
            else:
                return render_template('uploadimage.html', item=item)

@app.route('/item/<int:category_id>/item/<int:item_id>/deleteImage', methods=['GET', 'POST'])
def deleteImage(category_id, item_id):
    """ edit image """
    if 'username' not in login_session:
        return redirect(url_for('login'))
    else:
        item = SESSION.query(Item).filter(Item.category_id == category_id).filter(
            Item.id == item_id).one()
        if item.user_id != login_session['user_id']:
            flash(" You don't have access to delete this image!!")
            return render_template('showitems.html', category_id=category_id)
        else:
            item.image_path = None
            SESSION.add(item)
            SESSION.commit()
            return redirect(url_for('editItem', category_id=category_id, item_id=item_id))


@app.route('/login')
def login():
    """ login route """
    catquery = SESSION.query(Category).order_by(desc(Category.id)).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, category=catquery)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
