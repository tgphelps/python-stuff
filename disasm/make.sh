#!/bin/sh

nasm -felf64 hello.asm
ld -o hello hello.o
