
import sys
import re
from globals import g
import eval
import util


def p(args):
    nargs = len(args)
    if nargs == 1:
        print(args[0])
    elif nargs > 1:
        print(" ".join(str(a) for a in args))
    else:
        print(g.line)

def length(args):
    eval.must_have_args("len", 1, args)
    return len(args[0])

def chkargs_1or2(func,args):
    if len(args) == 1:
        target = g.line
    elif len(args) == 2:
        target = args[1]
    else:
        fatal_bad_args(func)
    return target

def locate(args):
    target = chkargs_1or2("lo", args)
    if args[0] in target:
        return True
    else:
        return False

def search(args):
    target = chkargs_1or2("lo", args)
    if args[0].search(target):
        return True
    else:
        return False

def match(args):
    target = chkargs_1or2("lo", args)
    if args[0].match(target):
        return True
    else:
        return False

def startswith(args):
    target = chkargs_1or2("lo", args)
    if target.startswith(args[0]):
        return True
    else:
        return False

def endswith(args):
    target = chkargs_1or2("lo", args)
    if target.endswith(args[0]):
        return True
    else:
        return False

def compile_regex(args):
    eval.must_have_args("compile-regex", 1, args)
    return re.compile(args[0])
