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

    @property
    def serialize(self):
        """
        Returns a dictionary with object atributtes as key and their values.
        """
        return {
            'id': self.id,
            'name': self.name
        }


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

    @property
    def serialize(self):
        """
        Devuelve un diccionario con pares atributo/valor.
        """
        return {
            'id': self.id,
            'name': self.name,
            'course': self.course,
            'description': self.description,
            'price': self.price
        }


# Point to our database
engine = create_engine('sqlite:///restaurantmenu.db')

# Create the defined structure in the data base
Base.metadata.create_all(engine)
