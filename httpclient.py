from HTTP import HTTPClient

client = HTTPClient("localhost", 7070)

client.send_http_request("GET", "/", ("localhost", 8080))
client.receive_http_response()

client.send_http_request("POST", "/", ("localhost", 8080))
client.receive_http_response()

client.send_http_request("UNKnOWN", "/", ("localhost", 8080))
client.receive_http_response()
