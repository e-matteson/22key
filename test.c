#include <avr/io.h>
#include <util/delay.h>
//#include <avr/sleep.h>
#include <avr/wdt.h>

#define BAUDRATE 9600
#define UBRR_VALUE (((F_CPU / (BAUDRATE * 16UL))) - 1)

void serial_init(void)
{
  // set baud rate
  UBRR0H = (uint8_t) (UBRR_VALUE>>8);
  UBRR0L = (uint8_t) UBRR_VALUE;
  // frame format: 8 data bits, no parity, 1 stop bit
  UCSR0C |= (1<<UCSZ01) | (1<<UCSZ00);
  //enable tx rx 
  UCSR0B |= (1<<RXEN0) | (1<<TXEN0);
}

void write_byte(uint8_t data)
{
  //wait until ready
  while(!(UCSR0A&(1<<UDRE0))){};
  // write to register
  UDR0 = data; 
}

uint8_t read_byte()
{
  //wait until ready
  while(!(UCSR0A&(1<<RXC0))){};
  // read from register
  return UDR0;
}

int main (void)
{
  wdt_disable();
  ACSR |= (1<<ACD); //disable comparator
  uint8_t byte;
 
  serial_init();
  // how to setup bluefruit?
  while(1){
    byte = 
    write_byte(byte);
    _delay_ms(1000);
  }
 
}


