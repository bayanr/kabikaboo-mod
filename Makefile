install:
	mkdir -p /usr/share/kabikaboo
	cp -rv ./ /usr/share/kabikaboo
	ln -s /usr/share/kabikaboo/kabikaboo /usr/bin/kabikaboo
	cp kabikaboo.desktop /usr/share/applications
	cp man/kabikaboo.1 /usr/local/share/man/man1

uninstall:
	rm -rf /usr/share/kabikaboo
	rm /usr/bin/kabikaboo
	rm /usr/share/applications/kabikaboo.desktop
	rm /usr/local/share/man/man1/kabikaboo.1
