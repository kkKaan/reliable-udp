# Reliable UDP Project

## Overview
This project implements a reliable UDP (User Datagram Protocol) service in Python. The service aims to provide reliable data transmission over UDP, which is inherently unreliable. This is achieved by adding reliability mechanisms, selective repeat, similar to those in TCP (Transmission Control Protocol), such as error checking and data retransmission.

## Structure

- `__init__.py` - Initializes the Python package.
- `constants.py` - Defines constants used throughout the project.
- `reliable_udp.py` - Core module implementing reliable UDP features.
- `utils.py` - Utility functions supporting the main modules.
- `client.py` - Client-side script to send data using the reliable UDP service.
- `server.py` - Server-side script to receive data using the reliable UDP service.
- `sum_times.py` - Python script to sum total transmission times from outputs.
- `generateobjects.sh` - Generates object files for testing.

## Scripts

- `check_tcp.sh` - Verifies the integrity of files received over TCP by comparing them to reference files.
- `check_udp.sh` - Verifies the integrity of files received over UDP.
- `sum_times.py` - Aggregates the total time recorded in `total_time.txt`, logs to a `.txt` file for analysis.

## Running the Project

To run the reliable UDP service, execute the following steps:

1. **Prepare Object Files**: Use `generateobjects.sh` to create large and small object files for testing.
2. **Start the Server**: Run `server.py` to start listening for incoming data on a Docker container.
3. **Run the Client**: Execute `client.py` to send data to the server on another container.
4. **Validate Transmissions**:
   - Use `check_tcp.sh` to validate files received over TCP.
   - Use `check_udp.sh` to validate files received over UDP.
5. **Sum Times**: Execute `sum_times.py` to calculate the total time taken for the UDP transmission.

Make sure you have the necessary permissions to execute the shell scripts (`chmod +x *.sh`).


For more information, you can explore [here](https://github.com/cengwins/ceng435).
