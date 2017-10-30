#https://www.youtube.com/watch?annotation_id=annotation_3321606705&feature=iv&index=7&list=PL1A2CSdiySGJeOmhFfV7d2EeiiunIDRZZ&src_vid=PkfwX6RjRaI&v=XiVVYfgDolU

import socket

def Main():
	host = '127.0.0.1' #host is this machine
	port = 5000

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((host, port))

	s.listen(1)
	(c, addr) = s.accept() #this function returns a new socket 'c' the address
	print("Connection from: " + str(addr))
	
	while True:
		data = c.recv(1024) #buffer is max 1024 bytes
		if not data: #if c.recv returns false cuz connection is closed
			break
		data = data.decode()
		print("From connected user: ", data)
		data = data.upper()
		print("sending: " + data)
		
		c.sendall(data.encode('utf-8'))
		
	c.close()

if __name__== '__main__':
	Main()

