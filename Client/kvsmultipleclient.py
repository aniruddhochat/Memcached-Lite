import multiprocessing
from kvsclient import KeyValueStoreClientRandom

def executeMultpleClients():
    for _ in range(0,50):
        multipleClients = multiprocessing.Process(target=KeyValueStoreClientRandom)
        multipleClients.start()
executeMultpleClients()
