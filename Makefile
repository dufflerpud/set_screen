#@HDR@	$Id$
#@HDR@		Copyright 2024 by
#@HDR@		Christopher Caldwell/Brightsands
#@HDR@		P.O. Box 401, Bailey Island, ME 04003
#@HDR@		All Rights Reserved
#@HDR@
#@HDR@	This software comprises unpublished confidential information
#@HDR@	of Brightsands and may not be used, copied or made available
#@HDR@	to anyone, except in accordance with the license under which
#@HDR@	it is furnished.

PROJECTSDIR?=$(shell echo $(CURDIR) | sed -e 's+/projects/.*+/projects+')
PROGRAMS=generate_screens generate_pics
LOGFILE=/var/log/stderr/set_screen
SCREENS=$(shell set_screen | sed -e 's/:.*//')

include $(PROJECTSDIR)/common/Makefile.std

test:		$(RESDIR)/.must_exist
		$(BINDIR)/simple_routing < tests/1 > $(RESDIR)/1

reset:
		make install
		killproc -y perl
		cat /dev/null > $(LOGFILE)
		tail -f $(LOGFILE)

regen_screens:
		rm -f messages/*
		for screen in $(SCREENS); do generate_pics -s$$screen | sh; done

install:
		$(INSTALL) -d -m 0777 $(WWWDIR)/media
		$(INSTALL) -d -m 0777 $(WWWDIR)/messages
		$(INSTALL) -d -m 0777 $(WWWDIR)/URLs
		@$(MAKE) std_install

%:
		@echo "Invoking std_$@ rule:"
		@$(MAKE) std_$@ ORIGINAL_TARGET=$@
