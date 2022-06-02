# Abigail A Appah 1871633 
import sys
from socket import *

# python3 Receiver2.py 54321 rfile

port = int(sys.argv[1].strip())
file_to_write = sys.argv[2].strip()


# create dgram udp socket
try:
    receiver_socket = socket(AF_INET, SOCK_DGRAM)
except socket.error:
    sys.exit()

receiver_socket.bind(('localhost', port))

expected_num = 1

with open(file_to_write, 'wb') as f:

    while True:
        # Get the next packet from the sender
        # print('receiving ...')
        pkt, addr = receiver_socket.recvfrom(1027)

        if not pkt:
            break

        seq_num, eof, data = pkt[0:2], pkt[2:3], pkt[3:]
        # print('Got packet', seq_num)

        seq_num = int.from_bytes(seq_num, 'big')
        eof = int.from_bytes(eof, 'big')

        # Send back an ACK
        if seq_num == expected_num:
            # print('Got expected packet')
            f.write(data)

            # print('Sending ACK', expected_num)

            pkt = expected_num.to_bytes(2, 'big')
            receiver_socket.sendto(pkt, addr)
            expected_num += 1

        else:
            # print('Not acknowledged or lost packet Sending ACK', expected_num - 1)
            last_sent_pkt = expected_num-1
            pkt = last_sent_pkt.to_bytes(2, 'big')
            receiver_socket.sendto(pkt, addr)

        if eof == 1:
            i = 0
            # sending last ack multiple times to sender
            while i < 5:
                receiver_socket.sendto(pkt, addr)
                i += 1
            break

receiver_socket.close()
