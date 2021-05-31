
import sys
from globals import g
import eval
    
def plus(args):
    return sum(args)

def minus(args):
    nargs = len(args)
    if nargs == 2:
        return args[0] - args[1]
    elif nargs == 1:
        return -args[0]
    else:
        util.fatal_error("minus takes 1 or 2 args")

def times(args):
    nargs = len(args)
    product = 1
    for arg in args:
        product *= arg
    return product

def div(args):
    eval.must_have_args("divide", 2, args)
    return args[0] // args[1]

def eq(args):
    eval.must_have_args("eq", 2, args)
    if args[0] == args[1]:
        return True
    else:
        return False

def lt(args):
    eval.must_have_args("lt", 2, args)
    if args[0] < args[1]:
        return True
    else:
        return False

def gt(args):
    eval.must_have_args("gt", 2, args)
    if args[0] > args[1]:
        return True
    else:
        return False
