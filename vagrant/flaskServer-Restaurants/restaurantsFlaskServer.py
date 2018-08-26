from flask import (Flask, render_template, request, redirect, url_for, flash,
                   jsonify)
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

# Create web app object
app = Flask(__name__)
app.secret_key = b'$()R73d_R4M_/n5idE?'

# Data base to ORM objects
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

# Session factory to create connections to our DB
DBSession = sessionmaker(bind=engine)


@app.route('/')
@app.route('/restaurants/')
def restaurantsMain():

    # Get restaurants form DB
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    entries = []

    # Get menu items count for each restaurant
    for restaurant in restaurants:
        num_menus = session.query(func.count(MenuItem.restaurant_id)) \
            .filter_by(restaurant_id=restaurant.id).scalar()
        entries.append((restaurant, num_menus))

    session.close()
    return render_template('RestaurantsTemplate.html', entries=entries)


@app.route('/restaurants/new/', methods=['GET', 'POST'])
def newRestaurant():

    # POST handler
    if request.method == 'POST':

        # Add new entry to the DB
        new_restaurant = Restaurant(name=request.form['name'])
        session = DBSession()
        session.add(new_restaurant)
        session.commit()

        # UI message
        flash('New restaurant added!')
        session.close()

        return redirect(url_for('restaurantsMain'))

    # GET handler
    else:
        return render_template('NewRestaurantTemplate.html')


@app.route('/restaurants/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    # POST handler
    if request.method == 'POST':

        # Get restaurant from DB
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        restaurant.name = request.form['name']

        # Update entry
        session.add(restaurant)
        session.commit()

        # UI message
        flash('Restaurant modified!')
        session.close()

        return redirect(url_for('restaurantsMain'))

    # GET handler
    else:

        # Get restaurant from DB
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        session.close()

        return render_template('EditRestaurantTemplate.html',
                               restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):

    # POST handler
    if request.method == 'POST':

        # Delete restaurant form DB
        session = DBSession()
        session.query(Restaurant).filter_by(id=restaurant_id).delete()
        session.commit()

        # UI message
        flash('Restaurant deleted!')
        session.close()

        return redirect(url_for('restaurantsMain'))

    # GET handler
    else:

        # Get restaurant form DB
        session = DBSession()
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        session.close()

        return render_template('DeleteRestaurantTemplate.html',
                               restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/')
@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):

    # Get menus from DB
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    session.close()
    return render_template('MenuTemplate.html', restaurant=restaurant,
                           items=items)


@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):

    # POST handler
    if request.method == 'POST':
        new_item = MenuItem(name=request.form['name'],
                            description=request.form['description'],
                            restaurant_id=restaurant_id)

        session = DBSession()
        session.add(new_item)
        session.commit()
        flash('New menu created!')
        session.close()

        # Redirect client
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    # GET handler
    else:
        return render_template('NewMenuTemplate.html',
                               restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):

    # POST handler
    if request.method == 'POST':

        # Retrieve and modify the menu item
        session = DBSession()
        menu_item = session.query(MenuItem) \
            .filter_by(id=menu_id, restaurant_id=restaurant_id).one()

        menu_item.name = request.form['name']
        menu_item.description = request.form['description']
        print(request.form)
        session.add(menu_item)
        session.commit()
        flash("Menu renamed to {}".format(request.form['name']))
        session.close()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    # GET handler
    else:

        # Retrieve menu item from DB
        session = DBSession()
        menu_item = session.query(MenuItem) \
            .filter_by(id=menu_id, restaurant_id=restaurant_id).one()

        return render_template('EditMenuTemplate.html', menu=menu_item)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):

    # POST handler
    if request.method == 'POST':

        # Delete menu item from DB
        session = DBSession()
        session.query(MenuItem) \
            .filter_by(id=menu_id, restaurant_id=restaurant_id).delete()
        session.commit()
        flash('Menu deleted')
        session.close()

        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))

    # GET handler
    else:

        # Retrieve the menu item from db
        session = DBSession()
        menu_item = session.query(MenuItem). \
            filter_by(id=menu_id, restaurant_id=restaurant_id).one()

        return render_template('DeleteMenuTemplate.html', menu=menu_item)


# REST API routes
@app.route('/restaurants/JSON/')
def restaurantsJSON():

    # Get restaurants form DB
    session = DBSession()
    restaurants = session.query(Restaurant).all()
    session.close()

    return jsonify(Restaurants=[res.serialize for res in restaurants])


@app.route('/restaurants/<int:restaurant_id>/JSON/')
def restaurantJSON(restaurant_id):

    # Get restaurant from DB
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    session.close()

    return jsonify(Restaurant=restaurant.serialize)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON/')
def restaurantMenuJSON(restaurant_id):

    # Get menus from DB
    session = DBSession()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_list = session.query(MenuItem) \
        .filter_by(restaurant_id=restaurant_id).all()
    session.close()

    return jsonify(RestaurantId=restaurant.id,
                   RestaurantName=restaurant.name,
                   MenuItems=[m.serialize for m in menu_list])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON/')
def menuJSON(restaurant_id, menu_id):

    # Retrieve menu from DB
    session = DBSession()
    menu_item = session.query(MenuItem) \
        .filter_by(restaurant_id=restaurant_id, id=menu_id).one()
    session.close()

    return jsonify(MenuItem=menu_item.serialize)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
