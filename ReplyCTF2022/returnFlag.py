#!/usr/bin/python3

file = open("flag.txt", 'r')
lines = file.readlines()

flag = ''

for line in lines:
    x = int(line) + 4
    flag += chr(x)
file.close()

print(flag)

