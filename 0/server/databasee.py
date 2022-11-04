import mysql.connector

def ConnectDatabase():
    global database
    try:
        database = mysql.connector.connect(user='root', password='', host='localhost', database='felhasznalok')
        print("Succesfully connected to mysql")
        return True
    except Exception as e:
        print(f"Error in connect to database: {e}")
        return False