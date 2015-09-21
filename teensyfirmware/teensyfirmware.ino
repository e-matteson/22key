#include <TimerOne.h>

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
//using input without pullup as hiZ state
#define HI_Z INPUT

char row_pins[NUM_ROWS]= {7,8,9};
char col_pins[NUM_COLS] = {3,4,5,6};

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
  for(char r = 0; r != NUM_ROWS; r++){
    pinMode(row_pins[r], INPUT_PULLUP);
  }
  for(char c = 0; c != NUM_COLS; c++){
    pinMode(col_pins[c], HI_Z);
  }

  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  last_change_was_press = false;
  Timer1.initialize(2083); //microsecs. multiple of 48MHz period.
  Timer1.attachInterrupt(decrement_timers);
  // intialize serial?
  //  intialize bluetooth;
} 

void loop() {
  /**** TODO
   * why is a -> ab -> a  non-deterministic? what should it be?
   */
  scanMatrix();
  checkForChanges();

  // if(chord_timer == 0 || repeat_period_timer == 0){
  if(chord_timer == 0){
    send(state);
  }
  // else if(chord_timer == PLEASE_SEND_LAST_STATE){
  //   send(last_state);
  // }
  last_state = state;
  //wait briefly?
}


void scanMatrix(){
  state = 0;
  int i = 0;
  bool val = 0;
  for (int c = 0; c != NUM_COLS; c++){
    // Serial.println(r);
    pinMode(col_pins[c], OUTPUT);
    digitalWrite(col_pins[c], LOW);
    delayMicroseconds(10); //todo find minimum, if things are slow
    
    for(int r = 0; r != NUM_ROWS; r++){
      //true if high
      val = (digitalRead(row_pins[r]) == LOW); //combine lines, don't use bool
      state ^= (-val ^ state) & 1<<i; //set i'th bit to switch value
      i++;
      // if (val){
      // 	Serial.println("BLARGH");
      // }
      }
    pinMode(col_pins[c], HI_Z);
  }
}

void send(uint32_t _state){
  //todo translate
  //write
  // uint32_t A_MASK = 1<<1;
  // uint32_t  B_MASK = 1<<4;
  // uint32_t C_MASK = 1<<7;
  // uint32_t D_MASK = 1<<9;
  if (!_state){
    //if everything was released, don't send anything
    // todo think about how this interacts with mods
    return;
  }

  uint32_t A_MASK = 1<<1;
  uint32_t  B_MASK = 1<<4;
  uint32_t C_MASK = 1<<7;
  uint32_t D_MASK = 1<<10;

  Serial.print("(");
  if (_state & A_MASK){
    // Keyboard.
    Serial.print("a");
  }
  if (_state & B_MASK){
    Serial.print("b");
  }
  if (_state & C_MASK){
    Serial.print("c");
  }
  if (_state & D_MASK){
    Serial.print("d");
  }
  
  Serial.print("), up ");
  Serial.println(chord_timer);

  chord_timer = ALREADY_SENT;
  repeat_period_timer = REPEAT_PERIOD;
  // Serial.println(state);
  // Serial.println(last_state);
}


/* if something changed, reset timers and set flags 
 * todo: catch quick tap here
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
      send(last_state);
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
