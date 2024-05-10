import socket
from Packet import Packet


class TCP:
    def __init__(self, host, port):
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.address)
        self.socket.settimeout(5)
        self.next_seq_number = 0
        self.expected_seq_num = 0
        self.handshake_succeeded = False

    def initiate_handshake(self, dest_address):
        # Send SYN packet
        syn_packet = Packet(
            self.next_seq_number, 0, "", flags=0b0000001
        )  # SYN flag set
        syn_packed = syn_packet.pack()
        self.socket.sendto(syn_packed, dest_address)

        # Wait for SYN-ACK packet
        while True:
            try:
                response, _ = self.socket.recvfrom(1024)
                syn_ack_packet = Packet.unpack(response)
                if syn_ack_packet.flags & 0b00000010:  # Check if SYN-ACK flag is set
                    self.next_seq_number = syn_ack_packet.seq_num + 1
                    self.expected_seq_num = syn_ack_packet.seq_num + 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for SYN-ACK packet. Retrying...")

        # Send ACK packet
        ack_packet = Packet(
            self.next_seq_number, syn_ack_packet.seq_num + 1, "", flags=0b0000010
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
                if syn_packet.flags & 0b00000001:  # Check if SYN flag is set
                    self.next_seq_number = syn_packet.seq_num + 1
                    self.expected_seq_num = syn_packet.seq_num + 1
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for SYN packet. Retrying...")

        # Send SYN-ACK packet
        syn_ack_packet = Packet(
            self.next_seq_number, syn_packet.seq_num + 1, "", flags=0b00000011
        )  # SYN-ACK flags set
        syn_ack_packed = syn_ack_packet.pack()
        self.socket.sendto(syn_ack_packed, sender_address)

        # Wait for ACK packet
        while True:
            try:
                ack_packet_data, _ = self.socket.recvfrom(1024)
                ack_packet = Packet.unpack(ack_packet_data)
                if ack_packet.flags & 0b00000010:  # Check if ACK flag is set
                    self.next_seq_number = ack_packet.ack_num
                    self.expected_seq_num = ack_packet.seq_num
                    self.handshake_succeeded = True
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for ACK packet. Retrying...")

        print("Handshake successful")

    def send(self, data, dest_address):
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

        # Wait for ACK
        while True:
            try:
                response, _ = self.socket.recvfrom(1024)
                ack_packet = Packet.unpack(response)

                # Check if ACK packet and expected sequence number
                if (
                    ack_packet.flags & 0b00000010
                    and ack_packet.ack_num == self.next_seq_number
                ):
                    self.next_seq_number += len(data)
                    break
            except socket.timeout:
                print("Timeout occurred while waiting for ACK packet. Retrying...")
                break

    def receive(self):
        while True:
            try:
                data, sender_address = self.socket.recvfrom(1024)
                recv_packet = Packet.unpack(data)

                # Check if expected sequence number
                if recv_packet.seq_num == self.expected_seq_num:
                    ack_packet = Packet(
                        self.next_seq_number,
                        self.expected_seq_num,
                        "",
                        flags=0b00000010,
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

                    return recv_packet.data
                else:
                    # Resend previous ACK
                    ack_packet = Packet(
                        self.next_seq_number,
                        self.expected_seq_num,
                        "",
                        flags=0b00000010,
                    )
                    ack_data = ack_packet.pack()

                    while True:
                        try:
                            self.socket.sendto(ack_data, sender_address)
                            break
                        except socket.error as e:
                            print(f"Error resending ACK packet: {e}")
                            continue

            except socket.timeout:
                print("Timeout occurred while waiting for data. Retrying...")
                continue
