#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
#from socket import *
import sys

def handleRequest(data, tcpSocket, url):
    path = url.split("/")
    object_path = path[3]
    disk_file = open(object_path, 'r')
    buff = disk_file.read()
    return buff

def webProxy(conn, client_addr):
	# get the request from browser
    request = conn.recv(1024)

    # parse the first line
    first_line = request.split('\n')[0]

    # get url
    url = first_line.split(' ')[1]
 
    # find the webserver and port
    http_pos = url.find("://")          # find pos of ://
    if (http_pos==-1):
        temp = url
    else:
        temp = url[(http_pos+3):]       # get the rest of url
    
    port_pos = temp.find(":")           # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos==-1 or webserver_pos < port_pos):      # default port
        port = 8000
        webserver = temp[:webserver_pos]
    else:       # specific port
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]

    # create a socket to connect to the web server
    web_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
    web_socket.connect((webserver, port))
    web_socket.send(request)         # send request to webserver
        
    while True:
        data = handleRequest(request, web_socket, url)
        conn.send(data)
        break
    web_socket.close()
    

def startServer(serverAddress, serverPort):
	# 1. Create server socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# 2. Bind the server socket to server address and server port
	server_socket.bind((serverAddress, serverPort))
	# 3. Continuously listen for connections to server socket
	server_socket.listen(1)
	print("Awaiting connection")
	# 4. When a connection is accepted, call handleRequest function, passing new connection socket (see https://docs.python.org/2/library/socket.html#socket.socket.accept)
	while True:
		conn, address = server_socket.accept()  # accept new connection
		try:
			webProxy(conn, address)
		finally:
			# 5. Close server socket
			conn.close()


startServer("", 8000)

