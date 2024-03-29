#include <WiFi.h> //Connect to WiFi Network
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display
#include <mpu6050_esp32.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

MPU6050 imu; //imu object called, appropriately, imu



char user[] = "Giannis";
char pswd[] = "Kaklamanis";

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

char room_descr[OUT_BUFFER_SIZE];
char menu_choices[OUT_BUFFER_SIZE];
char all_room_ids[5000];
char room_id[500]; // room_id to join
char room_id_copy[100];
char leaderboard [200];

char host[] = "Host room";
char join[] = "Join room";
char turn_off[] = "Turn off";

uint32_t state;
#define OFF 0
#define LOGIN_PAGE 1
#define MAIN_LOBBY 2
#define HOST_LOBBY 3
#define JOIN_LOBBY 4
#define ROOM 5
#define PUSH_UP_GAME 6
#define RECORD 7
#define LEADERBOARD 8
#define POKER_GAME 9
#define POKER_BET 10
#define POKER_RAISE 11

const uint8_t PIN_1 = 16; //button 1
const uint8_t PIN_2 = 5; //button 2

uint8_t new_selection;
uint8_t selection;
uint8_t no_of_selections;
boolean flag = true;
boolean flag2 = true;
uint8_t game_selection;

uint8_t selection_btn;
uint8_t transition_btn;
uint8_t old_selection_btn = 1; //for button edge detection!
uint8_t old_transition_btn = 1;

uint32_t timer;
const uint32_t ping_period = 10000;

// For Poker
char actions_buffer[1000];
char previous_actions_buffer[1000];
char poker_actions[100];
char action[50];
uint32_t get_actions_timer;


int bet_params[10];
int raise_params[10];
int bet_amount;
int bet_increment = 10;
int raise_amount;
int raise_increment = 10;


void setup() {
  Serial.begin(115200);
  tft.init();  //init screen
  tft.setRotation(1); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set color of font to green foreground, black background
  Serial.begin(115200); //begin serial comms
  Wire.begin();
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

  if (imu.setupIMU(1)) {
    Serial.println("IMU Connected!");
  } else {
    Serial.println("IMU Not Connected :/");
    Serial.println("Restarting");
    ESP.restart(); // restart the ESP (proper way)
  }

  timer = millis();
  get_actions_timer = millis();


  // ping_online(user, pswd); // will use same function to post online status every 10 seconds

  state = LOGIN_PAGE;
  flag = true;

}

uint8_t update_selection(uint8_t selection, uint8_t no_of_selections) {
  selection_btn = digitalRead(PIN_1);
  if (selection_btn != old_selection_btn && selection_btn == 1) {
    tft.fillScreen(TFT_BLACK); //fill background
    //    tft.setCursor(0, 0, 1); // set the cursor
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


void extract_poker_actions() {
  char delimiter[] = "@";
  char* ptr;

  char actions_buffer_copy[100];
  memset(actions_buffer_copy, 0, strlen(actions_buffer_copy));
  strcpy(actions_buffer_copy, actions_buffer);

  ptr = strtok(actions_buffer_copy, "$");
  no_of_selections = atoi(ptr) + 1; // update numbers of selections, adds 1 for page refresh option

  ptr = strtok(NULL, delimiter);

  memset(poker_actions, 0, strlen(poker_actions));

  while ( ptr != NULL ) {
    char act1[6];
    memcpy( act1, &ptr[0], 5 );
    act1[5] = '\0';

    char act2[4];
    memcpy( act2, &ptr[0], 3 );
    act2[3] = '\0';

    if (strcmp(act1, "raise") == 0) {
      strcat(poker_actions, "raise@");

      ptr = strtok(NULL, delimiter);
      raise_params[0] = atoi(ptr);
      ptr = strtok(NULL, delimiter);
      raise_params[1] = atoi(ptr);
      ptr = strtok(NULL, delimiter);
      raise_params[2] = atoi(ptr);
    }

    else if (strcmp(act2, "bet") == 0) {
      strcat(poker_actions, "bet@");

      ptr = strtok(NULL, delimiter);
      bet_params[0] = atoi(ptr);
      ptr = strtok(NULL, delimiter);
      bet_params[1] = atoi(ptr);
      ptr = strtok(NULL, delimiter);
      bet_params[2] = atoi(ptr);
    }

    else {
      char temp[10] = "";
      sprintf(temp, "%s@", ptr);
      strcat(poker_actions, temp);
    }

    ptr = strtok(NULL, delimiter);
  }

}


void extract_selected_poker_action() {
  char delimiter[] = "@";
  char *token;
  uint8_t counter = 1; // don't count first action, which is just refreshing the page
  char actions_copy[1000]; // copy of actions_buffer
  memset(action, 0, strlen(action));
  memset(actions_copy, 0, strlen(actions_copy));
  sprintf(actions_copy, poker_actions);
  /* get the first token */
  token = strtok(actions_copy, delimiter);
  /* walk through other tokens */
  while ( token != NULL ) {

    if (counter == selection) {
      sprintf(action, token); // found action corresponding to selection
      Serial.println(action);
      break;
    }
    token = strtok(NULL, delimiter);
    counter ++ ;
  }
}


void update_bet_amount() {
  int min_bet = bet_params[0];
  int max_bet = bet_params[1];
  int all_in = bet_params[2];

  if (bet_amount == all_in && selection != 2) {
    bet_amount = min_bet;
  }
  else {
    if (selection == 0) {
      // increment bet amount
      bet_amount = min(bet_amount + bet_increment, max_bet);
    }
    else if (selection == 1) {
      // decrement bet amount
      bet_amount = max(bet_amount - bet_increment, min_bet);
    }
    else if (selection == 2) {
      bet_amount = all_in;
    }
  }

}

void update_raise_amount() {
  int min_raise = raise_params[0];
  int max_raise = raise_params[1];
  int all_in = raise_params[2];

  if (raise_amount == all_in && selection != 2) {
    raise_amount = min_raise;
  }
  else {
    if (selection == 0) {
      // increment bet amount
      raise_amount = min(raise_amount + raise_increment, max_raise);
    }
    else if (selection == 1) {
      // decrement bet amount
      raise_amount = max(raise_amount - raise_increment, min_raise);
    }
    else if (selection == 2) {
      raise_amount = all_in;
    }
  }

}


void loop() {

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
      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_login_page(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        // selection = 0: login and ping online
        if (selection == 0) {
          ping_online(user, pswd);
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
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 3;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_lobby_menu(selection);
      }
      new_selection = update_selection(selection, no_of_selections);
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
          logout(user);
          state = LOGIN_PAGE;
        }
      }
      old_transition_btn = transition_btn;

      break;

    case HOST_LOBBY:
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 4;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_host_lobby_menu(selection);
      }
      new_selection = update_selection(selection, no_of_selections);
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
          host_room_post_req(user, selection);
          game_selection = selection; // to remember game played
          state = ROOM;
        }
      }
      old_transition_btn = transition_btn;
      break;

    case JOIN_LOBBY:
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        // no_of_selections = 4;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        join_room_get_req();
        extract_join_buffer(response_buffer); // also updates no_of_selections
        draw_join_lobby_menu(menu_choices, selection);
      }

      new_selection = update_selection(selection, no_of_selections);
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

          char room_id_copy[500];
          memset(room_id_copy, 0, strlen(room_id_copy));
          strcpy(room_id_copy, room_id);

          join_room_post_req(user, room_id);

          memset(room_id, 0, strlen(room_id));
          strcpy(room_id, room_id_copy);


          char delimiter[] = "$";
          char* ptr;
          ptr = strtok(response_buffer, delimiter);
          game_selection = atoi(ptr); // update numbers of selections

          ptr = strtok(NULL, delimiter);
          memset(room_descr, 0, strlen(room_descr));
          sprintf(room_descr, ptr);
          Serial.println(game_selection);

          state = ROOM;


        }
      }
      old_transition_btn = transition_btn;

      break;


    case ROOM:
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
        // check if server returns "1" (everything ok) or "-1" (need to leave the room, if inside one)
        if (strcmp(response_buffer, "-1\n") == 0) { // SOS: needs the "\n" extension, o/w it doesn't work
          state = MAIN_LOBBY;
          flag = true;
          Serial.println("Kicked out of room because host left!");
          draw_redirect_message();
          break;
        }
      }


      if (flag) {
        selection = 0;
        no_of_selections = 2; // CHANGE ME
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_room_screen(selection); // also extracts room id for future use
      }

      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        selection = new_selection;
        draw_room_screen(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        flag = true;
        if (selection == 0) {
          if (game_selection == 0) {
            state = POKER_GAME;
          } else if (game_selection == 2) {
            state = PUSH_UP_GAME;
          }
        } else if (selection == 1) {
          leave_room_post_req(user); // notify that user left room
          state = MAIN_LOBBY;
        }
      }
      old_transition_btn = transition_btn;

      break;

    case PUSH_UP_GAME:
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 3; // CHANGE ME
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_push_up_screen(selection);
        //        initialize();
      }

      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        Serial.println("new selection!");
        selection = new_selection;
        draw_push_up_screen(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        Serial.println("clicked on selection!");
        flag = true;
        if (selection == 0) {
          state = RECORD;
        } else if (selection == 1) {
          state = LEADERBOARD;
          Serial.println("Leaderboard!");
        } else if (selection == 2) {
          state = ROOM;
        }
      }
      old_transition_btn = transition_btn;

      break;

    case LEADERBOARD:
      if (flag) {
        selection = 0;
        no_of_selections = 1; // CHANGE ME
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        get_leaders();
        draw_leaderboard_screen(selection);
      }

      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        Serial.println("new selection!");
        selection = new_selection;

      }


      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        Serial.println("clicked on selection!");
        flag = true;
        state = PUSH_UP_GAME;
      }
      old_transition_btn = transition_btn;

      break;
    case RECORD:
      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 1; // CHANGE ME
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        initialize();
      }

      push_up_game();

      break;


    case POKER_GAME:

      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        char join[] = "join";

        if (flag2) {
          flag2 = false;
          handle_action_post_req(user, join, 0, room_id); // only time needed to hardcode action
        }

        //        Serial.println("room_id before get");
        //        Serial.println(room_id);

        char room_id_copy[500];
        memset(room_id_copy, 0, strlen(room_id_copy));
        strcpy(room_id_copy, room_id);

        get_poker_actions_req(user, room_id);
        //        Serial.println("room_id_copy after get");
        //        Serial.println(room_id_copy);

        memset(room_id, 0, strlen(room_id));
        strcpy(room_id, room_id_copy);
        //        Serial.println("room_id after get");
        //        Serial.println(room_id);

        extract_poker_actions();
        draw_poker_screen(poker_actions, selection);
        //Serial.println(actions_buffer);
        get_actions_timer = millis();

        // intitialize previous actions <- current actions when first entering game
        memset(previous_actions_buffer, 0, strlen(previous_actions_buffer));
        strcpy(previous_actions_buffer, actions_buffer);
      }

      //      if (millis() - get_actions_timer >= 5000) {
      //        get_poker_actions_req(user, room_id);
      //        //poker_actions_post_req(user, room_id);
      //        get_actions_timer = millis();
      //        //state = POKER_GAME;
      //
      //        Serial.println(strlen(actions_buffer));
      //        Serial.println(get_actions_timer);
      //
      //        if (strcmp(previous_actions_buffer, actions_buffer) != 0) {
      //
      //          Serial.println("different actions");
      //
      //          extract_poker_actions(); // only now are actions_buffer updated
      //          //get_actions_timer = millis();
      //
      //          selection = 0;
      //
      //          // if there is any game update (new actions), draw game screen again, otherwise do nothing
      //          draw_poker_screen(poker_actions, selection); // may need to reset selection (?)
      //          // set previous actions <- current actions when updating
      //          memset(previous_actions_buffer, 0, strlen(previous_actions_buffer));
      //          strcpy(previous_actions_buffer, actions_buffer);
      //        }
      //        Serial.println("about to exit if statement..");
      //      }


      //Serial.println("checking for new selection..");
      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        Serial.println("new selection");
        selection = new_selection;
        draw_poker_screen(poker_actions, selection);
      }


      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        if (selection == 0) { // if user wants to refresh page
          flag = true;
        }
        else {
          extract_selected_poker_action(); // fills action char array with selected action
          if (strcmp(action, "bet") == 0) {
            flag = true;
            state = POKER_BET;
          }
          else if (strcmp(action, "raise") == 0) {
            flag = true;
            state = POKER_RAISE;
          }
          else if (strcmp(action, "leave") == 0) {
            flag = true; // want to refresh actions page
            //handle_action_post_req(user, "leave", 0, room_id);
            state = ROOM;
          }
          else {
            flag = true; // want to refresh actions page
            handle_action_post_req(user, action, 0, room_id);
          }

        }
      }

      old_transition_btn = transition_btn;

      //state = POKER_GAME;

      break;


    case POKER_BET:

      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 5;
        bet_amount = bet_params[0];
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_poker_bet_screen(selection);
      }

      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        Serial.println("new selection");
        selection = new_selection;
        draw_poker_bet_screen(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        // flag = true;
        if (selection == 0 || selection == 1 || selection == 2) {
          update_bet_amount();
          draw_poker_bet_screen(selection);
        }
        else if (selection == 3) { // confirm bet, make post request (here action = "bet")
          flag = true;
          handle_action_post_req(user, action, bet_amount, room_id);
          state = POKER_GAME;
        }
        else if (selection == 4) {
          flag = true;
          state = POKER_GAME;
        }

      }

      old_transition_btn = transition_btn;

      break;


    case POKER_RAISE:

      if (millis() - timer >= ping_period) {
        ping_online(user, pswd);
        timer = millis();
      }

      if (flag) {
        selection = 0;
        no_of_selections = 5;
        raise_amount = raise_params[0];
        flag = false;
        tft.fillScreen(TFT_BLACK); //fill background
        draw_poker_raise_screen(selection);
      }

      new_selection = update_selection(selection, no_of_selections);
      if (new_selection != selection) {
        Serial.println("new selection");
        selection = new_selection;
        draw_poker_raise_screen(selection);
      }

      transition_btn = digitalRead(PIN_2);
      if (transition_btn != old_transition_btn && transition_btn == 1) {
        // flag = true;
        if (selection == 0 || selection == 1 || selection == 2) {
          update_raise_amount();
          draw_poker_raise_screen(selection);
        }
        else if (selection == 3) { // confirm raise, make post request (here action = "raise")
          flag = true;
          handle_action_post_req(user, action, raise_amount, room_id);
          state = POKER_GAME;
        }
        else if (selection == 4) {
          flag = true;
          state = POKER_GAME;
        }

      }

      old_transition_btn = transition_btn;

      break;



  }

}
