import socket			
import threading
netsoc = socket.socket()		
port = 12345			
netsoc.connect(('192.168.158.59', port))

#Sending
def sending(netsoc):
    reply = str(input())
    netsoc.send(reply.encode("UTF-8"))
    if reply=="exit":
        return reply

#Receiving 
def receive(netsoc):
    option = 0
    while option != 1:
        request = str(netsoc.recv(1024).decode("UTF-8"))
        if(request[-1]=='r'):
            print(request[0:(len(request)-2)])
            reply = sending(netsoc)
            if reply == "exit":
                option = 1
        else:
            print(request)

receive(netsoc)
netsoc.close()