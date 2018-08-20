from sqlalchemy import create_engine
from sqlalchemy import sessionmaker
from database_setup import Base, Restaurant, MenuItem


# Point the DB we want to comunicate
engine = create_engine('sqlite:///restaurantmenu.db')

# Bind engine to `Base` class.
# Connects our classes definitions to tables in the DB
Base.metadata.bind = engine

# Create a session object to connect to the DB
DBSession = sessionmaker(bind=engine)
session = DBSession()

# New row in `restaurant` table (instance of our `Restaurant` class)
myRestaurant = Restaurant(name='Pizza Palace')

# Add changes to staging zone
session.add(myRestaurant)

# New row in `menu_item` table (instance of our `MenuItem` class).
# Includes a Foreign key reference
cheese_pizza = MenuItem(name='Cheese Pizza',
                        description='Made with four types of cheese!',
                        course='Entree',
                        price='$8.99',
                        restaurant=myRestaurant)

# Add changes to staging zone
session.add(cheese_pizza)

# Commit all changes
session.commit()
