import models
import databasee
import threading, socket, time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ipAddress = "0.0.0.0"
portNumber = 42068
server_user = models.User(nickname="server",address=(ipAddress, portNumber), client=None, isAdmin=True, isServer=True)
BUFFER = 8192
stop_thread = False

#//TODO only for testing the main purpose is clients store that if somebody banned or admin
admins = []
bans = []

users = []
messages = []

database = None

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
            for user in users:
                if sender != user:
                    if user.IsServer:
                        print(message)
                    user.Client.send(message.encode('utf-8'))
        Log(message)
    except Exception as e:
        print(f"Broadcast - Error: {e}")

def handle(user):
    while True:
        try:
            Broadcast(user.Client.recv(BUFFER),user)
        except Exception as e:
            print(f"Handle - Error: {e}")
            users.remove(user)
            user.Client.close()
            Broadcast(f'{user.Nickname} left the chat.'.encode('utf-8'),"")
            break

def receive_thread():
    print("receive_thread is running...")
    while True:
        if stop_thread:
            break
        #
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        nickname=client.recv(BUFFER).decode('utf-8')
        isAdmin=False
        if nickname == "admin" and client.recv(BUFFER).decode('utf-8') == "admin123":
            isAdmin=True
        user = models.User(nickname=nickname, client=client, address=address, isAdmin=isAdmin, isServer=False)
        users.append(user)
        #
        Broadcast(f'{user.Nickname} joined the chat!'.encode('utf-8'),user)
        user.Client.send('Connected to the server!'.encode('utf-8'))
        #
        if messages is not None:
            user.Client.send("\n----- L A S T   M E S S A G E S -----\n".encode('utf-8'))
            for message in messages:
                user.Client.send((message + "\n").encode('utf-8'))
            user.Client.send("-------------------------------------".encode('utf-8'))

        #thread for handle
        thread = threading.Thread(target=handle, args=(user,))
        thread.start()

def write_thread():
    global stop_thread
    print("write_thread is running...")
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
            # elif message.startswith("/ban"):
            #     pass
            # elif message.startswith("/unban"):
            #     pass
            # elif message.startswith("/kick"):
            #     pass
            else:
                Broadcast(message.encode('utf-8'), server_user)
        except EOFError:
            if input("Are you sure you wanna shutdown the server? (y/n)") == "y":
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
        server.bind((ipAddress, portNumber))
        server.listen()
        users.append(server_user)
        print("server is listening..")

        #thread for handleInput
        threading.Thread(target=write_thread).start()
        receive_thread()
    except Exception as e:
        print(f"error in main_thread: {e}")