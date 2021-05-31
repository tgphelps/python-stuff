
DEST=/opt/tsm-oravm
# DEST=/root/tsm-oravm
install:
	echo I hope you are root when you do this.
	cp *.py *.sh *.sql $(DEST)
	cp ovmbackup  $(DEST)
	cp ovmlist    $(DEST)
	cp ovmprune   $(DEST)
	cp ovmcheck   $(DEST)

archive:
	echo This makes a tar file to install on tsm/oravm
	tar cvf tsm-oravm.tar *.py *.sh *.sql ovmbackup ovmlist ovmprune ovmcheck
