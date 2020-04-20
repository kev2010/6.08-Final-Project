void draw_lobby_menu(uint8_t selection) {
  tft.drawString("MAIN LOBBY", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString(host, 40, 50, 2);
  tft.drawString(join, 40, 70, 2);
  tft.drawString(turn_off, 40, 90, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}

void draw_host_lobby_menu(uint8_t selection) {
  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString("Poker", 20, 100, 1);
  tft.drawString("Blacjack", 20, 110, 1);
  tft.drawString("Tichu", 20, 120, 1);
  tft.drawString("Go back", 20, 130, 1);
  tft.drawString("*", 5, 100 + (selection * 10), 1);
}

void draw_join_lobby_menu(char* menu_choices, uint8_t selection) { // can only support 3-4 rooms on display
  tft.drawString("Go back", 10, 10, 1);

  char s[] = "@";
  char *token;
  uint8_t counter = 0;
  char menu_copy[OUT_BUFFER_SIZE]; // copy of menu_choices to draw menu correctly when updating selector ">"
  memset(menu_copy, 0, strlen(menu_copy));
  sprintf(menu_copy, menu_choices);
  /* get the first token */
  token = strtok(menu_copy, s);
  /* walk through other tokens */
  uint8_t i = 0;
  while ( token != NULL ) {
    if (i%2 == 0) {
      tft.drawString(token, 10, 35 + 25*counter, 1);
    } else if (i%2 == 1){
      tft.drawString(token, 10, 35 + 25*counter + 10, 1);
      counter ++ ;
    }    
    token = strtok(NULL, s);
    i ++ ;
  }

  tft.drawString(">", 3, 10 + (selection * 25), 1);
}

void draw_room_screen() {
  tft.drawString("Welcome to the room", 10, 50, 1);
  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString("Go back", 20, 100, 1);
  tft.drawString("*", 5, 100, 1);
}
