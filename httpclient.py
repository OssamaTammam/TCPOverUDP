from HTTP import HTTPClient

client = HTTPClient("localhost", 7070)
while True:
    client.send_http_request("aa", "/", ("localhost", 8080))
    client.receive_http_response()
