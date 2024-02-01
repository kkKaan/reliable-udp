from include import *

HOST = ''
TCP_PORT, UDP_PORT = 65432, 20001
TARGET_HOST_IP = "172.17.0.2"
UDP_TARGET_PORT, UDP_SENDER_PORT = 20001, 20001
TCP_TARGET_PORT, TCP_SENDER_PORT = 65432, 65432

def create_socket(host_ip, port_number):
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.bind((host_ip, port_number))
    return connection

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
    
def unpack_package(data):
    try:
        timestamp, chunk_length = struct.unpack('!dI', data[:constants.TCP_HEADER_BYTES])
        aligner_size = constants.TCP_MAX_CHUNK_SIZE - chunk_length
        chunk, _ = struct.unpack(f'!{chunk_length}s{aligner_size}s', data[constants.TCP_HEADER_BYTES:])
        return timestamp, chunk
    except:
        return None

# Requests a file from the server and saves it.
def request_file(host, port, filename):
    # client_socket = create_socket('', TCP_SENDER_PORT)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(filename.encode())

    timestamps = []

    with open('received_' + filename, 'wb') as file:
        while True:
            buffer = b''
            start_time = get_timestamp()
            while len(buffer) < MSS_VALUE:
                buffer_chunk = client_socket.recv(MSS_VALUE - len(buffer))
                if not buffer_chunk:
                    return  # No more data
                buffer += buffer_chunk

            _, chunk = unpack_package(buffer)
            timestamp_received = get_timestamp()
            timestamps.extend([start_time, timestamp_received])
            file.write(chunk)
            # timestamps.append(timestamp)

    client_socket.close() # Code never reaches here

# Starts an UDP file transmission server to receive a file.
def receive_udp(host, udp_port, output_filename):
    """
    :param host: The host IP address.
    :param udp_port: The UDP port number for the server.
    :param output_filename: The filename to save the received data.
    """
    timestamps = []

    with open(output_filename, 'wb') as result_file:
        client = UDPClient(host, udp_port)
        for package in client.process():
            timestamps.extend([package.timestamp_sent, package.timestamp_received])
            result_file.write(package.chunk)

    avg_time, total_time = calculate_time(timestamps)
    print('UDP Packets Average Transmission Time: {:.6f} ms'.format(avg_time))
    print('UDP Communication Total Transmission Time: {:.6f} ms'.format(total_time))
    with open('total_time.txt', 'a') as f:
        f.write(str(total_time) + '\n')

# Just sends a simple request with the name of the file to the server.
def send_request_to_server(server_ip, server_port, name):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(("REQUEST"+name).encode(), (server_ip, server_port))
    client_socket.close()

def main(index):

    ### TCP ###

    # start_time = get_timestamp()

    # for i in range(10):
    #     # print("Requesting " + str(i) + " file from server...")
    #     request_file(TARGET_HOST_IP, TCP_TARGET_PORT, 'large-' + str(i) + '.obj')
    #     request_file(TARGET_HOST_IP, TCP_TARGET_PORT, 'small-' + str(i) + '.obj')
    #     # print("File " + str(i) + " received from server.")

    # end_time = get_timestamp()
    # print("Total time: ", end_time - start_time)

    # with open('tcp_5cor.txt', 'a') as f:
    #     f.write(str(1000 * (end_time - start_time)) + '\n') # in ms

    ### UDP ###

    send_request_to_server(TARGET_HOST_IP, UDP_TARGET_PORT, 'large-'+str(index)+'.obj')
    print("Request sent to server, waiting to receive file...")
    receive_udp(HOST, UDP_PORT, 'udp_large-'+str(index)+'.obj')

    send_request_to_server(TARGET_HOST_IP, UDP_TARGET_PORT, 'small-'+str(index)+'.obj')
    print("Request sent to server, waiting to receive file...")
    receive_udp(HOST, UDP_PORT, 'udp_small-'+str(index)+'.obj')


if __name__ == "__main__":
    # TCP
    # for i in range(30):
    #     main(0)

    # UDP, will be run by run.sh for 30 tests
    for i in range(10):
        main(i)

