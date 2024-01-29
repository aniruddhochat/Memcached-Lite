import socket
from random import randint,choice
import subprocess
import configFile as c
import time

def KeyValueStoreClientRandom():
    # host = "127.0.0.1"
    # port = 9888
    host = c.SERVER
    port = c.PORT
    
    command = {0:'get',1:'set'}
    with open('keys.txt', 'r') as keyFile:
        sampleKeys = []
        for line in keyFile:
            sampleKeys.append(line.strip())
    with open('values.txt', 'r') as valueFile:
        sampleValue = []
        for line in valueFile:
            sampleValue.append(line.strip())

    
    clientSocket = socket.socket()
    clientSocket.connect((host, port))
    
    for i in range(0,100):
        currentCommand = command[randint(0, 1)]
        currentKey = choice(sampleKeys)
        if currentCommand == 'get':
            message = f'{currentCommand} {currentKey}'
        elif currentCommand == 'set':
            updatedValue = choice(sampleValue)
            updatedValue.strip()
            message = f'{currentCommand} {currentKey} {len(updatedValue)} \\r\\n {updatedValue} \\r\\n'
        else:
            print("Invalid command")
        print(message)
        clientSocket.send(message.encode(encoding=c.FORMAT))
        data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)
        
        if currentCommand == 'get' and (data is None or data == ''):
            print('Response received from server:\n' + 'KEY NOT FOUND')
        elif currentCommand == 'set' and (data is None or data == ''):
            print('Response received from server:\n' + 'NOT-STORED')
        else:
            print('Response received from server:\n' + data)

    if __name__ == "__main__":
        closingChoice = input("Choose 1. Close Client 2.Close Client and Server Both\n")
        closingOption = int(closingChoice)
        if closingOption==1:
            clientSocket.close()
        elif closingOption == 2:
            message = "exit"
            clientSocket.send(message.encode(encoding=c.FORMAT))
            data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)
            if data == "ok\n":
                clientSocket.close()

def generateFiles(noOfRows):
    keys =[]
    values = []

    for i in range(noOfRows):
        key = f'key{i}'
        value = f'value{i}'
        keyValue = f'{key},{value}'
        keys.append(key)
        values.append(value)
        
        keysFileName = "keys.txt"
        valuesFileName = "values.txt"

        with open(keysFileName,"w") as keyFile:
            keyFile.write('\n'.join(keys))

        with open(valuesFileName,"w") as valueFile:
            valueFile.write('\n'.join(values))
    print('key-value file generated successfully')
                
def getSetPerformance(getSetOption):
    host = c.SERVER
    port = c.PORT
    perfSet = [100,1000,10000,100000]
    perfDict ={}
    clientSocket = socket.socket()
    # if host == '0.0.0.0':
    #     clientSocket.connect((host, port))
    # else:
    #     clientSocket.connect(('0.0.0.0', port))
    
    clientSocket.connect((host, port))
    #generateFiles(max(perfSet))
    with open('keys.txt', 'r') as keyFile:
        sampleKeys = []
        for line in keyFile:
            sampleKeys.append(line.strip())
    with open('values.txt', 'r') as valueFile:
        sampleValue = []
        for line in valueFile:
            sampleValue.append(line.strip())
            
    for perf in perfSet:
        #generateFiles(perf)
        if getSetOption == 1:
            currentCommand = 'get'
            start = time.time()
            for i in range(perf):
                message = f'{currentCommand} {sampleKeys[i]}'
                clientSocket.send(message.encode(encoding=c.FORMAT))
                data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)
                
                if data is None or data == '':
                    print('Response received from server:\n' + 'KEY NOT FOUND')
                else:
                    print('Response received from server:\n' + data)
            end = time.time()
            
            print(f'Get command completed in {end-start} seconds for {len(sampleKeys)} records!!')
            
        elif getSetOption == 2:
            currentCommand = 'set'
            
            start = time.time()
            for i in range(perf):
                message = f'{currentCommand} {sampleKeys[i]} {len(sampleValue[i])} \\r\\n {sampleValue[i]} \\r\\n'
                print(message)
                clientSocket.send(message.encode(encoding=c.FORMAT))
                data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)
                
                if data is None or data == '':
                    print('Response received from server:\n' + 'NOT-STORED')
                else:
                    print('Response received from server:\n' + data)
            end = time.time()
            print(f'Set command completed in {end-start} seconds for {len(sampleKeys)} records!!')
            
        perfDict[perf] = end-start
    print(perfDict)        
    if __name__ == "__main__":
        closingChoice = input("Choose 1. Close Client 2.Close Client and Server Both\n")
        closingOption = int(closingChoice)
        if closingOption==1:
            clientSocket.close()
        elif closingOption == 2:
            message = "exit"
            clientSocket.send(message.encode(encoding=c.FORMAT))
            data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)
            if data == "ok\n":
                clientSocket.close()
                
def callClientManually():
    host = c.SERVER
    port = c.PORT
    clientSocket = socket.socket()
    
    # if host == '0.0.0.0':
    #     clientSocket.connect((host, port))
    # else:
    #     clientSocket.connect(('0.0.0.0', port))
    
    clientSocket.connect((host, port))
    
    
    message = input("Enter the command to be sent to Server:\n->")

    while message.lower().strip() != 'end':
        clientSocket.send(message.encode(encoding=c.FORMAT))
        data = clientSocket.recv(c.HEADER_SIZE).decode(encoding=c.FORMAT)

        print('Response received from server:\n' + data)

        if data == 'ok\n':
            break
        
        message = input("Enter the command to be sent to Server:\n -> ")

    clientSocket.close()

def startClient():
    testingChoice = input("Choose 1. Test Client Calls One by One 2.Performance Testing\n")
    testingOption = int(testingChoice)
    if testingOption == 1:
        callClientManually()
    elif testingOption == 2:
        getSetChoice = input("Choose 1. Test Get Performance 2.Test Set Performance\n")
        getSetOption = int(getSetChoice)
        if getSetOption == 1 or getSetOption == 2:
            getSetPerformance(getSetOption)
    else:
        KeyValueStoreClientRandom()

startClient()