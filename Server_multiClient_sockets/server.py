import socket

host = 'localhost'#socket.gethostname()
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try: 
	s.bind((host, port))

except socket.error as e:
	print(str(e))
	
s.listen(5)
conn, addr = s.accept()
#print("Connected to ", addr)
conn.send("Hello, you are now connected. Please enter a message.".encode("utf-8"))
print('connected to: ' + addr[0] + ':' + str(addr[1]))
while True:
	data = conn.recv(2048)

	if not data:
		break

	print(data.decode())
	conn.send(data)

s.close()