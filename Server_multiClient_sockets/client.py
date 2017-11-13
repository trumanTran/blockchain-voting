import socket

host = 'localhost'
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))


while True:
	data = s.recv(2048)
	print(data.decode())

	data = input('->' )
	s.send(data.encode("utf-8"))

s.close()