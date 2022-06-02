# Abigail A Appah 1871633 
from socket import *
import sys
import os
import time

filename = sys.argv[3].strip()
port = sys.argv[2].strip()
hostname = sys.argv[1].strip()
addr = (hostname, int(port))


def make_packet(seq, eof, packet):
    seq = seq.to_bytes(2, 'big')
    eof = eof.to_bytes(1, 'big')
    pkt = bytearray(seq)
    pkt.extend(bytearray(eof))
    pkt.extend(bytearray(packet))
    return pkt


# create dgram udp socket
try:
    sender_socket = socket(AF_INET, SOCK_DGRAM)
except socket.error:
    sys.exit()
    

file = open(filename, 'rb')
file_size = os.path.getsize(filename)
total_bytes_read = 0
seq_num = 0
eof = 0

while True:
    data = file.read(1024)
    total_bytes_read += len(data)

    if total_bytes_read < file_size:
        eof = 0
    else:
        eof = 1

    sender_socket.sendto(make_packet(seq_num, eof, data), addr)
    time.sleep(0.001)

    if total_bytes_read == file_size:
        # print("total bytes sent", str(total_bytes_read))
        break

    seq_num += 1

file.close()
sender_socket.close()
