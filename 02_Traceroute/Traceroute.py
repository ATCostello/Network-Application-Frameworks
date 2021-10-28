#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii
import os
import re
import sys
import struct
import socket

ICMP_ECHO_REQUEST = 8 #ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0 #ICMP type code for echo reply messages

def checksum(string):
	csum = 0
	countTo = (len(string) // 2) * 2
	count = 0

	while count < countTo:
		thisVal = ord(string[count+1]) * 256 + ord(string[count])
		csum = csum + thisVal
		csum = csum & 0xffffffff
		count = count + 2

	if countTo < len(string):
		csum = csum + ord(string[len(string) - 1])
		csum = csum & 0xffffffff

	csum = (csum >> 16) + (csum & 0xffff)
	csum = csum + (csum >> 16)
	answer = ~csum
	answer = answer & 0xffff
	answer = answer >> 8 | (answer << 8 & 0xff00)

	if sys.platform == 'darwin':
		answer = socket.htons(answer) & 0xffff
	else:
		answer = socket.htons(answer)

	return answer

def receiveOnePing(icmpSocket, destinationAddress, ID, timeout, timeSent):
	# 1. Wait for the socket to receive a reply
	while True:  # Loop until ping received
		waiting = select.select([icmpSocket], [], [], timeout)  # Looks at read port until something is sent
		# 2. Once received, record time of receipt, otherwise, handle a timeout
		if waiting[0] == []:  # If no packets are sent, timeout
			return
		timeReceived = time.time()  # Once packets received, record time
		# 3. Compare the time of receipt to time of sending, producing the total network delay
		# 4. Unpack the packet header for useful information, including the ID
		receivedPacket, address = icmpSocket.recvfrom(1024)  # Receive the information packet
		icmpHeader = receivedPacket[20:28]  # Set icmpHeader as received packet header
		receivedType, receivedCode, receivedChecksum, receivedID, sequence = struct.unpack(  # Unpack header to variables for access
			"BBHHH", icmpHeader
		)
		# 5. Check that the ID matches between the request and reply
		if receivedType != 8 and receivedID == ID:
			# 6. Return total network delay
			return timeReceived - timeSent

def sendOnePing(icmpSocket, destinationAddress, ID):
	chksum = 0
	# 1. Build ICMP header
	icmpHeader = struct.pack("BBHHH", ICMP_ECHO_REQUEST, 0, chksum, ID, 1)
	# 2. Checksum ICMP packet using given function
	chksum = checksum(icmpHeader)
	# 3. Insert checksum into packet
	icmpHeader = struct.pack(
		"BBHHH", ICMP_ECHO_REQUEST, 0, chksum, ID, 1
	)
	packet = icmpHeader
	# 4. Send packet using socket
	icmpSocket.sendto(packet, (destinationAddress, 1))
	# 5. Record time of sending
	return time.time()

def doOnePing(destinationAddress, timeout, ttl):
	# 1. Create ICMP socket
	icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	icmpSocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
	ID = os.getpid() & 0xFFFF
	# 2. Call sendOnePing function
	timeStart = sendOnePing(icmpSocket, destinationAddress, ID)
	# 3. Call receiveOnePing function
	delay = receiveOnePing(icmpSocket, destinationAddress, ID, timeout, timeStart)
	# 4. Close ICMP socket
	icmpSocket.close()
	# 5. Return total network delay
	return delay

def usage():
	print '''Usage: %s host port
Tries to connect to host at TCP port with increasing TTL (Time to live).
If /etc/services exists (on most Unix systems), you can give the protocol
name for the port. Example 'ssh' instead of 22.
''' % os.path.basename(sys.argv[0])

def test():
	if not len(sys.argv)==3:
		usage()
		sys.exit(1)
	ttl=1
	host, port = sys.argv[1:]
	port_int=None
	try:
		port_int=int(port)
	except ValueError:
		if not os.path.exists('/etc/services'):
			print 'port needs to be an integer if /etc/services does not exist.'
			sys.exit(1)
		fd=open('/etc/services')
		for line in fd:
			match = re.match(r'^%s\s+(\d+)/tcp.*$' % port, line)
			if match:
				port_int=int(match.group(1))
				break
		if not port_int:
			print 'port %s not in /etc/services' % port
			sys.exit(1)
	port=port_int
	for ttl in range(1, 30):
		s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
		s.settimeout(2)
		try:
			try:
				s.connect((host, port))
			except (socket.error, socket.timeout), err:
				print 'ttl=%02d: %s' % (ttl, err)
				continue
			except KeyboardInterrupt:
				print 'ttl=%02d (KeyboardInterrupt)' % ttl
				break
		finally:
			s.close()
		print 'ttl=%02d: OK' % (ttl)
		break

def traceroute(host):
	maxhops = 30
	ttl = 1
	destinationAddress = socket.gethostbyname(host)
	print("Tracing route to %s [%s}" %(host, destinationAddress))
	print("over a maximum of %d hops" %maxhops)
	test()
	#doOnePing(destinationAddress, 1, ttl)
	# DO THE STUFF

traceroute("lancaster.ac.uk")