//pseudo code
//should it send scancodes to bluefruit? or ascii? or what?
#include <avr/io.h>

#define MOD_HELD        -1  // mod keys don't have chord timers
#define ALREADY_SENT    -2  // >= ALREADY_SENT means currently pressed
#define NOT_PRESSED     -3  // <= NOT_PRESSED means not currently pressed
//#define MOD_RELEASED    -4

#define CHORD_DELAY    10    //timer units TBD
#define REPEAT_DELAY   1000
#define REPEAT_PERIOD  50
#define STANDBY_DELAY  10000   //different units than other timers, long!

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

#define IS_MOD(x) (x == S_ALT) || (x == S_CTRL) || (x == S_ESC) || (x == S_SHIFT)

/* MOD EXPLANATION 
Mods don't have chord timers. Their entries are set
to MOD_HELD when pressed. 

******** When a normal switch's chord timer runs out...
*** while ctrl is held: 

send 'ctrl down', 'normal key down', 'normal key up'. 
Then whenever ctrl is released, send 'ctrl up' immediately. This
should make emacs shortcuts like 'ctrl+x+s' and 'ctrl+x s' work
properly.


*** while alt is held:
send 'alt down', 'normal key down', 'normal key up', 'alt up'


*** while shift is held:
Use shift to determine normal key - shifted pairs may not match dvorak's pairs.
Send 'normal key down', 'normal key up'.
Should never need to send shift directly.

*** while esc is held:
TODO. is esc / meta weird? should it behave the same way as a typical
keyboard, or can I make meta holdable/reuseable
?
*/

//state holds countdown until chord is registered (>= 0) or other state description (< 0)
char chord_timers[22]; //signed char
short repeat_delay_timer;
short repeat_period_timer;
bool is_any_switch_pressed;
bool has_any_chord_timer_elapsed;
int standby_timer;
char num_pressed;
int switches_pressed; 

int setup(){

  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  is_any_switch_pressed = 0;
  has_any_chord_timer_elapsed = 0;

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


/* decrement timers */
void interrupt_handler_1ms(){
  is_any_switch_pressed = 0;
  for(int i=0; i<22; i++){
    if(chord_timers[i] > 0){
      //countdown from CHORD_DELAY to 0
      //excludes mods because MOD_HELD < 0
      chord_timers[i]--;
    }
    
    if(chord_timers[i] == 0){
      has_any_chord_timer_elapsed = 1;
    }

    if(chord_timers[i] >= ALREADY_SENT){
      //includes mods
      is_any_switch_pressed == 1;
    }
  }
  
  if (is_any_switch_pressed){
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

int loop(){
  scanMatrix();
  if(has_any_chord_timer_elapsed){
    process();
  }
  //sleep briefly?
}


/* update global chord_timers array */
void scanMatrix(){
  char i = 0;
  for (each hand){
    for(each row){
      set row pin low;
      //note: might need a nop between write and read, see p57
      for (each column){
	val = read from column pin;
	if( val == LOW && chord_timers[i] == NOT_PRESSED){
	  //newly pressed
	  if( IS_MOD(i) ){
	    //has no timer
	    chord_timers[i] == MOD_HELD;
	  }
	  else{
	    //reset chord timer
	    chord_timers[i] == CHORD_DELAY;
	  }
	  //reset delay timers
	  repeat_delay_timer = REPEAT_DELAY;
	  repeat_period_timer = REPEAT_PERIOD;
	}
	else if( val == HIGH && chord_timers[i] >= ALREADY_SENT){
	  //newly released, reset repeat timers
	  chord_timers[i] = NOT_PRESSED;
	  if(i == S_CTRL){
	    send_ctrl_released(); //or use general function, whatever
	  }
	  repeat_delay_timer = REPEAT_DELAY;
	  repeat_period_timer = REPEAT_PERIOD;
	}
	i++;
      }
      set row pin hi-z;           //(not hi, to save power?)
    }
  }
  
}


void process(){
  construct state; //binary representation of pressed switches
  //  check state against DEFINE list or enum;
  if (state == normal key, and no previous mods){
    send(key);
    for(s = pressed switches){
      chord_timers[s]=ALREADY_SENT;
    }
  }
  //ctrl sequences should only send when ctrl is released
  if (state == mod only){
    
  }
}


