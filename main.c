#include <avr/io.h>
#include <util/delay.h>
//#include <avr/sleep.h>
#include <avr/wdt.h>

#define BAUDRATE 9600
#define UBRR_VALUE (((F_CPU / (BAUDRATE * 16UL))) - 1)
#define TX_PIN_D 1

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

void write_byte_nopoint(const uint8_t data)
{
  //wait until ready to tx
  while(!(UCSRA&(1<<UDRE))){};
  // write to register
  UDR = data; 
}

void write_byte(const uint8_t *data)
{
  //wait until ready to tx
  while(!(UCSRA&(1<<UDRE))){};
  // write to register
  UDR = *data; 
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

void bluetooth_init(){
  uint8_t reset_cmd[15] = "AT+FACTORYRESET";
  // uint8_t hid_cmd[14] = "AT+BleHIDEn=On";
  // uint8_t no_echo_cmd[5] =  "ATE=0";
  uint8_t newline[1] =  {'\n'};

  uint8_t ok_cmd[5] = "OK\r\n";

  uint8_t rec[20] = {0};
  
  _delay_ms(300);
  uint8_t foo_cmd[5] = "+++\n";
  write_array(foo_cmd, 4);	//
  // write_byte(newline);
  _delay_ms(50);

  // for(uint8_t i = 0; i != 19; i++){
  // if(read_byte() == 'O'){
  // if(foo_cmd[0] == 'A'){
    // write_array(ok_cmd, 4);
  // }
  
  // write_array(foo_cmd, 2);
  // // write_byte(newline);
  // _delay_ms(500);

  // write_array(ok_cmd, 4);
  // // write_byte(newline);
  _delay_ms(500);

  
  // write_array(no_echo_cmd, 5);
  //  // write_byte(newline);
  // _delay_ms(2000);
  
  // write_array(hid_cmd, 14);
  // // write_byte(newline);
  // _delay_ms(3000);
}

int main(void)
{
  wdt_disable();
  ACSR |= (1<<ACD); //disable comparator  
  DDRD = (1<<TX_PIN_D); //set tx pin as output

  serial_init();
  // bluetooth_init();
  // how to setup bluefruit?
  
  uint8_t code_a[12]={0x9f,0x0a,0xa1,0x01,0x00,0x00, 0x04, 0x00,0x00,0x00,0x00,0x00};
  uint8_t code_none[12]={0x9f,0x0a,0xa1,0x01,0x00,0x00, 0x00, 0x00,0x00,0x00,0x00,0x00};

  uint8_t foo_cmd[5] = "+++\n";
  
  while(1){
    // for (uint8_t i = 0; i != 5; i++){
    // write_array(code_a, 12);
    // _delay_ms(50);
    // write_array(code_none, 12);
    // _delay_ms(1000);
    // }
    
    //wait until ready to tx
  while(!(UCSRA&(1<<UDRE))){};
  // write to register
  UDR = data; 
    
    write_byte_nopoint(0x01);
    // write_byte_nopoint(43);
    // write_byte_nopoint(43);
    // write_byte_nopoint(43);		
    // // write_byte(13) ;		// /r
    // write_byte_nopoint(10);             // /n
    _delay_ms(2000);

  }
  return 0;
}


