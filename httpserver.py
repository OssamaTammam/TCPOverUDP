from HTTP import HTTPServer

server = HTTPServer("localhost", 8080)
server.handle_http_request()
