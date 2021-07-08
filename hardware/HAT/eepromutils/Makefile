# Current tools are eepmake and eepdump

CC ?= gcc
CFLAGS ?= -Wall -Wextra
prefix ?= /usr/local
exec_prefix = ${prefix}

all: eepmake eepdump

eeprom: eeprom_settings.txt
	./eepmake eeprom_settings.txt eeprom.eep

eepmake: eeptypes.h eepmake.c
	$(CC) $(CFLAGS) eepmake.c -o eepmake

eepdump: eeptypes.h eepdump.c
	$(CC) $(CFLAGS) eepdump.c -o eepdump

install: all
	install -d $(DESTDIR)$(exec_prefix)/sbin
	install -d $(DESTDIR)$(prefix)/bin
	install eepmake $(DESTDIR)$(prefix)/bin/
	install eepdump $(DESTDIR)$(prefix)/bin/
	install eepflash.sh $(DESTDIR)$(exec_prefix)/sbin/

uninstall:
	rm -f $(DESTDIR)$(prefix)/bin/eepmake
	rm -f $(DESTDIR)$(prefix)/bin/eepdump
	rm -f $(DESTDIR)$(exec_prefix)/sbin/eepflash.sh

clean:
	rm -f eepmake eepdump eeprom.eep

flash: eeprom
	sudo ./eepflash.sh -w -t=24c32 -f=eeprom.eep
