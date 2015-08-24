#
# Makefile template for ATtiny45
# Derived from AVR Crosspack template
#

DEVICE_GCC     = attiny2313a           # See avr-help for all possible devices
DEVICE_DUDE     = attiny2313           # See avr-help for all possible devices
CLOCK      = 1000000               # 1Mhz
PROGRAMMER = -c avrispmkII -P usb  # For using waveshare avrisp xpII - is usb right?
OBJECTS    = main.o                # Add more objects for each .c file here
# FUSES      = -U lfuse:w:0x62:m -U hfuse:w:0xdf:m -U efuse:w:0xff:m  # settings as taken from http://www.engbedded.com/fusecalc/

AVRDUDE = avrdude $(PROGRAMMER) -p $(DEVICE_DUDE)
COMPILE = avr-gcc -Wall -Os -DF_CPU=$(CLOCK) -mmcu=$(DEVICE_GCC)

# symbolic targets:
all:	main.hex

.c.o:
	$(COMPILE) -c $< -o $@

.S.o:
	$(COMPILE) -x assembler-with-cpp -c $< -o $@

.c.s:
	$(COMPILE) -S $< -o $@

flash:	all
	$(AVRDUDE) -U flash:w:main.hex:i

# fuse:
# $(AVRDUDE) $(FUSES)

# install: flash fuse
install: flash

# if you use a bootloader, change the command below appropriately:
# load: all
# bootloadHID main.hex

clean:
	rm -f main.hex main.elf $(OBJECTS)

# file targets:
main.elf: $(OBJECTS)
	$(COMPILE) -o main.elf $(OBJECTS)

main.hex: main.elf
	rm -f main.hex
	avr-objcopy -j .text -j .data -O ihex main.elf main.hex
	avr-size --format=avr --mcu=$(DEVICE_GCC) main.elf
# If you have an EEPROM section, you must also create a hex file for the
# EEPROM and add it to the "flash" target.

# Targets for code debugging and analysis:
disasm:	main.elf
	avr-objdump -d main.elf

cpp:
	$(COMPILE) -E main.c
