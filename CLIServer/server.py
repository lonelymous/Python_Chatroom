import threading, socket, time, signal
BUFFER = 8192
clients = []
nicknames = []
messages = []
log = []

def Log(message):
    try:
        #Mindent logolunk, hogy Zuki bácsi büszke legyen ránk
        f = open(f"{time.localtime().tm_year}.{time.localtime().tm_mon}.{time.localtime().tm_mday}-log.txt", "a")
        f.write(f"{CorrectTime(time.localtime().tm_hour)}:{CorrectTime(time.localtime().tm_min)}:{CorrectTime(time.localtime().tm_sec)}-{message}\n")
        f.close()
    except Exception as e:
        print(f"Log - Error: {e}")

def CorrectTime(date):
    date = str(date)
    if len(date) < 2:
        return "0" + date
    else:
        return date

def Broadcast(message,sender):
    try:
        #Decode the message
        message = message.decode('utf-8')
        #Server messages doesn't went out on Broadcast
        if not message.startswith('[+]'):
            messages.append(message)
            for client in clients:
                if sender != client:
                    client.send(message.encode('utf-8'))
        print(message)
        Log(message)
    except Exception as e:
        print(f"Broadcast - Error: {e}")

def Handle(client):
    while True:
        index = clients.index(client)
        nickname = nicknames[index]
        try:
            Broadcast(client.recv(BUFFER),client)
        except Exception as e:
            print(f"Handle - Error: {e}")
            clients.remove(client)
            client.close()
            Broadcast(f'{nickname} left the chat.'.encode('utf-8'),"")
            nicknames.remove(nickname)
            break
    

def Receive():
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
        Broadcast(f'{nickname} joined the chat!'.encode('utf-8'),client)
        client.send('Connected to the server!'.encode('utf-8'))
        #
        if messages is not None:
            client.send("\n----- L A S T   M E S S A G E S -----\n".encode('utf-8'))
            for message in messages:
                client.send((message + "\n").encode('utf-8'))
            client.send("-------------------------------------".encode('utf-8'))
        #
        thread = threading.Thread(target=Handle, args=(client,))
        thread.start()

def Kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('utf-8'))
        client_to_kick.close()
        nicknames.remove(name)
        Broadcast(f'{name} was kicked by an admin!'.encode('utf-8'),"")

def Exit(signum, frame):
    res = input("Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        server.close()
        exit(1)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, Exit)
    ipAddress = "0.0.0.0"
    portNumber = 42069

    server.bind((ipAddress, portNumber))
    server.listen()
    print("Server is listening...")
    Receive()