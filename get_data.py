import socket
from struct import unpack
import threading
import time

global data
global isStopped
data = {}

def get_data(s):
        data = dict()
        #Récupération des données depuis le socket
        data['speed'] = unpack(b'@f', s.recv(4))[0] # speed
        data['distance'] = unpack(b'@f', s.recv(4))[0] # distance
        data['finish'] = unpack(b'@f', s.recv(4))[0] # finish
        data['curCP'] = unpack(b'@f', s.recv(4))[0] # numéro du CP actuel
        data['lastCPTime'] = unpack(b'@f', s.recv(4))[0] # temps au dernier CP
        data['curRaceTime'] = unpack(b'@f', s.recv(4))[0] # temps
        data['posx'] = unpack(b'@f', s.recv(4))[0] # position x
        return data

# Récupération des données 
def data_getter_function():
        global data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 9000))
                while not isStopped:
                        data = get_data(s)

# Threading 
def start_thread():
        global isStopped
        isStopped = False
        data_getter_thread = threading.Thread(target=data_getter_function, daemon=True)
        data_getter_thread.start()

def stop_thread():
        global isStopped
        isStopped = True

# Debug
if __name__ == "__main__":          
        time.sleep(0.2) # wait for connection
        #start_thread()

        while True :
                #print(data)
                pass
