from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
from pathlib import Path
import logging, json
import socket
from threading import Thread
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)s - %(levelname)s - %(message)s",
)

current_directory = Path(".")
SAVE_FILENAME = "data.json"
SAVE_FILE_DIRECTORY = "Storage"
SAVE_FILE_DIR_PATH = current_directory / SAVE_FILE_DIRECTORY
SAVE_FILE_PATH = SAVE_FILE_DIR_PATH / SAVE_FILENAME
UDP_IP_FOR_SERVER = "0.0.0.0"
UDP_IP_FOR_CLIENT = "127.0.0.1"
UDP_PORT = 5000
UDP_PACKAGE_SIZE = 1024

logging.info(f"SAVE_FILENAME: {SAVE_FILENAME}")
logging.info(f"SAVE_FILE_DIRECTORY: {SAVE_FILE_DIRECTORY}")
logging.info(f"SAVE_FILE_DIR_PATH: {SAVE_FILE_DIR_PATH}")
logging.info(f"SAVE_FILE_PATH: {SAVE_FILE_PATH}")

# http://localhost:3000/
# docker run -it -p 3000:3000 -v D:\Storage:/app/Storage  amarakheo/simple-web-app


class UDPHandler:
    def save_data(self, data: bytes) -> None:
        logging.info(f"Raw data: {data}")
        data_parsed = urllib.parse.unquote_plus(data.decode())
        logging.info(f"Decoded (from binary) and normalized data: {data_parsed}")
        data_dict = {
            key: value
            for key, value in [el.split("=") for el in data_parsed.split("&")]
        }
        logging.info(f"Data in dictionary: {data_dict}")
        logging.info(f"File EXIST: {SAVE_FILE_PATH.exists()}")

        if not SAVE_FILE_PATH.exists():
            logging.info(f"CREATING NEW: {SAVE_FILE_PATH}")
            SAVE_FILE_DIR_PATH.mkdir(exist_ok=True, parents=True)
            with open(SAVE_FILE_PATH, "w") as fh:
                fh.write("{}")

        logging.info(f"READING EXISTING: {SAVE_FILE_PATH}")
        with open(SAVE_FILE_PATH, "r") as fh:
            file_content = json.load(fh)
            logging.info(f"JSON content: {file_content}")

        with open(SAVE_FILE_PATH, "w") as fh:
            file_content.update({str(datetime.now()): data_dict})
            logging.info(f"WRITING: {file_content}")
            json.dump(file_content, fh, indent=2)

    def run_socket_server(
        self, address: str = UDP_IP_FOR_SERVER, port: int = UDP_PORT
    ) -> None:
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_sock.bind((address, port))
        logging.info(f"Created server socket: {server_sock} with {address} and {port}")

        while True:
            try:
                data, client_addr = server_sock.recvfrom(UDP_PACKAGE_SIZE)
                logging.info(
                    f"Received data on socket server: {data.decode()} from: {client_addr}"
                )
            finally:
                self.save_data(data)

    def send_UDP_message(self, message: bytes, ip: str, port: int = UDP_PORT) -> None:
        server = (ip, port)
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logging.info(f"Created client socket: {client_sock} with {ip} and {port}")
        client_sock.sendto(message, server)
        print(f"Send data: {message.decode()} to server: {server}")
        client_sock.close()


UDP = UDPHandler()


class HTTPRequestHandler(BaseHTTPRequestHandler):
    def return_file(self, filename: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def return_static(self) -> None:
        logging.info(f"Requested static resource: {self.path}")
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/":
            self.return_file("index.html")
        elif parsed_url.path == "/message":
            self.return_file("message.html")
        else:
            if Path().joinpath(parsed_url.path[1:]).exists():
                self.return_static()
            else:
                logging.error(f"Tried to get '{self.path}' but it does not exist: 404")
                self.return_file("error.html", 404)

    def do_POST(self) -> None:
        logging.info(f"Recieving POST-request")
        data = self.rfile.read(int(self.headers["Content-Length"]))
        logging.info(f"TRYING TO SEND DATA TO SOCKET SERVER")
        UDP.send_UDP_message(data, UDP_IP_FOR_CLIENT)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()


def run_server(
    server_class: HTTPServer = HTTPServer,
    handler_class: BaseHTTPRequestHandler = HTTPRequestHandler,
) -> None:
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    http.serve_forever()
    # http.server_close()


if __name__ == "__main__":
    socket_thread = Thread(target=UDP.run_socket_server, args=())
    socket_thread.start()
    http_thread = Thread(target=run_server, args=())
    http_thread.start()
