# Librerias para sevidor HTTP
from http.server import HTTPServer, BaseHTTPRequestHandler
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
from bs4 import BeautifulSoup
from copy import copy

# Librerias para conectar con la BD
from database_setup import Restaurant, MenuItem
from dbrestaurant import RestaurantsDB

from pathlib import Path


# Rutas a ficheros
RESTAURANTS_HTML_PATH = Path('./html/RestaurantList.html')
TEMPLATE_HTML_PATH = Path('./html/RestaurantEntryTemplate.html')
NEW_RESTAURANT_PATH = Path('./html/AddRestaurant.html')
EDIT_RESTAURANT_PATH = Path('./html/EditRestaurant.html')
DELETE_RESTAURANT_PATH = Path('./html/DeleteRestaurant.html')

# Ficheros html dinamicos
RESTAURANTS_HTML = ""
RESTAURANT_TEMP_HTML = ""

# Conexión a BD
RESTAURANTS_DB = None


class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Lista restaurantes
            if self.path == '/restaurants':

                # Cabecera de mensaje
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                # Contenido de mensaje
                self.wfile.write(getRestaurantsListHtml().encode())

            # Formulario nuevo restaurante
            if self.path == '/restaurants/new':

                # Cabeceras
                self.send_response(200, 'OK')
                self.send_header('Content-Type:', 'text/html')
                self.end_headers()

                # Contenido
                self.wfile.write(getNewRestaurantHtml().encode())

            # Formulario editar restaurante
            if self.path.endswith('/edit'):

                # Obtenemos id
                try:
                    id = int(self.path.split('/')[-2])

                except ValueError:
                    self.send_response(404, 'Page not found')
                    return

                # Recuperamos html y comprobamos si está correcto
                html_output = getEditRestaurantHtml(id)
                if html_output is None:
                    self.send_response(400, 'Bad request. Unexisting resource')
                    return

                # Cabecera mensaje
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                # Contenido mensaje
                self.wfile.write(html_output.encode())

            # Formulario editar restaurante
            if self.path.endswith('/delete'):

                # Obtenemos id
                try:
                    id = int(self.path.split('/')[-2])

                except ValueError:
                    self.send_response(404, 'Page not found')
                    return

                # Recuperamos html y comprobamos si está correcto
                html_output = getDeleteRestaurant(id)
                if html_output is None:
                    self.send_response(400, 'Bad request. Unexisting resource')
                    return

                # Cabecera mensaje
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                # Contenido mensaje
                self.wfile.write(html_output.encode())

        except IOError:
            self.send_response(500, 'Server error while serving the request')

    def do_POST(self):
        try:
            # Petición nuevo restaurante
            if self.path == '/restaurants/new':

                # Recuperamos contenido del mensaje
                content_len = int(self.headers.get('Content-Length', '0'))
                data_b = self.rfile.read(content_len)

                # Parseamos datos del formulario
                form_parser = StreamingFormDataParser(headers=self.headers)
                restaurant_name = ValueTarget()
                form_parser.register('restaurant_name', restaurant_name)
                form_parser.data_received(data_b)

                # Generamos entrada en la BD
                name_str = restaurant_name.value.decode()
                if name_str:
                    RESTAURANTS_DB.insertNewRestaurant(name_str)

                # Respuesta a petición
                self.send_response(303, 'Redirecto to main page')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            # Petición editar restaurante
            if self.path.endswith('/edit'):

                # Recuperamos contenido mensaje
                content_len = int(self.headers.get('Content-Length', '0'))
                data_b = self.rfile.read(content_len)

                # Parseamos datos formulario
                form_parser = StreamingFormDataParser(headers=self.headers)
                restaurant_name = ValueTarget()
                form_parser.register('restaurant_name', restaurant_name)
                form_parser.data_received(data_b)

                # Recuperamos id del restaurante
                try:
                    id = int(self.path.split('/')[-2])

                except ValueError:
                    self.send_response(400, 'Bad request')
                    return

                # Modificamos restaurante en BD
                new_name = restaurant_name.value.decode()
                if new_name:
                    print("Setting restaurant name")
                    RESTAURANTS_DB.setRestaurantNameById(id, new_name)

                # Respuesta a petición
                self.send_response(303, 'Redirect to main page')
                self.send_header('Location', '/restaurants')
                self.end_headers()

            if self.path.endswith('/delete'):

                # Recuperamos id del restaurante
                try:
                    id = int(self.path.split('/')[-2])

                except ValueError:
                    self.send_response(400, 'Bad request')
                    return

                # Eliminamos restaurante de BD
                RESTAURANTS_DB.deleteRestaurantById(id)

                # Respuesta a petición
                self.send_response(303, 'Redirect to main page')
                self.send_header('Location', '/restaurants')
                self.end_headers()

        except IOError:
            self.send_response(500, 'Server error while attending the request')


def startServer():
    """
    Lanza el servidor. Responderá peticiones hasta que reciba una interrupción
    por teclado (Ctrl + C).
    """
    try:
        server_address = ('', 8080)
        server = HTTPServer(server_address, WebserverHandler)
        print("Server running on port {}".format(server_address[1]))
        server.serve_forever()

    except KeyboardInterrupt:
        print("Stopping web server...")
        server.server_close()


def getRestaurantsListHtml():
    """
    Genera un html con una lista de todos los restaurantes en la base de datos
    """
    global RESTAURANTS_DB

    # Parseamos html base y plantilla
    main_html_soup = BeautifulSoup(RESTAURANTS_HTML, 'html.parser')
    template_html_soup = BeautifulSoup(RESTAURANT_TEMP_HTML, 'html.parser')

    # Recuperamos tag donde añadiremos las entradas de restaurantes
    main_list_div = main_html_soup.select('#restaurant-list')[0]
    template_div = template_html_soup.select('.restaurant-item')[0]

    # Obtenemos lista de restaurantes de la BD
    restaurants_list = RESTAURANTS_DB.getAllRestaurants()

    # Recorremos lista de restaurantes e insertamos entradas en el html
    for restaurant in restaurants_list:

        # Generamos copia de plantilla html y la modificamos
        temp_copy = copy(template_div)
        temp_copy['id'] = restaurant.id
        temp_copy.select('.edit')[0]['href'] = "{}/edit".format(restaurant.id)
        temp_copy.select('.delete')[0]['href'] = "{}/delete".format(restaurant.id)
        temp_copy.select('.restaurant-name')[0].string = restaurant.name

        # Añadimos entrada a html principal
        main_list_div.append(temp_copy)

    return main_html_soup.prettify()


def getNewRestaurantHtml():
    """
    Devuelve un html con el formulario para añadir un nuevo restaurante
    """
    newRestaurantHtml = ""
    with open(str(NEW_RESTAURANT_PATH), 'r') as htmlFile:
        newRestaurantHtml = htmlFile.read()

    return newRestaurantHtml


def getEditRestaurantHtml(id):
    """
    Devuelve un html con el formulario para editar el nombre del restaurante,
    o `None` si el identifcador del restaurante no existe.

    Args:
        id (int): Id del restaurante
    """
    editRestaurantHtml = ""
    with open(str(EDIT_RESTAURANT_PATH), 'r') as htmlFile:
        editRestaurantHtml = htmlFile.read()

    # Si el restaurante no existe en la BD devolvemos `None`
    restaurant = RESTAURANTS_DB.getRestaurantById(id)
    if restaurant is None:
        return None

    # Editamos html
    editRestaurantSoup = BeautifulSoup(editRestaurantHtml, 'html.parser')

    # Nombre de restaurante en casilla de texto
    input_text = editRestaurantSoup.select('#name')[0]
    input_text['value'] = restaurant.name

    # Nombre de restaurante bajo titulo
    subtitle_tag = editRestaurantSoup.new_tag('h3', id='restaurant-title')
    subtitle_tag.string = restaurant.name
    editRestaurantSoup.select('body')[0].insert(2, subtitle_tag)

    # Modificamos ruta del formulario
    editRestaurantSoup.select('form')[0]['action'] = "restaurants/{}/edit".format(id)

    return editRestaurantSoup.prettify()


def getDeleteRestaurant(id):
    """
    Devuelve un html con el formulario para eliminar el restaurante con el id
    recibido, o `None` si el identifcador del restaurante no existe.

    Args:
        id (int): Id del restaurante
    """
    with open(str(DELETE_RESTAURANT_PATH), 'r') as htmlFile:
        deleteRestaurantHtml = htmlFile.read()

    # Si el restaurante no existe en la BD devolvemos `None`
    restaurant = RESTAURANTS_DB.getRestaurantById(id)
    if restaurant is None:
        return None

    # Editamos html
    deleteRestaurantSoup = BeautifulSoup(deleteRestaurantHtml, 'html.parser')

    # Nombre de restaurant bajo el titulo
    subtitle_tag = deleteRestaurantSoup.new_tag('h3', id='restaurant-title')
    subtitle_tag.string = restaurant.name
    deleteRestaurantSoup.select('body')[0].insert(2, subtitle_tag)

    # Modificamos ruta de formulario
    deleteRestaurantSoup.select('form')[0]['action'] = "restaurants/{}/delete".format(id)

    return deleteRestaurantSoup.prettify()


def initServer():
    """
    Carga ficheros e inicializa variable sque necesita para su funcionamiento.
    """
    global RESTAURANTS_HTML
    with open(str(RESTAURANTS_HTML_PATH), 'r') as htmlFile:
        RESTAURANTS_HTML = htmlFile.read()

    global RESTAURANT_TEMP_HTML
    with open(str(TEMPLATE_HTML_PATH), 'r') as htmlFile:
        RESTAURANT_TEMP_HTML = htmlFile.read()

    global RESTAURANTS_DB
    RESTAURANTS_DB = RestaurantsDB()


if __name__ == "__main__":
    initServer()
    startServer()
