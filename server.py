from TCP import TCP


def server():
    host = "localhost"
    port = 12345

    tcp_server = TCP(host, port)

    print("Server listening on port", port)

    while True:
        data = tcp_server.receive()
        print("Received data:", data)


if __name__ == "__main__":
    server()
