import socket
import threading
import sys 
import argparse


#TODO: Implement a client that connects to your server to chat with other clients here
EXIT_KEY = "Exit"
#reference: https://www.digitalocean.com/community/tutorials/python-socket-programming-server-client
# https://docs.python.org/3/library/asyncio-stream.html
#ref: https://stackoverflow.com/questions/51104534/python-socket-receive-send-multi-threading

# Use sys.stdout.flush() after print statemtents
class Client():

	def __init__(self, host, port, username, passcode):
		self.host = host
		self.port = int(port)
		self.username = username
		self.passcode = passcode.strip()
		self.client_socket = socket.socket()
		self.client_socket.connect((self.host, self.port))
		self.verify_passcode()

	def input_main(self):
		#main thread handles getting input and sending it
		while True:
			new_msg = input("").strip()
			new_msg = new_msg.encode("utf8")
			self.client_socket.send(new_msg)

	def update_screen(self, server):
		# recieves data from server
		while True:
			data = server.recv(1024).decode('utf8')
			print(data)
			sys.stdout.flush()


	def verify_passcode(self):
		'''Initial connection to server that handles checking if the password is correct. This connection is persistant'''

		self.client_socket.send((self.username + " " + self.passcode).encode("utf-8"))
		threading.Thread(target=self.update_screen, args=(self.client_socket,)).start()
		self.input_main()

if __name__ == "__main__":
	# take in the from cli: IP address, listening port, username, password
	# python3 client.py -join -host <hostname> -port <port> -username <username> -passcode <passcode>
	parser = argparse.ArgumentParser()
	parser.add_argument('-join', required=True, action='store_true')
	parser.add_argument('-host', required=True)
	parser.add_argument('-port', required=True)
	parser.add_argument('-username', required=True)
	parser.add_argument('-passcode', required=True)
	args = parser.parse_args()
	client = Client(args.host, args.port, args.username, args.passcode)
