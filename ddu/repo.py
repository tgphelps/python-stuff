
import gzip
import hash
import logging
import os
import shutil
import time
from typing import Set, Tuple, List, Generator

from defns import Entry
import util

# --------------------

REPO_VERSION = '1'
LOCK_FILE = '/LOCK'
OBJECTS = '/objects'
BACKUPS = '/backups'
SIG = '/signature'

COMP_LEVEL = 9  # gzip compression level to use

# -------------------- Exported functions.


class Repo:
    """Functions performed by a repository."""

    def __init__(self, repo: str):
        self.repo = repo
        self.lock_name = repo + LOCK_FILE
        self.objects = repo + OBJECTS
        self.backups = repo + BACKUPS
        self.all_backups = self.get_all_backups()
        self.sig_file = repo + SIG
        if not self.quick_verify():
            util.fatal(f'{repo} is not a repository')
        self.bytes_written = 0

    def lock(self) -> bool:
        """Lock the repo. Return True if successful"""
        logging.info(f'locking repo: {self.repo}')
        if os.path.isfile(self.lock_name):
            logging.warning('repo is already locked')
            return False
        else:
            open(self.lock_name, 'w').close()
            logging.info('repo locked')
            return True

    def unlock(self) -> None:
        """Unlock the repo, if it is locked."""
        logging.info(f'unlock repo: {self.repo}')
        if os.path.isfile(self.lock_name):
            os.remove(self.lock_name)
        else:
            util.warning(f'repo {self.repo} is not locked')

    def quick_verify(self) -> bool:
        """Verify existence of basic contents."""
        # logging.info(f'verify repo: {self.repo}')
        if not (os.path.isdir(self.objects) and
                os.path.isdir(self.backups)):
            return False

        if not os.path.isfile(self.sig_file):
            return False

        with open(self.sig_file, 'rt') as sig:
            line = sig.readline().strip()
            if line != 'sig=ddu-repo':
                return False
            # logging.info(line)

            line = sig.readline().strip()
            if line != 'version=1':
                return False

            line = sig.readline().strip()
            logging.info(line)
            if line != 'compressed=yes':
                return False

            line = sig.readline().strip()
            # logging.info(line)
            f = line.split('=')
            if f[0] != 'created':
                return False
        # logging.info('repo verify complete')
        return True

    def next_file(self, backup: str) -> Generator[Entry, None, None]:
        """Return the file entries from 'backup'."""
        fname = os.path.join(self.backups, backup)
        with open(fname, 'rt') as fd:
            for line in fd:
                if line[0:3] in ('old', 'new'):
                    yield Entry._make(line.rstrip().split('\t'))

    def find_orphans(self, delete=False) -> None:
        """Find hashes not linked to a backed up file. Maybe delete them."""
        hashes: Set[str] = set()
        for (d, f) in self.next_hash():
            hashes.add(d[-2:] + f)
        print(f'Hashes found: {len(hashes)}')
        for bkup in self.all_backups:
            print('backup:', bkup)
            for ent in self.next_file(bkup):
                hashes.discard(ent.hash)
        print(f'orphan count: {len(hashes)}')
        if delete and len(hashes) > 0:
            print("deleting...")
        for h in hashes:
            print(h)
            if delete:
                fname = self.fname_from_hash(h)
                os.remove(os.path.join(self.objects, fname[0], fname[1]))

    def store_file(self, path: str, hash: str) -> bool:
        """Store file 'path' in the repo with name taken from 'hash'.

        Store it like in a git repository, and return True. If there is
        already a stored file by that name, just return False.
        """
        # print(f'repo storing {path} as {hash}')
        (d, f) = self.fname_from_hash(hash)
        fname = os.path.join(d, f)
        if self.find_file(fname):
            # print(f'{fname} not stored')
            return False
        else:
            self.write_file(path, fname)
            return True

    def next_hash(self) -> Generator[Tuple[str, str], None, None]:
        """Yield each '(dd, h...h) in the object directory."""
        for d, _, files in os.walk(self.objects):
            for f in files:
                yield (d, f)

    def get_all_backups(self) -> List[str]:
        """Return a list of all backup files in the 'backups' directory."""
        return [f for f in os.listdir(self.backups)
                if os.path.isfile(os.path.join(self.backups, f))]

    def verify_all_hashes(self, delete=False) -> None:
        """Verify that all hashes are correct."""
        util.msg('verifying hashes...')
        nfiles = 0
        nerrors = 0
        for d, f in self.next_hash():
            nfiles += 1
            if not _verify_hash(d, f):
                print(f'ERROR: bad hash {d} {f}')
                if delete:
                    # print('deleting', os.path.join(d, f))
                    os.remove(os.path.join(d, f))
                nerrors += 1
        util.msg(f'files = {nfiles}, errors = {nerrors}')

    def verify_backups(self, only='') -> None:
        """Verify all, or only the latest, backup(s) in this repository.

        Iterate through every 'new' and 'old' entry in every (or latest)
        backup, and verify that (1) the hash exists, and (2) its contents
        matches its name.
        """
        if only == '':
            bkup_list = self.all_backups
        else:
            bkup_list = [only]
        num_backups = len(bkup_list)
        # entries = 0
        num_files = 0
        hits = 0
        all_hashes: Set[str] = set()
        good: Set[str] = set()
        bad: Set[str] = set()
        missing: Set[str] = set()
        for b in bkup_list:
            util.msg(f'Checking: {b}')
            bkup = os.path.join(self.backups, b)
            with open(bkup, 'rt') as f:
                line_num = 0
                saw_end = False
                for line in f:
                    line_num += 1
                    if line_num == 1 and not line.startswith('start'):
                        util.fatal(f'Backup {bkup} corrupted. No start.')
                    if line[0:3] in ('new', 'old'):
                        num_files += 1
                        flds = line.split('\t')
                        h = flds[1]
                        this_file = flds[3]
                        all_hashes.add(h)
                        if h in good:
                            hits += 1
                            # continue
                        elif h in bad:
                            hits += 1
                            util.error(f'invalid hash {h} for {this_file}')
                            # continue
                        else:
                            # We haven't seen this hash before
                            (d, ff) = self.fname_from_hash(h)
                            if self.find_file(os.path.join(d, ff)):
                                if _verify_hash(os.path.join(self.objects, d),
                                                ff):
                                    good.add(h)
                                else:
                                    bad.add(h)
                                    t = this_file
                                    util.error(f'invalid hash {h} for {t}')
                            else:
                                missing.add(h)
                                util.error(f'missing {h} for {this_file}')
                    else:
                        # print(line_num, line)
                        # This should be a trailer line
                        if line.startswith('end'):
                            saw_end = True
                if not saw_end:
                    util.warning(f'Backup {bkup} has no end marker')

        if len(all_hashes) != len(good) + len(bad) + len(missing):
            util.fatal(f'hash bug: {len(all_hashes)} \
                         {len(good)} {len(bad)} {len(missing)}')
        util.msg('Verify results:')
        util.msg(f'backups checked = {num_backups}')
        util.msg(f'files checked = {num_files}')
        util.msg(f'invalid = {len(bad)}')
        util.msg(f'missing = {len(missing)}')
        util.msg(f'cache hits = {hits}')

    def find_file(self, fname: str) -> bool:
        """Return True if 'fname' is in the repository.

        Filename looks like 'dd/h...h'.
        """
        # logging.info(f'finding {fname}')
        full_name = self.objects + '/' + fname
        if os.path.isfile(full_name):
            return True
        else:
            return False

    def write_file(self, path: str, fname: str) -> None:
        """Write contents of 'path' into the object 'fname'.

        'fname' should look like 'dd/h...h'.
        """
        logging.info(f'writing {fname}')
        full_name = self.objects + '/' + fname
        dir = self.objects + '/' + fname[0:2]
        # self.make_dir(dir)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        with open(path, 'rb') as f_in:
            with gzip.open(full_name, 'wb', compresslevel=COMP_LEVEL) as f_out:
                shutil.copyfileobj(f_in, f_out)
        hash_size = os.stat(full_name).st_size
        self.bytes_written += hash_size

    # def make_dir(self, dir: str) -> None:
        # """Make directory 'dir' if it does not exist."""
        # if not os.path.isdir(dir):
        #     os.mkdir(dir)

    @staticmethod
    def fname_from_hash(hash: str) -> Tuple[str, str]:
        """Convert a 40-char hash to a 2-char dir and 38-char filename."""
        assert len(hash) == 40
        d = hash[0:2]
        name = hash[2:]
        return (d, name)

    @staticmethod
    def create(repo: str) -> None:
        """Create a new repository in 'repo'.

        Make sure 'repo' is an empty directory.
        Call create_contents() to initialize it.
        """
        logging.info(f'creating repo: {repo}')
        if os.path.isdir(repo):
            if os.listdir(repo) == []:
                _create_repo_contents(repo)
                logging.info('repo creation complete')
            else:
                util.fatal(f'directory {repo} is not empty')
        else:
            util.fatal(f'{repo} is not a directory.')

# -------------------- Local functions


def _create_repo_contents(repo: str) -> None:
    """Create initial contents of the repo.

    Create the 'objects' and 'backups' directories.
    Create a signature file with: date/time, repo version.
    """
    os.mkdir(repo + '/objects')
    os.mkdir(repo + '/backups')
    with open(repo + '/signature', 'wt') as sig:
        print(f'sig=ddu-repo', file=sig)
        print(f'version={REPO_VERSION}', file=sig)
        print(f'compressed=yes', file=sig)
        now = time.asctime()
        print(f'created={now}', file=sig)


def _verify_hash(d: str, f: str) -> bool:
    """Return True if the hash file 'd/f' has the correct contents."""
    real_hash = hash.hash_gzip_file(os.path.join(d, f))
    hash_name = d[-2:] + f
    if real_hash != hash_name:
        # print(f'ERROR: {d} {f} {real_hash}')
        return False
    else:
        return True
