import sys
import time

from src import *

TARGET_HOST_IP = "172.17.0.2"
UDP_TARGET_PORT, UDP_SENDER_PORT = 20001, 20001
TCP_TARGET_PORT, TCP_SENDER_PORT = 65432, 65432

# Splits a file into chunks, yields the chunks respectively.
def chunk_file(filename, chunk_size):
    """
    :param filename: The path to the file to be chunked.
    :param chunk_size: The size of each chunk.
    """
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

# Sends the file data using the RDTOverUDP protocol.
def send_rdt_over_udp(filename, sender_port, target_host, target_port):
    """
    :param filename: Name of the file to be sent.
    :param sender_port: Port number for the UDP client.
    :param target_host: Target host address.
    :param target_port: Target port number.
    """
    data = chunk_file(filename, RDT_OVER_UDP_FILE_READ_SIZE)
    client = RDTOverUDPClient(sender_port, target_host, target_port, data)

    retransmission_count = client.process()
    print('UDP Transmission Re-transferred Packets:', retransmission_count)

# Sends the file data using the TCP protocol.
def send_tcp(filename, sender_port, target_host, target_port):
    """
    :param filename: Name of the file to be sent.
    :param sender_port: Port number for the TCP client.
    :param target_host: Target host address.
    :param target_port: Target port number.
    """
    data = chunk_file(filename, TCP_FILE_READ_SIZE)
    client = TCPClient(sender_port, target_host, target_port, data)

    client.process()

if __name__ == '__main__':
    time.sleep(1)  # Wait for RDTOverUDPServer to start
    send_rdt_over_udp('small-0.obj', UDP_SENDER_PORT, TARGET_HOST_IP, UDP_TARGET_PORT)

    time.sleep(1)  # Wait for TCPServer to start
    # send_tcp('transfer_file_TCP.txt', TCP_SENDER_PORT, TARGET_HOST_IP, TCP_TARGET_PORT)
