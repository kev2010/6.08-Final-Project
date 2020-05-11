void draw_login_page(uint8_t selection) {
  tft.drawString("LOGIN PAGE", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString("Login", 40, 50, 2);
  tft.drawString("Turn off", 40, 70, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}

void draw_leaderboard_screen(uint8_t selection) {

  char s[] = "&";
  char *token;
  uint8_t users = 0;
  char leader[OUT_BUFFER_SIZE]; // copy of menu_choices to draw menu correctly when updating selector ">"
  memset(leader, 0, strlen(leader));
  sprintf(leader, response_buffer);
  /* get the first token */
  token = strtok(leader, s);
  users = atoi(token);
  token = strtok(NULL, s);
  Serial.println(users);

  /* walk through other tokens */
  uint8_t cnt = 0;
  uint8_t i = 0;

  while ( token != NULL and i < 2 * users ) {
    char a[3] = "";
    sprintf(a, "%d.", cnt + 1);
    if (i % 2 == 0) {
      tft.drawString(a, 10, 10 + 15 * cnt, 1);
      tft.drawString(token, 30, 10 + 15 * cnt, 1);
    } else if (i % 2 == 1) {
      tft.drawString(token, 130, 10 + 15 * cnt, 1);
      cnt ++ ;
    }
    token = strtok(NULL, s);
    i ++ ;
  }


  tft.drawString("Go back", 20, 110, 1);
  tft.drawString(">", 5, 110 + 10 * selection, 1);
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
  tft.drawString("PushUps", 40, 90, 2);
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

void draw_room_screen(uint8_t selection) {
  char s[] = "@";
  char *token;
  uint8_t counter = 0;
  char room_message[OUT_BUFFER_SIZE]; // copy of menu_choices to draw menu correctly when updating selector ">"
  memset(room_message, 0, strlen(room_message));
  Serial.println(response_buffer);
  sprintf(room_message, room_descr); // changed

  /* get the first token, extract room_id of room hosted */
  memset(room_id, 0, strlen(room_id));
  token = strtok(room_message, "$");
  sprintf(room_id, token);
  /* walk through other tokens */

  token = strtok(NULL, s);

  while ( token != NULL ) {
    tft.drawString(token, 10, 50 + 15 * counter, 1);
    token = strtok(NULL, s);
    counter ++ ;
  }
  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString("Enter game", 20, 100, 1);
  tft.drawString("Go back", 20, 110, 1);
  tft.drawString(">", 5, 100 + 10 * selection, 1);
}


void draw_push_up_screen(uint8_t selection) {
  tft.drawString("PUSH UPS", 20, 10, 2);
  tft.drawString("-----------------------", 0, 30, 2);
  tft.drawString("Record", 40, 50, 2);
  tft.drawString("Leaderboard", 40, 70, 2);
  tft.drawString("Go back", 40, 90, 2);
  tft.drawString(">", 25, 50 + (selection * 20), 2);
}


void draw_poker_screen(char* poker_actions, uint8_t selection) {
  tft.fillScreen(TFT_BLACK);
  tft.drawString("POKER", 20, 5, 2);
  tft.drawString("-----------------------", 0, 20, 2);

  char s[] = "@";
  char *token;
  uint8_t counter = 0;
  char actions_copy[500]; // copy of menu_choices to draw menu correctly when updating selector ">"
  memset(actions_copy, 0, strlen(actions_copy));
  sprintf(actions_copy, poker_actions);
  /* get the first token */
  token = strtok(actions_copy, s);
  /* walk through other tokens */

  tft.drawString("refresh page", 20, 35 + 15 * counter, 1);
  counter ++ ;

  while ( token != NULL ) {
    tft.drawString(token, 20, 35 + 15 * counter, 1);
    counter ++ ;
    token = strtok(NULL, s);
  }

  tft.drawString(">", 10, 35 + (selection * 15), 1);

}


void draw_poker_bet_screen(uint8_t selection) {
  tft.fillScreen(TFT_BLACK);
  tft.drawString("CHOOSE BET AMOUNT", 10, 5, 2);
  tft.drawString("-----------------------", 0, 20, 2);

  int min_bet = bet_params[0];
  int max_bet = bet_params[1];
  int all_in = bet_params[2];

  tft.setTextColor(TFT_ORANGE, TFT_BLACK);

  char bet_amount_char[30];
  sprintf(bet_amount_char, "Bet amount:    %d", bet_amount);

  tft.drawString(bet_amount_char, 10, 35, 2);

  char min_bet_char[30];
  sprintf(min_bet_char, "min: %d", min_bet);
  char max_bet_char[30];
  sprintf(max_bet_char, "max: %d", max_bet);
  char all_in_char[30];
  sprintf(all_in_char, "all in: %d", all_in);

  tft.drawString(min_bet_char, 85, 60, 1);
  tft.drawString(max_bet_char, 85, 75, 1);
  tft.drawString(all_in_char, 85, 90, 1);

  tft.drawLine(80, 60, 80, 130, TFT_ORANGE);

  tft.setTextColor(TFT_GREEN, TFT_BLACK);


  tft.drawString("Increment", 10, 60, 1);
  tft.drawString("Decrement", 10, 75, 1);
  tft.drawString("All in", 10, 90, 1);
  tft.drawString("Confirm", 10, 105, 1);
  tft.drawString("Go back", 10, 120, 1);

  tft.drawString(">", 2, 60 + (selection * 15), 1);

}



void draw_poker_raise_screen(uint8_t selection) {
  tft.fillScreen(TFT_BLACK);
  tft.drawString("CHOOSE RAISE AMOUNT", 10, 5, 2);
  tft.drawString("-----------------------", 0, 20, 2);

  int min_raise = raise_params[0];
  int max_raise = raise_params[1];
  int all_in = raise_params[2];

  tft.setTextColor(TFT_ORANGE, TFT_BLACK);

  char raise_amount_char[30];
  sprintf(raise_amount_char, "Raise amount:    %d", raise_amount);

  tft.drawString(raise_amount_char, 10, 35, 2);

  char min_raise_char[30];
  sprintf(min_raise_char, "min: %d", min_raise);
  char max_raise_char[30];
  sprintf(max_raise_char, "max: %d", max_raise);
  char all_in_char[30];
  sprintf(all_in_char, "all in: %d", all_in);

  tft.drawString(min_raise_char, 85, 60, 1);
  tft.drawString(max_raise_char, 85, 75, 1);
  tft.drawString(all_in_char, 85, 90, 1);

  tft.drawLine(80, 60, 80, 130, TFT_ORANGE);

  tft.setTextColor(TFT_GREEN, TFT_BLACK);


  tft.drawString("Increment", 10, 60, 1);
  tft.drawString("Decrement", 10, 75, 1);
  tft.drawString("All in", 10, 90, 1);
  tft.drawString("Confirm", 10, 105, 1);
  tft.drawString("Go back", 10, 120, 1);

  tft.drawString(">", 2, 60 + (selection * 15), 1);

}


void draw_redirect_message() {
  tft.fillScreen(TFT_BLUE);
  tft.setTextColor(TFT_WHITE, TFT_BLUE);
  tft.drawString("Kicked out of room", 10, 30, 2);
  tft.drawString("because host left!", 10, 50, 2);
  tft.drawString("Redirecting...", 10, 70, 2);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  delay(8000);
}
