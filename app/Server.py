import socket  # noqa: F401

class Message():
    def print(self):
        res = self.render().decode()
        if len(self._headers.keys()) == 0:
            res = res[:-2]
            if self.body == "": #If there's not headers or body remove the carriage return separating them from request line as well
                res = res[:-2]
        if self.body == "":
            res = res[:-2]
        return res

class Response(Message):
    def __init__(self, http_version=1.1, status_code=None, status_reason=""):
        self.http_version = http_version
        self.status_code = status_code
        self.status_reason = status_reason
        self._headers = {}
        self.body = ""

    def render(self):
        if self.status_code is None:
            print("Status code must be specified before rendering!")
            raise Exception("Tried to render a response without a status code set")
        status = f"HTTP/{self.http_version} {self.status_code} {self.status_reason}"
        headers = "\r\n".join(self._headers)
        response = f"{status}\r\n{headers}\r\n{self.body}\r\n"
        return str.encode(response)

class Request(Message):
    def __init__(self, http_version=1.1, method="GET", target=None):
        self.http_version = http_version
        self.method = method
        self.target = target
        self._headers = {}
        self.body = ""

    def addHeader(self, key, value):
        self.headers[key] = value

    @property
    def request_line(self):
        return f"{self.method} {self.target} HTTP/{self.http_version}"
    
    @request_line.setter
    def request_line(self, req_str):
        self.method, self.target, http_version = req_str.split(" ")
        assert http_version.startswith("HTTP/"), "HTTP version should start with HTTP/"
        self.http_version = http_version[5:]

    @property
    def headers(self):
        return "\r\n".join([f"{k}: {v}" for k,v in self._headers.items()])
    
    @headers.setter
    def headers(self, str_headers: str | list):
        if isinstance(str_headers, str):
            header_list = str_headers.split("\r\n")
        else:
            header_list = str_headers
        for str_header in header_list:
            if str_header == "":
                continue
            kv = str_header.split(":", 1)
            self._headers[kv[0]] = kv[1]
    
    def parse(msg):
        dec_msg = msg.decode()
        parts = dec_msg.split("\r\n")

        req = Request()
        req.request_line = parts[0]
        req.headers = parts[1:-1]
        req.body = parts[-1]

        return req

    def render(self):
        if self.target is None:
            print("Target must be specified before rendering!")
            raise Exception("Tried to render a request without a target set")
        response = f"{self.request_line}\r\n{self.headers}\r\n{self.body}\r\n"
        return str.encode(response)

class Server:
    def __init__(self, address: tuple[str,str]=("localhost", 4221), **kwargs):
        self.server_socket = socket.create_server(address, **kwargs)
        self.srv_host, self.srv_addr = address
    
    def await_incoming_connection(self):
        self.conn, self.addr = self.server_socket.accept() # wait for client
        
        print(f"[{self.srv_host}:{self.srv_addr}] Connected by {self.addr}")
        self.OK_200()

    def listen(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                if not data: break
                req = Request.parse(data)
                print(f"[{self.addr[0]}:{self.addr[1]}] {req.print()}")
                if req.target == "/":
                    self.OK_200()
                else:
                    self.NOT_FOUND_404()

    def send(self, res: Response):
        print(f"[{self.srv_host}:{self.srv_addr}] {res.print()}")
        self.conn.sendall(res.render())

    def OK_200(self):
        self.send(Response(status_code=200, status_reason="OK"))
    
    def NOT_FOUND_404(self):
        self.send(Response(status_code=404, status_reason="Not Found"))
    