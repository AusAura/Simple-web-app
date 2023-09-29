from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import os, mimetypes
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

current_directory = os.path.dirname(os.path.abspath(__file__))

# http://localhost:8000/

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def return_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # file_path = os.path.join(current_directory, filename)
        # with open(file_path, 'rb') as fd:
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def return_static(self):
        logging.info(f"Requested static resource: {self.path}")
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        # print(parsed_url)
        if parsed_url.path == '/':
            self.return_file('index.html')
        elif parsed_url.path == '/message':
            self.return_file('message.html')
        else:
            if Path().joinpath(parsed_url.path[1:]).exists():
                self.return_static()
            else:
                logging.error(f"Tried to get '{self.path}' but it does not exist: 404")
                self.return_file('error.html', 404)


def run_server(server_class=HTTPServer, handler_class=HTTPRequestHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    run_server()