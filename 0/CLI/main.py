import models
import database
import threading, socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
BUFFER = 8192

ipAddress = "0.0.0.0"
portNumber = 42068

#//TODO only for testing the main purpose is clients store that if somebody banned or admin
admins = []
bans = []

clients = []
messages = []

if __name__ == "__main__":

    mode = input("server or client (s/c)")

    try:
        #Try to connect to the database
        if not database.ConnectDatabase():
            admins = ["admin"]

        #try to start the server
        # //TODO separeted try-expect? 
        starter_counter = 0
        while True:
            starter_counter += 1
            if starter_counter == 5:
                print("The server couldn't start 5 times do you want to continue? (y/n)")
                res = input()
                if res == "n":
                    break

            server.bind((ipAddress, portNumber))
            server.listen()
            print("Server is listening...")
            break
        print(admins)
        print(bans)

        #thread for handleInput
        threading.Thread(target=write_thread).start()
        
        receive_thread()
    except Exception as e:
        print(f"error in main_thread: {e}")