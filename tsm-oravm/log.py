import time

logf = None
log_level = 1

def log_open(fname):
    global logf
    if logf:
        # log is already open
        log('Duplicate log open')
    else:
        logf = open(fname, 'a')
        log('Log open')

def log_close():
    global logf
    if logf:
        log('Log close')
        logf.close()
        logf = None

def set_level(n):
    global log_level
    log_level = n
    log('Level = ' + str(n), level=1)

def log(msg, level=1):
    global logf, log_level
    if logf and level <= log_level:
        t = time.asctime()
        logf.write(t + ' ' + msg + '\n')
