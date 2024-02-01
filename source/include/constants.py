# Maximum Segment Size
MSS_VALUE = 8000

# The time to be waited before retransmitting
TIMEOUT = 0.008

# Size of sequence number in bytes
SEQUENCE_NUM_BYTES = 4

# Size in bytes for timestamp
TIMESTAMP_BYTES = 8

# Size of ACK packets in RDTOverUDP
ACK_PACKET_SIZE = TIMESTAMP_BYTES + SEQUENCE_NUM_BYTES

# Size in bytes for data length field
DATA_LENGTH_SIZE_BYTES = 4

# Header size for TCP based file transmission
TCP_HEADER_BYTES = TIMESTAMP_BYTES + DATA_LENGTH_SIZE_BYTES

# Maximum data size per chunk for TCP transmission
TCP_MAX_CHUNK_SIZE = MSS_VALUE - TCP_HEADER_BYTES

# Length of checksum string in bytes
CHECKSUM_LENGTH_BYTES = 16

# Header size for RDTOverUDP send packages
RDT_SEND_HEADER_SIZE = SEQUENCE_NUM_BYTES + TIMESTAMP_BYTES + CHECKSUM_LENGTH_BYTES + DATA_LENGTH_SIZE_BYTES

# Maximum data size per chunk for UDP transmission
UDP_MAX_CHUNK_SIZE = MSS_VALUE - RDT_SEND_HEADER_SIZE
