import struct
import hashlib


class Packet:
    MAX_DATA_LEN = 980  # Adjust based on your maximum data size
    MAX_CHECKSUM_LEN = 32  # Adjust based on your checksum size (e.g., MD5 hash length)

    FORMAT = f"!IIHH{MAX_DATA_LEN}s{MAX_CHECKSUM_LEN}s"

    def __init__(self, seq_num, ack_num, data, checksum=None, flags=0b0000000):
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.flags = flags
        # Consider adding a check here to ensure data length doesn't exceed MAX_DATA_LEN
        self.data = data[: self.MAX_DATA_LEN]  # Truncate data if exceeding limit
        self.checksum = checksum

    def pack(self):
        if self.checksum is None:
            self.checksum = self.calculate_checksum()

        encoded_data = self.data.encode("utf-8")
        encoded_checksum = self.checksum.encode("utf-8")
        data_len = len(encoded_data)

        # Pack the data into bytes according to the format string
        return struct.pack(
            Packet.FORMAT,
            self.seq_num,
            self.ack_num,
            self.flags,
            data_len,
            encoded_data,
            encoded_checksum,  # Encode checksum before packing
        )

    @classmethod
    def unpack(cls, packet):
        # Extract the fixed-length fields using unpack_from
        seq_num, ack_num, flags, data_len = struct.unpack_from("!IIHH", packet)

        data_offset = struct.calcsize("!IIHH")
        end_data = data_offset + data_len
        encoded_data = packet[data_offset:end_data]
        encoded_checksum = packet[992:]

        # Decode the data and checksum
        data = encoded_data.decode("utf-8")
        checksum = encoded_checksum.decode("utf-8")

        return cls(seq_num, ack_num, data, checksum, flags)

    def calculate_checksum(self):
        packet_content = f"{self.seq_num}{self.ack_num}{self.flags}{self.data}"
        return hashlib.md5(packet_content.encode()).hexdigest()

    def verify_checksum(self, sent_checksum):
        recalculated_checksum = self.calculate_checksum()
        return recalculated_checksum == sent_checksum
