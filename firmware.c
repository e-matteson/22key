//pseudo code

#include <avr/io.h>

#define ALREADY_SENT    -1
#define NOT_PRESSED     -2
#define DEBOUNCE_DELAY  10


int setup(){
  set column pins input + pullup;
  set row pins input + hi-z;

  intialize bluetooth;
 
  
  char timers[22] = {0}; //signed char
  //initialization might be unnecessary, depending on program flow / interrupts handlers?
  for (int i=0; i<22; i++){
    timers[i]=NOT_PRESSED;
  }
  return 0;
}


int loop(){

  
  
}


state_t getState(){
 // if memory problems, pass pointer to existing state instead
 //state_t is 3 bytes, maybe as union?
  state_t new_state;
  int i = 0;
  for (each hand){
    for(each row){
      set row pin low;
      //note: might need a nop between write and read, see p57
      for (each column){
	val = read from column pin;  
	new_state |= val<<i;
	i++;
      }
      set row pin hi-z;           //(not hi, to save power?)
    }
  }
  
}

