
import eval

class UnboundVar(Exception):
    pass


class Env:
    def __init__(self, parent, toplevel=False):
        self.parent = parent
        self.toplevel = toplevel
        self.vars = {}

    def add(self, id, value):
        "Add a var and var to this Env"
        if id in self.vars:
            # Should this be allowed
            assert False
        else:
            self.vars[id] = value

    def find(self, id):
        "Search this Env for a var"
        if id in self.vars:
            return (id, self.vars[id])
        else:
            return None

    def get_parent(self):
        return self.parent

    def get_all(self):
        "Return all (id,val) pairs in this Env"
        ents = []
        for k, v in self.vars.items():
            ents.append((k, v))
        return ents

    def search(self, id):
        "Lookup id in the chain of Envs, starting here"
        # print("searching:", self)
        ret = self.find(id)
        if ret:
            return ret
        else:
            env = self.parent
            while env:
                ret = env.find(id)
                if ret:
                    return ret[1]
                else:
                    env = env.get_parent()
                    # print("Try env:", env)
            # 'id' is not in any env. Maybe it's a builtin.
            return eval.get_builtin(id)


if __name__ == '__main__':
    env1 = Env(None)
    env1.add('x', 1)

    val = env1.find('x')
    print(f"value of x is {val[1]}")

    env1.add('y', 2)
    vars = env1.get_all()
    print('env1', vars)

    env2 = Env(env1)
    # env2.add('x', 3)

    # val = env2.find('x')
    # print(f"value of x is {val}")

    env2.add('y', 5)
    vars = env2.get_all()
    print('env2', vars)

    val = env2.search('y')
    print(f"y is {val}")
    val = env2.search('x')
    print(f"x is {val}")

    # print("back to env1")
    # env = env2.get_parent()
    # vars = env.get_all()
    # print(vars)

    print("Should raise exception")
    val = env2.search('xxx')
