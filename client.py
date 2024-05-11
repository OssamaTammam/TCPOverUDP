from TCP import TCP


def client():
    host = "localhost"
    port = 54321

    server_host = "localhost"
    server_port = 12345
    server_address = (server_host, server_port)

    tcp_client = TCP(host, port)

    data_to_send = "Hello from client!"
    while True:
        tcp_client.send(data_to_send, server_address)
        print("Sent data to server:", data_to_send)
        break


if __name__ == "__main__":
    client()
