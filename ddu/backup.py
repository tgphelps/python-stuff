
from datetime import datetime
import glob
import logging
import os
import time
from typing import List
import sys

from hash import hash_file
from repo import Repo
import util


class Backup:
    """Class to perform a de-duped backup."""

    def __init__(self, repos: str, prefix: str, verbose=False):
        """Open the backup detail file, and get ready to backup files."""
        self.verbose = verbose
        self.repos_name = repos
        self.repo = Repo(repos)
        now = datetime.now()
        str_now = now.strftime('%Y%m%d_%H%M%S')
        self.bk_name = prefix + '_' + str_now
        fname = os.path.join(self.repo.backups, self.bk_name)
        self.bkf = open(fname, 'wt')
        print('start', file=self.bkf)
        logging.info(f'start backup: {fname}')
        if self.verbose:
            print("start backup")

        # backup stats
        self.files_total = 0
        self.files_stored = 0
        self.files_not_stored = 0
        self.files_errors = 0
        self.bytes_read = 0
        self.start_time = time.time()
        self.elapsed_time: int

    def finish(self) -> None:
        """Write the backup detail file trailer and statistics."""
        print('end', file=self.bkf)
        self.elapsed_time = int(time.time() - self.start_time)
        self.show_stats()
        self.bkf.close()
        logging.info('end backup')
        if self.verbose:
            print('end backup')

    def show_stats(self) -> None:
        """Print final stats to stderr and the 'backup' file."""
        self.print_stat(f'total files = {self.files_total}')
        self.print_stat(f'files stored = {self.files_stored}')
        self.print_stat(f'files not stored = {self.files_not_stored}')
        self.print_stat(f'bytes read = {self.bytes_read}')
        self.print_stat(f'bytes written = {self.repo.bytes_written}')
        self.print_stat(f'errors = {self.files_errors}')
        self.print_stat(f'elapsed time = {self.elapsed_time}')

    def print_stat(self, s: str) -> None:
        print(s)
        print(s, file=self.bkf)

    def backup_object(self, obj: str) -> None:
        """Backup an object. Must be a directory or ordinary file."""
        logging.info(f'backup: {obj}')
        if os.path.isdir(obj):
            self.backup_dir(obj)
        elif os.path.isfile(obj):
            self.backup_file(obj)
        else:
            util.fatal(f'ABORT: {obj} is not a file or directory')

    def backup_dir(self, path: str) -> None:
        """Backup all files in the tree rooted at 'path'."""
        assert os.path.isdir(path)
        for root, _, files in os.walk(path):
            for f in files:
                self.backup_file(os.path.join(root, f))

    def backup_file(self, path: str) -> None:
        """Backup the file 'path' to the repository.

        Write the hashed contents to 'objects' if it isn't already there.
        Write a line in the backup file to describe the backed up file.
        """
        if self.verbose:
            print('backup', path)
        self.files_total += 1
        s = os.stat(path)
        # self.bytes_read += os.stat(path).st_size
        self.bytes_read += s.st_size
        h = hash_file(path)
        # mtime = os.path.getmtime(path) # XXX get this from os.stat ?
        mtime = s.st_mtime
        if self.repo.store_file(path, h):
            print(f'new\t{h}\t{mtime}\t{path}', file=self.bkf)
            self.files_stored += 1
            s = os.stat(path)
        else:
            print(f'old\t{h}\t{mtime}\t{path}', file=self.bkf)
            self.files_not_stored += 1


def run_backup(repo_name: str, prefix: str, paths: List[str],
               verify=True,
               verbose=False) -> None:
    """Perform a backup to the repository of all dirs/files in the list.

    Make sure we have an unlocked DDU repository. Process all items in
    'paths'. If an item is '-', read path names from stdin.
    """
    logging.info(f"backup list: {paths}")
    logging.info(f"backup repo: {repo_name}")
    print(f"Backing up to {repo_name} with prefix '{prefix}'.")
    repos = Repo(repo_name)
    if repos.lock():
        bkup = Backup(repo_name, prefix, verbose=verbose)
        for g in paths:
            if g == '-':
                for f in sys.stdin:
                    if not f:
                        continue
                    f = f.rstrip()
                    if os.path.isfile(f) or os.path.isdir(f):
                        bkup.backup_object(f)
                    else:
                        util.warning(f'{f} is not a file or directory')
            else:
                if util.os_is_windows:
                    # You have to use globbing on Windows. Shell is too stupid.
                    path_list = glob.glob(g)
                    if path_list == []:
                        util.warning(f'File/dir {g} not found.')
                    else:
                        for f in glob.glob(g):
                            bkup.backup_object(f)
                else:
                    bkup.backup_object(g)
        bkup.finish()
        repos.unlock()
        if verify:
            repos.verify_backups(only=bkup.bk_name)
    else:
        util.fatal(f'repo {repo_name} is LOCKED')
