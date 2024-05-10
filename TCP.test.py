import unittest
from TCP import TCP


class TestTCP(unittest.TestCase):
    def setUp(self):
        self.server_address = ("localhost", 12345)
        self.client_address = ("localhost", 54321)
        self.server = TCP(*self.server_address)
        self.client = TCP(*self.client_address)

    def tearDown(self):
        self.server.socket.close()
        self.client.socket.close()

    def test_send_receive(self):
        # Send data from client to server
        data_to_send = "Hello, server!"
        self.client.send(data_to_send, self.server_address)

        # Receive data at server
        received_data = self.server.receive()

        # Check if received data matches sent data
        self.assertEqual(received_data, data_to_send)


if __name__ == "__main__":
    unittest.main()
