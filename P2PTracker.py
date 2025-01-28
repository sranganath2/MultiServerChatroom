import socket
import argparse
import threading
import sys
import hashlib
import time
import logging
import collections
clients_list = []
NAME = "P2PTracker"
chunk_dict = collections.defaultdict(list) #keys = chunk index, value = [hash, (ip, port)]
check_list = []

logging.basicConfig(filename="logs.log", format="%(message)s", filemode="a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def listen(listen_socket):
	listen_socket.listen()
	while True:
		client, address = listen_socket.accept()
		threading.Thread(target=listenToClient, args=(client, address)).start()

def listenToClient(client, address):
	size = 9000
	while True:
		message = str(client.recv(size).decode("utf-8"))
		#x = message.split("\n")
		#for command in x:
		command = message
		p = command.split(",")[0]
		if p == "LOCAL_CHUNKS":
			recv_LOCAL_CHUNKS(command)
		elif p == "WHERE_CHUNK":
			recv_WHERE_CHUNK(client, command)

def recv_WHERE_CHUNK(client, recv_message):
	"""
	Send list of other clients that have the requested chunk
	:return:
	"""
	#first iteration of this assumed that recv would contain requests for multiple chunks at a time
	#for chunk in recv_message.split("\n"):
	p = recv_message.split(",")
	chunk_index = p[1]

	return_message = ""
	if chunk_index in chunk_dict:
		chunk_hash = chunk_dict[chunk_index][0][0]
		return_message = "GET_CHUNK_FROM," + chunk_index + "," + chunk_hash
		for entry in chunk_dict[chunk_index]:
			return_message += "," + entry[1] + "," + entry[2]
	else: #no clients with chunk
		return_message = "CHUNK_LOCATION_UNKNOWN," + chunk_index
	client.send(return_message.encode("utf-8"))
	logger.info("%s,%s", NAME, return_message)
	print("SENDING MSG: " + return_message)




def recv_LOCAL_CHUNKS(command):
	global clients_list

	#print(command)
	p = command.split(",")
	chunk_index = p[1]
	file_hash = p[2]
	chunk_ip = p[3]
	chunk_port = p[4]

	if (chunk_index, file_hash) in check_list:
		chunk_dict[chunk_index].append(( file_hash, chunk_ip, chunk_port))
		#multiple same file hashes

	else:
		#do we ever remove from this?
		check_list.append((chunk_index, file_hash))
	print("RECIVED :" + command)


	#print("LOCAL_CHUNKS")

def flush_print(msg):
	#print(msg)
	pass
	#sys.stdout.flush()




if __name__ == "__main__":
	port = 5100
	host = "127.0.0.1"
	passcode = "1234"
	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.bind((host, port))
	listen(listen_socket)