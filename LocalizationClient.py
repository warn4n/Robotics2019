import socket

class LocalizationClient():

	TCP_IP = '127.0.0.1'
	TCP_PORT = 42069
	BUFFER_SIZE = 1024
	# MESSAGE = "Hello, World!"
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def __init__(self):
		self.s.connect((self.TCP_IP, self.TCP_PORT))
		print("connected to server")


	def sendData(self,MESSAGE):
		self.s.send(MESSAGE)

	def reciveMessage(self):
		data = self.s.recv(self.BUFFER_SIZE)

	def close(self):
		self.s.close()