#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii

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
			"BBHHh", icmpHeader
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

def doOnePing(destinationAddress, timeout):
	# 1. Create ICMP socket
	icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname("icmp"))
	ID = os.getpid() & 0xFFFF
	# 2. Call sendOnePing function
	timeStart = sendOnePing(icmpSocket, destinationAddress, ID)
	# 3. Call receiveOnePing function
	delay = receiveOnePing(icmpSocket, destinationAddress, ID, timeout, timeStart)
	# 4. Close ICMP socket
	icmpSocket.close()
	# 5. Return total network delay
	return delay

def ping(host, timeout=1):
	loop = 0  # set to 0 to run a preset amount of times (amount)
	amount = 3  # Number of times to ping
	destinationAddress = socket.gethostbyname(host)  # Get IP from hostname
	minDelay = 999999  # minimum delay
	maxDelay = 0  # maximum delay
	totalDelay = 0  # total overall delay
	avgDelay = 0  # average delay
	x = 0  # run count
	print ("Pinging %s [%s]" % (host, destinationAddress))
	if loop == 1:  # If set to indefinite loop
		while True:
			delay = doOnePing(destinationAddress, timeout)
			delay = delay * 1000  # convert delay from seconds to milliseconds
			print ("Reply from %s: delay = %0.4fms" % (destinationAddress, delay))
			time.sleep(1)  # wait one second
	if loop == 0:  # If set to loop for a set amount
		while(x<amount):
			x = x+1
			delay = doOnePing(destinationAddress, timeout)
			delay = delay * 1000  # convert delay from seconds to milliseconds
			print ("Reply from %s: delay = %0.4fms" % (destinationAddress, delay))
			if(delay<minDelay):  # If current delay is smaller than min delay
				minDelay = delay  # set min delay
			if(delay>maxDelay):  # If current delay is larger than max delay
				maxDelay = delay  # Set max delay
			totalDelay = totalDelay + delay  # Add current delay to total
			time.sleep(1)  # wait one second

	avgDelay = totalDelay/x  # Calculate average
	print("Minimum = %0.4fms, Maximum = %0.4fms, Average = %0.4fms" % (minDelay, maxDelay, avgDelay))

ping("lancaster.ac.uk")