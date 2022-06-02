import sys
import socket

def main():
    #port filename probability
    port = int(sys.argv[1].strip())  
    filename = sys.argv[2].strip()
    window_size = int(sys.argv[3].strip()) 

    buffer = {}
    reciever_base = 1

    try:
        file = open(filename, 'wb')
    except IOError:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))

    while True:
        pkt, addr = sock.recvfrom(1027) 
        seq_num, eof, data = pkt[0:2], pkt[2:3], pkt[3:]
        seq_num = int.from_bytes(seq_num, 'big')
        eof = int.from_bytes(eof, 'big')

        if not pkt:
            break

        if seq_num >= reciever_base and seq_num <= reciever_base+window_size-1:

            if seq_num != reciever_base:
                buffer[seq_num] = eof, data

            else:
                file.write(data)
                to_send = reciever_base.to_bytes(2, 'big')
                sock.sendto(to_send, addr)
                reciever_base+=1
                while len(buffer) != 0:
                    for key,val in buffer.items():
                        to_send = key.to_bytes(2, 'big')
                        file.write(val[1])
                        sock.sendto(to_send, addr)
                        reciever_base+=1
                        del buffer[key]

        if seq_num >= reciever_base-window_size and seq_num <= reciever_base-1:
            file.write(data)
            sock.sendto(to_send, addr)

    file.close()
    sock.close()
                
if __name__ == '__main__':
    main()
