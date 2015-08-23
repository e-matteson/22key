#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>
#include <avr/wdt.h>

#define S_INTERVAL 0x00
#define S_FLASH 0x01
#define S_SLEEP 0x02
#define L_LONG 0x00
#define L_SHORT 0x01
#define PIN_LONG 2
#define PIN_SHORT 3
#define PIN_BRIGHT 0

//fuse low byte: 1110 0110 
//no prescale, no pinout, default SUT, 128k watchdog


const double CONV_SEC = 7.385; //secs to cycles
const double CONV_MIN = 7.385*60; //secs to cycles
volatile char state;
volatile char length;
volatile uint16_t cnt;

volatile uint16_t flash_counter = 0;
volatile unsigned char num_flashes;
volatile uint16_t cnt_interval;
volatile uint16_t cnt_flash;
volatile unsigned char max_bars;
volatile unsigned char bars;
volatile unsigned char shift;
volatile unsigned char bar_counter;
volatile unsigned char portb_pattern;
volatile unsigned char pattern;

void init_long(void){
  //long work interval settings
  length = L_LONG;
  max_bars = 10;                      //max # of bargraph sections lit up
  shift = 1;                          //spacing b/w bargraph sections
  pattern = 0x80;                     //starting pattern for bargraph multiplexing
  cnt_interval = (int) (2.5*CONV_MIN); //period of each bar
  cnt_flash=(int) (.45*CONV_SEC);       //(half)period of flashe
  num_flashes=6;                      //times LED inverted during alarm

  state = S_INTERVAL;
  bars = max_bars;
  bar_counter = 1;
  portb_pattern=pattern;
  cnt=0;
}
void init_short(void){
  //short break settings
  length = L_SHORT;
  max_bars = 5;
  shift = 2;
  pattern = 0x40;
  cnt_interval =  (int) (1*CONV_MIN); //period of each bargraph section
  cnt_flash= (int) (.15*CONV_SEC);       //(half)period of flashes
  num_flashes=10;

  state = S_INTERVAL;
  portb_pattern=pattern;
  bars = max_bars;
  bar_counter = 1;
  cnt=0;
}

ISR(TIMER0_OVF_vect){
  cnt++;
}

ISR(INT0_vect){
//ok to disable interrupts in here?
  GIMSK &= ~((1<<INT0) | (1<<INT1));  //ext ints disabled  
  init_long();
}

ISR(INT1_vect){
  //ok to disable interrupts in here?
  GIMSK &= ~((1<<INT0) | (1<<INT1));  //ext ints disabled  
  init_short();
}


int main(void){
  wdt_disable();
  set_sleep_mode(SLEEP_MODE_PWR_DOWN); //probs with powerdown + bounce?
  
  ACSR |= (1<<ACD); //disable comparator
  //todo set 11 outs, 2 ins
  DDRB = 0xff; //all out
  DDRD = ~((1<<PIN_LONG)|(1<<PIN_SHORT)); //2 3 in, rest out
  PORTD |= (1<<PIN_LONG)|(1<<PIN_SHORT); //enable pullups 
  
  //timer setup
  TCCR0A = 0x00; //normal mode, disable OC0A and OC0B
  TCCR0B = 0x03; //prescale by 1024, no force output compare
  TIMSK |= 1<<TOIE0;//enable overflow interrupt
  
  init_long();
  sei(); //enable global interrupts      

  while(1){
    switch(state){
    case(S_INTERVAL):
      //cycle leds
      //handle the two portD LEDS
      if(bars==max_bars && bar_counter==bars)
	PORTD ^= (1<<4);
      else
	PORTD &= ~(1<<4);
      if(bars>=max_bars-1 && bar_counter==bars && length==L_LONG)
	PORTD ^= (1<<6);
      else
	PORTD &= ~(1<<6);
      
      //scan through portB LEDs
      if(bar_counter > bars){
	bar_counter = 1;
	portb_pattern=pattern;
      }
      else{
	portb_pattern >>= shift;
      }
      PORTB = portb_pattern;
      bar_counter++;

      //poll buttons, time
      if(!(PIND&(1<<PIN_LONG))){	
	init_long();
      }
      else if(!(PIND&(1<<PIN_SHORT))){
	init_short();
      }
      else if(bars<=0){
	state = S_FLASH;
	PORTB = 0x00;
	PORTD |= (1<<PIN_BRIGHT);
	flash_counter=0;
	cnt = 0;
      }
      else if(cnt > cnt_interval){
	bars--;
	bar_counter=1;
	portb_pattern=pattern;
	cnt = 0;
      }
      break;

    case S_FLASH:
      //flash when time is up
      if(!(PIND&(1<<PIN_LONG))){
	init_long();
      }
      else if(!(PIND&(1<<PIN_SHORT))){
	init_short();
      }
      else if(flash_counter > num_flashes){
	flash_counter=0;
	PORTD &= ~(1<<PIN_BRIGHT);
	cnt=0;
	if(length==L_LONG)
	  init_short();
	else
	  state = S_SLEEP;
      }
      else if(cnt > cnt_flash){
	PORTD ^= (1<<PIN_BRIGHT);
	cnt = 0;
	flash_counter++;
      }
      break;

    case S_SLEEP:
      //this case should only run once, unless switch bounce wakes MCU w/o 
      //  triggering interrupt?
      TIMSK &= ~(1<<TOIE0);  //disable overflow int
      sleep_enable();
      GIMSK |= (1<<INT0) | (1<<INT1);  //enable ext ints, default low level
      sleep_cpu();
      //int0 or int1 handler should run here, set state
      sleep_disable();
      TIMSK |= 1<<TOIE0;//re-enable overflow int
      break;

    default:
      0==0;
    }
  }
}
