import sys
import argparse
import socket
import time
import pickle

serverPort = ''
myName = ''
serverIp = ''
serverPort = ''
clientPort = ''

def main():
	global serverPort, myName, serverIp, serverPort, clientPort
	parser = argparse.ArgumentParser()
	group = parser.add_mutually_exclusive_group()
	group.add_argument('-s', nargs = 1, dest = 'serverPort')
	group.add_argument('-c', nargs = 4, dest = 'clientArg')
	argResult = parser.parse_args()
	if (argResult.serverPort is None):
		myName, serverIp, serverPort, clientPort = argResult.clientArg
		try:
			serverPort = int(serverPort)	
			clientPort = int(clientPort)
			socket.inet_aton(serverIp)
		except ValueError:
			print 'server/client port should be an integer'
		except socket.error:
			print 'serverIp is invalid'
		client()
	else:
		try:
			serverPort = int(argResult.serverPort[0])
		except ValueError:
			print 'server port should be an integer'
		server()

def myRecv(length, s):
	res = ''
	while (len(res) < length):
		res += s.recv(1024)
	return res

def mySend(length, data, s, serverIp, serverPort):
	s.sendto(str(length), (serverIp, serverPort))
	time.sleep(1)
	s.sendto(data, (serverIp, serverPort))


def server():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('127.0.0.1', serverPort))

	userTable = {}

	while True:
		length, (addr, port) = s.recvfrom(1024)
		userInfo = myRecv(int(length), s)
		print userInfo
		userInfo.split(',')
		userTable[userInfo[0]] = addr + ',' + str(port) + ',' + '0'
		s.sendto('[Welcome, You are registered.]', (addr, port))



def client():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	userInfo = myName + ',' + str(clientPort)
	print userInfo
	mySend(len(userInfo), userInfo, s, serverIp, serverPort)
	time.sleep(1)
	while (True):
		print '>>>',

		data = raw_input()


	s.close()

main()





