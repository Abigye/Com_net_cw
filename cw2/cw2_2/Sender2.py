# Abigail A Appah 1871633 
import sys  
from socket import *
import time
import os 


# For example: python3 Sender2.py localhost 54321 sfile 10

# time_list for start times 
l = []

stop_time = 0

filename = sys.argv[3].strip()
port = int(sys.argv[2].strip())
host = sys.argv[1].strip()
retry_timeout = int(sys.argv[4].strip())

def make_packet(seq, eof, packet):
    seq = seq.to_bytes(2, 'big')
    eof = eof.to_bytes(1, 'big')
    pkt = bytearray(seq)
    pkt.extend(bytearray(eof))
    pkt.extend(bytearray(packet))
    return pkt

eof = 0
addr = (host, port)
total_bytes = 0
retransmission = 0

# create dgram udp socket
try:
    sender_socket = socket(AF_INET, SOCK_DGRAM)
except socket.error:
    sys.exit()

# sender_socket.bind((host,port))
# setting time_out
sender_socket.settimeout(retry_timeout*(10**-3))

file = open(filename, 'rb')
file_size = os.path.getsize(filename)
total_bytes_read = 0
seq_num = 1
eof = 0

while True:
    data = file.read(1024)
    total_bytes_read += len(data)

    if total_bytes_read < file_size:
        eof = 0
    else:
        eof = 1

    
    pkt = make_packet(seq_num, eof, data)
    sender_socket.sendto(pkt, addr)
    start_time = time.time()
    l.append(start_time)
    
    ack_received = False

    while not ack_received:
        try:
            # receive data from receiver
            # print('send: GETTING ACK')
            reply, addr = sender_socket.recvfrom(2)
            ack = int.from_bytes(reply, 'big')
            # print("Got ack: ", ack)
        except timeout:
            # print('send: TIMEOUT')
            # print("retransmitting packet: ", str(seq_num))
            sender_socket.sendto(pkt, addr)
            retransmission += 1
            # print("number of retransmissions: ", str(retransmission))

        else:
            # print('Checking for ACK ' + str(seq_num))
            if ack == seq_num:
                ack_received = True
                # gives the stop time for each ack received 
                stop_time = time.time() 
                break



    # print('ACK FOUND, CHANGING SEQ')

    if total_bytes_read == file_size:
        # print("total bytes sent", str(total_bytes_read))
        break

    seq_num += 1


file_len_KB = file_size*(10**-3)

# l[0] = time for first packet transmission 
transfer_time = stop_time - l[0]

throughput = round(file_len_KB/transfer_time,2)

# print(file_size)

# print("no of retransmissions: ", str(retransmission))

# print("stop_time :", stop_time)

# print("transfer time: ", str(transfer_time))

# print("throughput: ", str(throughput))


print('{0} {1} '.format(retransmission,throughput))

file.close()
sender_socket.close()




