import sys
import argparse
import socket
import time
import json
import threading
import logging
import os

#from __future__ import print_function
#tPrint = lambda x: sys.stdout.write("%s\n" % x)

# message type
REG = '1'
TABLE = '2'
MSG = '3'
ACK = '4'
INFO = '5'
DEREG = '6'
OFFLINE = '7'
HEART = '8'


myName = ''
serverIp = ''
serverPort = ''
clientPort = ''

userTable = {}

fileLockMap = {}

ackMap = {}
ackLock = threading.Lock()
ackNum = 0

def checkPort(port):
	if (port < 1024 or port > 65536):
		print 'port ' + str(port) + 'invalid'
		exit(2) 

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
			checkPort(serverPort)	
			clientPort = int(clientPort)
			checkPort(clientPort)	
			socket.inet_aton(serverIp)
		except ValueError:
			print 'server/client port should be an integer'
		except socket.error:
			print 'serverIp is invalid'
		client()
	else:
		try:
			serverPort = int(argResult.serverPort[0])
			checkPort(serverPort)	
		except ValueError:
			print 'server port should be an integer'
		server()

#------------------------------ shared functions  --------------------------------


def myRecv(s):
	data, (addr, port) = s.recvfrom(1024)
	data = data.split(',')
	length = int(data[0])
	msgType = data[1]
	label = int(data[2])
	print 'debug in myRecv: ' 
	print data
	res = ''
	while (len(res) < length):
		tmp, (a, b) = s.recvfrom(1024)
		res += tmp
	return [msgType, res, addr, port, label]

def mySend(head, data, s, serverIp, serverPort):
	print 'send: '
	print 'head: ' + head
	print 'data: ' + str(data)
	print 'ip: ' + serverIp
	print 'port: ' + str(serverPort)
	s.sendto(str(head), (serverIp, serverPort))
	s.sendto(str(data), (serverIp, serverPort))

def readTable(user):
	global userTable
	value = userTable[user]
	print 'debug in readTable:'
	print value
	return [value[0], int(value[1]), value[2]]

def waitAck(num):
	global ackMap
	num = int(num)
	count = 0
	while (ackMap[num] != 2):	
		count = count + 1
		time.sleep(0.1)
		if (count == 5):
			del ackMap[num]
			return False	
	del ackMap[num]
	return True	

def getAckNum(needAck):
	global ackLock, ackNum, ackMap
	ackLock.acquire()
	msg = ackNum
	ackNum = ackNum + 1		
	ackLock.release()
	if (needAck):
		ackMap[msg] = 1
	return msg

def recvAckUpdate(num):
	global ackMap	
	print 'debug in recvAckUpdate: here'
	num = int(num)
	if (num in ackMap and ackMap[num] == 1):
		ackMap[num] = 2	
	
def genHead(data, msgType):
	global MSG, HEART, DEREG
	needAck = False
	if (msgType == MSG or msgType == HEART or msgType == DEREG):
		needAck = True
	label = getAckNum(needAck)
	return [str(len(str(data))) + ',' + msgType + ',' + str(label), label]

#------------------------------ server  --------------------------------

def broadcast():
	global TABLE, userTable
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	tableStream = json.dumps(userTable)
	for user in userTable:
		(addr, port, status) = readTable(user)
		if (status == 1):
			mySend(genHead(tableStream, TABLE)[0], tableStream, s, addr, port)
	s.close()


def offlineHelper(sender, receiver, offlineMsg, s):
	global userTable, fileLockMap 
        userTable[receiver][2] = 0
	broadcast()
        fileName = receiver + '.txt'
        fileLock = fileLockMap[fileName]
        fileLock.acquire()
        f = None
        if (os.path.isfile(fileName) == False):
	        f = open(fileName, 'w') 
        else:
                f = open(fileName, 'a')
        localtime = time.asctime(time.localtime(time.time()))
        offlineMsg = '[' + localtime + '] ' + offlineMsg
        f.write(offlineMsg)              
        f.close()
        fileLock.release() 
        info = '[Messages received by the server and saved]'
	(addr, port, status) = readTable(sender)
        mySend(genHead(info, INFO)[0], info, s, addr, port)	

def offlineHdl(data, addr):
	global HEART, uesrTable
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	offMsg = data
	sender = offMsg[0] 
	receiver = offMsg[1]
	offlineMsg = offMsg[2] + '\n'
	if (userTable[receiver][2] == 1):
		msg = 'beat'
		receiverIp = userTable[receiver][0]
		receiverPort = userTable[receiver][1]
		head = genHead(msg, HEART)
		mySend(head[0], str(msg), s, receiverIp, receiverPort)
		if (waitAck(head[1])):
			info = '[Client %s exists!!]' % receiver
			serverSend(info, INFO, addr, port)
			broadcast()
		else:
			offlineHelper(sender, receiver, offlineMsg, s)
	else:
		offlineHelper(sender, receiver, offlineMsg, s)
	s.close()

def getOfflineMsg(user):
	global fileLockMap
	fileName = user + '.txt'
	if (os.path.isfile(fileName)):
		fileLock = fileLockMap[fileName]
		fileLock.acquire()
		f = open(fileName, 'r')
		info = f.read()
		f.close()
		os.remove(fileName)	
		fileLock.release()
		return info
	return ''
			

def regHdl(userInfo, addr):
	global userTable
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	userInfo = userInfo.split(',')
	port = int(userInfo[1])
	userTable[userInfo[0]] = [addr, port, 1]
	info =  '\n>>> [Welcome, You are registered.]'
	head = genHead(info, INFO)
	print head
	mySend(head[0], info, s, addr, port)
	sys.stdout.flush()
	
	broadcast()
	offLineMsg = getOfflineMsg(userInfo[0])
	if (len(offLineMsg) > 0):
		mySend(genHead(offLineMsg, INFO)[0], offLineMsg, s, addr, port)
	s.close()

def deregHdl(user, addr, label):
	global userTable
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
       	userTable[user][2] = 0
	port = userTable[user][1]
        info = str(label)
	print 'debug in deregHdl'
        mySend(genHead(info, ACK)[0], info, s, addr, port)
        broadcast()
	s.close()
		
def server():
	global REG, TABLE, DEREG, OFFLINE, ACK, userTable, fileLockMap
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('127.0.0.1', serverPort))

	while True:
		msgType, userInfo, addr, port, label = myRecv(s)
		print userInfo
		if (msgType == REG):
			t = threading.Thread(target = regHdl, args =(userInfo, addr,))
			t.start()
		elif (msgType == DEREG):
			t = threading.Thread(target = deregHdl, args =(userInfo, addr, label,))
			t.start()
		elif (msgType == OFFLINE):
			stream = json.loads(userInfo)		
			fileName = stream[1] + '.txt'
			print 'debug in server():'
			print stream
			print 'fileName = ' + fileName
			if (fileName not in fileLockMap):
				fileLockMap[fileName] = threading.Lock()
			t = threading.Thread(target = offlineHdl, args =(stream, addr,))
			t.start()
		elif (msgType == ACK):
			recvAckUpdate(userInfo)	
			
#------------------------------ client --------------------------------

def register(s):
	global userTable, myName, clientPort
	userInfo = myName + ',' + str(clientPort)
	mySend(genHead(userInfo, REG)[0], userInfo, s, serverIp, serverPort)
	return userTable

def clientListen(s):
	global TABLE, MSG, ACK, INFO, HEART, userTable, myName
	while (True):
		msgType, data, addr, port, label = myRecv(s)
		if (msgType == TABLE):
			userTable = json.loads(data)	
			print '\n>>> [Client table update.]'
			print '>>> ',
		elif (msgType == INFO):
			print '\n>>> ' + data
			print '>>> ',
		elif (msgType == ACK):
			recvAckUpdate(data)
		elif (msgType == MSG or msgType == HEART):
			if (msgType == MSG):
				print '\n>>> ' + data
			ackMsg = label 
			ackSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = serverIp
			if (msgType == MSG):
				tmp = data.split(':')
				print 'debug in clientListen: tmp = '
				print tmp
				port = int(userTable[tmp[0]][1])
			print 'debug in clientListen: port = ' + str(port)
			mySend(genHead(ackMsg, ACK)[0], ackMsg, ackSocket, addr, port)
			ackSocket.close()
			if (msgType == MSG):
				print '>>> ',
			
		sys.stdout.flush()
	
def sendOffline(s, msg, receiver):
	global userTable, myName, OFFLINE 
	offMsg = [myName, receiver, msg]
	stream = json.dumps(offMsg)
	mySend(genHead(stream, OFFLINE)[0], stream, s, serverIp, serverPort)
	

def send(s):
	global userTable, MSG, DEREG, waitingACK, myName
	try:
		msg = raw_input()
	except KeyboardInterrupt:
		head = genHead(myName, DEREG)
		mySend(head[0], myName, s, serverIp, serverPort)
		if (waitAck(head[1]) == False):
			print '\n>>> [Server not responding]'
			print '\n>>> [Exiting]'
			s.close()		
			exit(0)

		print '\n>>> [You are Offline. Bye.]'
		s.close()
		exit(0)
	
	print 'debug: in send(): ' + msg 
	msg = msg.split(' ')
	if (len(msg) != 3 or (msg[0] != 'send' and msg[0] != 'reg')):
		print '\n>>> [msg invalid]'
		print '>>> ',
		return
	if (msg[0] == 'send'):
		receiver = msg[1]
		if (receiver not in userTable):
			print '\n>>> [cannot find receiver]'
			print '>>> ',
			return	
		(addr, port, status) = readTable(receiver)
	
		content = myName + ': ' + msg[2]
		head = genHead(content, MSG)
		mySend(head[0], content, s, addr, port)
		
		if (waitAck(head[1]) == False):
			print '\n>>> [No ACK from %s, message sent to server.]' % receiver
			print '>>> ',
			sendOffline(s, content, receiver)
		else:
			print '\n>>> [Message received by %s.]\n' % receiver
			print '>>> ',
	else:
		myName = msg[1]	
		register(s)	
	

def client():
	global userTable, clientPort, clientIp
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind(('127.0.0.1', clientPort))
	s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	listenThread = threading.Thread(target = clientListen, args = (s,))
	listenThread.daemon = True
	listenThread.start()
	register(s)
	print '\n>>> ',
	while (True):
		send(s1)
				
main()

