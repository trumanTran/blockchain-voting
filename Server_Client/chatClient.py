import socket
import threading
import time

tLock = threading.Lock()
shutdown = False

def recieving(name, sock):
	while not shutdown:
		try:
			tLock.acquire()
			while True:
				data, addr = sock.recvfrom(1024)
				print(data)
		except:
			pass
		finally:
			tLock.release() #when there is nothing left to grab from recieving buffer
							#will throw error and break out of while loop
							
host = '127.0.0.1'	
port = 0 #port 0 means system can choose any port not being used

server = ('127.0.0.1', 5000)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
s.setblocking(0)

rT = threading.Thread(target=recieving, args=("RecvThread", s))
rT.start()

alias = input("Name: ")

message = input("-> ")

while message != 'q':
	if message != '':
		s.sendto(alias.encode('utf-8') + message.encode('utf-8'), server)
	tLock.acquire()
	message = input(alias + "-> ")
	tLock.release()
	time.sleep(0.2)
	
shutdown = True
rT.join()
s.close()

		