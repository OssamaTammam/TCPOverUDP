from Packet import Packet


def main():
    # Create a sample packet
    seq_num = 1
    ack_num = 2
    flags = 0b0000000
    data = "Sample data"
    packet = Packet(seq_num, ack_num, data)

    # Pack the packet
    packed_packet = packet.pack()

    # Unpack the packet
    unpacked_packet = Packet.unpack(packed_packet)

    # Verify checksum
    checksum_verified = unpacked_packet.verify_checksum()

    print("Original Packet:", packet.__dict__)
    print("Packed Packet:", packed_packet)
    print("Unpacked Packet:", unpacked_packet.__dict__)
    print("Checksum Verified:", checksum_verified)


if __name__ == "__main__":
    main()
