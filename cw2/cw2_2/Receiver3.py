# Abigail A Appah 1871633 
import socket
import sys

# Receive packets from the sender
def receive(port, filename):
    # Open the file for writing

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('',port)) 

    try:
        file = open(filename, 'wb')
    except IOError:
        # print('Unable to open', filename)
        return
    
    expected_num = 1
    while True:
        # Get the next packet from the sender
        pkt, addr = sock.recvfrom(1027)

        # if not pkt:
        #     # print("I ma here")
        #     break

        seq_num, eof, data = pkt[0:2], pkt[2:3], pkt[3:]

        seq_num = int.from_bytes(seq_num, 'big')
        eof = int.from_bytes(eof, 'big')
     
        # print('Got packet', seq_num)

        # Send back an ACK
        if seq_num == expected_num:
            # print('Got expected packet')
            
            file.write(data)
            to_send = expected_num.to_bytes(2, 'big')
            i=0
            while i <20:
                sock.sendto(to_send, addr)
            # print('Sending ACK', expected_num)
                i+=1

            expected_num += 1
        
        else:
            # print('Sending ACK', expected_num - 1)
            pkt = (expected_num-1).to_bytes(2, 'big')
            j=0
            while j<10:
                sock.sendto(pkt, addr)
                j+=1

        if eof == 1:
            k=0
            while k<50:
                sock.sendto(seq_num.to_bytes(2,'big'), addr)
                # print('Sending ACK',seq_num)
                k+=1
            break

    file.close()
    sock.close()

# Main function
if __name__ == '__main__':

    filename = sys.argv[2].strip()
    port = int(sys.argv[1].strip())
    
    receive(port, filename)
 