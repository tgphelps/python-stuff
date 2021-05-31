
import sys

def fatal_error(msg):
    print("ERROR:", msg, file=sys.stderr)
    sys.exit(2)
