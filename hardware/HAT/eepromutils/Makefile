# Current tools are eepmake and eepdump

CC ?= gcc
CFLAGS ?= -Wall -Wextra
prefix ?= /usr/local
exec_prefix = ${prefix}

EEPROM_SIZE_KB := 4

.PHONY: all install uninstall erase_and_flash clear_eeprom flash_full check \
flash_full_and_check dtb flash_complete flash_complete_and_check check_complete

all: eepmake eepdump

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

eeprom.eep: eepmake eeprom_settings.txt
	./eepmake eeprom_settings.txt eeprom.eep

blank.eep:
	dd if=/dev/zero ibs=1k count=$(EEPROM_SIZE_KB) of=blank.eep

full_image.eep: eeprom.eep blank.eep
	cp blank.eep full_image.eep
	dd if=eeprom.eep of=full_image.eep conv=sync,notrunc

flash_full: full_image.eep
	sudo ./eepflash.sh -w -t=24c32 -f=full_image.eep

flash_full_and_check: flash_full check

check:
	@cmp -s /sys/class/i2c-adapter/i2c-0/0-0050/eeprom full_image.eep; \
	RETVAL=$$?; \
	if [ $$RETVAL -eq 0 ]; then \
			echo "Flash successfully verified"; \
	else \
			echo "Verification failed"; \
	fi

erase_and_flash: eeprom.eep clear_eeprom
	sudo ./eepflash.sh -w -t=24c32 -f=eeprom.eep

clear_eeprom: blank.eep
	sudo ./eepflash.sh -w -t=24c32 -f=blank.eep

clean:
	rm -f eepmake eepdump *.eep pscope_hat.dtb

pscope_hat.dtb:
	dtc -q -@ -I dts -O dtb -o pscope_hat.dtb pscope_hat.dts

dtb: pscope_hat.dtb

complete.eep: eepmake eeprom_settings.txt pscope_hat.dtb
	./eepmake eeprom_settings.txt complete.eep pscope_hat.dtb

complete_image.eep: complete.eep blank.eep
	cp blank.eep complete_image.eep
	dd if=complete.eep of=complete_image.eep conv=sync,notrunc

flash_complete: complete_image.eep
	sudo ./eepflash.sh -w -t=24c32 -f=complete_image.eep

flash_complete_and_check: flash_complete check_complete

check_complete:
	@cmp -s /sys/class/i2c-adapter/i2c-0/0-0050/eeprom complete_image.eep; \
	RETVAL=$$?; \
	if [ $$RETVAL -eq 0 ]; then \
			echo "Flash successfully verified"; \
	else \
			echo "Verification failed"; \
	fi
