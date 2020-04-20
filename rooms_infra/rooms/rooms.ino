
#include <WiFi.h> //Connect to WiFi Network
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

char network[] = "";  //SSID for 6.08 Lab
char password[] = ""; //Password for 6.08 Lab

char user[] = "jkaklam";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host

const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response

char host[] = "Host room";
char join[] = "Join room";
char turn_off[] = "Turn_off";

uint8_t state;
#define MAIN_LOBBY 0
#define HOST_LOBBY 1
#define JOIN_LOBBY 2
#define ROOM 3

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

void setup() {
  Serial.begin(115200);
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set color of font to green foreground, black background
  Serial.begin(115200); //begin serial comms
  delay(100); //wait a bit (100 ms)
  pinMode(PIN_1, INPUT_PULLUP);
  pinMode(PIN_2, INPUT_PULLUP);

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



  tft.drawString("-----------------------", 0, 90, 1);
  tft.drawString(host, 20, 100, 1);
  tft.drawString(join, 20, 110, 1);
  tft.drawString(turn_off, 20, 120, 1);
  tft.drawString("*", 5, 100, 1);

  ping_online();

  state = MAIN_LOBBY;
  flag = true;

}

uint8_t update_selection(uint8_t selection, uint8_t initial_height, uint8_t no_of_selections) {
  selection_btn = digitalRead(PIN_1);
  if (selection_btn != old_selection_btn && selection_btn == 1) {
    tft.fillScreen(TFT_BLACK); //fill background
    tft.setCursor(0, 0, 1); // set the cursor
    // tft.println(response_buffer); //print the result
    selection  = (selection + 1) % no_of_selections;
  }
  old_selection_btn = selection_btn;
  return selection;
}

void loop() {

  switch (state) {
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
          host_room_post_req();
        }

        old_transition_btn = transition_btn;

        break;

      case JOIN_LOBBY:
        if (flag) {
          selection = 0;
          no_of_selections = 4;
          flag = false;
          tft.fillScreen(TFT_BLACK); //fill background
          draw_join_lobby_menu(selection);
        }
        new_selection = update_selection(selection, 100, no_of_selections);
        if (new_selection != selection) {
          selection = new_selection;
          draw_join_lobby_menu(selection);
        }
        transition_btn = digitalRead(PIN_2);
        if (transition_btn != old_transition_btn && transition_btn == 1) {
          flag = true;
          if (selection == 0) {
            state = ROOM;
          } else if (selection == 1) {
            state = ROOM;
          } else if (selection == 2) {
            state = ROOM;
          } else if (selection == 3) {
            state = MAIN_LOBBY;
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
        //      new_selection = update_selection(selection, 100, no_of_selections);
        //      if (new_selection != selection) {
        //        selection = new_selection;
        //        draw_room_screen();
        //      }
        transition_btn = digitalRead(PIN_2);
        if (transition_btn != old_transition_btn && transition_btn == 1) {
          flag = true;
          if (selection == 0) {
            state = MAIN_LOBBY;
          }
        }
        old_transition_btn = transition_btn;

        break;
      }

  }