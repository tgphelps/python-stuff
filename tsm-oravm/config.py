#!/usr/bin/env python3

import sys

import util

# ----- CONSTANTS -----

VERSION = '1.4'
CONFIG = './oravm-config'
DEF_SCHED = 'ANY'

# ----- CLASSES -----

class Vm:
    def __init__(self, name, pri, intvl, repos, sch, local, retain):
        self.name = name
        self.priority = int(pri)
        self.interval = float(intvl)
        self.repos = repos
        self.schedule = sch
        self.local = float(local)
        self.retain = int(retain)
        # Age and days_late will be used when this
        # VM gets added to the work queue
        self.age = 0
        self.days_late = 0



class Repos:
    def __init__(self, name, server, share, mount):
        self.name = name
        self.server = server
        self.share = share
        self.mount = mount


# Default config values

# These values are overwritten by the config file entries.

cfg_temp = '/tmp/'
cfg_history = '/tmp/'
cfg_tmpout = cfg_temp + 'tgptsm.out'
cfg_max_duration = 60
cfg_max_megabytes = 20
cfg_logfile = cfg_temp + 'ORAVMLOG'
cfg_loglevel = 'DEBUG'
cfg_mail_to = ['tgphelps@acbl.net']
cfg_inventory = '/tmp/'
cfg_database = 'inventory.db'
cfg_vm_list = []
cfg_repos_list = []
# The config file MUST override this.
cfg_local_dir = '/invalid'
cfg_borg_repos = '/invalid'
cfg_tsm_enable = True



# Functions

def print_config():
    print('CONFIG')
    print('temp =', cfg_temp)
    print('history =', cfg_history)
    print('max duration (secs) =', cfg_max_duration)
    print('max megabytes =', cfg_max_megabytes)
    print('log file =', cfg_logfile)
    print('log level =', cfg_loglevel)
    print('mail to =', cfg_mail_to)
    print('inventory =', cfg_inventory)
    print('local =', cfg_local_dir)
    print('borg =', cfg_borg_repos)
    print('tsm enabled =', cfg_tsm_enable)



def do_temp(d):
    global cfg_temp
    global cfg_tmpout

    assert d['label'] == 'temp'
    assert 'dir' in d

    cfg_temp = d['dir']
    cfg_tmpout = cfg_temp + 'tgptsm.out'



def do_history(d):
    global cfg_history

    assert d['label'] == 'history'
    assert 'dir' in d

    cfg_history = d['dir']



def do_log(d):
    global cfg_logfile
    global cfg_loglevel

    assert d['label'] == 'log'
    if 'fil' in d:
        cfg_logfile = d['fil']
    if 'lev' in d:
        cfg_loglevel = d['lev']



def do_mail(d):
    global cfg_mail_to
    assert d['label'] == 'mail'
    assert 'to' in d

    cfg_mail_to = []
    # For now, we allow only ONE email address
    cfg_mail_to.append(d['to'])



def do_backup(d):
    global cfg_max_duration
    global cfg_max_megabytes

    assert d['label'] == 'backup'
    if 'dur' in d:
        # convert minutes to seconds
        cfg_max_duration = int(d['dur']) * 60
    if 'max' in d:
        # convert gigs to megs
        cfg_max_megabytes = int(d['max']) * 1024



# Append a Vm object to cfg_vm_list

def do_vm(d):
    name = d['nam'].lower()
    pri = d['pri']
    intvl = d['int']
    repos = d['rep']
    # Verify that 'repos' is legal
    ok = 0
    for r in cfg_repos_list:
        if r.name == repos: ok = 1
    if not ok:
        util.perror('Invalid repos {} in VM {} config'.format(repos, name))
        raise
    if 'sch' in d:
        sch = d['sch']
    else:
        sch = DEF_SCHED
    if 'loc' in d:
        local = d['loc']
        iloc = float(local)
        assert iloc > 0.0
    else:
        # Zero mean 'never do local backup'
        local = 0
    if 'ret' in d:
        retain = d['ret']
        assert int(retain) > 0
    else:
        retain = 9999
    cfg_vm_list.append(Vm(name, pri, intvl, repos, sch, local, retain))



def do_repos(d):
    name = d['nam']
    server = d['ser']
    share = d['sha']
    mount = d['mou']
    cfg_repos_list.append(Repos(name, server, share, mount))



def do_inventory(d):
    global cfg_inventory

    assert 'dir' in d
    cfg_inventory = d['dir']



def do_database(d):
    global cfg_database

    assert 'fil' in d
    cfg_database = d['fil']



def do_local(d):
    global cfg_local_dir

    assert 'dir' in d
    cfg_local_dir = d['dir']



def do_borg(d):
    global cfg_borg_repos

    assert 'rep' in d
    cfg_borg_repos = d['rep']



def do_tsm(d):
    global cfg_tsm_enable

    assert 'ena' in d
    if d['ena'] == 'no':
        cfg_tsm_enable = False



def read_one_line(f):
    line = f.readline()
    if not line:
        return None
    else:
        return line



# This function returns the next complete line, including continuation
# lines, from the config file. If the last character of the line is a
# backslash, the line is continued on the next physical line. We will
# fetch lines until we get one that does NOT end with a backslash, and
# then remove all the backslashes and concatenate the lines together,
# and return that long line.

def get_complete_line(f):
    lines = []
    # Get one, possibly continued, line
    while 1:
        line = read_one_line(f)
        if line:
            line = line.strip()
            if line == '':
                line = ' '
            lines.append(line)
            if len(line) == 0 or line[-1] != '\\':
                break
        else:
            break

    # Array 'lines' has all the lines we want
    if len(lines) == 0:
        return None
    if len(lines) == 1:
        return lines[0]
    else:
        # Remove the backslashes and concatenate
        s = ''
        for l in lines:
            if l[-1] == '\\':
                l = l[0:-1] + ' '
            s += l
        return s
    
cfg_func = {
        'temp': do_temp,
        'log': do_log,
        'mail': do_mail,
        'backup': do_backup,
        'vm': do_vm,
        'repos': do_repos,
        'inventory': do_inventory,
        'database': do_database,
        'history': do_history,
        'local': do_local,
        'borg': do_borg,
        'tsm': do_tsm
    }

def read_config():
    with open(CONFIG, 'rt') as f:
        while True:
            line = get_complete_line(f)
            if not line: break
            fld = line.split()
            if len(fld) == 0 or fld[0].startswith('#'):
                continue
            d = util.parse_config_line(fld)
            label = fld[0]
            if label in cfg_func:
                cfg_func[label](d)
            else:
                util.perror('Aborting: invalid config file line:')
                util.perror(line)
                sys.exit(1)



if __name__ == "__main__":
    read_config()
    print_config()

