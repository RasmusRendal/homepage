---
title: "Assembly Reference"
date: 2021-10-03T18:49:51+02:00
draft: false
---
I'm pretty good at learning x86_64 assembly.
I've done it more times than I can count.
But now I've reached the point where I would like to stop learning assembly, and just have a good reference for assembly.
But I couldn't find one, so I made a reference for assembly.

This reference is a work in progress, and will be continuously updated as I find myself looking up stuff. 

## General Purpose Registers
The following are the "general purpose" registers for x86_64.
The calling convention describes the convention for *nix systems.
All registers not denoted "Callee Saved" are caller saved, if required.
| Quadword | Doubleword | Word | Byte | Calling Convention           |
| -------- | ---------- | ---- | ---- | ---------------------------  |
| rax      | eax        | ax   | al   | Return Value                 |
| rbx      | ebx        | bx   | bl   | Callee Saved                 |
| rcx      | ecx        | cx   | cl   | Argument 4                   |
| rdx      | edx        | dx   | dl   | Argument 3                   |
| rsi      | esi        | si   | sil  | Argument 2                   |
| rdi      | edi        | di   | dil  | Argument 1                   |
| rbp      | ebp        | bp   | bpl  | Base Pointer (Callee Saved)  |
| rsp      | esp        | sp   | spl  | Stack Pointer (Callee Saved) |
| r8       | r8d        | r8w  | r8b  | Argument 5                   |
| r9       | r9d        | r9w  | r9b  | Argument 6                   |
| r10      | r10d       | r10w | r10b |                              |
| r11      | r11d       | r11w | r11b |                              |
| r12      | r12d       | r12w | r12b | Callee Saved                 |
| r13      | r13d       | r13w | r13b | Callee Saved                 |
| r14      | r14d       | r14w | r14b | Callee Saved                 |
| r15      | r15d       | r15w | r15b | Callee Saved                 |

## rFlags
The rFlags register is a special register that contains information about the status of, amongst other things, arithmetic operations.
It is used a lot in, for instance, control flow operations.
Many of them are "system registers", which I haven't had a reason to care about yet, and therefore are not included.

| Bit  | Mnemonic | Description         |
| ---- | -------- | -----------         |
| 0    | CF       | Carry Flag          |
| 2    | PF       | Parity Flag         |
| 4    | AF       | Auxilary Carry Flag |
| 6    | ZF       | Zero Flag           |
| 7    | SF       | Sign Flag           |
| 10   | DF       | Direction Flag      |
| 11   | OF       | Overflow Flag       |

### Carry Flag
If the last integer operation has resulted in a carry on the most significant bit, the value of this flag is set to 1. Otherwise, it is set to zero.
On subtraction, it is set to one in the case of a borrow.

It is not changed by increment, decrement. Bit shifting shift into the carry flag.

### Zero flag
If the last arithmetic operation resulted in zero, this flag is set to one, otherwise it is set to zero.
This flag is also set by the `test` and `cmp` instructions.

## Instructions
### cbw/cwde/cdqe
These instructions [sign extend](https://en.wikipedia.org/wiki/Sign_extension) `al` into `ax`, `ax` into `eax`, and `eax` into `rax`, respectively.
### mov
First of all, [`mov`](https://github.com/xoreaxeaxeax/movfuscator) is Turing-complete.
So keep this in mind before stepping into this particular hell.
 * The `zx` affix means that the `mov` does sign extension
### jmp
The `jmple`, `jmpge`, etc. are computed based on the information in rFlags.
Things like `jmple` can be computed by combining the information from the carry flag and the zero flag.

## Mistakes
If you found something wrong, or a notable omission, I would love to hear it. Please, send me an [e-mail](mailto:rasmus@rend.al).

# Sources / Further Information:
 * [Wikipedia: X86 calling convention](https://en.wikipedia.org/wiki/X86_calling_conventions)
 * [AMD64 Architecture Programmer's Manual](https://www.amd.com/en/support/tech-docs/amd64-architecture-programmers-manual-volumes-1-5)
