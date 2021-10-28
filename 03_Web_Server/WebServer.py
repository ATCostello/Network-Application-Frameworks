#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
#from socket import *
import sys

def handleRequest(tcpSocket):
	# 1. Receive request message from the client on connection socket
	data = tcpSocket.recv(1024)
	# 2. Extract the path of the requested object from the message (second part of the HTTP header)
	first_line = data.split('\n')[0]
	url = first_line.split(' ')[1]
	if(".html" in url):
		object_path = url
		object_path = "." + object_path
	# 3. Read the corresponding file from disk
		disk_file = open(object_path, 'r')
	# 4. Store in temporary buffer
		buff = disk_file.read()
	# 5. Send the correct HTTP response error

	# 6. Send the content of the file to the socket
		tcpSocket.sendall(buff)
	# 7. Close the connection socket
	tcpSocket.close()

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 2. Bind the server socket to server address and server port
	server_socket.bind((serverAddress, serverPort))
	# 3. Continuously listen for connections to server socket
	server_socket.listen(1)
	print("Waiting for connection")
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
	while True:
		conn, address = server_socket.accept()  # accept new connection
		try:
			print("Request Received")
			handleRequest(conn)
		finally:
			# 5. Close server socket
			conn.close()


startServer("", 8000)

