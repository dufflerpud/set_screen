#indx#	Makefile - Instructions for building and installing set_screen utilities
#@HDR@	$Id$
#@HDR@
#@HDR@	Copyright (c) 2024-2026 Christopher Caldwell (Christopher.M.Caldwell0@gmail.com)
#@HDR@
#@HDR@	Permission is hereby granted, free of charge, to any person
#@HDR@	obtaining a copy of this software and associated documentation
#@HDR@	files (the "Software"), to deal in the Software without
#@HDR@	restriction, including without limitation the rights to use,
#@HDR@	copy, modify, merge, publish, distribute, sublicense, and/or
#@HDR@	sell copies of the Software, and to permit persons to whom
#@HDR@	the Software is furnished to do so, subject to the following
#@HDR@	conditions:
#@HDR@	
#@HDR@	The above copyright notice and this permission notice shall be
#@HDR@	included in all copies or substantial portions of the Software.
#@HDR@	
#@HDR@	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
#@HDR@	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#@HDR@	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
#@HDR@	AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#@HDR@	HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#@HDR@	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#@HDR@	FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#@HDR@	OTHER DEALINGS IN THE SOFTWARE.
#
#hist#	2026-02-19 - Christopher.M.Caldwell0@gmail.com - Created
########################################################################
#doc#	Makefile - Instructions for building and installing set_screen utilities
########################################################################

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
		-$(RM) -f /usr/local/bin/$(PROJECT) 2>/dev/null
		$(LN) -s $(WWWDIR)/index.cgi /usr/local/bin/$(PROJECT)
ifeq (,$(wildcard lib/screens.map*))
		echo "default" > lib/screens.map
endif
ifeq (,$(wildcard lib/URLs.map*))
		touch lib/URLs.map
endif
		@$(MAKE) std_install

%:
		@echo "Invoking std_$@ rule:"
		@$(MAKE) std_$@ ORIGINAL_TARGET=$@
