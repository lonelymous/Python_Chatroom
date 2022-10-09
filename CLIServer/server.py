import threading, socket,time
BUFFER = 8192
clients = []
nicknames = []
messages = []
log = []

def correctTime(date):
    if len(str(date)) < 2:
        return "0" + date
    else:
        return date

def broadcast(message,sender):
    #Dekódoljuk az üzenetet
    msg = message.decode('utf-8')
    #Ami nem szerver üzenet azt ne küldük el
    if not msg.startswith('[+]'):
        messages.append(msg)
        for client in clients:
            if sender != client:
                client.send(msg.encode('utf-8'))
    #Mindent logolunk, hogy Zuki bácsi büszke legyen ránk
    f = open(f"{time.localtime().tm_year}.{time.localtime().tm_mon}.{time.localtime().tm_mday}-log.txt", "a")
    f.write(f"{correctTime(time.localtime().tm_hour)}:{correctTime(time.localtime().tm_min)}:{correctTime(time.localtime().tm_sec)}-{msg}\n")
    print(msg)
    f.close()

def handle(client):
    while True:
        index = clients.index(client)
        nickname = nicknames[index]
        try:
            msg = client.recv(BUFFER)
            broadcast(msg,client)
            hm = msg.decode('utf-8')[4:]
        except Exception:
            clients.remove(client)
            client.close()
            broadcast(f'{nickname} left the chat.'.encode('utf-8'),"")
            nicknames.remove(nickname)
            break

def receive():
    while True:
        #
        client, address = server.accept()
        print(f'Connected with {str(address)}')
        #
        nickname = client.recv(BUFFER).decode('utf-8')
        #
        with open('bans.txt', 'r') as f:
            bans = f.readlines()
        #
        if address[0] in bans:
            client.send('You are banned from the server!'.encode('utf-8'))
            client.close()
            continue
        #
        nicknames.append(nickname)
        clients.append(client)
        #
        broadcast(f'{nickname} joined the chat!'.encode('utf-8'),client)
        client.send('Connected to the server!'.encode('utf-8'))
        #
        if messages is not None:
            client.send("\n----- L A S T   M E S S A G E S -----\n".encode('utf-8'))
            for message in messages:
                client.send((message + "\n").encode('utf-8'))
            client.send("-------------------------------------".encode('utf-8'))
        #
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin!'.encode('utf-8'),"")

if __name__ == "__main__":
    ipAddress = "0.0.0.0"
    portNumber = 42069
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ipAddress, portNumber))
    server.listen()
    print("Server is listening...")
    receive()