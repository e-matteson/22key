#include <TimerOne.h>
#define PRESS_DELAY    100    // * ~2ms

#define RELEASE_DELAY  150    // * ~2ms
#define REPEAT_DELAY   20000
#define REPEAT_PERIOD  50
#define DEBOUNCE_DELAY 1     //only applies to quick tap/release

// #define MOD_HELD        -1  // mod keys don't have chord timers

#define ALREADY_SENT  -1  // >= ALREADY_SENT means currently pressed
#define HELD          -2
#define NOT_PRESSED   -3  // <= NOT_PRESSED means not currently pressed
// #define PLEASE_SEND_LAST_STATE -4
#define NUM_ROWS 3
#define NUM_COLS 4
#define NUM_HANDS 2
//using input without pullup as hiZ state
#define HI_Z INPUT

//uint8_t row_pins[NUM_HANDS][NUM_ROWS]= {{7,8,9}, {20, 21,22}};
//uint8_t col_pins[NUM_HANDS][NUM_COLS] = {{3,4,5,6}, {16, 17, 18, 19}};
uint8_t row_pins[NUM_HANDS][NUM_ROWS]= {{3,4,5}, {20, 21,22}};
uint8_t col_pins[NUM_HANDS][NUM_COLS] = {{6,7,8,9}, {16, 17, 18, 19}};

int32_t chord_timer;
short repeat_delay_timer;
short repeat_period_timer;
// bool has_any_chord_timer_elapsed;  //determined by interrupt handler, reset after sending
uint32_t standby_timer;
uint32_t state = 0;
uint32_t last_state = 0;
bool last_change_was_press; //1 if last change was a press, 0 if last change was a release
uint32_t state_changes;
/* uint16_t state_array; */

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
  scanMatrix();
  checkForChanges();
  
  /* Serial.println(state); */
  if(chord_timer == 0 || repeat_period_timer == 0){
    if(chord_timer == 0){
      translate_and_send(state);
    }
  }
  last_state = state;
    //wait briefly?
    //delay(100);
}

void scanMatrix(){
  state = 0;
  int i = 0;
  bool val = 0;
  for (uint8_t h = 0; h != NUM_HANDS; h++){
    for (uint8_t c = 0; c != NUM_COLS; c++){
      pinMode(col_pins[h][c], OUTPUT);
      digitalWrite(col_pins[h][c], LOW);
      delayMicroseconds(10); //todo find minimum, if things are slow
    
      for(uint8_t r = 0; r != NUM_ROWS; r++){
        //val is true if the switch is pressed
        val = (digitalRead(row_pins[h][r]) == LOW); //combine lines, don't use bool
        state ^= (-val ^ state) & 1<<i; //set i'th bit to switch value
        i++;
        /* if (val && state != last_state){ */
        /*   Serial.print(r); */
        /*   Serial.print(", "); */
        /*   Serial.println(c); */
        /* } */
      }
      pinMode(col_pins[h][c], HI_Z);
    }
  }
}

void send(uint8_t letter, uint8_t mod_byte){
  //but Keyboard uses names, BLE uses usage codes...
  Serial.print("sending:");
  Serial.println(letter);
  Keyboard.set_key1(letter);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  Keyboard.set_modifier(mod_byte);
  Keyboard.send_now();
  
  delay(50);
  Keyboard.set_key1(0);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  //todo consider not releasing modifiers. does it ever matter?
  Keyboard.set_modifier(0);
  Keyboard.send_now();

  chord_timer = ALREADY_SENT;
  repeat_period_timer = REPEAT_PERIOD;
}




/* if something changed, reset timers and set flags 
 * if a switch was tapped and released, send the last_state immediately
 */
void checkForChanges(){
  state_changes = state ^ last_state;

  if (state_changes & state){
    //SOMETHING WAS PRESSED
    //always reset/extend chord_timer
    Serial.println("new press");
    chord_timer = PRESS_DELAY;
    last_change_was_press = true;
  }
  else if (state_changes & last_state){    
    //SOMETHING WAS RELEASED
    Serial.println("new release");
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
    Serial.print("last: ");
    Serial.println(last_state);
    Serial.print("state: ");
    Serial.println(state);
  }
}

 
void decrement_timers(){
  // Serial.println("dec");

   if(chord_timer > 0){
      //countdown from CHORD_DELAY to 0
     /* if (!(chord_timer % 5)){ */
       /* Serial.println(chord_timer); */
     /* } */
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



