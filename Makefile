PREFIX = /usr
MANDIR = $(PREFIX)/share/man

all: build

build:
	python setup.py build

install:
	python setup.py install --prefix=${PREFIX}

install-doc:
	@mkdir -p $(DESTDIR)$(MANDIR)/man1
	@cp -p docs/hyfetch.1 $(DESTDIR)$(MANDIR)/man1
	@cp -p docs/neofetch.1 $(DESTDIR)$(MANDIR)/man1/neowofetch.1

uninstall:
	@rm -rf $(DESTDIR)$(PREFIX)/bin/hyfetch
	@rm -rf $(DESTDIR)$(PREFIX)/bin/neowofetch
	@rm -rf $(DESTDIR)$(MANDIR)/man1/hyfetch.1*
	@rm -rf $(DESTDIR)$(MANDIR)/man1/neowofetch.1*

clean:
	rm -rf build/ HyFetch.egg-info

install-neofetch:
	@mkdir -p $(DESTDIR)$(PREFIX)/bin
	@mkdir -p $(DESTDIR)$(MANDIR)/man1
	@cp -p neofetch $(DESTDIR)$(PREFIX)/bin/neofetch
	@cp -p docs/neofetch.1 $(DESTDIR)$(MANDIR)/man1
	@chmod 755 $(DESTDIR)$(PREFIX)/bin/neofetch

uninstall-neofetch:
	@rm -rf $(DESTDIR)$(PREFIX)/bin/neofetch
	@rm -rf $(DESTDIR)$(MANDIR)/man1/neofetch.1*
