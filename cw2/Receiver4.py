import sys
import socket
import struct
import random
import threading


def parseMsg(msg):  # Parsing the Message received from client
	header = msg[0:8]
	data = msg[8:]
	sequenceNum = struct.unpack('=I', header[0:4])
	checksum = struct.unpack('=H', header[4:6])
	identifier = struct.unpack('=H', header[6:])
	dataDecoded = data.decode('UTF-8')
	return sequenceNum, checksum, identifier, dataDecoded


def formAckPackets(seqAcked, type):
	seqNum = struct.pack('=I', seqAcked)  # SEQUENCE NUMBER BEING ACKED
	if type == 0:
		zero16 = struct.pack('=H', 0)
	else:
		zero16 = struct.pack('=H', 1)
	# ACK INDICATOR - 1010101010101010[INT 43690]
	ackIndicator = struct.pack('=H', 43690)
	ackPacket = seqNum+zero16+ackIndicator
	return ackPacket


def main():
	#port filename probability

	port = int(sys.argv[1])  # PORT ON WHICH SERVER WILL ACCEPT UDP PACKETS
	filename = sys.argv[2]  # NAME OF THE NEW FILE CREATED
	prob = float(sys.argv[3])  # PACKET DROP PROBABILITY
	buffer = {}
	flag = True
	maxSeqNum = 0

	soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	host = socket.gethostname()
	soc.bind((host, port))

	while flag or len(buffer) < maxSeqNum:
		receivedMsg, sender_addr = soc.recvfrom(
			1024)  # Receive packets sent by client
		sequenceNum, checksum, identifier, data = parseMsg(receivedMsg)
		if int(sequenceNum[0]) not in buffer:
			if random.uniform(0, 1) > prob:  # PACKET MAY BE DROPPED BASED ON RANDOM VALUE
				chksumVerification = verifyChecksum(data, int(checksum[0]))
				if chksumVerification == True:
					if data != '00000end11111':  # If not the END Packet
						buffer[int(sequenceNum[0])] = data
					else:
						flag = False
						maxSeqNum = int(sequenceNum[0])
						#print('ACKED:'+str(sequenceNum[0]))
					ackPacket = formAckPackets(
						int(sequenceNum[0]), 0)  # Generating ACK Packet
					soc.sendto(ackPacket, sender_addr)  # Sending ACK
			else:
				# Packet dropped if randomValue <= probability
				print('PACKET LOSS, SEQUENCE NUMBER = '+str(sequenceNum[0]))

	ackPacket = formAckPackets(maxSeqNum+1, 1)
	soc.sendto(ackPacket, sender_addr)
	#print('Termination Initiated')
	fileHandler = open(filename, 'a')
	for i in range(0, maxSeqNum):
		fileHandler.write(buffer[i])
	fileHandler.close()
	print('File Received Successfully at the Server')
	soc.close()


if __name__ == '__main__':
	main()
