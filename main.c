#include <avr/io.h>
#include <util/delay.h>
//#include <avr/sleep.h>
#include <avr/wdt.h>

#define BAUDRATE 9600
#define UBRR_VALUE (((F_CPU / (BAUDRATE * 16UL))) - 1)
#define TX_PIN_D 1
#define REC_BUFF_SIZE 1

void serial_init(void)
{

  // set baud rate
  UBRRH = (uint8_t) (UBRR_VALUE>>8);
  UBRRL = (uint8_t) UBRR_VALUE;
  // frame format: 8 data bits, no parity, 1 stop bit
  UCSRC |= (1<<UCSZ1) | (1<<UCSZ0);
  //enable tx rx 
  UCSRB |= (1<<RXEN) | (1<<TXEN);
}

void write_byte(const uint8_t *data)
{
  //wait until ready to tx
  while(!(UCSRA&(1<<UDRE))){};
  // write to register
  UDR = *data; 
}

void write_byte_nopoint(const uint8_t character)
{
  //wait until ready to tx
  while(!(UCSRA&(1<<UDRE))){};
  // write to register
  UDR = character; 
}


uint8_t read_byte()
{
  //wait until rx complete
  while(!(UCSRA&(1<<RXC))){};
  // read from register
  return UDR;
}


void write_array(const uint8_t *array, const uint8_t len){
  for(uint8_t i = 0; i != len; i++){
    write_byte(array+i);
  }
  //should it send newline? for cmds, not data?  
}

int main(void)
{
  wdt_disable();
  ACSR |= (1<<ACD); //disable comparator  
  DDRD = (1<<TX_PIN_D); //set tx pin as output

  serial_init();
  // uint8_t foo_cmd[5] = "+++\n";
  uint8_t rec[REC_BUFF_SIZE] = {0};
  
  _delay_ms(1000);
  write_byte_nopoint(65);
  write_byte_nopoint(84);
  write_byte_nopoint(10);
  _delay_ms(500);

  for(int i = 0; i!=REC_BUFF_SIZE; i++){
    rec[i]=read_byte();
  }
  
  while(1){
    //wait until ready to tx
    _delay_ms(1000);
    // write_byte(rec[0]);
    write_array(rec, REC_BUFF_SIZE);
    
  }
  return 0;
}


