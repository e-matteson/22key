#include <TimerOne.h>
// maximum values of the countdown timers
#define CHORD_DELAY    25   
#define HELD_DELAY     100
#define DEBOUNCE_DELAY 2
#define REPEAT_DELAY   400
#define REPEAT_PERIOD  15

// units for timers
#define TIMER_TICK     2083  //microsecs. 2083 is multiple of 48MHz period.

//keyboard size
#define NUM_ROWS 3
#define NUM_COLS 4
#define NUM_HANDS 2
//(there's 22 physical switches, but the array must fit all 24 row/col/hand combos)
#define NUM_SWITCHES NUM_ROWS*NUM_COLS*NUM_HANDS 

//using input without pullup as hiZ state
#define HI_Z INPUT 

//possible statuses for the status_array
enum status_t{
  DEBOUNCE,        // newly pressed, might be a bounce (increase delay at end of loop if there's still bounce)
  PRESSED,         // pressed and not sent yet
  ALREADY_SENT,    // sent, don't resend
  HELD,            // sent, but ok to resend
  NOT_PRESSED,     // not currently pressed
};

//teensy LC I/O pin numbers
uint8_t row_pins[NUM_HANDS][NUM_ROWS]= {{3,4,5}, {20, 21,22}};
uint8_t col_pins[NUM_HANDS][NUM_COLS] = {{6,7,8,9}, {16, 17, 18, 19}};

//variables to hold timer values
int32_t chord_timer;
int32_t held_timer;
int32_t repeat_delay_timer;
int32_t repeat_period_timer;
int32_t debounce_timer;
uint32_t standby_timer;

bool pressed_array[NUM_SWITCHES];    //simple boolean values, set by scanMatrix()
status_t status_array[NUM_SWITCHES]; //used in a state machine for complex behaviors

bool is_any_switch_pressed;           //flag used by decrement_timers()


void setup() {
  //initialize pins for rows and columns of keyboard matrix
  for(uint8_t h = 0; h != NUM_HANDS; h++){
    for(uint8_t r = 0; r != NUM_ROWS; r++){
      pinMode(row_pins[h][r], INPUT_PULLUP);
    }
    for(char c = 0; c != NUM_COLS; c++){
      pinMode(col_pins[h][c], HI_Z);
    }
  }
  //initialize switch statuses
  for(uint8_t i = 0; i != NUM_SWITCHES; i++){
    status_array[i] = NOT_PRESSED;
  }
  //initialize flag
  is_any_switch_pressed = 0;

  //initialize timers
  chord_timer = -1;
  held_timer = -1;
  debounce_timer = -1;
  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  Timer1.initialize(TIMER_TICK); //microsecs
  Timer1.attachInterrupt(decrement_timers);
  //todo: intialize serial? seems to work out-of-the-box
}

void loop() {
  scanMatrix();
  updateSwitchStatuses();

  if(held_timer == 0){
    checkForHeldSwitches();
    held_timer = -1;
  }

  if(chord_timer == 0 || repeat_period_timer == 0){
    // translation is implemented in a separate file
    translateAndSendState(getState());
  }
  //wait briefly? helps with debouncing
  delay(2); //millisecs
}

void scanMatrix(){
  int i = 0;
  bool pressed = 0;
  for (uint8_t h = 0; h != NUM_HANDS; h++){
    for (uint8_t c = 0; c != NUM_COLS; c++){
      pinMode(col_pins[h][c], OUTPUT);
      digitalWrite(col_pins[h][c], LOW);
      delayMicroseconds(10); //todo find minimum, if things are slow
      for(uint8_t r = 0; r != NUM_ROWS; r++){
        //true if the switch is pressed
        pressed_array[i] = (digitalRead(row_pins[h][r]) == LOW);
        i++;
      }
      pinMode(col_pins[h][c], HI_Z);
    }
  }
}

/* if something changed, reset timers and set flags 
 * if a switch was tapped and released, send the last_state immediately
 */
void updateSwitchStatuses(){
  is_any_switch_pressed = 0;
  for(uint8_t i=0; i!=NUM_SWITCHES; i++){
    if(!pressed_array[i]){
      // switch is NOT pressed
      switch(status_array[i]){

      case NOT_PRESSED:
      case DEBOUNCE:
        status_array[i] = NOT_PRESSED;
        break;

      case ALREADY_SENT:
      case HELD:
        //switch was released, and it was already sent previously
        status_array[i] = NOT_PRESSED;
        resetInactivityTimers();
        break;

      case PRESSED:
        //switch was quickly tapped and released, and should be sent now
        status_array[i] = PRESSED;
        chord_timer = 0; //force send
        resetInactivityTimers();
        break;
      }
    }
    else if(pressed_array[i]){
      // switch IS pressed
      is_any_switch_pressed = 1;
      switch(status_array[i]){

      case ALREADY_SENT:
      case HELD:
      case PRESSED:
        break;

      case NOT_PRESSED:
        //maybe it's a new press, debounce it first
        status_array[i] = DEBOUNCE;
        /* debounce_timer = DEBOUNCE_DELAY; */
        break;

      case DEBOUNCE:
        //using the debounce timer makes chording unreliable - todo why?
        /* if(!debounce_timer){ */
          //new press
          status_array[i] = PRESSED;
          chord_timer = CHORD_DELAY;
          //could just stay at 0, but lets make timers be -1 when not in use
          /* debounce_timer = -1; */
          resetInactivityTimers();
        /* } */
        break;
      }
    }
  }
}

void resetInactivityTimers(){
  //call this when something changes, to reset the timers that check for changes
  held_timer = HELD_DELAY;
  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  //todo put standby timer in here too
}

void checkForHeldSwitches(){
  // if any switches have been held down for a while, let them be re-sent
  //  in future chords.
  for(uint8_t i = 0; i!= NUM_SWITCHES; i++){
    if(status_array[i] == ALREADY_SENT){
      status_array[i] = HELD;
    }
  }
}

uint32_t getState(){
  //construct a binary representation of the keyboard state from the status_array
  uint32_t state_to_send = 0;
  for(uint8_t i = 0; i!= NUM_SWITCHES; i++){
    if (status_array[i] == PRESSED){
      state_to_send |= 1<<i; //add to state, so it will be sent
      status_array[i] = ALREADY_SENT;
    }
    else if(status_array[i] == HELD){
      state_to_send |= 1<<i; //add to state, so it will be sent
      //keep status as HELD
    }
  }
  return state_to_send; 
}

void sendOverUSB(uint32_t key_code, uint8_t mod_byte){
  //but Keyboard uses names, BLE uses usage codes...
  /* Serial.print("sending:"); */
  /* Serial.println(key_code); */
  
  Keyboard.set_key1(key_code);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  Keyboard.set_modifier(mod_byte);
  Keyboard.send_now();
  
  delay(1); //millisecs
  Keyboard.set_key1(0);
  Keyboard.set_key2(0);
  Keyboard.set_key3(0);
  Keyboard.set_key4(0);
  Keyboard.set_key5(0);
  Keyboard.set_key6(0);
  //todo consider not releasing modifiers. does it ever matter?
  Keyboard.set_modifier(0);
  Keyboard.send_now();

  chord_timer = -1;
  repeat_period_timer = REPEAT_PERIOD;
}

void decrement_timers(){
  //check all timers, and decrement them if necessary
  if(chord_timer > 0){
    chord_timer--;
  }
  if(held_timer > 0) {
    held_timer--;
  }
  /* if(debounce_timer > 0) { */
  /*   debounce_timer--; */
  /* } */
  if (is_any_switch_pressed){ 
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

