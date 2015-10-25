#define SHIFT_SWITCH_NUM 131072 
#define CTRL_SWITCH_NUM 8388608 
#define ALT_SWITCH_NUM 2048 
#define GUI_SWITCH_NUM 32 

void translate_and_send(uint32_t _state){
  //blank out mods except shift, set mod_byte
  char mod_byte = 0;
  if(_state & 1<<23){		//KEY_CTRL
    mod_byte |= MODIFIERKEY_CTRL;
    _state &= ~ (1<<23);
  }
  if(_state & 1<<5){		//KEY_GUI
    mod_byte |= MODIFIERKEY_GUI;
    _state &= ~ (1<<5);
  }
  if(_state & 1<<11){		//KEY_ALT
    mod_byte |= MODIFIERKEY_ALT;
    _state &= ~ (1<<11);
  }
  if(_state == 0){
    send(0, mod_byte);
    return;
}
  //exact matches that depend on shift, some are macros

  if(_state == 32776){		//KEY_PERCENT
    send(KEY_5, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4194306){		//KEY_DOLLAR
    send(KEY_4, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 65552){		//KEY_PERIOD
    send(KEY_PERIOD, mod_byte );
    return;
  }
  if(_state == 2098176){		//KEY_HASH
    send(KEY_3, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 262272){		//KEY_AMPERSAND
    send(KEY_7, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 263168){		//KEY_AT
    send(KEY_2, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 32784){		//KEY_DOUBLEQUOTE
    send(KEY_QUOTE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 262152){		//KEY_SLASH
    send(KEY_SLASH, mod_byte );
    return;
  }
  if(_state == 32896){		//KEY_BANG
    send(KEY_1, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 5120){		//KEY_GRAVE
    send(KEY_TILDE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4224){		//KEY_ASTERISK
    send(KEY_8, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4194368){		//KEY_LEFT_CURLY
    send(KEY_LEFT_BRACE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4194816){		//KEY_LEFT_ANGLE
    send(KEY_COMMA, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 2097153){		//KEY_EQUAL
    send(KEY_EQUAL, mod_byte );
    return;
  }
  if(_state == 4104){		//KEY_QUESTION
    send(KEY_SLASH, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 524352){		//KEY_RIGHT_CURLY
    send(KEY_RIGHT_BRACE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4098){		//KEY_COLON
    send(KEY_SEMICOLON, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 8208){		//KEY_COMMA
    send(KEY_COMMA, mod_byte );
    return;
  }
  if(_state == 524296){		//KEY_RIGHT_BRACE
    send(KEY_RIGHT_BRACE, mod_byte );
    return;
  }
  if(_state == 8194){		//KEY_CARET
    send(KEY_6, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4097){		//KEY_MINUS
    send(KEY_MINUS, mod_byte );
    return;
  }
  if(_state == 32769){		//KEY_UNDERSCORE
    send(KEY_MINUS, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 524800){		//KEY_RIGHT_ANGLE
    send(KEY_PERIOD, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 524289){		//KEY_RIGHT_PAREN
    send(KEY_0, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 32770){		//KEY_SEMICOLON
    send(KEY_SEMICOLON, mod_byte );
    return;
  }
  if(_state == 2097280){		//KEY_PIPE
    send(KEY_BACKSLASH, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 4112){		//KEY_QUOTE
    send(KEY_QUOTE, mod_byte );
    return;
  }
  if(_state == 4194312){		//KEY_LEFT_BRACE
    send(KEY_LEFT_BRACE, mod_byte );
    return;
  }
  if(_state == 4194305){		//KEY_LEFT_PAREN
    send(KEY_9, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 2097160){		//KEY_BACKSLASH
    send(KEY_BACKSLASH, mod_byte );
    return;
  }
  if(_state == 576){		//KEY_5
    send(KEY_5, mod_byte );
    return;
  }
  if(_state == 36864){		//KEY_4
    send(KEY_4, mod_byte );
    return;
  }
  if(_state == 131081){		//KEY_7
    send(KEY_7, mod_byte );
    return;
  }
  if(_state == 2490368){		//KEY_6
    send(KEY_6, mod_byte );
    return;
  }
  if(_state == 9){		//KEY_1
    send(KEY_1, mod_byte );
    return;
  }
  if(_state == 2359296){		//KEY_0
    send(KEY_0, mod_byte );
    return;
  }
  if(_state == 72){		//KEY_3
    send(KEY_3, mod_byte );
    return;
  }
  if(_state == 294912){		//KEY_2
    send(KEY_2, mod_byte );
    return;
  }
  if(_state == 262145){		//KEY_PLUS
    send(KEY_EQUAL, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(_state == 33792){		//KEY_TILDE
    send(KEY_TILDE, mod_byte );
    return;
  }
  if(_state == 131144){		//KEY_9
    send(KEY_9, mod_byte );
    return;
  }
  if(_state == 425984){		//KEY_8
    send(KEY_8, mod_byte );
    return;
  }

  //matches disregarding shift
  //set shift_flag, clear shift bit in state
  if(_state & 1<<17){
   mod_byte |= MODIFIERKEY_SHIFT;
  }
  _state &= ~ (1<<17);
  if(_state == 98304){		//KEY_END
    send(KEY_END, mod_byte);
    return;
  }
  if(_state == 524288){		//KEY_E
    send(KEY_E, mod_byte);
    return;
  }
  if(_state == 1){		//KEY_G
    send(KEY_G, mod_byte);
    return;
  }
  if(_state == 32768){		//KEY_F
    send(KEY_F, mod_byte);
    return;
  }
  if(_state == 8192){		//KEY_A
    send(KEY_A, mod_byte);
    return;
  }
  if(_state == 6291456){		//KEY_PAGE_DOWN
    send(KEY_PAGE_DOWN, mod_byte);
    return;
  }
  if(_state == 1728){		//KEY_PRINTSCREEN
    send(KEY_PRINTSCREEN, mod_byte);
    return;
  }
  if(_state == 262146){		//KEY_D
    send(KEY_D, mod_byte);
    return;
  }
  if(_state == 4096){		//KEY_M
    send(KEY_M, mod_byte);
    return;
  }
  if(_state == 512){		//KEY_L
    send(KEY_L, mod_byte);
    return;
  }
  if(_state == 65536){		//KEY_O
    send(KEY_O, mod_byte);
    return;
  }
  if(_state == 256){		//KEY_SPACE
    send(KEY_SPACE, mod_byte);
    return;
  }
  if(_state == 4194304){		//KEY_I
    send(KEY_I, mod_byte);
    return;
  }
  if(_state == 2){		//KEY_H
    send(KEY_H, mod_byte);
    return;
  }
  if(_state == 65600){		//KEY_K
    send(KEY_K, mod_byte);
    return;
  }
  if(_state == 65544){		//KEY_J
    send(KEY_J, mod_byte);
    return;
  }
  if(_state == 524304){		//KEY_ESC
    send(KEY_ESC, mod_byte);
    return;
  }
  if(_state == 16){		//KEY_T
    send(KEY_T, mod_byte);
    return;
  }
  if(_state == 524290){		//KEY_W
    send(KEY_W, mod_byte);
    return;
  }
  if(_state == 65537){		//KEY_V
    send(KEY_V, mod_byte);
    return;
  }
  if(_state == 262160){		//KEY_Q
    send(KEY_Q, mod_byte);
    return;
  }
  if(_state == 2097152){		//KEY_P
    send(KEY_P, mod_byte);
    return;
  }
  if(_state == 1024){		//KEY_S
    send(KEY_S, mod_byte);
    return;
  }
  if(_state == 64){		//KEY_R
    send(KEY_R, mod_byte);
    return;
  }
  if(_state == 1048832){		//KEY_ENTER
    send(KEY_ENTER, mod_byte);
    return;
  }
  if(_state == 2097168){		//KEY_X
    send(KEY_X, mod_byte);
    return;
  }
  if(_state == 24){		//KEY_UP
    send(KEY_UP, mod_byte);
    return;
  }
  if(_state == 65538){		//KEY_B
    send(KEY_B, mod_byte);
    return;
  }
  if(_state == 1536){		//KEY_RIGHT
    send(KEY_RIGHT, mod_byte);
    return;
  }
  if(_state == 66048){		//KEY_Z
    send(KEY_Z, mod_byte);
    return;
  }
  if(_state == 786432){		//KEY_PAGE_UP
    send(KEY_PAGE_UP, mod_byte);
    return;
  }
  if(_state == 128){		//KEY_N
    send(KEY_N, mod_byte);
    return;
  }
  if(_state == 1048576){		//KEY_BACKSPACE
    send(KEY_BACKSPACE, mod_byte);
    return;
  }
  if(_state == 12288){		//KEY_HOME
    send(KEY_HOME, mod_byte);
    return;
  }
  if(_state == 3){		//KEY_DOWN
    send(KEY_DOWN, mod_byte);
    return;
  }
  if(_state == 262144){		//KEY_U
    send(KEY_U, mod_byte);
    return;
  }
  if(_state == 8){		//KEY_C
    send(KEY_C, mod_byte);
    return;
  }
  if(_state == 4194320){		//KEY_TAB
    send(KEY_TAB, mod_byte);
    return;
  }
  if(_state == 192){		//KEY_LEFT
    send(KEY_LEFT, mod_byte);
    return;
  }
  if(_state == 2097154){		//KEY_Y
    send(KEY_Y, mod_byte);
    return;
  }
  //else unknown combo, or only mods are down
  Serial.println("warning: unknown switch combination");
  send(0, mod_byte);
}