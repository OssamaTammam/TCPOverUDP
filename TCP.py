import socket
import random
from Packet import Packet
import time


class TCP:
    def __init__(self, host, port, loss_prob=0.1, corruption_prob=0.1):
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.address)
        self.socket.settimeout(5)
        self.next_seq_number = 0
        self.expected_seq_num = 0
        self.handshake_succeeded = False
        self.loss_prob = loss_prob  # Probability of packet loss
        self.corruption_prob = corruption_prob  # Probability of packet corruption

    def initiate_handshake(self, dest_address):
        # Send SYN packet
        syn_packet = Packet(
            self.next_seq_number, 0, "", flags=0b1000000
        )  # SYN flag set
        syn_packed = syn_packet.pack()
        self.socket.sendto(syn_packed, dest_address)

        # Wait for SYN-ACK packet
        while True:
            try:
                response, _ = self.socket.recvfrom(1024)
                syn_ack_packet = Packet.unpack(response)
                if syn_ack_packet.flags & 0b1100000:  # Check if SYN-ACK flag is set
                    self.next_seq_number = syn_ack_packet.seq_num + 1
                    self.expected_seq_num = syn_ack_packet.seq_num + 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for SYN-ACK packet. Retrying...")

        # Send ACK packet
        ack_packet = Packet(
            self.next_seq_number, syn_ack_packet.seq_num + 1, "", flags=0b0100000
        )  # ACK flag set
        ack_packed = ack_packet.pack()
        self.socket.sendto(ack_packed, dest_address)
        self.handshake_succeeded = True

        print("Handshake successful")

    def respond_handshake(self):
        # Wait for SYN packet
        while True:
            try:
                syn_packet_data, sender_address = self.socket.recvfrom(1024)
                syn_packet = Packet.unpack(syn_packet_data)
                if syn_packet.flags & 0b1000000:  # Check if SYN flag is set
                    self.next_seq_number = syn_packet.seq_num + 1
                    self.expected_seq_num = syn_packet.seq_num + 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for SYN packet. Retrying...")

        # Send SYN-ACK packet
        syn_ack_packet = Packet(
            self.next_seq_number, syn_packet.seq_num + 1, "", flags=0b1100000
        )  # SYN-ACK flags set
        syn_ack_packed = syn_ack_packet.pack()
        self.socket.sendto(syn_ack_packed, sender_address)

        # Wait for ACK packet
        while True:
            try:
                ack_packet_data, _ = self.socket.recvfrom(1024)
                ack_packet = Packet.unpack(ack_packet_data)
                if ack_packet.flags & 0b0100000:  # Check if ACK flag is set
                    self.next_seq_number = ack_packet.ack_num
                    self.expected_seq_num = ack_packet.seq_num
                    self.handshake_succeeded = True
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for ACK packet. Retrying...")

        print("Handshake successful")

    def send(self, data, dest_address):
        if not self.handshake_succeeded:
            self.initiate_handshake(dest_address)

        packet = Packet(self.next_seq_number, self.expected_seq_num, data)
        packet_data = packet.pack()

        # Send packet
        while True:
            try:
                self.socket.sendto(packet_data, dest_address)
                break
            except socket.error as e:
                print(f"Error sending packet: {e}")
                continue

        # Wait for ACK with retransmission
        retries = 3  # Maximum number of retries
        while retries > 0:
            try:
                response, _ = self.socket.recvfrom(1024)
                ack_packet = Packet.unpack(response)

                # Check if ACK packet and expected sequence number
                if (
                    ack_packet.flags & 0b0100000
                    and ack_packet.ack_num == self.next_seq_number
                ):
                    self.next_seq_number += len(data)
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for ACK packet. Retrying...")
                retries -= 1
                if retries == 0:
                    print("Maximum number of retries reached. Aborting.")
                    return
                # Retransmit packet
                self.socket.sendto(packet_data, dest_address)

    def receive(self):
        if not self.handshake_succeeded:
            self.respond_handshake()

        while True:
            try:
                data, sender_address = self.socket.recvfrom(1024)

                # Simulate packet loss
                if random.random() < self.loss_prob:
                    print("Packet loss simulated.")
                    continue

                # Simulate packet delay
                time.sleep(random.uniform(0, 0.5))  # Adjust delay as needed

                if random.random() < self.corruption_prob:  # Simulate packet corruption
                    # Corrupt packet data
                    print("Packet corruption simulated")
                    data = self.corrupt_packet(data)

                recv_packet = Packet.unpack(data)
                recv_checksum = recv_packet.checksum

                # Check if expected sequence number
                if (
                    recv_packet.seq_num == self.expected_seq_num
                    and recv_packet.verify_checksum(recv_checksum)
                ):
                    ack_packet = Packet(
                        self.next_seq_number,
                        self.expected_seq_num,
                        "",
                        flags=0b0100000,
                    )
                    ack_data = ack_packet.pack()

                    # Send ACK
                    while True:
                        try:
                            self.socket.sendto(ack_data, sender_address)
                            break
                        except socket.error as e:
                            print(f"Error sending ACK packet: {e}")
                            continue

                    # Update sequence numbers
                    self.expected_seq_num += len(recv_packet.data)
                    self.next_seq_number = recv_packet.ack_num

                    return recv_packet.data, sender_address
                else:
                    # Request retransmission
                    nack_packet = Packet(
                        self.next_seq_number,
                        self.expected_seq_num,
                        "",
                        flags=0b1000000,  # NACK flag set
                    )
                    nack_data = nack_packet.pack()

                    # Send NACK
                    while True:
                        try:
                            self.socket.sendto(nack_data, sender_address)
                            break
                        except socket.error as e:
                            print(f"Error sending NACK packet: {e}")
                            continue

            except socket.timeout:
                print("Timeout occurred while waiting for data. Retrying...")
                continue

    def corrupt_packet(self, packet_data):
        # Randomly corrupt a byte in the packet data
        index = random.randint(0, len(packet_data) - 1)
        byte_value = random.randint(0, 255)
        corrupted_data = bytearray(packet_data)
        corrupted_data[index] = byte_value
        return bytes(corrupted_data)

    def close_connection_client(self, dest_address):
        # Send FIN packet
        fin_packet = Packet(
            self.next_seq_number, self.expected_seq_num, "", flags=0b0010000
        )  # FIN flag set
        fin_packed = fin_packet.pack()
        self.socket.sendto(fin_packed, dest_address)

        # Wait for FIN-ACK packet
        while True:
            try:
                response, _ = self.socket.recvfrom(1024)
                fin_ack_packet = Packet.unpack(response)
                if fin_ack_packet.flags & 0b0100000:  # Check if ACK flag is set
                    self.next_seq_number += 1
                    self.expected_seq_num += 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for FIN-ACK packet. Retrying...")

        # Send ACK for FIN-ACK packet
        ack_packet = Packet(
            self.next_seq_number, fin_ack_packet.seq_num + 1, "", flags=0b0100000
        )  # ACK flag set
        ack_packed = ack_packet.pack()
        self.socket.sendto(ack_packed, dest_address)

        print("Connection closed successfully.")

    def close_connection_server(self):
        # Wait for FIN packet
        while True:
            try:
                fin_packet_data, sender_address = self.socket.recvfrom(1024)
                fin_packet = Packet.unpack(fin_packet_data)
                if fin_packet.flags & 0b0010000:  # Check if FIN flag is set
                    self.next_seq_number = fin_packet.seq_num + 1
                    self.expected_seq_num = fin_packet.seq_num + 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for FIN packet. Retrying...")

        # Send FIN-ACK packet
        fin_ack_packet = Packet(
            self.next_seq_number, fin_packet.seq_num + 1, "", flags=0b0100000
        )  # FIN-ACK flags set
        fin_ack_packed = fin_ack_packet.pack()
        self.socket.sendto(fin_ack_packed, sender_address)

        print("Connection closed successfully.")
