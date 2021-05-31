ELF INvestigator
================
A program to view and explore Intel x64 ELF files, both executable
and relocatable types. Eventually, I hope it can disassemble code.

Usage
-----
    elfin <options> <ELF-file>
    No options yet
Elfin reads commands from stdin and writes to stdout, for now.

Commands
--------
    p hdr | pht | sht
    ('print', 'what')

    d hdr | pht NUM | sht NUM | HEX HEX
    ('dump', 'hdr')
    ('dump', 'what', which)
    ('dump', ('range', start, count))
    help
    ('help')

    q
    ('quit')

cmd -> p-cmd | d-cmd | help-stmt | quit-stmt

help-stmt -> HELP

quit-stmt -> QUIT

p-cmd -> PRINT tbl

tbl -> HDR | PHT | SHT

d-cmd -> DUMP entry
         DUMP range

entry -> PHT NUM
         SHT NUM

range -> NUM NUM
