from multiprocessing.connection import Client
import threading
import socket

class User:
    Nickname = None
    Address = None
    Client = None
    Is_admin = None
    Is_server = None

    def __init__(self, nickname, address, client, is_admin = False, is_server = False):
        self.Nickname = nickname
        self.Address = address
        self.Client = client
        self.Is_admin = is_admin
        self.Is_server = is_server

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_address = s.getsockname()[0]
s.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port_number = 42069
server_user = User(nickname="server",address=(local_address, port_number), client=None, is_admin=True, is_server=True)

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

def GetUserByIp(address):
    for user in users:
        if user.Address == address:
            return user
    return None

def GetNicknameByIp(address):
    for user in users:
        if user.Address == address:
            return user.Nickname
    return None

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

def BroadcastMessage(sender, message, source_address):
    try:
        header = CreateHeader(source_address, "M", "255.255.255.255", "0")
        if source_address == None:
            header = CreateHeader(local_address, "M", "255.255.255.255", "0")
        messages.append(message)
        for user in users:
            if sender != user:
                if user.Is_server:
                    print(f"{GetNicknameByIp(source_address)}> {message}")
                    continue
                user.Client.send(CreatePacket(header, message).encode('utf-8'))
    except Exception as e:
        print(f"BroadcastMessage - error: {e}")

def BroadcastPacket(sender, packet):
    try:
        header, data = GetPacket(packet.decode('utf-8'))
        source_address, mode, destination_addres, counter = GetHeader(header)

        message = data

        if mode.lower() == "m":
            messages.append(message)
            for user in users:
                if sender != user:
                    if user.Is_server:
                        print(f"{GetNicknameByIp(source_address)}> {message}")
                        continue
                    user.Client.send(CreatePacket(CreateHeader(source_address, "M", "255.255.255.255", "0"), message).encode('utf-8'))
    except Exception as e:
        print(f"BroadcastPacket - error: {e}")

def Handle(user):
    while True:
        try:
            packet = user.Client.recv(BUFFER)
            header, data = GetPacket(packet.decode('utf-8'))
            source_address, mode, destination_addres, counter = GetHeader(header)
            print(f"Packet: {packet}")
            print(f"Mode: {mode}")
            
            if mode.lower() == 'a':
                print(f"Mode: A = {packet}")
            if mode.lower() == 'm':
                BroadcastPacket(user, packet)
            if mode.lower() == 'f':
                print(f"Mode: F = {packet}")
            if mode.lower() == 'c':
                if user.Is_admin:
                    data_items = data.split(' ')
                    if data_items[0] == "/kick":
                        user = data_items[1]
                        #Check if IP
                        if not user.__contains__('.'):
                            user = DNSResolver(user)
                        if IPChecker(user):
                            #Check in users
                            user = GetUserByIp(user)
                            #kick => close connection via message
                            PacketToUser(user, "You have been kicked from the chat!")
                            users.remove(user)
                            user.Client.close()
                            BroadcastMessage(None, f"{user.Nickname} was kicked from the chat.",local_address)
                        else:
                            print("error not a valid user")
        except Exception as e:
            print(f"Handle - error: {e}")
            users.remove(user)
            user.Client.close()
            BroadcastMessage(None, f"{user.Nickname} left the chat.",local_address)
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
        print(f"Connected with {address}")
        
        header, data = GetPacket(client.recv(BUFFER).decode('utf-8'))
        source_address, mode, destination_addres, counter = GetHeader(header)
        
        data_items = data.split('|')
        nickname = data_items[0]

        is_admin=False
        #//TODO save admin user to an .ini file.
        if nickname == "admin":
            if data_items[1] == "admin123":
                is_admin=True
            else:
                # I can't use PacketToUser() method because we don't initalize user yet.
                client.send(CreatePacket(CreateHeader(local_address, "M", address, "0"), 'Authentication failed!').encode('utf-8'))
        
        user = User(nickname=nickname, client=client, address=source_address, is_admin=is_admin, is_server=False)
        users.append(user)

        BroadcastMessage(user, f"{user.Nickname} joined the chat!",local_address)
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
                BroadcastMessage(server_user, message, local_address)
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
        if "y" == input("Do you want to manage the chatroom?\nif not you have to use client to write.\n").lower():
            #thread for handleInput
            threading.Thread(target=Write).start()
        server.bind((local_address, port_number))
        server.listen()
        users.append(server_user)
        print("server is listening..")
        Receive()
    except Exception as e:
        print(f"error in main_thread: {e}")