from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


NEW_VBURGER_PRICE = '$2.99'

# Point to the DB and bind our objects
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

# Create a connection to the DB
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Query for 'Veggie Burgers' in the table menu_items
veggie_burgers = session.query(MenuItem).filter_by(name='Veggie Burger').all()

# Print result info
print("{0:} CURRENT PRICE {0:}\n".format('#'*30))
for burger in veggie_burgers:
    print("Id: {}\nName: {}\nPrice: {}\nRestaurant: {}\n".format(burger.id,
                                                                 burger.name,
                                                                 burger.price,
                                                                 burger.restaurant.name))

# Update prices
print(">> Updating prices...\n")
for burger in veggie_burgers:
    if burger.price != NEW_VBURGER_PRICE:
        burger.price = NEW_VBURGER_PRICE
        session.add(burger)

session.commit()

# Check update
veggie_burgers = session.query(MenuItem).filter_by(name='Veggie Burger').all()
print("{0:} UPDATED PRICE {0:}\n".format('#'*30))
for burger in veggie_burgers:
    print("Id: {}\nName: {}\nPrice: {}\nRestaurant: {}\n".format(burger.id,
                                                                 burger.name,
                                                                 burger.price,
                                                                 burger.restaurant.name))
