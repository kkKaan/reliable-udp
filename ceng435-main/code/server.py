import sys
from src import *

HOST = '0.0.0.0'
TCP_PORT, UDP_PORT = 65432, 20001

# Calculates the average transmission time for each package and the total transmission time,
# returns a tuple containing the average time and total transmission time in milliseconds.
def calculate_avg_and_total_time(timestamps):
    """
    :param timestamps: A list of timestamps representing sent and received times of packages.
    """
    if not timestamps:
        return 0, 0  # Return 0 if there are no timestamps

    total_time = (timestamps[-1] - timestamps[0]) * 1000  # Total time in milliseconds

    # Calculate differences between sent and received times
    time_diffs = [abs(timestamps[i + 1] - timestamps[i]) * 1000 for i in range(0, len(timestamps), 2)]
    avg_time = sum(time_diffs) / len(time_diffs)  # Average time in milliseconds

    return avg_time, total_time

# Starts an RDTOverUDP file transmission server to receive a file.
def receive_rdt_over_udp(host, udp_port, output_filename):
    """
    :param host: The host IP address.
    :param udp_port: The UDP port number for the server.
    :param output_filename: The filename to save the received data.
    """
    timestamps = []

    with open(output_filename, 'wb') as result_file:
        server = RDTOverUDPServer(host, udp_port)
        for package in server.process():
            timestamps.extend([package.timestamp_sent, package.timestamp_received])
            result_file.write(package.chunk)

    avg_time, total_time = calculate_avg_and_total_time(timestamps)
    print('UDP Packets Average Transmission Time: {:.6f} ms'.format(avg_time))
    print('UDP Communication Total Transmission Time: {:.6f} ms'.format(total_time))

# Starts a TCP file transmission server to receive a file.
def receive_tcp(host, tcp_port, output_filename):
    """
    :param host: The host IP address.
    :param tcp_port: The TCP port number for the server.
    :param output_filename: The filename to save the received data.
    """
    timestamps = []

    with open(output_filename, 'wb') as result_file:
        server = TCPServer(host, tcp_port)
        for timestamp_sent, timestamp_received, chunk in server.process():
            timestamps.extend([timestamp_sent, timestamp_received])
            result_file.write(chunk)

    avg_time, total_time = calculate_avg_and_total_time(timestamps)
    print('TCP Packets Average Transmission Time: {:.6f} ms'.format(avg_time))
    print('TCP Communication Total Transmission Time: {:.6f} ms'.format(total_time))

if __name__ == '__main__':
    receive_rdt_over_udp(HOST, UDP_PORT, 'transfer_file_UDP.txt')
    # receive_tcp(HOST, TCP_PORT, 'transfer_file_TCP.txt')

