#define NULL 0 
void translateAndSendState(uint32_t state){
  //blank out mods except shift, set mod_byte
  char mod_byte = 0;
  if(state & 1<<23){		//KEY_CTRL
    mod_byte |= MODIFIERKEY_CTRL;
    state &= ~ (1<<23);
  }
  if(state & 1<<5){		//KEY_GUI
    mod_byte |= MODIFIERKEY_GUI;
    state &= ~ (1<<5);
  }
  if(state & 1<<11){		//KEY_ALT
    mod_byte |= MODIFIERKEY_ALT;
    state &= ~ (1<<11);
  }
  if(state == 0){
    sendOverUSB(0, mod_byte);
    return;
}
  //exact matches that depend on shift, some are macros

  if(state == 32776){		//KEY_PERCENT
    sendOverUSB(KEY_5, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4194432){		//KEY_DOLLAR
    sendOverUSB(KEY_4, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4194305){		//KEY_PERIOD
    sendOverUSB(KEY_PERIOD, mod_byte );
    return;
  }
  if(state == 2097216){		//KEY_HASH
    sendOverUSB(KEY_3, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 262272){		//KEY_AMPERSAND
    sendOverUSB(KEY_7, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 262208){		//KEY_AT
    sendOverUSB(KEY_2, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 32784){		//KEY_DOUBLEQUOTE
    sendOverUSB(KEY_QUOTE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 262152){		//KEY_SLASH
    sendOverUSB(KEY_SLASH, mod_byte );
    return;
  }
  if(state == 32896){		//KEY_BANG
    sendOverUSB(KEY_1, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4104){		//KEY_ASTERISK
    sendOverUSB(KEY_8, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 65544){		//KEY_LEFT_CURLY
    sendOverUSB(KEY_LEFT_BRACE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 66048){		//KEY_LEFT_ANGLE
    sendOverUSB(KEY_COMMA, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 2097153){		//KEY_EQUAL
    sendOverUSB(KEY_EQUAL, mod_byte );
    return;
  }
  if(state == 524296){		//KEY_RIGHT_CURLY
    sendOverUSB(KEY_RIGHT_BRACE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4194312){		//KEY_COMMA
    sendOverUSB(KEY_COMMA, mod_byte );
    return;
  }
  if(state == 524352){		//KEY_RIGHT_BRACE
    sendOverUSB(KEY_RIGHT_BRACE, mod_byte );
    return;
  }
  if(state == 524416){		//KEY_CARET
    sendOverUSB(KEY_6, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4097){		//KEY_MINUS
    sendOverUSB(KEY_MINUS, mod_byte );
    return;
  }
  if(state == 32769){		//KEY_UNDERSCORE
    sendOverUSB(KEY_MINUS, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 524800){		//KEY_RIGHT_ANGLE
    sendOverUSB(KEY_PERIOD, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 524289){		//KEY_RIGHT_PAREN
    sendOverUSB(KEY_0, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4194368){		//KEY_SEMICOLON
    sendOverUSB(KEY_SEMICOLON, mod_byte );
    return;
  }
  if(state == 4112){		//KEY_QUOTE
    sendOverUSB(KEY_QUOTE, mod_byte );
    return;
  }
  if(state == 65600){		//KEY_LEFT_BRACE
    sendOverUSB(KEY_LEFT_BRACE, mod_byte );
    return;
  }
  if(state == 65537){		//KEY_LEFT_PAREN
    sendOverUSB(KEY_9, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 2097160){		//KEY_BACKSLASH
    sendOverUSB(KEY_BACKSLASH, mod_byte );
    return;
  }
  if(state == 4224){		//KEY_QUESTION
    sendOverUSB(KEY_SLASH, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4160){		//KEY_GRAVE
    sendOverUSB(KEY_TILDE, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 4194816){		//KEY_COLON
    sendOverUSB(KEY_SEMICOLON, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 262145){		//KEY_PLUS
    sendOverUSB(KEY_EQUAL, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }
  if(state == 32832){		//KEY_TILDE
    sendOverUSB(KEY_TILDE, mod_byte );
    return;
  }
  if(state == 2097280){		//KEY_PIPE
    sendOverUSB(KEY_BACKSLASH, mod_byte |MODIFIERKEY_SHIFT);
    return;
  }

  //matches disregarding shift
  //set shift_flag, clear shift bit in state
  if(state & 1<<17){
   mod_byte |= MODIFIERKEY_SHIFT;
  }
  state &= ~ (1<<17);
  if(state == 98304){		//KEY_END
    sendOverUSB(KEY_END, mod_byte);
    return;
  }
  if(state == 524288){		//KEY_E
    sendOverUSB(KEY_E, mod_byte);
    return;
  }
  if(state == 1){		//KEY_G
    sendOverUSB(KEY_G, mod_byte);
    return;
  }
  if(state == 32768){		//KEY_F
    sendOverUSB(KEY_F, mod_byte);
    return;
  }
  if(state == 8192){		//KEY_A
    sendOverUSB(KEY_A, mod_byte);
    return;
  }
  if(state == 1728){		//KEY_PRINTSCREEN
    sendOverUSB(KEY_PRINTSCREEN, mod_byte);
    return;
  }
  if(state == 262146){		//KEY_D
    sendOverUSB(KEY_D, mod_byte);
    return;
  }
  if(state == 4096){		//KEY_M
    sendOverUSB(KEY_M, mod_byte);
    return;
  }
  if(state == 512){		//KEY_L
    sendOverUSB(KEY_L, mod_byte);
    return;
  }
  if(state == 65536){		//KEY_O
    sendOverUSB(KEY_O, mod_byte);
    return;
  }
  if(state == 256){		//KEY_SPACE
    sendOverUSB(KEY_SPACE, mod_byte);
    return;
  }
  if(state == 4194304){		//KEY_I
    sendOverUSB(KEY_I, mod_byte);
    return;
  }
  if(state == 2){		//KEY_H
    sendOverUSB(KEY_H, mod_byte);
    return;
  }
  if(state == 65552){		//KEY_K
    sendOverUSB(KEY_K, mod_byte);
    return;
  }
  if(state == 65538){		//KEY_J
    sendOverUSB(KEY_J, mod_byte);
    return;
  }
  if(state == 524304){		//KEY_ESC
    sendOverUSB(KEY_ESC, mod_byte);
    return;
  }
  if(state == 16){		//KEY_T
    sendOverUSB(KEY_T, mod_byte);
    return;
  }
  if(state == 4194306){		//KEY_W
    sendOverUSB(KEY_W, mod_byte);
    return;
  }
  if(state == 65664){		//KEY_V
    sendOverUSB(KEY_V, mod_byte);
    return;
  }
  if(state == 262160){		//KEY_Q
    sendOverUSB(KEY_Q, mod_byte);
    return;
  }
  if(state == 2097152){		//KEY_P
    sendOverUSB(KEY_P, mod_byte);
    return;
  }
  if(state == 1024){		//KEY_S
    sendOverUSB(KEY_S, mod_byte);
    return;
  }
  if(state == 64){		//KEY_R
    sendOverUSB(KEY_R, mod_byte);
    return;
  }
  if(state == 2097154){		//KEY_Y
    sendOverUSB(KEY_Y, mod_byte);
    return;
  }
  if(state == 2097168){		//KEY_X
    sendOverUSB(KEY_X, mod_byte);
    return;
  }
  if(state == 8320){		//KEY_Z
    sendOverUSB(KEY_Z, mod_byte);
    return;
  }
  if(state == 8){		//KEY_C
    sendOverUSB(KEY_C, mod_byte);
    return;
  }
  if(state == 24){		//KEY_UP
    sendOverUSB(KEY_UP, mod_byte);
    return;
  }
  if(state == 524290){		//KEY_B
    sendOverUSB(KEY_B, mod_byte);
    return;
  }
  if(state == 7077888){		//KEY_DELETE
    sendOverUSB(KEY_DELETE, mod_byte);
    return;
  }
  if(state == 786432){		//KEY_PAGE_UP
    sendOverUSB(KEY_PAGE_UP, mod_byte);
    return;
  }
  if(state == 128){		//KEY_N
    sendOverUSB(KEY_N, mod_byte);
    return;
  }
  if(state == 1048576){		//KEY_BACKSPACE
    sendOverUSB(KEY_BACKSPACE, mod_byte);
    return;
  }
  if(state == 3){		//KEY_DOWN
    sendOverUSB(KEY_DOWN, mod_byte);
    return;
  }
  if(state == 262144){		//KEY_U
    sendOverUSB(KEY_U, mod_byte);
    return;
  }
  if(state == 36864){		//KEY_5
    sendOverUSB(KEY_5, mod_byte);
    return;
  }
  if(state == 576){		//KEY_4
    sendOverUSB(KEY_4, mod_byte);
    return;
  }
  if(state == 2129920){		//KEY_7
    sendOverUSB(KEY_7, mod_byte);
    return;
  }
  if(state == 65){		//KEY_6
    sendOverUSB(KEY_6, mod_byte);
    return;
  }
  if(state == 2359296){		//KEY_1
    sendOverUSB(KEY_1, mod_byte);
    return;
  }
  if(state == 9){		//KEY_0
    sendOverUSB(KEY_0, mod_byte);
    return;
  }
  if(state == 294912){		//KEY_3
    sendOverUSB(KEY_3, mod_byte);
    return;
  }
  if(state == 72){		//KEY_2
    sendOverUSB(KEY_2, mod_byte);
    return;
  }
  if(state == 266240){		//KEY_9
    sendOverUSB(KEY_9, mod_byte);
    return;
  }
  if(state == 520){		//KEY_8
    sendOverUSB(KEY_8, mod_byte);
    return;
  }
  if(state == 6291456){		//KEY_PAGE_DOWN
    sendOverUSB(KEY_PAGE_DOWN, mod_byte);
    return;
  }
  if(state == 1048832){		//KEY_ENTER
    sendOverUSB(KEY_ENTER, mod_byte);
    return;
  }
  if(state == 8208){		//NULL
    sendOverUSB(NULL, mod_byte);
    return;
  }
  if(state == 73){		//KEY_F2
    sendOverUSB(KEY_F2, mod_byte);
    return;
  }
  if(state == 1536){		//KEY_RIGHT
    sendOverUSB(KEY_RIGHT, mod_byte);
    return;
  }
  if(state == 110592){		//KEY_CAPS_LOCK
    sendOverUSB(KEY_CAPS_LOCK, mod_byte);
    return;
  }
  if(state == 12288){		//KEY_HOME
    sendOverUSB(KEY_HOME, mod_byte);
    return;
  }
  if(state == 4194320){		//KEY_TAB
    sendOverUSB(KEY_TAB, mod_byte);
    return;
  }
  if(state == 192){		//KEY_LEFT
    sendOverUSB(KEY_LEFT, mod_byte);
    return;
  }
  //else unknown combo, or only mods are down
  Serial.println("warning: unknown switch combination");
  sendOverUSB(0, mod_byte);
}