#define SHIFT_SWITCH_NUM 131072 
#define CTRL_SWITCH_NUM 1048576 
#define ALT_SWITCH_NUM 8388608 
#define GUI_SWITCH_NUM 32 

void translate_and_send(uint32_t _state){
  //blank out mods except shift, set mod_byte
  char mod_byte = 0;
  if(_state & 1<<20){		//key_ctrl
    mod_byte |= MODIFIERKEY_CTRL;
 }
  if(_state & 1<<5){		//key_gui
    mod_byte |= MODIFIERKEY_GUI;
 }
  if(_state & 1<<23){		//key_alt
    mod_byte |= MODIFIERKEY_ALT;
 }

  //exact matches that depend on shift, some are macros

  if(_state == 4718592){		//macro_paren
    send(38, mod_byte |MODIFIERKEY_SHIFT);
    send(39, mod_byte |MODIFIERKEY_SHIFT);
    send(80, mod_byte );
    return;
  }
  if(_state == 73728){		//key_1
    send(30, mod_byte );
    return;
  }
  if(_state == 589824){		//key_2
    send(31, mod_byte );
    return;
  }

  //matches disregarding shift
  //set shift_flag, clear shift bit in state
  if(_state & 1<<17){
   mod_byte |= MODIFIERKEY_SHIFT;
  }
  _state &= ~ 1<<SHIFT_SWITCH_NUM;
  if(_state == 524288){		//key_e
    send(8, mod_byte);
    return;
  }
  if(_state == 64){		//key_d
    send(7, mod_byte);
    return;
  }
  if(_state == 1){		//key_g
    send(10, mod_byte);
    return;
  }
  if(_state == 8){		//key_f
    send(9, mod_byte);
    return;
  }
  if(_state == 8192){		//key_a
    send(4, mod_byte);
    return;
  }
  if(_state == 512){		//key_b
    send(5, mod_byte);
    return;
  }
  if(_state == 65536){		//key_o
    send(18, mod_byte);
    return;
  }
  if(_state == 128){		//key_n
    send(17, mod_byte);
    return;
  }
  if(_state == 32768){		//key_i
    send(12, mod_byte);
    return;
  }
  if(_state == 2){		//key_h
    send(11, mod_byte);
    return;
  }
  if(_state == 4194304){		//key_u
    send(24, mod_byte);
    return;
  }
  if(_state == 16){		//key_t
    send(23, mod_byte);
    return;
  }
  if(_state == 2097152){		//key_p
    send(19, mod_byte);
    return;
  }
  if(_state == 1024){		//key_s
    send(22, mod_byte);
    return;
  }
  if(_state == 262144){		//key_y
    send(28, mod_byte);
    return;
  }
  if(_state == 4096){		//key_x
    send(27, mod_byte);
    return;
  }
  //else unknown combo, or only mods are down
  Serial.println('warning: unknown switch combination');
  send(0, mod_byte);
}