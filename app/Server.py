import socket  # noqa: F401

class Response:
    def __init__(self, http_version=1.1, status_code=None, status_reason=""):
        self.http_version = http_version
        self.status_code = status_code
        self.status_reason = status_reason
        self.headers = {}
        self.body = ""

    def render(self):
        if self.status_code is None:
            print("Status code must be specified before rendering!")
            raise Exception("Tried to render a response without a status code set")
        status = f"HTTP/{self.http_version} {self.status_code} {self.status_reason}"
        headers = "\r\n".join(self.headers)
        response = f"{status}\r\n{headers}\r\n{self.body}\r\n"
        return str.encode(response)

class Request:
    def __init__(self, http_version=1.1, method="GET", target=None):
        self.http_version = http_version
        self.method = method
        self.target = target
        self.headers = {}
        self.body = ""

    def addHeader(self, key, value):
        self.headers[key] = value

    @property
    def request_line(self):
        return f"{self.method} {self.target} HTTP/{self.http_version}\r\n"
    
    @request_line.setter
    def request_line(self, req_str):
        self.method, self.target, http_version = req_str.split(" ")
        assert http_version.startswith("HTTP/"), "HTTP version should start with HTTP/"
        self.http_version = http_version[5:]
    
    def parse(msg):
        dec_msg = msg.decode()
        print(dec_msg)
        parts = dec_msg.split("\r\n")

        req = Request()
        req.request_line = parts[0]


    def render(self):
        if self.status_code is None:
            print("Status code must be specified before rendering!")
            raise Exception("Tried to render a response without a status code set")
        status = f"HTTP/{self.http_version} {self.status_code} {self.status_reason}"
        headers = "\r\n".join(self.headers)
        response = f"{status}\r\n{headers}\r\n{self.body}\r\n"
        return str.encode(response)

class Server:
    def __init__(self, address: tuple[str,str]=("localhost", 4221), **kwargs):
        self.server_socket = socket.create_server(address, **kwargs)
    
    def await_incoming_connection(self):
        self.conn, self.addr = self.server_socket.accept() # wait for client
        
        print(f"Connected by {self.addr}")
        self.OK_200()

    def listen(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                if not data: break
                print(f"[{self.addr[0]}:{self.addr[1]}] {data.decode()}")

                Request.parse(data)

                self.OK_200()

    def OK_200(self):
        res = Response(status_code=200, status_reason="OK")
        self.conn.sendall(res.render())
    
    def NOT_FOUND_404(self):
        res = Response(status_code=404, status_reason="Not Found")
        self.conn.sendall(res.render())
    