#include <TimerOne.h>
// #include <TimerOne.h>
#define SHIFT_SWITCH_NUM 26 

#define PRESS_DELAY    100    // * ~2ms
#define RELEASE_DELAY  150    // * ~2ms
#define REPEAT_DELAY   20000
#define REPEAT_PERIOD  50
#define DEBOUNCE_DELAY 1     //only applies to quick tap/release

// #define MOD_HELD        -1  // mod keys don't have chord timers

#define ALREADY_SENT  -2  // >= ALREADY_SENT means currently pressed

// #define NOT_PRESSED     -3  // <= NOT_PRESSED means not currently pressed
// #define PLEASE_SEND_LAST_STATE -4
#define NUM_ROWS 3
#define NUM_COLS 4
#define NUM_HANDS 2
//using input without pullup as hiZ state
#define HI_Z INPUT

uint8_t row_pins[NUM_HANDS][NUM_ROWS]= {{20, 21,22}, {7,8,9}};
uint8_t col_pins[NUM_HANDS][NUM_COLS] = {{16, 17, 18, 19}, {3,4,5,6}};

int32_t chord_timer;
short repeat_delay_timer;
short repeat_period_timer;
// bool has_any_chord_timer_elapsed;  //determined by interrupt handler, reset after sending
uint32_t standby_timer;
uint32_t state = 0;
uint32_t last_state = 0;
bool last_change_was_press; //1 if last change was a press, 0 if last change was a release
uint32_t state_changes;

void setup() {
// row_pins 
//initialize rows and columns - todo both hands
  for(uint8_t h = 0; h != NUM_HANDS; h++){
    for(uint8_t r = 0; r != NUM_ROWS; r++){
      pinMode(row_pins[h][r], INPUT_PULLUP);
    }
    for(char c = 0; c != NUM_COLS; c++){
      pinMode(col_pins[h][c], HI_Z);
    }
  }
  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  last_change_was_press = false;
  Timer1.initialize(2083); //microsecs. multiple of 48MHz period.
  Timer1.attachInterrupt(decrement_timers);
  // intialize serial? seems to work out-of-the-box
  //  intialize bluetooth;

} 

void loop() {
  Serial.println(KEY_A);
  Serial.println(KEY_B);
  // Serial.println(KEY_
    

  /**** TODO
   * why is a -> ab -> a  non-deterministic? what should it be?
   */
  /* delay(50); */
  /* Keyboard.set_key2(KEY_B); */
  /* Keyboard.send_now(); */
  /* delay(50); */
  /* Keyboard.set_key1(0); */
  /* Keyboard.set_key2(0); */
  /* Keyboard.send_now(); */

  // scanMatrix();
  // checkForChanges();

  // Serial.println(state);
    // uint32_t F_MASK = 1<<1;
    // Serial.println(F_MASK);
 
  
  // if(chord_timer == 0 || repeat_period_timer == 0){
  // if(chord_timer == 0){
  //       translate_and_send(state);
  // }
  // last_state = state;
  //wait briefly?
}


void scanMatrix(){
  state = 0;
  int i = 0;
  bool val = 0;
  for (uint8_t h = 0; h != NUM_HANDS; h++){

    for (uint8_t c = 0; c != NUM_COLS; c++){
      // Serial.println(r);
      pinMode(col_pins[h][c], OUTPUT);
      digitalWrite(col_pins[h][c], LOW);
      delayMicroseconds(10); //todo find minimum, if things are slow
    
      for(uint8_t r = 0; r != NUM_ROWS; r++){
	//true if high
	val = (digitalRead(row_pins[h][r]) == LOW); //combine lines, don't use bool
	state ^= (-val ^ state) & 1<<i; //set i'th bit to switch value
	i++;
	if (val && state != last_state){
		Serial.print(r);
		Serial.print(", ");
		Serial.println(c);
	}
      }
      pinMode(col_pins[h][c], HI_Z);
    }
  }
}

void send(uint8_t letter, bool flag_shift, uint8_t mod_byte){
  //but Keyboard uses names, BLE uses usage codes...

  
  // Serial.print("(");
  // if (flag_ctrl){
  //   Serial.print("^");
  // }
  // Serial.print(letter);
  // Serial.print(")");
  // Serial.println(chord_timer);

  Keyboard.set_key1(letter);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  
  if (flag_shift){
    Keyboard.set_modifier(MODIFIERKEY_SHIFT);
  }
  Keyboard.send_now();
  
  delay(50);
  Keyboard.set_key1(0);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  // if (!flag_shift){
    Keyboard.set_modifier(0);
  // }
  Keyboard.send_now();

  chord_timer = ALREADY_SENT;
  repeat_period_timer = REPEAT_PERIOD;
}

void translate_and_send(uint32_t _state){
    //blank out mods except shift, set mod_byte
  char mod_byte = 0;
  //exact matches that depend on shift, some are macros

  //matches disregarding shift
  //set shift_flag, clear shift bit in state
  bool shift_flag=_state && 1<<SHIFT_SWITCH_NUM; 
  _state &= ~ 1<<SHIFT_SWITCH_NUM;
  if(_state == 32768){		//KEY_d
    send(7, shift_flag, mod_byte);
  }
  if(_state == 131072){		//KEY_g
    send(10, shift_flag, mod_byte);
  }
  if(_state == 65536){		//KEY_f
    send(9, shift_flag, mod_byte);
  }
  if(_state == 8192){		//KEY_a
    send(4, shift_flag, mod_byte);
  }
  if(_state == 16384){		//KEY_b
    send(5, shift_flag, mod_byte);
  }
  if(_state == 4){		//KEY_m
    send(16, shift_flag, mod_byte);
  }
  if(_state == 1){		//KEY_v
    send(25, shift_flag, mod_byte);
  }
  if(_state == 4096){		//KEY_o
    send(18, shift_flag, mod_byte);
  }
  if(_state == 128){		//KEY_n
    send(17, shift_flag, mod_byte);
  }
  if(_state == 1048576){		//KEY_i
    send(12, shift_flag, mod_byte);
  }
  if(_state == 512){		//KEY_h
    send(11, shift_flag, mod_byte);
  }
  if(_state == 8){		//KEY_k
    send(14, shift_flag, mod_byte);
  }
  if(_state == 16){		//KEY_j
    send(13, shift_flag, mod_byte);
  }
  if(_state == 1024){		//KEY_u
    send(24, shift_flag, mod_byte);
  }
  if(_state == 256){		//KEY_t
    send(23, shift_flag, mod_byte);
  }
  if(_state == 2){		//KEY_w
    send(26, shift_flag, mod_byte);
  }
  if(_state == 3072){		//KEY_q
    send(20, shift_flag, mod_byte);
  }
  if(_state == 262144){		//KEY_p
    send(19, shift_flag, mod_byte);
  }
  if(_state == 64){		//KEY_s
    send(22, shift_flag, mod_byte);
  }
  if(_state == 2097152){		//KEY_x
    send(27, shift_flag, mod_byte);
  }
  if(_state == 524288){		//KEY_y
    send(28, shift_flag, mod_byte);
  }
  if(_state == 2048){		//KEY_e
    send(8, shift_flag, mod_byte);
  }
  else{
    //only mods are down
    send(0, shift_flag, mod_byte);
  }
}

// void MANUALtranslate_and_send(uint32_t _state){
//   // Serial.print("transend! ");
//   // Serial.print(_state);
  

//   uint32_t CTRL_MASK = 1<<0;  
//   uint32_t F_MASK = 1<<1;
//   uint32_t  B_MASK = 1<<4;
//   uint32_t N_MASK = 1<<7;
//   uint32_t P_MASK = 1<<10;
  
//   //blank out mods except shift, set mod flags
//   int flag_ctrl = _state & CTRL_MASK && 1;		//KEY_leftcontrol
//   _state &= ~CTRL_MASK; //blank out ctrl bit
//   // Serial.print(", ");
//   // Serial.println(_state);
  
//     if (!_state){
//   //if everything was released, don't send anything
//   // todo think about how this interacts with mods
//     send(0, flag_ctrl);
//     return;
//   }
  
//   if (_state == F_MASK){
//     send(KEY_X, flag_ctrl);
//   }
//   else if (_state == B_MASK){
//     send(KEY_B, flag_ctrl);
//   }
//   else if (_state == N_MASK){
//     send(KEY_N, flag_ctrl);
//   }
//   else if (_state == P_MASK){
//     send(KEY_P, flag_ctrl);
//   }
//   else{
//     // Serial.print("BAD STATE: ");
//     // Serial.print(_state);
//     send(0, flag_ctrl);
//   }
//   return;
// }
  //exact matches that depend on shift, some are macros

  
  // if(_state == 24580){		//macro_paren
  //   send(38, 1, mod_byte);
  //   send(39, 1, mod_byte);
  //   send(80, 0, mod_byte);
  // }

  // //matches disregarding shift
  // set shift_flag, blank out shift bit in _state
  // if(_state == 1056784){		//KEY_E
  //   send(8, shift_flag, mod_byte);
  // }
  // if(_state == 2105376){		//KEY_D
  //   send(7, shift_flag, mod_byte);
  // }
  // if(_state == 270340){		//KEY_G
  //   send(10, shift_flag, mod_byte);
  // }
  // if(_state == 532488){		//KEY_F
  //   send(9, shift_flag, mod_byte);
  // }
  // if(_state == 73744){		//KEY_I
  //   send(12, shift_flag, mod_byte);
  // }
  // if(_state == 40968){		//KEY_J
  //   send(13, shift_flag, mod_byte);
  // }
  // else{
  //   //only mods are down
  //   send(0, shift_flag, mod_byte);}


/* if something changed, reset timers and set flags 
 * if a switch was tapped and released, send the last_state immediately
 */
void checkForChanges(){
  state_changes = state ^ last_state;
  if (state_changes & state){
    //SOMETHING WAS PRESSED
    //always reset/extend chord_timer
    chord_timer = PRESS_DELAY;
    last_change_was_press = true;
  }
  else if (state_changes & last_state){    
    //SOMETHING WAS RELEASED
    if (last_change_was_press
	&& chord_timer > 0
	&& chord_timer <= (PRESS_DELAY-DEBOUNCE_DELAY)){
	//switch was quickly tapped, force it to send last_state now
      translate_and_send(last_state);
    }
    chord_timer = RELEASE_DELAY;
    last_change_was_press = false;
  }
  if (state_changes){
    // either pressed or released - common code
    //reset repeat timers
    repeat_delay_timer = REPEAT_DELAY;
    repeat_period_timer = REPEAT_PERIOD;
  }
}

 
void decrement_timers(){
  // Serial.println("dec");

   if(chord_timer > 0){
      //countdown from CHORD_DELAY to 0
     // if (!(chord_timer % 25)){
     //   Serial.println(chord_timer);
     // }
     chord_timer--;
   }
  
  // if (state && 1){ // at least 1 switch is pressed        
  if (state){ // at least 1 switch is pressed        
    // standby_timer = STANDBY_DELAY;
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


      // if (!val){
      // 	Serial.print(r);
      // 	Serial.print(", ");
      // 	Serial.println(c);
      // }



