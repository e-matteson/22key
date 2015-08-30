//#include avr stuff? 
void translate(uint32_t state){

    //blank out mods except shift, set mod_byte

  if(masked _state == 139296){		//KEY_leftcontrol
    mod_byte |= 1;
 }

  //exact matches that depend on shift, some are macros

  if(_state == 24580){		//macro_paren
    send(38, 1, mod_byte);
    send(39, 1, mod_byte);
    send(80, 0, mod_byte);
  }

  //matches disregarding shift
  set shift_flag, blank out shift bit in _state
  if(_state == 1056784){		//KEY_E
    send(8, shift_flag, mod_byte);
  }
  if(_state == 2105376){		//KEY_D
    send(7, shift_flag, mod_byte);
  }
  if(_state == 270340){		//KEY_G
    send(10, shift_flag, mod_byte);
  }
  if(_state == 532488){		//KEY_F
    send(9, shift_flag, mod_byte);
  }
  if(_state == 73744){		//KEY_I
    send(12, shift_flag, mod_byte);
  }
  if(_state == 40968){		//KEY_J
    send(13, shift_flag, mod_byte);
  }
  else{
    //only mods are down
    send(0, shift_flag, mod_byte);}
}