#!/usr/bin/env python
"""
ddu.py: Deduplicating utility for backup/restore

Usage:
    ddu.py [--log=<level>] (create | unlock) REPO
    ddu.py verify [--backups] [--hashes] [--orphans] [-d] REPO
    ddu.py backup [-v] [--verify] [--prefix=<pre>] --repo=<repo> FILE ...
    ddu.py restore REPO
    ddu.py --version
    ddu.py --help

Options:
    --version          Show version and exit.
    -h --help          Show this message and exit.
    -v                 Be verbose to stdout.
    --log <level>      Set log level. (Not used.)
    --backups          Verify that all hashes linked to backups are there.
    --hashes           Verify that all hash contents are correct.
    --orphans          Show, and maybe delete, orphaned hashes.
    -d                 Delete bad or orphan hashes, if found.
    --verify           Verify the backup, after doing it.
    --prefix <pre>     Prefix for backup name. Suffixed by date, time.
"""

# -------------------- imports

import logging
import re
import time

import backup
import docopt  # type: ignore
from repo import Repo
import restore
import util

# -------------------- constants

VERSION = '0.01'
LOG_FILE = 'LOG.txt'
LOG_LEVEL = logging.INFO
alphanum = re.compile('[A-Za-z0-9]+$')

# -------------------- functions


def main() -> None:
    args = docopt.docopt(__doc__, version=VERSION)
    logging.basicConfig(filename=LOG_FILE, filemode='a',
                        format='%(levelname)s - %(message)s', level=LOG_LEVEL)
    now = time.asctime()
    logging.info(f'log start: {now}')
    logging.info(f'args: {args}')

    repo_file = args['REPO']
    if args['create']:
        Repo.create(repo_file)
    elif args['verify']:
        repos = Repo(repo_file)
        logging.info(f'Verifying repo {repo_file}')
        n = 0
        if args['--hashes']:
            repos.verify_all_hashes(delete=args['-d'])
            n += 1
        if args['--backups']:
            repos.verify_backups()
            n += 1
        if args['--orphans']:
            repos.find_orphans(delete=args['-d'])
            n += 1
        if n == 0:
            util.msg('You must use --hashes, --backups, or --orphans')
    elif args['unlock']:
        # XXX Could this be: Repo(repo_file).unlock() ?
        repos = Repo(repo_file)
        repos.unlock()
    elif args['backup']:
        arg_prefix = args['--prefix']
        prefix = arg_prefix if arg_prefix else 'backup'
        if not alphanum.match(prefix):
            util.fatal('prefix must be alphanumeric')
        want_verify = args['--verify']
        backup.run_backup(args['--repo'], prefix, args['FILE'],
                          verify=want_verify,
                          verbose=args['-v'])
    elif args['restore']:
        restore.restore(repo_file)

    now = time.asctime()
    logging.info(f'log end: {now}')

# --------------------


if __name__ == '__main__':
    main()
