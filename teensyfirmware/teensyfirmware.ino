#include <TimerOne.h>
#define CHORD_DELAY    25   // * ~2ms
#define HELD_DELAY     200
#define REPEAT_DELAY   20000
#define REPEAT_PERIOD  50
#define DEBOUNCE_DELAY 1     //only applies to quick tap/release


#define PRESSED       1  // pressed and not sent yet
#define ALREADY_SENT  2  // sent, don't resend
#define HELD          3  // sent, but ok to resend
/* #define TAPPED        4  // released before chord timer ran out, please send */
#define NOT_PRESSED   0  // not currently pressed
// #define PLEASE_SEND_LAST_STATE -4
#define NUM_ROWS 3
#define NUM_COLS 4
#define NUM_HANDS 2
//there's 22 physical switches, but the array must hold all 24 row/col/hand combos
#define NUM_SWITCHES NUM_ROWS*NUM_COLS*NUM_HANDS 
//using input without pullup as hiZ state
#define HI_Z INPUT

uint8_t row_pins[NUM_HANDS][NUM_ROWS]= {{3,4,5}, {20, 21,22}};
uint8_t col_pins[NUM_HANDS][NUM_COLS] = {{6,7,8,9}, {16, 17, 18, 19}};

int32_t chord_timer;
int32_t held_timer;
int32_t repeat_delay_timer;
int32_t repeat_period_timer;
uint32_t standby_timer;
uint32_t state = 0;
bool pressed_array[NUM_SWITCHES];
uint8_t status_array[NUM_SWITCHES];
bool is_any_switch_pressed;

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
  for(uint8_t i = 0; i != NUM_SWITCHES; i++){
    status_array[i] = NOT_PRESSED;
  }
  chord_timer = -1;
  held_timer = -1;
  repeat_delay_timer = REPEAT_DELAY;
  repeat_period_timer = REPEAT_PERIOD;
  is_any_switch_pressed = 0;

  Timer1.initialize(2083); //microsecs. multiple of 48MHz period.
  /* Timer1.initialize(2083*10000); //microsecs. multiple of 48MHz period. */
  Timer1.attachInterrupt(decrement_timers);
  // intialize serial? seems to work out-of-the-box
  //  intialize bluetooth;

}

void loop() {
  scanMatrix();
  checkForChanges();
  if(held_timer == 0){
    for(uint8_t i = 0; i!= NUM_SWITCHES; i++){
      if(status_array[i] == ALREADY_SENT){
        status_array[i] = HELD;
      }
    }
  }
  /* if(chord_timer == 0 || repeat_period_timer == 0){ */
  if(chord_timer == 0){
    state = 0;
    for(uint8_t i = 0; i!= NUM_SWITCHES; i++){
      if(status_array[i] == ALREADY_SENT){
        Serial.println(held_timer);
      }
      if (status_array[i] == PRESSED || status_array[i] == HELD){
        state |= 1<<i;
        status_array[i] = ALREADY_SENT;
      }
    }
    translate_and_send(state);
  }
  //wait briefly?
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

        /* if (pressed_array[i]){ */
        /*   Serial.print(r); */
        /*   Serial.print(", "); */
        /*   Serial.println(c); */
        /*   Serial.println(i); */
        /* } */
        i++;
      }
      pinMode(col_pins[h][c], HI_Z);
    }
  }
}

/* if something changed, reset timers and set flags 
 * if a switch was tapped and released, send the last_state immediately
 */
void checkForChanges(){
  /* state_changes = state ^ last_state; */
  state = 0;
  is_any_switch_pressed = 0;
  for(uint8_t i=0; i!=NUM_SWITCHES; i++){
    if(!pressed_array[i]){
      // switch is NOT pressed
      switch(status_array[i]){
      case NOT_PRESSED:
        break;
      case ALREADY_SENT:
        held_timer = HELD_DELAY;
        status_array[i] = NOT_PRESSED;
        break;
      case HELD:
        held_timer = HELD_DELAY;
        status_array[i] = NOT_PRESSED;
        break;
      case PRESSED:
        held_timer = HELD_DELAY;
        if (chord_timer <= (CHORD_DELAY - DEBOUNCE_DELAY)){
          //this is a quick tap and should be sent
          status_array[i] = PRESSED;
          // force a send during this loop
          chord_timer = 0;
          break;
        }
      }
    }
    else if(pressed_array[i]){
      // switch IS pressed
      is_any_switch_pressed = 1;
      switch(status_array[i]){
      case NOT_PRESSED:
        //new press
        chord_timer = CHORD_DELAY;
        held_timer = HELD_DELAY;
        status_array[i] = PRESSED;
        break;
      case ALREADY_SENT:
        break;
      case HELD:
        break;
      case PRESSED:
        break;
      }
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

  chord_timer = -1;
  repeat_period_timer = REPEAT_PERIOD;
}


 
void decrement_timers(){
  if(chord_timer > 0){
    //countdown from CHORD_DELAY to 0
    /* if (!(chord_timer % 5)){ */
    /* Serial.println(chord_timer); */
    /* } */
    chord_timer--;
  }
  if(held_timer > 0) {
    held_timer--;
  }
  if (is_any_switch_pressed){ // at least 1 switch is pressed
    /* standby_timer = STANDBY_DELAY; */
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





