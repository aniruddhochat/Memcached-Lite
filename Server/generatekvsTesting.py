import random
import string
import os
keys =[]
values = []
keyValuePair = []

for i in range(100):
    key = f'key{i}'
    value = f'value{i}'
    keyValue = f'{key},{value}'
    keyValuePair.append(keyValue)

keyValuePairFileName ="KeyValueStore.txt"

with open(keyValuePairFileName,"w") as keyValuePairFile:
   keyValuePairFile.write('\n'.join(keyValuePair))

print('key-value file generated successfully')