from include import *

HOST = ''
TCP_PORT, UDP_PORT = 65432, 20001
TARGET_HOST_IP = "172.17.0.3"
UDP_TARGET_PORT, UDP_SENDER_PORT = 20001, 20001
TCP_TARGET_PORT, TCP_SENDER_PORT = 65432, 65432

def create_socket(host_ip, port_number):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.bind((host_ip, port_number))
    return connection

def pack_package(chunk):
    timestamp = get_timestamp()
    chunk_length = len(chunk)
    aligner_size = constants.TCP_MAX_CHUNK_SIZE - chunk_length
    return struct.pack(f'!dI{chunk_length}s{aligner_size}s', timestamp, chunk_length, chunk, b' ' * aligner_size)

# Sends the file data using the TCP protocol.
def send_file(conn, filename):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(TCP_MAX_CHUNK_SIZE)
            if not chunk:
                break
            packed = pack_package(chunk)
            conn.sendall(packed)

# Handles the client connection to receive a file request and send the file.
def handle_client_connection(conn):
    request = conn.recv(1024).decode()  # Assuming the request is a simple file name
    # print(f"Client requested file: {request}")
    send_file(conn, request)
    conn.close()

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

# Calculates the average transmission time for each package and the total transmission time,
# returns a tuple containing the average time and total transmission time in milliseconds.
# Used for UDP.
def calculate_time(timestamps):
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

# Sends the file data using the UDP protocol.
def send_udp(filename, sender_port, target_host, target_port):
    """
    :param filename: Name of the file to be sent.
    :param sender_port: Port number for the UDP client.
    :param target_host: Target host address.
    :param target_port: Target port number.
    """
    data = chunk_file(filename, UDP_MAX_CHUNK_SIZE)
    server = UDPServer(sender_port, target_host, target_port, data) 

    retransmission_count = server.process()
    print('UDP Transmission Re-transferred Packets:', retransmission_count)

def listen_for_requests(udp_socket):
    while True:
        data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes for req message
        if data.decode()[:7] == "REQUEST":
            return addr, data.decode()[7:]
        

def main():

    ### Running TCP Server ###
    # server = create_socket(HOST, TCP_PORT)
    # server.listen()

    # while True:
    #     conn, addr = server.accept()
    #     # print(f"Connected to {addr}, waiting for file request...")
    #     handle_client_connection(conn)

    ### Running UDP Server ###
    udp_socket = create_udp_socket(HOST, UDP_PORT)
    # print("Server is waiting for client requests...")
    client_addr, name = listen_for_requests(udp_socket)
    # print(f"Received request from {client_addr}, sending files...")
  
    send_udp(name, UDP_SENDER_PORT, client_addr[0], UDP_TARGET_PORT)

if __name__ == "__main__":
    while True:
        main()