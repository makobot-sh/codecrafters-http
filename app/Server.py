import socket  # noqa: F401

class Server:
    def __init__(self, address: tuple[str,str]=("localhost", 4221), **kwargs):
        self.server_socket = socket.create_server(address, **kwargs)
    
    def await_incoming_connection(self):
        self.conn, self.addr = self.server_socket.accept() # wait for client
        
        print(f"Connected by {self.addr}")
        self.conn.sendall(b"HTTP/1.1 200 CONNECTED!!\r\n\r\n")

    def listen(self):
        with self.conn:
            while True:
                data = self.conn.recv(1024)
                if not data: break
                print(f"Got message {data}")
                self.conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    