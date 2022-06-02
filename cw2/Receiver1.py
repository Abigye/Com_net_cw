# Abigail A Appah 1817633
from socket import *
import sys 

port = sys.argv[1].strip()
file_to_write = sys.argv[2].strip()

rec_add = ('',int(port))

try:
   receiver_socket = socket(AF_INET, SOCK_DGRAM)
except socket.error:
    sys.exit()

receiver_socket.bind(rec_add)

with open(file_to_write,'wb') as f:

    # print("Waiting to receive messages...")
    while True:
        data, sender_address = receiver_socket.recvfrom(1027)
     
        seq, eof, actual_data = data[0:2], data[2:3], data[3:]

        f.write(actual_data)

        # print("sequence no .....: ", str(int.from_bytes(seq, 'big')))


        if int.from_bytes(eof,'big') == 1:
            break
        
         
receiver_socket.close()







    
