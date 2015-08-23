//#include avr stuff? 
void translate(uint32_t state){
  if(_state == 8){
    return 225;
  }
  if(_state == 32){
    return 224;
  }
  if(_state == 1){
    return 230;
  }
  if(_state == 2097152){
    return 4;
  }
  if(_state == 2097160){
    return 5;
  }
  if(_state == 3145728){
    return 6;
  }
}
