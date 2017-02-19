from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import BASE, Restaurant, MenuItem

ENGINE = create_engine('sqlite:///restaurantmenu.db')


BASE.metadata.bind = ENGINE
DBS = sessionmaker(bind=ENGINE)

SESS = DBS()

NORREC = "<h1>Sorry no records</h1>"

LISTALL = """
    <html>
        <body>
            <ul>
                %s
            </lu>
        </body>
    </html>
"""

EDIT = """ 
    <html>
        <body>
            <form method="POST" enctype='multipart/form-data'>
                <input type="hidden" name="id" value="%s"></input><br>
                New Name: <input type="text" name="name"></input><br>
                <input type="submit"></input>
            </form>
        </body>
    </html>
"""

NEW = """ 
    <html>
        <body>
            <form method="POST" enctype='multipart/form-data' action='/restaurants/new'>
                New Restaurant: <input type="text" name="name"></input>
                <input type="submit"></input>
            </form>
        </body>
    </html>
"""

def get_all():
    try:
        all_rest = SESS.query(Restaurant).all()
        if all_rest is not None:
            list_string = ''
            for rest in all_rest:
                list_string += '<li>'+rest.name+'</li>'+ \
                "<a href='/restaurants/"+ str(rest.id)+ \
                "/edit'>Edit</a><br><a href='/restaurants/"+str(rest.id)+ \
                "/delete'>Delete</a>"
            return_list = LISTALL % (list_string)
            return return_list
        else:
            return NORREC
    except Exception, error:
        print error

def edit(id):
    try:
        return EDIT % (id)
    except Exception, error:
        print error
def new():
    try:
        return NEW
    except:
        pass

def add_rest(name):
    try:
        new_rest = Restaurant(name=name)
        SESS.add(new_rest)
        SESS.commit()
        return 0
    except:
        pass

def rec_update(id,name):
    try:
        rec = SESS.query(Restaurant).get(id)
        rec.name = name
        SESS.add(rec)
        SESS.commit()
        return 0
    except: 
        pass

