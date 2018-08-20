import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


# Classes declaration that corresponds to tables in the data base
class Restaurant(Base):
    # Variable to indicate the table name
    __tablename__ = 'restaurant'

    # Variables to represent columns in the DB (Mapper)
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class MenuItem(Base):
    # Variable to indicate the table name
    __tablename__ = 'menu_item'

    # Variables to represent columns in the DB (Mapper)
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))

    # Represent a foreign key from another table
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


# Point to our database
engine = create_engine('sqlite:///restaurantmenu.db')

# Create the defined structure in the data base
Base.metadata.create_all(engine)
