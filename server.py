import socket
import threading
import sys 
import argparse
import time
import datetime
#TODO: Implement all code for your server here
# Use sys.stdout.flush() after print statemtents
#https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client

#main thread listens to new clients
#new thread is spawned for each client
#threads will communicate by reading from a queue that is filled with messages


clients_list = []

def listen(listen_socket):
	flush_print("Server started on port " + str(port) + ". Accepting connections")
	listen_socket.listen()
	while True:
		client, address = listen_socket.accept()
		threading.Thread(target=listenToClient, args=(client, address)).start()

def listenToClient(client, address):
	size = 1024
	big_string = str(client.recv(size).decode("utf-8")).split(" ")
	client_username = big_string[0]
	client_passcode = big_string[1]
	if client_passcode == passcode:
		flush_print(client_username + " joined the chatroom")

		join_msg = client_username + " joined the chatroom" #sent to all clients
		sendallclients(join_msg)
		addclientsthread(client, address)

		connected_msg = ("Connected to 127.0.0.1 on port " + str(port)).encode("utf8")
		client.send(connected_msg)
		while True:
			message = client.recv(1024).decode("utf8")
			output_msg = client_username + ": " + message

			if message == ":)":
				output_msg = client_username + ": [feeling happy]"
			elif message == ":(":
				output_msg = client_username + ": [feeling sad]"
			elif message == ":mytime":
				output_msg = client_username + ": " + time.strftime("%a %b %-d %H:%M:%S %Y", time.localtime())
			elif message == ":+1hr":
				t = datetime.datetime.now()
				t += datetime.timedelta(hours=1)
				t = t.strftime("%a %b %d %H:%M:%S %Y")

				output_msg = client_username + ": " + str(t)
			elif message == ":Exit":
				output_msg = client_username + " left the chatroom"
				flush_print(output_msg)
				sendallclients(output_msg)
				client.close()
				return

			sendallclients(output_msg)
			flush_print(output_msg)
      
	else:
		msg = "Incorrect passcode".encode('utf8')
		client.send(msg)
		pass

def addclientsthread(sock, addr):
	global clients_list
	clients_list += [sock]
	#print('Client connected on ' + addr[0])
	#start_new_thread(clientthread, (conn,))

def sendallclients(message):
	message = message.encode('utf8')
	for cl in clients_list:
		cl.send(message)

def flush_print(msg):
	print(msg)
	sys.stdout.flush()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('-start', required=True, action='store_true')
	parser.add_argument('-port', required=True)
	parser.add_argument('-passcode', required=True)
	args = parser.parse_args()
	port = int(args.port)
	host = "127.0.0.1"
	passcode = args.passcode.strip()
	listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listen_socket.bind((host, port))
	listen(listen_socket)

