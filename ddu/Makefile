
SRC=ddu.py repo.py util.py hash.py backup.py walk2.py restore.py defns.py lexer.py parser_ddu.py

REPO=c:\tgp\repo

check:
	pipenv run mypy $(SRC)
flake8:
	pipenv run flake8 $(SRC)
unlock:
	pipenv run ddu.py unlock $(REPO)
restore:
	pipenv run ddu.py restore $(REPO)
orphans:
	pipenv run ddu.py verify --orphans $(REPO)
verify-hashes:
	pipenv run ddu.py verify --hashes -d $(REPO)
verify-backups:
	pipenv run ddu.py verify --backups -d $(REPO)
backup:
	pipenv run ddu.py backup --repo $(REPO) $(PATHS)
backup-stdin:
	pipenv run ddu.py backup --verify --repo $(REPO) -
backup-src:
	walk2.py . | pipenv run ddu.py backup --verify --repo $(REPO) -
create:
	pipenv run ddu.py create $(REPO)
destroy:
	rm -fr $(REPO)/backups
	rm -fr $(REPO)/objects
	rm -fr $(REPO)/signature
	rm -fr $(REPO)/lock
	rm -fr c:/tgp/tmp
