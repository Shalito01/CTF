## ELF header
`readelf -h ./hunting`
```bash
ELF Header:
  Magic:   7f 45 4c 46 01 01 01 00 00 00 00 00 00 00 00 00
Class:                             ELF32
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              DYN (Position-Independent Executable file)
  Machine:                           Intel 80386
  Version:                           0x1
  Entry point address:               0x1200
  Start of program headers:          52 (bytes into file)
  Start of section headers:          12804 (bytes into file)
  Flags:                             0x0
  Size of this header:               52 (bytes)
  Size of program headers:           32 (bytes)
  Number of program headers:         12
  Size of section headers:           40 (bytes)
  Number of section headers:         29
  Section header string table index: 28
```

## Program header

```bash
Elf file type is DYN (Position-Independent Executable file)
Entry point 0x1200
There are 12 program headers, starting at offset 52

Program Headers:
  Type           Offset   VirtAddr   PhysAddr   FileSiz MemSiz  Flg Align
  PHDR           0x000034 0x00000034 0x00000034 0x00180 0x00180 R   0x4
  INTERP         0x0001b4 0x000001b4 0x000001b4 0x00013 0x00013 R   0x1
      [Requesting program interpreter: /lib/ld-linux.so.2]
  LOAD           0x000000 0x00000000 0x00000000 0x00570 0x00570 R   0x1000
  LOAD           0x001000 0x00001000 0x00001000 0x005f4 0x005f4 R E 0x1000
  LOAD           0x002000 0x00002000 0x00002000 0x00210 0x00210 R   0x1000
  LOAD           0x002ea8 0x00003ea8 0x00003ea8 0x00228 0x0022c RW  0x1000
  DYNAMIC        0x002eb0 0x00003eb0 0x00003eb0 0x000f8 0x000f8 RW  0x4
  NOTE           0x0001c8 0x000001c8 0x000001c8 0x00060 0x00060 R   0x4
  GNU_PROPERTY   0x0001ec 0x000001ec 0x000001ec 0x0001c 0x0001c R   0x4
  GNU_EH_FRAME   0x002048 0x00002048 0x00002048 0x0005c 0x0005c R   0x4
  GNU_STACK      0x000000 0x00000000 0x00000000 0x00000 0x00000 RWE 0x10
  GNU_RELRO      0x002ea8 0x00003ea8 0x00003ea8 0x00158 0x00158 R   0x1

 Section to Segment mapping:
  Segment Sections...
   00
   01     .interp
   02     .interp .note.gnu.build-id .note.gnu.property .note.ABI-tag .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rel.dyn .rel.plt
   03     .init .plt .plt.got .plt.sec .text .fini
   04     .rodata .eh_frame_hdr .eh_frame
   05     .init_array .fini_array .dynamic .got .data .bss
   06     .dynamic
   07     .note.gnu.build-id .note.gnu.property .note.ABI-tag
   08     .note.gnu.property
   09     .eh_frame_hdr
   10
   11     .init_array .fini_array .dynamic .got
```
## Section header
```bash
There are 29 section headers, starting at offset 0x3204:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .interp           PROGBITS        000001b4 0001b4 000013 00   A  0   0  1
  [ 2] .note.gnu.bu[...] NOTE            000001c8 0001c8 000024 00   A  0   0  4
  [ 3] .note.gnu.pr[...] NOTE            000001ec 0001ec 00001c 00   A  0   0  4
  [ 4] .note.ABI-tag     NOTE            00000208 000208 000020 00   A  0   0  4
  [ 5] .gnu.hash         GNU_HASH        00000228 000228 000020 04   A  6   0  4
  [ 6] .dynsym           DYNSYM          00000248 000248 000140 10   A  7   1  4
  [ 7] .dynstr           STRTAB          00000388 000388 0000de 00   A  0   0  1
  [ 8] .gnu.version      VERSYM          00000466 000466 000028 02   A  6   0  2
  [ 9] .gnu.version_r    VERNEED         00000490 000490 000030 00   A  7   1  4
  [10] .rel.dyn          REL             000004c0 0004c0 000048 08   A  6   0  4
  [11] .rel.plt          REL             00000508 000508 000068 08  AI  6  24  4
  [12] .init             PROGBITS        00001000 001000 000024 00  AX  0   0  4
  [13] .plt              PROGBITS        00001030 001030 0000e0 04  AX  0   0 16
  [14] .plt.got          PROGBITS        00001110 001110 000020 10  AX  0   0 16
  [15] .plt.sec          PROGBITS        00001130 001130 0000d0 10  AX  0   0 16
  [16] .text             PROGBITS        00001200 001200 0003d9 00  AX  0   0 16
  [17] .fini             PROGBITS        000015dc 0015dc 000018 00  AX  0   0  4
  [18] .rodata           PROGBITS        00002000 002000 000046 00   A  0   0  4
  [19] .eh_frame_hdr     PROGBITS        00002048 002048 00005c 00   A  0   0  4
  [20] .eh_frame         PROGBITS        000020a4 0020a4 00016c 00   A  0   0  4
  [21] .init_array       INIT_ARRAY      00003ea8 002ea8 000004 04  WA  0   0  4
  [22] .fini_array       FINI_ARRAY      00003eac 002eac 000004 04  WA  0   0  4
  [23] .dynamic          DYNAMIC         00003eb0 002eb0 0000f8 08  WA  7   0  4
  [24] .got              PROGBITS        00003fa8 002fa8 000058 04  WA  0   0  4
  [25] .data             PROGBITS        00004000 003000 0000d0 00  WA  0   0 32
  [26] .bss              NOBITS          000040d0 0030d0 000004 00  WA  0   0  1
  [27] .comment          PROGBITS        00000000 0030d0 00002b 01  MS  0   0  1
  [28] .shstrtab         STRTAB          00000000 0030fb 000108 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings), I (info),
  L (link order), O (extra OS processing required), G (group), T (TLS),
  C (compressed), x (unknown), o (OS specific), E (exclude),
  D (mbind), p (processor specific)
```
  
## ELF features

### Base address
The virtual addresses in the program headers might not represent the actual virtual addresses of the program's memory image. The system chooses virtual addresses for individual processes, it maintains the segments’ relative positions. Because position-independent code uses relative addressing between segments, the difference between virtual addresses in memory must match the difference between virtual addresses in the file.

Thus, the base address for a process is a single constant value that represents the difference between the virtual addresses in memory and the virtual addresses in the file.

### Global Offset Table (GOT)
```bash
gef➤  got
[*] .gef-2b72f5d0d9f0f218a91cd1ca5148e45923b950d5.py:L8817 'checksec' is deprecated and will be removed in a feature release. Use Elf(fname).checksec()

GOT protection: Full RelRO | GOT functions: 13

[0x56558fb4] read@GLIBC_2.0  →  0xf7e7d0c0
[0x56558fb8] signal@GLIBC_2.0  →  0xf7daa600
[0x56558fbc] alarm@GLIBC_2.0  →  0xf7e50b00
[0x56558fc0] perror@GLIBC_2.0  →  0xf7dcad30
[0x56558fc4] strcpy@GLIBC_2.0  →  0xf7e15700
[0x56558fc8] open@GLIBC_2.0  →  0xf7e7cb40
[0x56558fcc] srand@GLIBC_2.0  →  0xf7dadf30
[0x56558fd0] mmap@GLIBC_2.0  →  0xf7e8f290
[0x56558fd4] __libc_start_main@GLIBC_2.0  →  0xf7d94560
[0x56558fd8] memset@GLIBC_2.0  →  0xf7eede90
[0x56558fdc] prctl@GLIBC_2.0  →  0xf7e954a0
[0x56558fe0] rand@GLIBC_2.0  →  0xf7dae620
[0x56558fe4] close@GLIBC_2.0  →  0xf7e7de10
gef➤  vmmap
[ Legend:  Code | Heap | Stack ]
Start      End        Offset     Perm Path
0x56555000 0x56556000 0x000000 r-- /home/dady/hunting
0x56556000 0x56557000 0x001000 r-x /home/dady/hunting
0x56557000 0x56558000 0x002000 r-- /home/dady/hunting
0x56558000 0x56559000 0x002000 r-- /home/dady/hunting
0x56559000 0x5655a000 0x003000 rw- /home/dady/hunting
0x7a560000 0x7a561000 0x000000 rw- /dev/zero (deleted)
0xf7d73000 0xf7d93000 0x000000 r-- /usr/lib/i386-linux-gnu/libc.so.6
0xf7d93000 0xf7f15000 0x020000 r-x /usr/lib/i386-linux-gnu/libc.so.6
0xf7f15000 0xf7f9a000 0x1a2000 r-- /usr/lib/i386-linux-gnu/libc.so.6
0xf7f9a000 0xf7f9b000 0x227000 --- /usr/lib/i386-linux-gnu/libc.so.6
0xf7f9b000 0xf7f9d000 0x227000 r-- /usr/lib/i386-linux-gnu/libc.so.6
0xf7f9d000 0xf7f9e000 0x229000 rw- /usr/lib/i386-linux-gnu/libc.so.6
0xf7f9e000 0xf7fa8000 0x000000 rw-
0xf7fbd000 0xf7fbe000 0x000000 rwx /dev/zero (deleted)
0xf7fbe000 0xf7fc0000 0x000000 rw-
0xf7fc0000 0xf7fc4000 0x000000 r-- [vvar]
0xf7fc4000 0xf7fc6000 0x000000 r-x [vdso]
0xf7fc6000 0xf7fc7000 0x000000 r-- /usr/lib/i386-linux-gnu/ld-linux.so.2
0xf7fc7000 0xf7fec000 0x001000 r-x /usr/lib/i386-linux-gnu/ld-linux.so.2
0xf7fec000 0xf7ffb000 0x026000 r-- /usr/lib/i386-linux-gnu/ld-linux.so.2
0xf7ffb000 0xf7ffd000 0x034000 r-- /usr/lib/i386-linux-gnu/ld-linux.so.2
0xf7ffd000 0xf7ffe000 0x036000 rw- /usr/lib/i386-linux-gnu/ld-linux.so.2
0xfffdd000 0xffffe000 0x000000 rwx [stack]
```
The stack has read-write permission and is executable.

## Vulnerability types
- [[Buffer Overflow]]
- [[Stack Overflow]]
- [[Format String Vulnerability]]
- [[Heap Overflow]]

