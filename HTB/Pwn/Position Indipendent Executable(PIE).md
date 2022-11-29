# Position Indipendent Executable(PIE)

This protection works by randomizing the address where to place the machine code and executing it regardless of its absolute address. It uses GOT for access to all functions that are used in the program. Addresses in GOT also are not absolute. I disabled this protection before with `--no-pie` argument.

Firstly, let's see the `stack-overflow` binary without PIE in gdb:
```bash
gef➤  disas main
Dump of assembler code for function main:
   0x08049243 <+0>:	endbr32
   0x08049247 <+4>:	push   ebp
   0x08049248 <+5>:	mov    ebp,esp
   0x0804924a <+7>:	and    esp,0xfffffff0
   0x0804924d <+10>:	call   0x8049263 <__x86.get_pc_thunk.ax>
   0x08049252 <+15>:	add    eax,0x2dae
   0x08049257 <+20>:	call   0x8049211 <vuln_func>
   0x0804925c <+25>:	mov    eax,0x0
   0x08049261 <+30>:	leave  
   0x08049262 <+31>:	ret    
End of assembler dump.
gef➤  
gef➤  r
Starting program: /home/shogun/repos/basics-of-pwn/content/stack-overflow/stack-overflow
AAAA

Breakpoint 1, 0x08049262 in main ()

0x8049257 <main+20>        call   0x8049211 <vuln_func>
 0x804925c <main+25>        mov    eax, 0x0
 0x8049261 <main+30>        leave  
→  0x8049262 <main+31>        ret    
↳  0xf7ddaee5 <__libc_start_main+245> add    esp, 0x10
   0xf7ddaee8 <__libc_start_main+248> sub    esp, 0xc
   0xf7ddaeeb <__libc_start_main+251> push   eax
   0xf7ddaeec <__libc_start_main+252> call   0xf7df4170 <exit>
   0xf7ddaef1 <__libc_start_main+257> push   esi
   0xf7ddaef2 <__libc_start_main+258> push   esi
```

You can see that addresses of instructions is fixed to concrete addresses. Even in output of objdump you can find exactly the same addresses:
```bash
08049243 <main>:
 8049243:	f3 0f 1e fb          	endbr32
 8049247:	55                   	push   %ebp
 8049248:	89 e5                	mov    %esp,%ebp
 804924a:	83 e4 f0             	and    $0xfffffff0,%esp
 804924d:	e8 11 00 00 00       	call   8049263 <__x86.get_pc_thunk.ax>
 8049252:	05 ae 2d 00 00       	add    $0x2dae,%eax
 8049257:	e8 b5 ff ff ff       	call   8049211 <vuln_func>
 804925c:	b8 00 00 00 00       	mov    $0x0,%eax
 8049261:	c9                   	leave  
 8049262:	c3                   	ret
```

Consider the binary with enabled PIE in gdb:
```bash
gef➤  disas main
Dump of assembler code for function main:
   0x0000127a <+0>:	endbr32
   0x0000127e <+4>:	push   ebp
   0x0000127f <+5>:	mov    ebp,esp
   0x00001281 <+7>:	and    esp,0xfffffff0
   0x00001284 <+10>:	call   0x129a <__x86.get_pc_thunk.ax>
   0x00001289 <+15>:	add    eax,0x2d47
   0x0000128e <+20>:	call   0x1248 <vuln_func>
   0x00001293 <+25>:	mov    eax,0x0
   0x00001298 <+30>:	leave  
   0x00001299 <+31>:	ret    
End of assembler dump.
gef➤  
gef➤  r
Starting program: /home/shogun/repos/basics-of-pwn/content/security-techniques/stack-overflow-with-pie
AAAA

Breakpoint 1, 0x56556299 in main ()

0x5655628e <main+20>        call   0x56556248 <vuln_func>
0x56556293 <main+25>        mov    eax, 0x0
0x56556298 <main+30>        leave  
→ 0x56556299 <main+31>        ret    
↳  0xf7ddaee5 <__libc_start_main+245> add    esp, 0x10
   0xf7ddaee8 <__libc_start_main+248> sub    esp, 0xc
   0xf7ddaeeb <__libc_start_main+251> push   eax
   0xf7ddaeec <__libc_start_main+252> call   0xf7df4170 <exit>
   0xf7ddaef1 <__libc_start_main+257> push   esi
   0xf7ddaef2 <__libc_start_main+258> push   esi
```
Here, we have the same instructions as if it was without PIE.

Let's see the GOT.

Without PIE:
```bash
gef➤  got

GOT protection: Partial RelRO | GOT functions: 4

[0x804c00c] gets@GLIBC_2.0  →  0xf7e2d1b0
[0x804c010] system@GLIBC_2.0  →  0x8049050
[0x804c014] __libc_start_main@GLIBC_2.0  →  0xf7ddadf0
[0x804c018] setuid@GLIBC_2.0  →  0x8049070
gef➤
```

With PIE:
```bash
gef➤  got

GOT protection: Full RelRO | GOT functions: 4

[0x56558fdc] gets@GLIBC_2.0  →  0xf7e2d1b0
[0x56558fe0] system@GLIBC_2.0  →  0xf7e01830
[0x56558fe4] __libc_start_main@GLIBC_2.0  →  0xf7ddadf0
[0x56558fe8] setuid@GLIBC_2.0  →  0xf7e8a0f0
gef➤
```

This is proof that all addresses come from the addition of the static addresses + some random base offset.

Thus, not a classic stack overflow attack with shellcode nor a ret2libc attack doesn't work with this protection. But, again like with other security techniques that we discussed before this protection can be evaded. For this, you need to have a vulnerable place in the program to somehow leak the one address of the program and then calculate the offset and use it offset in the future to calculate all needed addresses for your attack whether it's a classic shellcode injection or ret2libc attack.
