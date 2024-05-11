from TCP import TCP
from time import sleep


def client():
    host = "localhost"
    port = 54321

    server_host = "localhost"
    server_port = 12345
    server_address = (server_host, server_port)

    tcp_client = TCP(host, port)

    i = 1
    data_to_send = "Hello from client!"
    while True:
        tcp_client.send(data_to_send + " " + str(i), server_address)
        print("Sent data to server:", data_to_send + " " + str(i))
        i += 1
        sleep(2)


if __name__ == "__main__":
    client()
