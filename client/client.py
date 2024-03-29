import threading, socket, sys
BUFFER = 1024
stop_thread = False

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
local_address = s.getsockname()[0]
s.close()

server_address = None

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

def Receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            packet = client.recv(BUFFER).decode('utf-8')
            print(packet)
            header, data = GetPacket(packet)
            print(header)
            source_address, mode, destination_addres, counter = GetHeader(header)
            print(f"{source_address}> {data}")
        except Exception as e:
            print(f"Error - Receive: {e}")
            print(e.args)
            print(e.with_traceback())
            client.close()
            break
        
def Write():
    global stop_thread
    while True:
        try:
            if stop_thread:
                break
            message = input().strip()
            if message == "":
                continue
            if message.startswith('/'):
                if message.startswith("/exit"):
                    #//TODO send to the server that client is leaving?
                    print("You left the chat.")
                    stop_thread = True
                    client.close()
                if message.startswith("/msg"):
                    message_items = message.split(' ')
                    client.send(CreatePacket(CreateHeader(local_address, 'C', message_items[1], "0"), message_items[2]).encode("utf-8"))
                else:
                    client.send(CreatePacket(CreateHeader(local_address, 'C', server_address, "0"), message).encode('utf-8'))
            else:
                header = CreateHeader(local_address, "M", "255.255.255.255", "0")
                client.send(CreatePacket(header, message).encode('utf-8'))
        except Exception as e:
            print(f"Error - write: {e}")

if __name__ == "__main__":
    ip = input("Server ip and port: ")
    server_address = ip.split(':')[0]
    port_number = int(ip.split(':')[1])

    nickname = input("Choose a nickname: ")
    password = " "
    if nickname == "admin":
        password = input("password: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_address, port_number))

    header = CreateHeader(local_address, "L", server_address, "0")
    client.send(CreatePacket(header, f"{nickname}|{password}").encode('utf-8'))

    receive_thread = threading.Thread(target=Receive)
    receive_thread.start()

    write_thread = threading.Thread(target=Write)
    write_thread.start()