
import sys
from globals import g
import env
import nums
import special
import strs
import util

def eval(obj):
    if g.trace:
        print("eval:", obj, file=g.trace)
    if type(obj) in (int, str,bool):
        return obj
    if type(obj) == tuple:
        assert obj[0] == 'ID'
        return get_value(obj[1])
    if type(obj) != list:
        util.fatal_error(f"eval: bad obj {type(obj)}")

    # We have a list to evaluate
    f = obj[0][1]
    if f in special:
        ret = func[f](obj[1:])
        if g.trace:
            print("ret:", ret, file=g.trace)
        return ret
    elif f in func:
        args = []
        for a in obj[1:]:
            args.append(eval(a))
        if g.trace:
            print("call:", f, "with", args,  file=g.trace)
        ret = func[f](args)
        if g.trace:
            print("ret:", ret, file=g.trace)
        return ret
    else:
        util.fatal_error(f"unbound function: {f}")
    

def get_value(id):
    # print("lookup", id)
    # print("toplevel:", toplevel)
    if id in toplevel:
        val = toplevel[id]
    else:
        val = get_builtin(id)
    # elif id in builtins:
        # val = get_builtin(id)
    # else:
        # util.fatal_error(f"unbound: {id}")
    if g.trace:
        print("ID", id, "=", val, file=g.trace)
    return val

def get_builtin(id):
    if id == 'line':
        return g.line
    elif id == 'file':
        return g.file_name
    elif id == 'num':
        return g.line_num
    elif id == 'rel_num':
        return g.rel_num
    raise env.UnboundVar


def land(args):
    if len(args) == 0:
        return True
    for arg in args:
        val = eval(arg)
        if not val: return False
    return val

def lor(args):
    if len(args) == 0:
        return False
    for arg in args:
        val = eval(arg)
        if val: return val
    return val


def must_have_args(func, num, args):
    if len(args) != num:
        util.fatal_error(f"function {func} requires {num} args")

def fatal_bad_args(func):
    util.fatal_error(f"function {func}: wrong number of args")

func = {
        'first'   : special.begin
       ,'last'    : special.begin
       ,'foreach' : special.begin
       ,'if'      : special.iff
       ,'p'       : strs.p
       ,'+'       : nums.plus
       ,'-'       : nums.minus
       ,'*'       : nums.times
       ,'/'       : nums.div
       ,'len'     : strs.length
       ,'='       : nums.eq
       ,'<'       : nums.lt
       ,'>'       : nums.gt
       ,'def'     : special.define
       ,'lo'      : strs.locate
       ,'compile-regex' : strs.compile_regex
       ,'se'      : strs.search
       ,'ma'      : strs.match
       ,'startswith' : strs.startswith
       ,'endswith'   : strs.endswith
       ,'and'     : land
       ,'or'      : lor
       }

# Variables that refer to built-in variables

builtins = {
            'line': 0
           ,'file': 0
           ,'rel_num': 0
           ,'num' : 0
          }

# "defines" go here
toplevel = {}

# Functions that should not have their args evaluated

special = {
            'begin': 0
           ,'first': 0
           ,'last': 0
           ,'foreach': 0
           ,'if': 0
           ,'def': 0
           ,'and': 0
          }
