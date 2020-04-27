
#include <WiFi.h> //Connect to WiFi Network
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

char network[] = "NETGEAR_EXT_2";  //SSID for 6.08 Lab
char password[] = "vastbug510"; //Password for 6.08 Lab

char user[] = "giannis";

char user2[] = "petros";
char user3[] = "christos";
char user4[] = "dimitris";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host

const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 6000; //size of buffer to hold HTTP response // max is 35,000
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response

char response_buffer_2[OUT_BUFFER_SIZE]; // may need multiple char array buffers to hold HTTP response (not used now)

char menu_choices[OUT_BUFFER_SIZE];
char all_room_ids[5000];
char room_id[500]; // room_id to join

char host[] = "Host room";
char join[] = "Join room";
char turn_off[] = "Turn off";

uint8_t state;
#define OFF 0
#define LOGIN_PAGE 1
#define MAIN_LOBBY 2
#define HOST_LOBBY 3
#define JOIN_LOBBY 4
#define ROOM 5

const uint8_t PIN_1 = 16; //button 1
const uint8_t PIN_2 = 5; //button 2

uint8_t new_selection;
uint8_t selection;
uint8_t no_of_selections;
boolean flag = true;

uint8_t selection_btn;
uint8_t transition_btn;
uint8_t old_selection_btn = 1; //for button edge detection!
uint8_t old_transition_btn = 1;

uint32_t timer;
const uint32_t ping_period = 10000;

void setup() {
  Serial.begin(115200);
  tft.init();  //init screen
  tft.setRotation(1); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set color of font to green foreground, black background
  Serial.begin(115200); //begin serial comms
  delay(100); //wait a bit (100 ms)
  pinMode(PIN_1, INPUT_PULLUP);
  pinMode(PIN_2, INPUT_PULLUP);

  pinMode(14, OUTPUT);
  digitalWrite(14, 1);

  WiFi.begin(network, password); //attempt to connect to wifi
  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  Serial.println(network);
  while (WiFi.status() != WL_CONNECTED && count < 12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.printf("%d:%d:%d:%d (%s) (%s)\n", WiFi.localIP()[3], WiFi.localIP()[2],
                  WiFi.localIP()[1], WiFi.localIP()[0],
                  WiFi.macAddress().c_str() , WiFi.SSID().c_str());
    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect 😕  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }

  timer = millis();


  // ping_online(user); // will use same function to post online status every 10 seconds

  state = LOGIN_PAGE;
  flag = true;

}

uint8_t update_selection(uint8_t selection, uint8_t initial_height, uint8_t no_of_selections) {
  selection_btn = digitalRead(PIN_1);
  if (selection_btn != old_selection_btn && selection_btn == 1) {
    tft.fillScreen(TFT_BLACK); //fill background
    tft.setCursor(0, 0, 1); // set the cursor
    selection  = (selection + 1) % no_of_selections;
  }
  old_selection_btn = selection_btn;
  return selection;
}

void extract_join_buffer(char* response_buffer) {
  char delimiter[] = "&";
  char* ptr;
  ptr = strtok(response_buffer, delimiter);
  memset(all_room_ids, 0, strlen(all_room_ids));
  sprintf(all_room_ids, ptr);
  Serial.println(all_room_ids);

  ptr = strtok(NULL, delimiter);
  no_of_selections = atoi(ptr) + 1; // update numbers of selections, add 1 for "Go back" selection
  //Serial.println(no_of_selections);

  ptr = strtok(NULL, delimiter);
  memset(menu_choices, 0, strlen(menu_choices));
  sprintf(menu_choices, ptr);
}

void extract_room_id() {
  char delimiter[] = "$";
  char *token;
  uint8_t counter = 1;
  char all_room_ids_copy[5000]; // copy of all_room_ids
  memset(room_id, 0, strlen(room_id));
  sprintf(all_room_ids_copy, all_room_ids);
  /* get the first token */
  token = strtok(all_room_ids_copy, delimiter);
  /* walk through other tokens */
  while ( token != NULL ) {
    if (counter == selection) {
      sprintf(room_id, token); // found room_id corresponding to selection
      Serial.println(room_id);
      break;
    }
    token = strtok(NULL, delimiter);
    counter ++ ;
  }
}


void loop() {
  // only ping online if in states that require online status
  if (state != OFF && state != LOGIN_PAGE ) {
    if (millis() - timer >= ping_period) {
      ping_online(user);
      timer = millis();
    }
  }

  switch (state) {

    case OFF:
      if (flag) {
        selection = 0;
        no_of_selections = 1;
        flag = false;
        digitalWrite(14, 0);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        digitalWrite(14, 1);
        state = LOGIN_PAGE;
      }
      old_transition_btn = transition_btn;

      break;

    case LOGIN_PAGE:
      if (flag) {
        selection = 0;
        no_of_selections = 2;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_login_page(selection);
      }
      new_selection = update_selection(selection, 100, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_login_page(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        // selection = 0: login and ping online
        if (selection == 0) {
          ping_online(user);
          timer = millis();
          state = MAIN_LOBBY;

        // selection = 1: turn off
        } else if (selection == 1) {
          state = OFF;
        }
      }
      old_transition_btn = transition_btn;

      break;

    case MAIN_LOBBY:
      if (flag) {
        selection = 0;
        no_of_selections = 3;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_lobby_menu(selection);
      }
      new_selection = update_selection(selection, 100, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_lobby_menu(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        if (selection == 0) {
          state = HOST_LOBBY;
        } else if (selection == 1) {
          state = JOIN_LOBBY;
        } else if (selection == 2) { // logout
          //logout(user);
          state = LOGIN_PAGE;
        }
      }
      old_transition_btn = transition_btn;

      break;

    case HOST_LOBBY:
      if (flag) {
        selection = 0;
        no_of_selections = 4;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_host_lobby_menu(selection);
      }
      new_selection = update_selection(selection, 100, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_host_lobby_menu(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        if (selection == 3) {
          state = MAIN_LOBBY;
        } else {
          state = ROOM;
          host_room_post_req(user, selection);
        }
      }
      old_transition_btn = transition_btn;
      break;

    case JOIN_LOBBY:
      if (flag) {
        selection = 0;
        // no_of_selections = 4;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        join_room_get_req();
        extract_join_buffer(response_buffer); // also updates no_of_selections
        draw_join_lobby_menu(menu_choices, selection);
      }

      new_selection = update_selection(selection, 100, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_join_lobby_menu(menu_choices, selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        if (selection == 0) {
          state = MAIN_LOBBY;
        }
        // make POST request when joining room
        else {
          extract_room_id();
          join_room_post_req(user, room_id);
          state = ROOM;

        }
      }
      old_transition_btn = transition_btn;


      break;

    case ROOM:
      if (flag) {
        selection = 0;
        no_of_selections = 1; // CHANGE ME
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_room_screen();
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        if (selection == 0) {
          leave_room_post_req(user); // notify that user left room
          state = MAIN_LOBBY;
        }
      }
      old_transition_btn = transition_btn;

      break;
  }

}
