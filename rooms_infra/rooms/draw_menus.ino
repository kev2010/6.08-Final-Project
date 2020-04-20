void draw_lobby_menu(uint8_t selection) {
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

void draw_join_lobby_menu(char* menu_choices, uint8_t selection) {
  tft.drawString("Go back", 20, 90, 1);
  tft.drawString(menu_choices, 20, 100, 1);
  tft.drawString("*", 5, 100 + (selection * 10), 1);
}

void draw_room_screen() {
  tft.drawString("Welcome to the room", 10, 50, 1);
  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString("Go back", 20, 100, 1);
  tft.drawString("*", 5, 100, 1);
}
