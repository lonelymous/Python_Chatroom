import threading, socket, os
from playsound import playsound
SEPARATOR = "<SEPARATOR>"
BUFFER = 8192
psound = False
stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(BUFFER).decode('utf-8')
            #####
            print(message)
            if psound:
                try:
                    playsound('discord-notification.mp3')
                except Exception:
                    print("Error with playing sound")
        except Exception:
            print("An error occurred!")
            client.close()
            break
        
def write():
    #Globális változót hozunk létre a psound-ból.
    global psound,stop_thread
    while True:
        #Ha lekell állnia akkor álljon le.
        if stop_thread:
            break
        #bekérjük az üzenetet a felhasználótól
        message = input()
        #Megnézzük, hogy valamilyen parancs-e, ha nem akkor csak kiírjuk.
        if message.startswith('/'):
            ### exit command
            if message.startswith('/exit'):
                print("You left the chat.")
                stop_thread = True
                client.close()
            ### mute command
            elif message.startswith('/mute'):
                print("You muted the application")
                client.send(f"[+] {nickname} muted the application".encode('utf-8'))
                psound = False
            ### unmute command
            elif message.startswith('/unmute'):
                print("You unmuted the application")
                client.send(f"[+] {nickname} unmuted the application".encode('utf-8'))
                psound = True
            ### send command
            elif message.startswith('/send'):
                client.send(f'[+] {message}'.encode('utf-8'))
                SendFile(message,client)
            ###
            else:
                print("Error")
        else:
            client.send(f"{nickname}> {message}".encode('utf-8'))

def SendFile(message,client):
    try:
        filename = "D:/Disk Third/Github/Python_TCPChatroom/Console Application/new/ASD/eladasok.xlsx"
        # get the file size
        filesize = os.path.getsize(filename)
        # send the filename and filesize
        client.send(f"{filename}{SEPARATOR}{filesize}".encode())
        # start sending the file
        with open(filename, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in 
                # busy networks
                client.sendall(bytes_read)
        print("Done..")
    except:
        pass

###########################################################################################
if __name__ == "__main__":
    #Bekérjük az IP-t amennyiben üresen hagyja akkor az alapértelmezettel fut tovább
    ip = input("Server ip and port: ")
    if ip:
        ipAddress = ip.split(':')[0]
        portNumber = int(ip.split(':')[1])
    else:
        #Felcsatlakozik a Google szervereire majd azt az IP-t menti el amivel csatlakozott.
        #Ezzel kizárjuk a VirtualBoxos IP-k használatát.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipAddress = s.getsockname()[0]
        portNumber = 42069
        s.close()

    #Választunk egy becenevet.
    nickname = input("Choose a nickname: ")
    #Megmondjuk, hogy milyen lesz a szerver IPv4-es és TCP kapcsolat
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Felcsatlakozunk a szerverre.
    client.connect((ipAddress, portNumber))
    client.send(nickname.encode('utf-8'))

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()