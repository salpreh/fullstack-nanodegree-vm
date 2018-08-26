from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create a flask app
app = Flask(__name__)

# Create a DB session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurantsMenu')
def showAllMenus():

    # Get all menu items in DB
    menu_items = session.query(MenuItem).all()
    output = "<html><body>"
    for menu_item in menu_items:
        output += "<h2>{}</h2>".format(menu_item.name)
        output += "<p><b>Description:</b>{}</p>".format(menu_item.description)
        output += "<p><b>Price:</b>{}</p><br>".format(menu_item.price)

    output += "</html></body>"

    return output


@app.route('/restaurantsMenu/<int:restaurant_id>/')
def showRestaurantMenu(restaurant_id):

    # Get menu items for requested restaurant
    menu_items = session.query(MenuItem) \
                 .filter_by(restaurant_id=restaurant_id).all()

    # List menu items
    output = "<html><body>"
    for menu_item in menu_items:
        output += "<h2>{}</h2>".format(menu_item.name)
        output += "<p><b>Description:</b>{}</p>".format(menu_item.description)
        output += "<p><b>Price:</b>{}</p><br>".format(menu_item.price)

    output += "</html></body>"

    return output


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
