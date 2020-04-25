void draw_login_page(uint8_t selection) {
  tft.drawString("LOGIN PAGE", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString("Login", 40, 50, 2);
  tft.drawString("Turn off", 40, 70, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}

void draw_lobby_menu(uint8_t selection) {
  tft.drawString("MAIN LOBBY", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString(host, 40, 50, 2);
  tft.drawString(join, 40, 70, 2);
  tft.drawString("Logout", 40, 90, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}

void draw_host_lobby_menu(uint8_t selection) {
  tft.drawString("HOST LOBBY", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString("Poker", 40, 50, 2);
  tft.drawString("Blackjack", 40, 70, 2);
  tft.drawString("Tichu", 40, 90, 2);
  tft.drawString("Go back", 40, 110, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}

void draw_join_lobby_menu(char* menu_choices, uint8_t selection) { // can only support 3-4 rooms on display
  if (selection <= 4) {
    tft.drawString("Go back", 10, 10, 1);
  }

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

  uint8_t room_number = 1;
  while ( token != NULL ) {
    if ((room_number - 1) / 4 < (selection - 1) / 4) {
      if (i % 2 == 1) {
        room_number ++ ;
      }
    }
    else {
      if (i % 2 == 0) {
        tft.drawString(token, 10, 35 + 25 * counter, 1);
      } else if (i % 2 == 1) {
        tft.drawString(token, 10, 35 + 25 * counter + 10, 1);
        counter ++ ;
      }
    }
    token = strtok(NULL, s);
    i ++ ;
  }

  if (selection == 0) {
    tft.drawString(">", 3, 10 , 1);
  } else {
    tft.drawString(">", 3, 35 + (((selection - 1) % 4) * 25), 1);
  }

}

void draw_room_screen() {
  char s[] = "@";
  char *token;
  uint8_t counter = 0;
  char room_message[OUT_BUFFER_SIZE]; // copy of menu_choices to draw menu correctly when updating selector ">"
  memset(room_message, 0, strlen(room_message));
  Serial.println(response_buffer);
  sprintf(room_message, response_buffer);
  /* get the first token */
  token = strtok(room_message, s);
  /* walk through other tokens */
  while ( token != NULL ) {
    tft.drawString(token, 10, 50 + 15 * counter, 1);
    token = strtok(NULL, s);
    counter ++ ;
  }
  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString("Go back", 20, 100, 1);
  tft.drawString(">", 5, 100, 1);
}
