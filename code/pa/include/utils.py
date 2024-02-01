import hashlib

def get_checksum(data):
    return hashlib.md5(data).digest()

def check_checksum(checksum, data):
    return checksum == get_checksum(data)
