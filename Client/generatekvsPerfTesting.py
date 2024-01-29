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
    keys.append(key)
    values.append(value)
    keyValuePair.append(keyValue)
    
keysFileName = "keys.txt"
valuesFileName = "values.txt"
keyValuePairFileName ="KeyValueStore.txt"

with open(keysFileName,"w") as keyFile:
    keyFile.write('\n'.join(keys))

with open(valuesFileName,"w") as valueFile:
    valueFile.write('\n'.join(values))

#with open(keyValuePairFileName,"w") as keyValuePairFile:
#    keyValuePairFile.write('\n'.join(keyValuePair))

print('key-value file generated successfully')