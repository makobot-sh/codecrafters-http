from app.Server import Server

def main():
    server = Server(reuse_port=True)
    while True:
        server.await_incoming_connection()
        server.listen()

if __name__ == "__main__":
    main()
