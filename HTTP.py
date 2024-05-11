from TCP import TCP


class HTTPServer:
    def __init__(self, host, port, loss_prob=0.02, corruption_prob=0.1):
        self.tcp = TCP(host, port, loss_prob, corruption_prob)

    def handle_http_request(self):
        while True:
            # Receive HTTP request from client
            data, sender_address = self.tcp.receive()
            request_lines = data.split("\r\n")
            method, path, http_version = request_lines[0].split(" ")

            # Handle GET request
            if method == "GET":
                # Process the GET request
                # Here, you can retrieve the requested resource and send it back to the client

                # Example:
                response_body = "<html><body><h1>Hello, World!</h1></body></html>"
                response_headers = (
                    "HTTP/1.0 200 OK\r\nContent-Length: "
                    + str(len(response_body))
                    + "\r\n\r\n"
                )
                response = response_headers + response_body

                # Send HTTP response
                self.tcp.send(response, sender_address)

            # Handle POST request
            elif method == "POST":
                # Process the POST request
                # Here, you can extract the data from the request and perform necessary actions

                # Example:
                response_body = (
                    "<html><body><h1>Received POST request!</h1></body></html>"
                )
                response_headers = (
                    "HTTP/1.0 200 OK\r\nContent-Length: "
                    + str(len(response_body))
                    + "\r\n\r\n"
                )
                response = response_headers + response_body

                # Send HTTP response
                self.tcp.send(response, sender_address)

            else:
                # Unsupported HTTP method
                response_body = (
                    "<html><body><h1>Received UNKNOWN request!</h1></body></html>"
                )
                response_headers = (
                    "HTTP/1.0 404 NOT FOUND\r\nContent-Length: "
                    + str(len(response_body))
                    + "\r\n\r\n"
                )
                response = response_headers + response_body

                # Send HTTP response
                self.tcp.send(response, sender_address)

    def start(self):
        # Start listening for HTTP requests
        self.handle_http_request()


class HTTPClient:
    def __init__(self, host, port, loss_prob=0.02, corruption_prob=0.1):
        self.tcp = TCP(host, port, loss_prob, corruption_prob)

    def send_http_request(self, method, path, dest_address):
        # Construct HTTP request
        request = method + " " + path + " HTTP/1.0\r\n\r\n"

        # Send HTTP request
        self.tcp.send(request, dest_address)

    def receive_http_response(self):
        # Receive HTTP response
        data, _ = self.tcp.receive()

        # Process HTTP response
        # Here, you can parse the response, extract headers and body, and take appropriate actions
        print("Received HTTP response:")
        print(data)

    def start(self, method):
        # Send HTTP request
        self.send_http_request(method, "/")

        # Receive HTTP response
        self.receive_http_response()
