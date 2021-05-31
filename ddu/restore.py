
import fnmatch
import gzip
import os
import re
import shutil
import time
from typing import Generator

import parser_ddu as parser

from pager import Pager
from repo import Repo
import util

# -----------------

PROMPT1 = '-> '
PROMPT2 = '*> '
NO_BKUP = '<none>'
NO_DEST = '<none>'

# -----------------


class Globals:
    repo: Repo
    backup: str
    destination: str


g = Globals()
g.backup = NO_BKUP
g.destination = NO_DEST

# -----------------


def restore(repo_file: str) -> None:
    """Interact with the user to perform repo query and backup function."""
    g.repo = Repo(repo_file)
    g.repo.lock()

    parser.init()
    while True:
        result = parser.run(read_statement())
        # if stmt == '':
        #     continue
        # result = (None, None, None, None)
        print('parsed:', result)
        if not result:
            continue

        cmd = result[0]
        if not cmd:
            continue
        if cmd == 'QUIT':
            break
        elif cmd == 'LIST_BACKUPS':
            list_backups()
        elif cmd == 'LIST_FILES':
            list_all_files()
        elif cmd == 'LIST':
            if g.backup == NO_BKUP:
                util.error('You must select a backup first.')
            else:
                list_files(result[1], g.backup)
        elif cmd == 'FIND':
            find_files(result[1])
        elif cmd == 'USE':
            use_backup(result[1])
        elif cmd == 'SET_DEST':
            set_destination(result[1])
        elif cmd == 'RESTORE':
            # looks like ('RESTORE', 'a', ('FROM', 'b'), ('TO', 'c'))
            restore_files(result[1], result[2][1], result[3][1])
        elif cmd == 'INFO':
            show_info()
        elif cmd == 'HELP':
            show_help()
        else:
            util.msg(f'syntax error: {cmd}')
    g.repo.unlock()


def show_info() -> None:
    """Show various items of interest."""
    print(f'repository: {g.repo.repo}')
    print(f'backup in use: {g.backup}')
    print(f'destination for restores:  {g.destination}')


def show_help() -> None:
    """Just print the contents of grammar.txt"""
    with open('grammar.txt', 'rt') as f:
        for line in f:
            print(line.rstrip())


def find_files(pattern: str) -> None:
    """Search all backups for files matching 'pattern'."""
    p = Pager()
    try:
        xpat = fnmatch.translate(pattern)
        pat = re.compile(xpat)
        stop = False
        for b in g.repo.all_backups:
            if not stop:
                for f in g.repo.next_file(b):
                    fname = normalize(f.fname)
                    if pat.match(fname):
                        mtime = time.ctime(float(f.mtime))
                        if not p.print(f'{b}\t{mtime}\t{fname}'):
                            stop = True
                            break
    except re.error:
        util.error('Bad search pattern')


def list_backups() -> None:
    """List all backups in the repository."""
    backups = g.repo.all_backups
    p = Pager()
    for b in backups:
        if not p.print(b):
            break


def list_all_files() -> None:
    """List all files in the open backup.

    We really don't need this, since "list '*'" does the same thing.
    """
    if g.backup == NO_BKUP:
        util.msg("You must 'use' a backup first.")
    else:
        p = Pager()
        count = 0
        for f in g.repo.next_file(g.backup):
            count += 1
            if not p.print(normalize(f.fname)):
                break
        print('Files found:', count)


def list_files(pattern: str, backup: str) -> None:
    """List files in 'backup' that match 'pattern'."""
    xpat = fnmatch.translate(pattern)
    try:
        pat = re.compile(xpat)
        count = 0
        p = Pager()
        for f in g.repo.next_file(backup):
            fname = normalize(f.fname)
            if pat.match(fname):
                if not p.print(fname):
                    break
                count += 1
        # print('Files found:', count)
    except re.error:
        util.error('Bad search pattern')


def use_backup(backup_name: str) -> None:
    """Save the backup name for future use."""
    if backup_name in g.repo.all_backups:
        g.backup = backup_name
    else:
        util.error(f'invalid backup: {backup_name}')


def set_destination(dest: str) -> None:
    """Set the default destination for restored files."""
    print('set destination', dest)
    g.destination = dest


def restore_files(pattern: str, src: str, dest_dir: str) -> None:
    """Restore files that match 'pattern' from 'src' to 'dest_dir'"""
    if g.backup == NO_BKUP and src == '':
        util.msg('You must specify a backup to restore from.')
    elif dest_dir == '' and g.destination == NO_BKUP:
        util.msg('You must specify a destination first')
    else:
        if dest_dir == '':
            dest_dir = g.destination
        if src == '':
            src = g.backup
        else:
            backup_name = os.path.join(g.repo.backups, src)
            if not os.path.exists(backup_name):
                util.error(f'Invalid backup: {src}')
                return
        xpat = fnmatch.translate(pattern)
        try:
            pat = re.compile(xpat)
            num_restored = 0
            num_skipped = 0
            for f in g.repo.next_file(src):
                fname = normalize(f.fname)
                if pat.match(fname):
                    d, fn = Repo.fname_from_hash(f.hash)
                    h = os.path.join(g.repo.objects, d, fn)
                    dest_file = os.path.join(dest_dir, fname)
                    if os.path.exists(dest_file):
                        util.warning(f'SKIPPED: Already exists {dest_file}.')
                        num_skipped += 1
                    elif not os.path.exists(h):
                        # The hash will be missing if it failed verification.
                        util.warning(f'SKIPPED: Missing hash for {dest_file}.')
                        num_skipped += 1
                    else:
                        print(f'copy_hash {h} -> {dest_file}')
                        copy_hash(h, dest_file)
                        mtime = float(f.mtime)
                        os.utime(dest_file, (mtime, mtime))
                        num_restored += 1
            print(f'Files restored/skipped = {num_restored}/{num_skipped}.')
        except re.error:
            util.error('Bad search pattern.')


def read_statement() -> Generator[str, None, None]:
    """Read a complete statement from stdin.

    The statment may extend over several lines by ending all lines
    except the last one with a backslash ('\').
    """
    stmt = ''
    prompt = PROMPT1
    while True:
        try:
            line = input(prompt)
        except EOFError:
            line = 'q'
        if line.endswith('\\'):
            stmt += ' ' + line[0:-1]
            prompt = PROMPT2
        else:
            stmt += ' ' + line
            break
    yield stmt + ' <end>'


def copy_hash(src: str, dest_file: str) -> None:
    """Copy hash file 'src' to file 'dest_file'.

    The 'src' file must by a gzipped version of the real data.
    Assuming permissions are okay, copying the file should fail only if
    not all the intermediate directories are there. If that happend, we
    will make all those directories, and retry it.
    """
    try:
        with gzip.open(src, 'rb') as f_in, open(dest_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    except FileNotFoundError:
        dest_dir = os.path.dirname(dest_file)
        print('making dir:', dest_dir)
        os.makedirs(dest_dir)
        with gzip.open(src, 'rb') as f_in, open(dest_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def normalize(fname: str) -> str:
    """Fixup 'fname' to work better with restores.

    Two things:
    1. If it starts with './' or '.\', remove those two characters.
    2. If it's an absolute pathname, e.g., 'c:\' or 'c:/' on Windows,
    remove those three characters. This way, we can concatenate the destination
    directory with this new fname, and it'll work like we expect.
    """
    if fname[0] == '.':
        return fname[2:] if fname[1] in ('/', '\\') else fname
        # if fname[1] in ('/', '\\'):
        #     return fname[2:]
        # else:
        #     return fname
    elif fname[0] == '/':
        # On Linux
        return fname[1:]
    elif fname[0].isalpha() and util.os_is_windows:
        if fname[1] == ':' and fname[2] in ('/', '\\'):
            return fname[3:]
        else:
            return fname
    else:
        return fname
