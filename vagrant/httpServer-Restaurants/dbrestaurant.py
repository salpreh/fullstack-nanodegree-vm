from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, Restaurant, MenuItem


class RestaurantsDB:
    """
    Clase para gestionar las llamadas a la base de datos
    """
    _database_address = 'sqlite:///restaurantmenu.db'
    _DBSession = None

    def __init__(self):
        # Enlazamos objetos proxy con la BD
        engine = create_engine(RestaurantsDB._database_address)
        Base.metadata.bind = engine

        # Factoría que generará sesiones (conexiones) a la BD
        RestaurantsDB._DBSession = sessionmaker(bind=engine)

    def getAllRestaurants(self):
        """
        Devuelve una lista con todos los restaurantes de la BD. La información
        de los restaurantes viene encapsulada en objetos
        `database_setup.Restaurant`.
        """

        # Creamos sesión a la BD
        session = RestaurantsDB._DBSession()

        # Recuperamos lista de todos los restaurantes
        restaurant_list = session.query(Restaurant).order_by(Restaurant.id).all()
        session.close()

        return restaurant_list

    def insertNewRestaurant(self, restaurant_name):
        """
        Inserta un restaurante un la base de datos.

        Args:
            restaurant_name (str): Nombre del restaurante
        """

        # Creamos sesión a la BD
        session = RestaurantsDB._DBSession()

        # Creamos nueva entrado y la añadimos los cambios a la session
        new_restaurant = Restaurant(name=restaurant_name)
        session.add(new_restaurant)

        # Confirmamos cambios y cerramos sesión
        session.commit()
        session.close()

    def getRestaurantById(self, id):
        """
        Devuelve la entrada del restaurante con la `id` recibida, o `None`
        si no existe un restaurante con ese identificador. La entrada del
        restaurante se devolverá encapsulada en un objeto
        `database_setup.Restaurant`.

        Args:
            id (int): Id del restaurante.
        """

        # Creamos sesión a la BD
        session = RestaurantsDB._DBSession()

        # Recuperamos entrada
        try:
            return session.query(Restaurant).filter_by(id=id).one()

        except NoResultFound:
            return None

        finally:
            session.close()

    def setRestaurantNameById(self, id, new_name):
        """
        Modifica el nombre del restaurante con la `id` recibida, si no existe
        un restaurante con el identificador proporcionado no se realizará
        ninguna acción.

        Args:
            id (int): Id del restaurante.
            new_name (str): Nuevo nombre del restaurante
        """

        # Creamos sesión a la BD
        session = RestaurantsDB._DBSession()

        # Recuperamos y modificamos la entrada
        try:
            restaurant = session.query(Restaurant).filter_by(id=id).one()
            restaurant.name = new_name
            session.add(restaurant)
            session.commit()

        except NoResultFound:
            print('Restaurant not found in DB')
            pass

        finally:
            session.close()

    def deleteRestaurantById(self, id):
        """
        Elimina la entrada del restaurante con la `id` recibida, si no existe
        un restaurante con el identificador proporcionado no se realizará
        ninguna acción.

        Args:
            id (int): Id del restaurante.
        """

        # Creamos sesión a la BD
        session = RestaurantsDB._DBSession()

        # Eliminamos entrada
        session.query(Restaurant).filter_by(id=id).delete()
        session.commit()
        session.close()
