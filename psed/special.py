
import eval

def begin(args):
    ret = None
    for arg in args:
        ret = eval.eval(arg)
    # 'ret' contains the value of the last one
    # print("begin returns:", ret)
    return ret


def iff(args):
    nargs = len(args)
    if nargs in (2,3):
        test = eval.eval(args[0])
        if test:
            return eval.eval(args[1])
        else:
            if nargs == 3:
                return eval.eval(args[2])
            else:
                return None

def define(args):
    eval.must_have_args('def', 2, args)
    if args[0][0] != 'ID':
        util.fatal_error("define: bad ID")
    id = args[0][1]
    val = eval.eval(args[1])
    if id in eval.toplevel:
        util.fatal_error(f"def: duplicate definition of {id}")
    eval.toplevel[id] = val

