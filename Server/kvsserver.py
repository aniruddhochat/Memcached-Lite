import threading
from socket import *
import configFile as c
from google.cloud import storage
import os
import json
import redis

redisHost = c.REDIS_HOST
redisPort = c.REDIS_PORT
redisPassword = c.REDIS_PASSWORD

try:
    r = redis.StrictRedis(host=redisHost, port=redisPort, password=redisPassword, decode_responses=True)
    print(f'Redis connection successful {r}')
except Exception as e:
    print(f'Error connecting to Redis : {e}') 

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = c.CREDENTIALS
client = storage.Client()
bucket = client.bucket(c.BUCKET_NAME)

class KeyValueStore:
    def __init__(self,fileName,storageOption,bucket):
        self.fileName = fileName
        self.storageOption = storageOption
        self.bucket = bucket
        self.data = {}
        self.loadFile()
        self.loadBlob()
        self.lock = threading.Lock()
        self.concurrentTasks = threading.Semaphore(5)
        self.serverEvent = threading.Event()
        
    def loadFile(self):
        with open(self.fileName,"r") as readFile:
            for line in readFile:
                key,value = line.strip().split(',')
                self.data[key] = value
    def loadBlob(self):
        currentBlob = bucket.blob(c.BLOB_NAME)
        if not currentBlob.exists():
            currentBlob.upload_from_string(json.dumps(self.data),content_type='application/json')
    def saveFile(self,key):
        with open(self.fileName,"r") as file:
            temp = []
            for line in file:
                lineKey, lineValue = line.split(',')
                if lineKey == key:
                    line = f'{lineKey},{self.data.get(key).strip()}\n'
                    #print(line)
                temp.append(line)
        with open(self.fileName,"w") as file:
            file.writelines(temp)
            
    def getData(self,key):
        with self.lock:
            if self.storageOption == 1:
                if key is not None and key !='':
                    value = self.data.get(key)
                    if value is not None:
                        return f"VALUE {key} {len(value.strip())} \r\n{value}\r\n"
                    else:
                        return "VALUE NOT FOUND\r\n"
                else:
                    return "Key Not Found\n"
            elif self.storageOption == 2:
                currentBlob = bucket.blob(c.BLOB_NAME)
                if currentBlob.exists():
                    data = json.loads(currentBlob.download_as_string())
                    if key in data:
                        value = data[key]
                        return f"VALUE {key} {len(value.strip())} \r\n{value}\r\n"
                    else:
                        return "KEY NOT FOUND\n"
                else:
                    return "Blob Not Found\n"
            elif self.storageOption == 3:
                if key is not None and key !='':
                    if r.exists(key):
                        value = r.get(key)
                        if value is not None and value !='':
                            return f"VALUE {key} {len(value.strip())} \r\n{value}\r\n"
                        else:
                            return "VALUE NOT FOUND\n"
                    else:
                        return "KEY NOT FOUND\n"
                else:
                    return "Invalid Key\n"
            
    def setData(self,key,value):
        with self.lock:
            if self.storageOption == 1:
                if key in self.data:
                    value.strip()
                    self.data[key] = value
                    self.saveFile(key)
                    return "STORED\r\n"
                else:
                    temp =[]
                    self.data[key] = value.strip()
                    line = f'{key},{value.strip()}\n'
                    temp.append(line)
                    with open(self.fileName,"a") as file:
                        file.writelines(temp)
                    return "STORED\r\n"
            elif self.storageOption == 2:
                currentBlob = bucket.blob(c.BLOB_NAME)
                dict = {}
                if currentBlob.exists():
                    dict = json.loads(currentBlob.download_as_string())
                    dict[key] = value.strip()
                    self.data[key] = value.strip()
                    currentBlob.upload_from_string(json.dumps(dict),content_type='application/json')
                    return "STORED\r\n"
                else:
                    return "NOT STORED\r\n"
            elif self.storageOption == 3:
                self.data[key] = value
                r.set(key,value)
                return "STORED\r\n"
                
                    
    
def processClientCalls(socketConnection,socketAddress,keyValueStore):
    with kvs.concurrentTasks:
        print(f"Accepted connection from {socketAddress}")
        while True:
            try:
                request = socketConnection.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT).strip()
                
                if not request:
                    print("END\r\n")
                    break
                
                if request == "exit":
                    keyValueStore.serverEvent.set()
                    response = "ok\n"
                    socketConnection.send(response.encode(encoding=c.FORMAT))
                    break
                
                data = None
                data = request.split()
                
                command = data[0]
                if command == 'get':
                    key = data[1]
                    response = keyValueStore.getData(key)
                elif command == 'set':
                    key = data[1]
                    value = ' '.join(data[4:])
                    value = value.strip('\\r\\n')
                    response = keyValueStore.setData(key,value)
                else:
                    response = f'Invalid Command'
                socketConnection.send(response.encode(encoding=c.FORMAT))
            except Exception as e:
                print(f"Error: {e}")
                print(f'Request: {request} has error {e}')
                response = 'ERROR\n'
                socketConnection.send(response.encode(encoding=c.FORMAT))
                break
        socketConnection.close()

def startServer():
    host = c.SERVER
    port = c.PORT
    socketserver = socket(AF_INET, SOCK_STREAM)
    try:
        socketserver.bind((host, port))
    except OSError as e:
        socketserver.bind(('0.0.0.0', port))
    socketserver.listen()
    print(f'Server Started on host {host}.')
    
    try:
        while True:
            socketConnection, socketAddress = socketserver.accept()
            tasks = threading.Thread(target=processClientCalls,args=(socketConnection, socketAddress,kvs))
            tasks.start()
            print("Current Active Connections in Threading", threading.activeCount() - 1)
            #tasks.join()
            if kvs.serverEvent.is_set():
                break
        socketserver.close()

    except RuntimeError as e:
        print(f'Runtime Error : {e}')   
    except BrokenPipeError as e:
        print(f'Broken Pipe Error : {e}')
    except IOError as e:
        print(f'I/O Error : {e}') 
    except Exception as e:
        print(f'{e}')
    except KeyboardInterrupt:
        print("Close server connection !!")
        socketserver.close()
    print("Close server connection !!")
    socketserver.close()

fileName = c.FILENAME
storageChoice = input("Choose 1. Local VM Disk 2.Google Cloud Storage Bucket 3. Redis Memory Store\n")
storageOption = int(storageChoice)
kvs = KeyValueStore(fileName,storageOption,bucket)
startServer()
