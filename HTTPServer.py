from TCP import TCP


class HTTPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.tcp = TCP(host, port)

    def handle_request(self):
        while True:
            self.tcp.respond_handshake()

            data = self.tcp.receive()
            print("Received request:", data)
            method = data.split()[0]
            # Process the request and generate response
            if method == "GET" or method == "POST":
                response = "HTTP/1.0 200 OK\nContent-Type: text/plain\n\n200 OK"
            else:
                response = "HTTP/1.0 501 Not Implemented\nContent-Type: text/plain\n\n501 Not Implemented"
            self.tcp.send(response.encode())

            self.tcp.close_connection_server()
