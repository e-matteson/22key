//pseudo code
//
#include <avr/io.h>

#define MOD_HELD        -1  // mod keys don't have chord timers
#define ALREADY_SENT    -2  // >= ALREADY_SENT means currently pressed
#define NOT_PRESSED     -3  // <= NOT_PRESSED means not currently pressed
//#define MOD_RELEASED    -4

#define PRESS_DELAY    10    //timer units TBD
#define RELEASE_DELAY    10    //timer units TBD
#define REPEAT_DELAY   1000
#define REPEAT_PERIOD  50
#define STANDBY_DELAY  10000   //different units than other timers, long!

// //for flag_send_ctrl and flag_send_alt
// #define SEND_NOTHING   0
// #define SEND_DOWN      1
// #define SEND_UP        2

#define  S_L_T1 0
#define  S_L_T2 1
#define  S_L_T3 2
#define  S_L_Ib 3
#define  S_L_Mb 4
#define  S_L_Rb 5
#define  S_L_Pb 6
#define  S_L_It 7
#define  S_L_Mt 8
#define  S_L_Rt 9
#define  S_L_Pt 10
#define  S_R_T1 11
#define  S_R_T2 12
#define  S_R_T3 13
#define  S_R_Ib 14
#define  S_R_Mb 15
#define  S_R_Rb 16
#define  S_R_Pb 17
#define  S_R_It 18
#define  S_R_Mt 19
#define  S_R_Rt 20
#define  S_R_Pt 21

// these mod switches never change meaning in chords
// check for them in loops, for mod-specific behavior
#define S_ALT   S_R_T2
#define S_CTRL  S_L_T2
#define S_SHIFT S_R_T3
#define S_ESC   S_L_T3

/* todo: should it send scancodes to bluefruit? or ascii? or what?
 *         -mod strategy requires scancodes with up and down
 * idea: reduce scan frequency if no keypresses detected for a while
 * idea: only insert pairs of parens etc: ()<leftarrow>
 *
 */

//chord_timers holds countdown until chord is registered (>= 0) or
//holds other state description (< 0). Technically only needs to be 19
//or 20 bytes, because some mods don't have stored states. But this
//way we don't have to worry about array order vs scanning order.
// char chord_timers[22]; //signed char
char chord_timer;
short repeat_delay_timer;
short repeat_period_timer;
// bool has_any_chord_timer_elapsed;  //determined by interrupt handler, reset after sending
uint32_t standby_timer;
uint32_t state
uint32_t last_state
bool was_pressed_last; //1 if last change was a press, 0 if last change was a release

// char num_pressed;
// int switches_pressed; 
// char flag_ctrl; //set by scanMatrix, then handled after scan is complete
// char flag_alt;

int main(){
  setup();
  
  while(1){
    scanMatrix();
    checkForChanges();
    
    if(chord_timer == 0 || repeat_period_timer == 0){
      code = translate(state); //translate switches to keys
      send(code)
    }
    // else if(standby_timer == 0){
    //   enter standby mode;
    // }
    // need to set pin interrupts to wake up again if we do that

    //wait briefly?
  }
  return 1;
}

int send(uint32 _state){
  //translate
  //write
  chord_timer = ALREADY_SENT;
  repeat_period_timer = REPEAT_PERIOD;
}

/* update global vars state and last_state */
void scanMatrix(){
  last_state = state;
  state = 0;
  char i = 0;
  for (each hand){
    for(each row){
      set row pin low;
      //note: might need a nop between write and read, see p57
      for (each column){
	val = read from column pin; //combine lines, don't use bool
	state ^= (-val ^ state) & 1<<i; //set i'th bit to switch value
	i++;
      }
      set row pin hi-z;           //(not hi, to save power?)
    }
  }
}

/* if something changed, reset timers and set flags 
 * todo: catch quick tap here
 */
function checkForChanges(){
  if ((state ^ last_state) & state){
    //SOMETHING WAS PRESSED
    if (!was_pressed_last){ //first new press
      chord_timer = PRESS_DELAY;
    }
    //reset repeat timers
    repeat_delay_timer = REPEAT_DELAY;
    repeat_period_timer = REPEAT_PERIOD;
    was_pressed_last = 1;
  }
  else if ((state ^ last_state) & last_state){    
    //SOMETHING WAS RELEASED
    if (was_pressed_last){ //first new release
      if (chord_timer > 0){ //switch was quickly tapped
	send(last_state);
      }
      chord_timer = RELEASE_DELAY;
    }
    repeat_delay_timer = REPEAT_DELAY;
    repeat_period_timer = REPEAT_PERIOD;
    was_pressed_last = 0;
  }
}

/* decrement timers */
void interrupt_handler_1ms(){
   if(chord_timer > 0){
      //countdown from CHORD_DELAY to 0
      chord_timer--;
   }
  
  if (state && 1){ // at least 1 switch is pressed        
    standby_timer = STANDBY_DELAY;
    if (repeat_delay_timer > 0){
      //countdown from REPEAT_DELAY to 0 
      repeat_delay_timer--;
    }
    else if(repeat_delay_timer == 0 && repeat_period_timer > 0){
      //this timer will trigger re-sends after the repeat_delay_timer has run out
      repeat_period_timer--;
    } 
  }
}

void interrupt_handler_LONG(){
  if(standby_timer > 0){
    standby_timer--;
  }
}


int setup(){
  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  was_pressed_last = 0;
  
  //initialization might be unnecessary, depending on program flow / interrupts handlers?
  for (int i=0; i<22; i++){
    chord_timers[i]=NOT_PRESSED;
  }
  
  set column pins input + pullup;
  set row pins input + hi-z;

  intialize serial;
  intialize bluetooth;
   
  return 0;
}


// /* translate switches to keys: TODO HOW? */
// void process(){
//   construct state; //binary representation of pressed switches
//   //  check state against DEFINE list or enum;
//   if (state == normal key, and no previous mods){
//     send(key);
//     for(s = pressed switches){
//       chord_timers[s]=ALREADY_SENT;
//     }
//   }
//   //ctrl sequences should only send when ctrl is released
//   if (state == mod only){
    
//   }
// }
