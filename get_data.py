import socket
from struct import unpack
import threading
import time

global data
data = {}

def get_data(s):
        data = dict()
        #data['time'] = time.ctime()
        data['speed'] = unpack(b'@f', s.recv(4))[0] # speed
        data['distance'] = unpack(b'@f', s.recv(4))[0] # distance
        data['finish'] = unpack(b'@f', s.recv(4))[0] # finish
        data['curCP'] = unpack(b'@f', s.recv(4))[0] # finish
        data['lastCPTime'] = unpack(b'@f', s.recv(4))[0] # finish
        data['curRaceTime'] = unpack(b'@f', s.recv(4))[0] # finish
        data['posx'] = unpack(b'@f', s.recv(4))[0] #Position x
        return data

# function that captures data from openplanet 
def data_getter_function():
        global data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("127.0.0.1", 9000))
                while True:
                        data = get_data(s)
        
def start_thread():
        data_getter_thread = threading.Thread(target=data_getter_function, daemon=True)
        data_getter_thread.start()


if __name__ == "__main__":          
        time.sleep(0.2) # wait for connection
        start_thread()

        while True :
                #print(data)
                pass
                