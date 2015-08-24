#include <stdio.h>		//
#include <stdint.h>		//
// #include <iostream>

void write_byte(const uint8_t *data)
{
  printf("%d\n", *data);
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

  uint8_t foo_cmd[20] = "abc";

  write_array(foo_cmd, 3);
  
  // // _delay_ms(2000);
  // write_array(reset_cmd, 15);
  // // write_byte(newline);
  // // _delay_ms(2000);


  // write_array(foo_cmd, 7);
  // // write_byte(newline);
  // // _delay_ms(1000);


  // write_array(foo_cmd, 7);
  // write_byte(newline);
  // // _delay_ms(3000);

  
  // write_array(no_echo_cmd, 5);
  //  // write_byte(newline);
  // _delay_ms(2000);
  
  // write_array(hid_cmd, 14);
  // // write_byte(newline);
  // _delay_ms(3000);
}

int main(void)
{
  bluetooth_init();
  // how to setup bluefruit?
  
  uint8_t code_a[12]={0x9f,0x0a,0xa1,0x01,0x00,0x00, 0x04, 0x00,0x00,0x00,0x00,0x00};
  uint8_t code_none[12]={0x9f,0x0a,0xa1,0x01,0x00,0x00, 0x00, 0x00,0x00,0x00,0x00,0x00};
  
  // while(1){
  //   write_array(code_a, 12);
  //   _delay_ms(50);
  //   write_array(code_none, 12);
  //   _delay_ms(1000);
  // }
  return 0;
}


