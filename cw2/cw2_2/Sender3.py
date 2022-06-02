# Abigail A Appah 1871633 
import socket 
import time
import os
import sys
import threading

stop_time_list = []
start_time_list = []
base = 1
next_to_send = 1
start = 0
last_time = -1
last_time = float(last_time)
threadLock = threading.Lock()

#  thread to recieve ack
class ACKRecievingThread(threading.Thread):
    def __init__(self, sock,packet_size):
        threading.Thread.__init__(self)
        self.sock = sock
        self.packet_size = packet_size
        self.acks = set([])
              
    def run(self):
        global base
        global next_to_send
        global start
        global stop_time_list

        try:
            while True:
            # while True:
                pkt_recv, _ = self.sock.recvfrom(2)
                ack = int.from_bytes(pkt_recv, 'big')

                # print("ACK Num recieved:"+' '+str(ack))

                # self.acks.add(ack)
              
               
                if base == self.packet_size+1 and ack == self.packet_size:
                    stop_time_list.append(time.time())
                    self.sock.close()
                    break
                
                threadLock.acquire()
                if base <= ack+1:
                    base = ack+1
               
                # print("base updated: ", base)
            
                threadLock.release()

                if base == next_to_send:
                    start =0
       
            # print(len(self.acks)) 
            self.sock.close()
        except:
            self.sock.close()

         
# thread to send ack
class SenderThread(threading.Thread):
    def __init__(self, sock, port, host,filename, retry_timeout, window_size):
        threading.Thread.__init__(self)
        self.sock = sock
        self.port = port
        self.host = host
        self.retry_timeout = retry_timeout
        self.filename = filename
        self.window_size = window_size


    def make_packet(self, seq, eof, packet):
        seq = seq.to_bytes(2, 'big')
        eof = eof.to_bytes(1, 'big')
        pkt = b"".join([seq, eof,packet])
        return pkt

    def get_packets(self):
        file = open(self.filename, 'rb')
        file_size = os.path.getsize(self.filename)
        total_bytes_read = 0
        packets = []
        pkts = ['']
        seq_num = 1
        eof = 0
        while True:
            data = file.read(1024)
            total_bytes_read += len(data)

            if not data:
                break
            else:
                if total_bytes_read < file_size:
                    eof = 0
                else:
                    eof = 1
                packets.append(self.make_packet(seq_num, eof, data))
            seq_num += 1
        
        pkts.extend(packets)

        file.close()

        return pkts

    def run(self):

        # print("Sender is up and running")
        global next_to_send
        global base
        global start
        global last_time
        global start_time_list
      
        # Add all the packets to the buffer
        packets = self.get_packets()
        num_packets = len(packets)
        # converting timeout value from milliseconds to seconds
        timeout = self.retry_timeout*(10**-3)
        try:
            while True:
                threadLock.acquire() 
                # 
                if next_to_send < base+self.window_size and next_to_send<num_packets:
                # Send the packets in the window
                    # print('Sending packet', next_to_send)
                    self.sock.sendto(packets[next_to_send], (self.host, self.port))
                    start_time_list.append(time.time())
                    if(base == next_to_send):
                        # timer for a sent packet
                        last_time = time.time()
                        start=1
                    
                    next_to_send += 1
                 
                 
                if time.time()-last_time >= timeout and start==1:
                    # print("Timeout")
                    next_to_send = base
                    start=0

                threadLock.release()

                if base == num_packets:
                    break 
            # self.sock.sendto(b"",(self.host,self.port))         
            self.sock.close()
        except:
            self.sock.close()


def main():
    filename = sys.argv[3].strip()
    host = sys.argv[1].strip()
    port = int(sys.argv[2].strip())
    retry_timeout = int(sys.argv[4].strip())
    window_size = int(sys.argv[5].strip())
    size = os.path.getsize(filename)

    packet_size = (size // 1024) + 1

    sock_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock_s.bind((host,port))

    threads = []

    ackr = ACKRecievingThread(sock_s,packet_size)
    ackr.start()
    time.sleep(0.1)

    sender = SenderThread(sock_s, port, host,filename,retry_timeout,window_size)
    sender.start()

    threads.append(ackr)
    threads.append(sender)

    for t in threads:
        t.join()
 
    file_size_KB = size*(10**-3)

    transfer_time = stop_time_list[-1] - start_time_list[0]
    throughput = round(file_size_KB/transfer_time,2)
    # print(file_size_KB)
    print(throughput)
    # print("base: ", base)
    # print(window_size)
    # print(packet_size)
    # print(len(stop_time_list))
    # print(len(start_time_list))
  

    sock_s.close()

if __name__ == '__main__':
        main()
        sys.exit()
