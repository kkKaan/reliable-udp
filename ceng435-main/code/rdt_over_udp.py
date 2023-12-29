import socket
import struct
from collections import deque

from . import utils, constants

WINDOW_SIZE = 100

STATE_WAITING = 0
STATE_SENT = 1
STATE_RECEIVED = 2
STATE_ACKED = 3

# A basic function to create and bind sockets
def create_socket(host_ip, port_number):
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    connection.bind((host_ip, port_number))
    return connection

def pack_send_package(seq_no, chunk):
    timestamp = utils.get_timestamp()

    chunk_length = len(chunk)
    checksum = utils.get_checksum(bytes(str(seq_no), 'utf8') + bytes(str(timestamp), 'utf8') + \
            bytes(str(chunk_length), 'utf8') + chunk)

    align_size = constants.RDT_OVER_UDP_FILE_READ_SIZE - chunk_length

    return struct.pack(f'!Id16sI{chunk_length}s{align_size}s', seq_no, timestamp, \
                            checksum, chunk_length, chunk, b' ' * align_size)

def unpack_send_package(data):
    try:
        # Unpack the header to get sequence number, timestamp, checksum, and chunk length
        header_format = '!Id16sI'  # format: sequence number, timestamp, checksum, chunk length
        header_size = constants.RDT_OVER_UDP_SEND_HEADER_SIZE
        seq, timestamp, checksum, chunk_length = struct.unpack(header_format, data[:header_size])

        # Calculate alignment size
        align_size = constants.RDT_OVER_UDP_FILE_READ_SIZE - chunk_length

        # Unpack the chunk data
        chunk_format = f'!{chunk_length}s{align_size}s'  # format for chunk and alignment
        chunk, _ = struct.unpack(chunk_format, data[header_size:])

        # Verify checksum
        checksum_data = bytes(str(seq), 'utf8') + bytes(str(timestamp), 'utf8') + \
                        bytes(str(chunk_length), 'utf8') + chunk
        if not utils.check_checksum(checksum, checksum_data):
            return seq, timestamp, None  # Invalid checksum, return None for chunk

        return seq, timestamp, chunk

    except struct.error:
        # Handle unpacking error (e.g., corrupted data)
        return None
    except Exception as e:
        # General exception handling
        print(f"Error unpacking package: {e}")
        return None


def pack_ack_package(seq):
    timestamp = utils.get_timestamp()
    return struct.pack('!Id', seq, timestamp)

def unpack_ack_package(data):
    try:
        return struct.unpack('!Id', data)
    except KeyboardInterrupt as e: # These line is required to stop the code in case of a KeyboardInterrupt.
        raise e
    except:
        return None

# The PackageData class encapsulates the information about each data packet used in the RDT protocol.
class PackageData:
    # Constructor for initializing a PackageData. 
    def __init__(self, seq_no, chunk=None):
        """
        :param seq_no: The sequence number of the packet. It's used to uniquely identify and order packets in the protocol.
        :param chunk: The actual data that the packet is carrying. This can be any serializable data.
        """
        self.seq_no = seq_no % 10000  # Reset sequence number every 10000 packets to avoid overflow
        self.chunk = chunk
        self.state = STATE_WAITING  # Initial state is 'waiting' indicating the packet is yet to be processed

    # Marks the packet as sent by setting its state and recording the timestamp when it was sent.
    def mark_as_sent(self):
        self.timestamp_sent = utils.get_timestamp()  # Record the time of sending
        self.state = STATE_SENT  # Update the state to 'sent'

    # Marks the packet as acknowledged (ACKed) by changing its state.
    def mark_as_acked(self):
        self.state = STATE_ACKED  # Update the state to 'acknowledged'

    # Marks the packet as received by setting its state and updating the timestamps.
    def mark_as_received(self, timestamp_sent, chunk):
        """
        :param timestamp_sent: The timestamp when the packet was originally sent.
        :param chunk: The chunk of data received.
        """
        self.chunk = chunk
        self.timestamp_sent = timestamp_sent  # Record the original sending time
        self.timestamp_received = utils.get_timestamp()  # Record the time of reception
        self.state = STATE_RECEIVED  # Update the state to 'received'

    ### may be deleted ### 
    # String representation of the PackageData object, typically used for logging and debugging.
    def __str__(self):
        return f'Seq No: {self.seq_no}, State: {self.state}'

    # Official string representation of the PackageData object. 
    def __repr__(self):
        return self.__str__()
    ######################


class RDTOverUDPServer:
    # Initialize the RDT server with a host IP and port number.
    def __init__(self, listen_host_ip, listen_port_no):
        """
        :param listen_host_ip: IP address on which the server listens.
        :param listen_port_no: Port number on which the server listens.
        """
        self.listen_host = listen_host_ip
        self.listen_port = listen_port_no

        # Window for storing package data
        self.window = deque()

        # Flag to indicate if the transmission has finished
        self.has_finished = False

        # Initialize the window with PackageData instances
        for i in range(WINDOW_SIZE):
            package_data = PackageData(i)
            self.window.append(package_data)

    # Send an acknowledgment (ACK) for a received packet.
    def send_ack(self, address, seq_no):
        """
        :param address: Address to which the ACK is sent.
        :param seq_no: Sequence number of the packet being acknowledged.
        """
        packed = pack_ack_package(seq_no)  # Pack the ACK packet
        self.socket.sendto(packed, address)  # Send the ACK packet

    # Mark the packet as received based on its sequence number.
    def mark_package_data_as_received_by_seq(self, seq_no, timestamp, chunk):
        """
        :param seq_no: Sequence number of the received packet.
        :param timestamp: Timestamp when the packet was sent.
        :param chunk: The data chunk of the packet.
        """
        for package_data in self.window:
            if package_data.seq_no == seq_no and package_data.state == STATE_WAITING:
                package_data.mark_as_received(timestamp, chunk)
                break

    # The main processing loop of the server.
    def process(self):
        # Create and configure the server socket
        self.socket = create_socket(self.listen_host, self.listen_port)
        self.socket.settimeout(20.0)  # Set a timeout for the socket operations

        while len(self.window) > 0:
            try:
                # Receive a packet from the socket
                packed, address = self.socket.recvfrom(constants.PACKAGE_SIZE)
            except socket.timeout:
                break  # Break the loop if a timeout occurs

            if packed and len(packed) == constants.PACKAGE_SIZE:
                result = unpack_send_package(packed)  # Unpack the received package

                if result:
                    seq_no, timestamp, chunk = result

                    # Check if it's the last packet (indicated by a zero-length chunk)
                    if chunk is not None and len(chunk) == 0:
                        # Send multiple ACKs for the last packet
                        for _ in range(5):
                            self.send_ack(address, seq_no)

                        # Clear remaining packages as the transmission has ended
                        while len(self.window) > 0 and self.window[-1].seq_no != seq_no:
                            self.window.pop()

                        self.window.pop()
                        self.has_finished = True
                    elif chunk:
                        # Send ACK for the received packet
                        self.send_ack(address, seq_no)

                        # Mark the packet as received
                        self.mark_package_data_as_received_by_seq(seq_no, timestamp, chunk)

                        # Process and remove received packets from the window
                        while len(self.window) > 0:
                            if self.window[0].state != STATE_RECEIVED:
                                break

                            yield self.window[0]

                            new_sequential_number = self.window[-1].seq_no + 1
                            self.window.popleft()

                            # Add new package data if more packets are expected
                            if not self.has_finished:
                                new_package_data = PackageData(new_sequential_number)
                                self.window.append(new_package_data)

        # Close the socket at the end
        self.socket.close()

class RDTOverUDPClient:
    def __init__(self, sender_port, target_host, target_port, data):
        self.sender_port = sender_port
        self.target = (target_host, target_port)

        self.data = data
        self.retransmission_count = 0

        self.window = deque() # The sender window
        self.fill_window() # The function that fills the sender window

    def next_seq(self):
        if len(self.window) > 0: return self.window[-1].seq_no + 1
        return 0

    def fill_window(self):
        while len(self.window) < WINDOW_SIZE:
            try:
                chunk = next(self.data) # Fetch the next chunk from the generator
                package_data = PackageData(self.next_seq(), chunk)
                self.window.append(package_data)
            except StopIteration: # The generator raises an error in the end
                break

    def send_package_data(self, package_data):
        packed = pack_send_package(package_data.seq_no, package_data.chunk)
        self.socket.sendto(packed, self.target)

        # If the sent package data has already been sent, then
        # increase the retransmission count by one.
        if package_data.state == STATE_SENT:
            self.retransmission_count += 1

        # Mark the package_data as sent and update the `timestamp_sent` timestamp.
        package_data.mark_as_sent()

    def mark_package_data_acked_by_seq(self, seq_no):
        for package_data in self.window:
            if package_data.seq_no == seq_no:
                package_data.mark_as_acked()
                break

    def process(self):
        self.socket = create_socket('', self.sender_port) # Create a UDP socket
        # Set the timeout of the socket with RETRANSMISSION_TIMEOUT timeout
        self.socket.settimeout(constants.RETRANSMISSION_TIMEOUT)

        # If the window size not zero, i.e. there are still package_data's must be
        # sent, send every package that in waiting state (not sent before) and wait
        # for incoming packages.
        while len(self.window) > 0:
            for package_data in self.window:
                if package_data.state == STATE_WAITING:
                    self.send_package_data(package_data)
                    break

            self.wait()

        # Since the window size is zero, there are no package_data's must be send,
        # and all package_data's sent are ACK-ed by the server, the socket can be closed.
        self.socket.close()

        # Return the retransmission count
        return self.retransmission_count

    def must_wait(self):
        for package_data in self.window:
            if package_data.state == STATE_SENT:
                return True

        return False

    def wait(self):
        while self.must_wait(): # If the code must wait.
            try:
                # RDT_OVER_UDP_ACK_PACKAGE_SIZE is the size of the ACK package which is
                # defined in constants.py.
                packed, _ = self.socket.recvfrom(constants.RDT_OVER_UDP_ACK_PACKAGE_SIZE)

                # If the packed data is not none
                if packed is not None:
                    result = unpack_ack_package(packed)

                    # If the result unpacked data is not none, that means no unpacking
                    # error occurred.
                    if result is not None:
                        # Fetch the sequential number from the result tuple
                        # and send a ACK message
                        seq, _ = result

                        self.mark_package_data_acked_by_seq(seq)

            # The code waited enough for receiving an ACK message, either the ACK messages take
            # too long to come, or some SEND or ACK messages have been lost or corrupted.
            except socket.timeout:
                pass

            # Calculate threshold_timestamp, the first time that the package_data's must resend.
            threshold_timestamp = utils.get_timestamp() - constants.RETRANSMISSION_TIMEOUT

            # Check every package_data in the sender window, if their timestamp_sent are below
            # the threshold, resend them.
            for package_data in self.window:
                if package_data.state == STATE_SENT and package_data.timestamp_sent < threshold_timestamp:
                    self.send_package_data(package_data)

            # Remove the first packages from the window has already been ACK-ed,
            # and refill the sender window.
            while len(self.window) > 0:
                if self.window[0].state == STATE_ACKED:
                    self.window.popleft()
                else:
                    break

            self.fill_window()
