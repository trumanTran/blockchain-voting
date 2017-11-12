import socket
import sys

host = 'localhost'
port = 9999
server = ('localhost', 9999)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

outgoing_message = ''

while outgoing_message != 'quit':
	incoming_message = sock.recv(4096)
	if incoming_message == ' ':
		sock.sendto(incoming_message, server)
	print(incoming_message)
	
	outgoing_message = input("-> ")
	if outgoing_message != '':
		sock.sendto(outgoing_message.encode('utf-8'), server)

	if not outgoing_message:
		print("Closing Socket", sock.getsockname(), file=sys.stderr)
		sock.close()

	#time.sleep(0.2)	
#s.close()