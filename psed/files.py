
import sys

def next_line(files):
    for f in files:
        file = f
        line_num = 0
        if f == '-':
            for line in sys.stdin:
                line_num += 1
                yield file, line_num, line.rstrip()
        else:
            with open(f, 'rt') as fd:
                for line in fd:
                    line_num += 1
                    yield file, line_num, line.rstrip()

def main():
    files = ['files.py', '-']
    for line in next_line(files):
        print(line)

if __name__ == '__main__':
    main()
