import socket
import random
import time


class UDPConnection:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM
        )  ## IPV4 UDP Connection
        self.socket.bind(
            (self.host, self.port)
        )  ## Bind the socket to this (host, port)

    def send(self, data):
        self.socket.sendto(data, (self.host, self.port))

    def receive(self, buffer_size=1024):
        return self.socket.recvfrom(buffer_size)

    def close(self):
        self.socket.close()

    def simulate_packet_loss(self, loss_rate):
        if random.random() < loss_rate:
            return True
        return False

    def simulate_packet_corruption(self, corruption_rate):
        if random.random() < corruption_rate:
            return True
        return False

    def simulate_packet_delay(self, delay):
        time.sleep(delay)
