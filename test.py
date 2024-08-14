from collections import Counter
from random import randint
import time

def xorand(arr):
    count = 0
    print("Array length: ", len(arr))
    unique = Counter(arr)
    
    unique_list = list(unique.keys())
    n = len(unique_list)

    print("Unique list length: ", n)

    for i in range(n):
        for j in range(i+1, n):
            if (unique_list[i] ^ unique_list[j]) > unique_list[i] & unique_list[j]:
                count += unique[unique_list[i]] * unique[unique_list[j]]

    return count

def xoranddefault(arr):
    count = 0
    n = len(arr)
    
    for i in range(n):
        for j in range(i+1, n):
            if (arr[i] ^ arr[j]) > arr[i] & arr[j]:
                count += 1
    
    return count

arr = []

for i in range(100000):
    arr.append(randint(0, 50))
print("Starting now")
start = time.time()

print(xorand(arr))
print(time.time() - start)

start = time.time()

print(xoranddefault(arr))
print(time.time() - start)

