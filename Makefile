export SHELL = sh
PACKAGE = udev-notify
VERSION = 0.1
COPYRIGHTYEAR = 2011
AUTHOR = USU Team
EMAIL = lfu.project@gmail.com

all: debian

debian: translations
	[ ! -d ./build/debian/ ] || rm -r ./build/debian/
	mkdir -p ./build/debian/usr/bin
	mkdir -p ./build/debian/etc/xdg/autostart
	mkdir -p ./dist
	
	cp src/udev-notify-autostart.desktop ./build/debian/etc/xdg/autostart/
	cp src/udev-notify ./build/debian/usr/bin/udev-notify
	
	mkdir -p ./build/debian/usr/share/udev-notify
	cp src/udev-notify.py ./build/debian/usr/share/udev-notify/udev-notify.py
	cp -r src/pyudev ./build/debian/usr/share/udev-notify/
	cp -r locale ./build/debian/usr/share
	
	./tools/debian-package.sh "$(PACKAGE)" "$(VERSION)" "$(AUTHOR)" "$(EMAIL)"

	
pot:
	[ -d ./po/ ] || mkdir ./po
	xgettext --default-domain="$(PACKAGE)" --output="po/$(PACKAGE).pot" src/*.py
	sed -i 's/SOME DESCRIPTIVE TITLE/Translation template for $(PACKAGE)/' po/$(PACKAGE).pot
	sed -i "s/YEAR THE PACKAGE'S COPYRIGHT HOLDER/$(COPYRIGHTYEAR)/" po/$(PACKAGE).pot
	sed -i 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/$(AUTHOR) <$(EMAIL)>, $(COPYRIGHTYEAR)/' po/$(PACKAGE).pot
	sed -i 's/Report-Msgid-Bugs-To: /Report-Msgid-Bugs-To: $(EMAIL)/' po/$(PACKAGE).pot
	sed -i 's/CHARSET/UTF-8/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE VERSION/$(PACKAGE) $(VERSION)/' po/$(PACKAGE).pot
	sed -i 's/PACKAGE/$(PACKAGE)/' po/$(PACKAGE).pot

update-po: pot
	for i in po/*.po ;\
	do \
	mv $$i $${i}.old ; \
	(msgmerge $${i}.old po/$(PACKAGE).pot | msgattrib --no-obsolete > $$i) ; \
	rm $${i}.old ; \
	done

translations: po/*.po
	mkdir -p locale
	@for po in $^; do \
		language=`basename $$po`; \
		language=$${language%%.po}; \
		target="locale/$$language/LC_MESSAGES"; \
		mkdir -p $$target; \
		msgfmt --output=$$target/$(PACKAGE).mo $$po; \
	done

clean:
	rm -rf dist
	rm -rf build
	rm -rf locale

