#CTF #binary

---
## File overview
```bash
~/Reply/Binary100 $ file mlem

mlem: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=e086d1324eb201f3cde089a265f1e303cdb28238, for GNU/Linux 3.2.0, stripped
```
Opening the file with ghidra we can see a ptrace which we will deal later and \[...\].
![[Screenshot 2022-10-20 at 09.21.30.png | 400]]
Reading the code we understand that the program takes the lenght of the input word and uses it to call a `for loop` which copies the characters of our word into the variable `local_918`, whose size is only 4 chars.  If the input word's length is greater than 4 the other characters will overflow and will overwrite the content of the other variables in the stack.
Then we see a bunch of `if` statements with basic equations using the variables in the stack conditions.
![[Screenshot 2022-10-20 at 09.22.16.png | 400]]
Solving the equations we get the decimal values of ascii printable characters:
```TXT
    INPUT[0] - 	119  : 	w
    INPUT[1] - 	66   : 	B
    INPUT[2] - 	72   : 	H
    INPUT[3] - 	67   : 	C
	OFW1 - 		54   : 	6
    OFW2 - 		44   : 	,
    OFW3 - 		114  : 	r
    OFW4 - 		47   : 	/
    OFW5 - 		110  : 	n
    OFW6 - 		104  : 	h
    OFW7 - 		48   : 	0
    OFW8 - 		108  : 	l
    OFW9 - 		108  : 	l
	OFW10 - 	47   : 	/
    OFW11 - 	96   : 	`
    OFW12 - 	91   : 	[
    OFW13 - 	45   : 	-
    OFW14 - 	49   : 	1
    OFW15 - 	91   : 	[
    OFW16 - 	95   : 	_
    OFW17 - 	44   : 	,
    OFW18 - 	44   : 	,
    OFW19 - 	104  : 	h
    OFW20 - 	121  : 	y
```

Final string:
```
wBHC6,r/nh0ll/`[-1[_,,hy
```

![[Screenshot 2022-10-20 at 09.57.07.png | 400]]
## GDB
Now we run the file inside gdb but we have to remeber to bypass the ptrace.

// Bypass ptrace

After inserting the word we continue by single instruction and we can see that the only thing th function does is adding 0x04 to every char so I wrote a python script to do so and get the flag.
```TXT
/flag.txt
119
66
72
67
54
44
114
47
110
104
48
108
108
47
96
91
45
49
91
95
44
44
104
121
```
```python
#!/bin/python3

file = open("flag.txt", 'r')
lines = file.readlines()

flag = ''

for line in lines:
    x = int(line) + 4
    flag += chr(x)
file.close()

print(flag)

```
