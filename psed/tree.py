

def to_list(tree):
    if tree == None:
        return []
    assert type(tree) == tuple
    l = [tree[0]]
    tail = tree[1]
    while True:
        if type(tail) == tuple:
            l.append(tail[0])
            tail = tail[1]
        else:
            break
    return l

def main():
    tree = None
    tree = (1, None)
    tree = (1, (2, None))
    print(tree)
    l = to_list(tree)
    print(l)

if __name__ == '__main__':
    main()
