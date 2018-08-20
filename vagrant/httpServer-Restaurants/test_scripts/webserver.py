from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from streaming_form_data import StreamingFormDataParser
from streaming_form_data.targets import ValueTarget
# import cgi


FORM_HTML = """
    <form method='POST' enctype='multipart/form-data' action='/hello'>
        <h2> What would you like me to say? </h2>
        <input name='message' type='text'>
        <input type='submit' value='Submit'> </form>
            """


class WebserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == '/hello':

                # Request response header
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                # Request response message
                output = "<html><body>"
                output += "<h2>Hello!</h2>"
                output += FORM_HTML
                output += "</body></html>"
                self.wfile.write(output.encode())

            if self.path == '/hola':

                # Request response header
                self.send_response(200, 'OK')
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                # Request response message
                output = "<html><body>"
                output += "<h2>&#161Hola!</h2>"
                output += "<a href='/hello'>Back to Hello</a>"
                output += FORM_HTML
                output += "</body></html>"
                self.wfile.write(output.encode())

        except IOError:
            self.send_response(404, "File not found in {}".format(self.path))

    def do_POST(self):
        try:

            # Get the posted form data if it exists
            if self.headers.get('Content-Type', '').startswith('multipart/form-data'):

                # Get content length and retrieve query content
                content_len = int(self.headers.get('Content-Length', '0'))
                data_b = self.rfile.read(content_len)

                # Create a form parser and indicate the management for data
                form_parser = StreamingFormDataParser(headers=self.headers)
                message = ValueTarget()
                form_parser.register('message', message)

                # Parse the body of the request
                form_parser.data_received(data_b)

                # Write the output
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<h2> Okay, how about this: </h2>"
                output += "<h1> {} </h1>".format(message.value.decode())
                output += FORM_HTML
                output += "</body></html>"
                self.wfile.write(output.encode())

        except IOError:
            self.send_response(500, 'Server unable to handle the request')


def main():
    try:
        server_address = ('', 8080)
        server = HTTPServer(server_address, WebserverHandler)
        print("Web server running on port {}".format(server_address[1]))
        server.serve_forever()

    except KeyboardInterrupt:
        print("^C entred, stopping web server...")
        server.server_close()


if __name__ == "__main__":
    main()
