# 22key

Firmware for an attiny2313a in a 22 key chording keyboard.

Unfinished.



## MOD KEY EXPLANATION

BUT THERE'S NO RELATIVE UP/DOWN COMMAND, JUST SEND LIST OF CURRENTLY PRESSED KEYS

Mods don't have chord timers. Either they're sent immediately, or
their entries are set to MOD_HELD when pressed.

### For ctrl and alt:
  Send 'ctrl down' as soon as ctrl is pressed.
  Send 'ctrl up' as soon as ctrl is released. (and same for alt)

### For esc: TODO
  Should it behave like a normal keyboard?
  Or can meta be made holdable/reuseable, like ctrl and alt?

### For shift: 
  Set chord_timer[i] to MOD_HELD when pressed.
  Use when translating matrix to key after some other chord timer runs out.
  Don't send directly - shift pairs may not match dvorak's pairs.
  Set chord_timer[i] to NOT_PRESSED when released.


## Translation ideas

Need to associate switch matrix states with usage codes. Maybe with key names in between, for clarity. 

### binary, indexing into usage code array

1. represent current state as 22bit binary value (in int32 or whatever).
2. use value to index into char[?] array containing corresponding usage codes.

Problem: array is huge and sparse. worst case is char[2^22], no go.


### binary, else-if

1. represent current state as 22bit binary value (in int32 or whatever).
2. have giant list of `#define KEYNAME 0xState`
3. have giant chain of `else if(state == KEYNAME){ send(usage_code);}`


### binary, generated else-if

1. Write python to:

  1. parse a nice keymap config file
  
  2. construct translate function, output to translate.c: (pass pointer if needed)
  
   ```c
   char translate(uint32_t state, unsigned char usage_codes,  ){
   	if(state == 0xMatrix){
	   return 0xUsageCode;
	}
	if(state ==  ...
   }
   ```
2. in main file, `#include <translate.h>`

### Benefits:

* no big lists of #defines
* little stack usage, compared to arrays or enums.
* easier to re-map than if manually maintained

### Drawbacks:

* c code is less readable without accompanying python script



## Notes:

USB-HID spec has requirements this probably won't meet, especially for boot keyboards.
I want to use bluefruit for Tx only...