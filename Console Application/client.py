import threading, socket
from playsound import playsound

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ipAddress = s.getsockname()[0]
portNumber = 42069

if input("Other IP?:").__contains__('y'):
    ip = input("Server ip and port: ")
    ipAddress = ip.split(':')[0]
    portNumber = int(ip.split(':')[1])

nickname = input("Choose a nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin: ")

psound = True

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((ipAddress, portNumber))

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(8192).decode('utf-8')
            if message == 'NICK':
                client.send(nickname.encode('utf-8'))
                next_message = client.recv(8192).decode('utf-8')
                if next_message == 'PASS':
                    client.send(password.encode('utf-8'))
                    if client.recv(8192).decode('utf-8') == 'REFUSE':
                        print("Connection was refused! Wrong password")
                        stop_thread = True
                elif next_message == 'BAN':
                    print('Connection refused because of ban!')
                    client.close()
                    stop_thread = True
            else:
                print(message)
                if psound:
                    playsound('discord-notification.mp3')
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    global psound
    while True:
        if stop_thread:
            break
        message = f'{nickname}: {input()}'
        if message[len(nickname)+2:].startswith('/'):
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('utf-8'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('utf-8'))
            elif message[len(nickname)+2:].startswith('/exit'):
                client.close()
            elif message[len(nickname)+2:].startswith('/mute'):
                client.send(f"{nickname} muted the application".encode('utf-8'))
                psound = False
            elif message[len(nickname)+2:].startswith('/unmute'):
                client.send(f"{nickname} unmuted the application".encode('utf-8'))
                psound = True
            else:
                print("Commands can only be executed by the admin!")
        else:
            client.send(message.encode('utf-8'))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()