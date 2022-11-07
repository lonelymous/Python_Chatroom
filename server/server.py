from multiprocessing.connection import Client
import threading
import socket

class User:
    Nickname = None
    Address = None
    Client = None
    IsAdmin = None
    IsServer = None

    def __init__(self, nickname, address, client, isAdmin = False, isServer = False):
        self.Nickname = nickname
        self.Address = address
        self.Client = client
        self.IsAdmin = isAdmin
        self.IsServer = isServer

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_address = s.getsockname()[0]
s.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port_number = 42069
server_user = User(nickname="server",address=(local_address, port_number), client=None, isAdmin=True, isServer=True)

stop_thread = False
BUFFER = 1024

users = []
messages = []

def IPChecker(address):
    for user in users:
        if user.Address == address:
            return True
    return False

def DNSResolver(nickname):
    for user in users:
        if user.Nickname == nickname:
            return user.Address
    return ""

def CreatePacket(header, data):
    return header + data

def FixCounter(counter):
    if len(counter) < 6:
        counter += " " * (6 - len(counter))
    return counter

def FixIP(address):
    if len(address) < 15:
        address += " " * (15 - len(address))
    return address

def CreateHeader(source_address, mode, destination_addres, counter):
    return "<" + FixIP(source_address) + mode + FixIP(destination_addres) + "|" + FixCounter(counter) + ">"

def GetPacket(packet):
    header = packet[:40]
    data = packet[40:]
    return header, data

def GetHeader(header):
    source_address = header[1:15]
    mode = header[16]
    destination_addres = header[17:32]
    counter = header[33:39]
    return source_address, mode, destination_addres, counter

def PacketToUser(user, message):
    user.Client.send(CreatePacket(CreateHeader(local_address, "M", user.Address, "0"), message).encode('utf-8'))

def BroadcastMessage(message):
    messages.append(message)
    for user in users:
        if user == server_user:
            print(message)
            continue
        user.Client.send(CreatePacket(CreateHeader(local_address, "M", user.Address, "0"), message).encode('utf-8'))

def BroadcastPacket(message, sender):
    try:
        header, data = GetPacket(message.decode('utf-8'))
        source_address, mode, destination_addres, counter = GetHeader(header)

        message = data

        if mode.lower() == "m":
            messages.append(message)
            for user in users:
                if sender != user:
                    print(user)
                    if user == server_user:
                        print(message)
                        continue
                    user.Client.send(CreatePacket(CreateHeader(source_address, "M", user.Address, "0"), message).encode('utf-8'))
    except Exception as e:
        print(f"Broadcast - error: {e}")

def Handle(user):
    while True:
        try:
            BroadcastPacket(user.Client.recv(BUFFER),user)
        except Exception as e:
            print(f"Handle - error: {e}")
            users.remove(user)
            user.Client.close()
            BroadcastMessage(f"{user.Nickname} left the chat.",None)
            break

def GetLastMessages(user):
    if messages is not None:
        PacketToUser(user, "\n----- L A S T   M E S S A G E S -----\n")
        for message in messages:
            PacketToUser(user, message + "\n")
        PacketToUser(user, "---------------------------------------")

def Receive():
    global stop_thread
    while True:
        if stop_thread:
            break
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        header, data = GetPacket(client.recv(BUFFER).decode('utf-8'))
        source_address, mode, destination_addres, counter = GetHeader(header)
        
        data_items = data.split('|')
        nickname = data_items[0]

        isAdmin=False
        #//TODO save admin user to an .ini file.
        if nickname == "admin":
            if data_items[1] == "admin123":
                isAdmin=True
            else:
                # I can't use PacketToUser() method because we don't initalize user yet.
                client.send(CreatePacket(CreateHeader(local_address, "M", address, "0"), 'Authentication failed!').encode('utf-8'))
        
        user = User(nickname=nickname, client=client, address=source_address, isAdmin=isAdmin, isServer=False)
        users.append(user)

        BroadcastMessage(f"{user.Nickname} joined the chat!",user)
        PacketToUser(user, "Connected to the server!")

        #thread for handle
        thread = threading.Thread(target=Handle, args=(user,))
        thread.start()

def Write():
    global stop_thread
    while True:
        if stop_thread:
            break
        try:
            message = input().strip()
            if message == "":
                continue
            elif message == "/exit":
                stop_thread = True
                continue
            else:
                BroadcastMessage(message, server_user)
        except EOFError:
            if input("Are you sure you wanna shutdown the server? (y/n)").lower() == "y":
                break
        except Exception as e:
            print(f"Error in write_thread: {e}")
    ShutdownServer()

def ShutdownServer():
    try:
        print("shutdowning..")
        server.close()
        print("done")
        exit(1)
    except Exception as e:
        print(f"error in ShutdownServer: {e}")

if __name__ == "__main__":
    try:
        print("starting server..")
        if "y" == input("Do you want to manage the chatroom?\nif not you have to use client to write").lower():
            #thread for handleInput
            threading.Thread(target=Write).start()
        server.bind((local_address, port_number))
        server.listen()
        users.append(server_user)
        print("server is listening..")
        Receive()
    except Exception as e:
        print(f"error in main_thread: {e}")