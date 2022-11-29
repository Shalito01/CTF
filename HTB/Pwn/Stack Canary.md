# Stack Canary

It is a protection against stack overflow that works by placing an integer value onto the stack and check it in each function return, if it was changed, then the program exits immediately. this value changes every time the program is started. To disable this protection you need to compile the program with `-fno-stack-protector` argument.

Let's try to smash the stack. But firstly, consider the low-level code of the vuln_func():
```bash
$ gdb -q stack-overflow-with-canary
gef➤  disas vuln_func
Dump of assembler code for function vuln_func:
   0x08049231 <+0>:	endbr32
   0x08049235 <+4>:	push   ebp
   0x08049236 <+5>:	mov    ebp,esp
   0x08049238 <+7>:	push   ebx
   0x08049239 <+8>:	sub    esp,0x104
   0x0804923f <+14>:	call   0x80492a0 <__x86.get_pc_thunk.ax>
   0x08049244 <+19>:	add    eax,0x2dbc
   0x08049249 <+24>:	mov    ecx,DWORD PTR gs:0x14
   0x08049250 <+31>:	mov    DWORD PTR [ebp-0xc],ecx
   0x08049253 <+34>:	xor    ecx,ecx
   0x08049255 <+36>:	sub    esp,0xc
   0x08049258 <+39>:	lea    edx,[ebp-0x106]
   0x0804925e <+45>:	push   edx
   0x0804925f <+46>:	mov    ebx,eax
   0x08049261 <+48>:	call   0x8049090 <gets@plt>
   0x08049266 <+53>:	add    esp,0x10
   0x08049269 <+56>:	nop
   0x0804926a <+57>:	mov    eax,DWORD PTR [ebp-0xc]
   0x0804926d <+60>:	xor    eax,DWORD PTR gs:0x14
   0x08049274 <+67>:	je     0x804927b <vuln_func+74>
   0x08049276 <+69>:	call   0x8049330 <__stack_chk_fail_local>
   0x0804927b <+74>:	mov    ebx,DWORD PTR [ebp-0x4]
   0x0804927e <+77>:	leave  
   0x0804927f <+78>:	ret    
End of assembler dump.
gef➤
```

Now here we have a new function call `0x08049276 <+69>: call 0x8049330 <__stack_chk_fail_local>`, which do the check of the canary. Also, you can see that we have also a generation of the canary with `0x08049249 <+24>: mov ecx,DWORD PTR gs:0x14` and then placing it onto the stack with `0x08049250 <+31>: mov DWORD PTR [ebp-0xc],ecx`.

Smash the stack:
```bash
gef➤  r < <(python -c 'print "A" * 250')
Starting program: /home/shogun/repos/basics-of-pwn/content/security-techniques/stack-overflow-with-canary < <(python -c 'print "A" * 250')
[Inferior 1 (process 6667) exited normally]
gef➤  r < <(python -c 'print "A" * 260')
Starting program: /home/shogun/repos/basics-of-pwn/content/security-techniques/stack-overflow-with-canary < <(python -c 'print "A" * 260')
*** stack smashing detected ***: terminated

Program received signal SIGABRT, Aborted.
0xf7fd0b49 in __kernel_vsyscall ()
```
Stack crashed and the program exited.

There are two methods to bypass stack canary: leak the canary and brute-force it.

## Stack canary leaking

This is possible if you have some vulnerable code that allows you to read the memory of the stack and see it in output. So, for example, you will have the format string vulnerability and with it, you can leak the canary which you then use in you exploit and bypass this protection(Actually, here, there is no way to do a nice exploit without using pwntools. It is too hard to deal with output and so on...)

## Brute-force the canary

The canary is placed at the start of the program. So, if it has a few forks and we can control input in them, then we can brute-force through them our canary.
