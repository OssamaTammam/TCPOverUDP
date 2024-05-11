from TCP import TCP


class HTTPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tcp = TCP(host, port)

    def send_request(self, method, dest_address):
        self.tcp.initiate_handshake(dest_address)
        request = f"{method} / HTTP/1.0"
        self.tcp.send(request.encode())
        response = self.tcp.receive()
        print("Received response:", response)
        self.tcp.close_connection_client(dest_address)
