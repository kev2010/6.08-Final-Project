#include <WiFi.h> //Connect to WiFi Network
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display
#include <string.h>  //used for some string handling and processing.

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h

char network[] = "BTHub6-3JRW";  //SSID for 6.08 Lab 2.4 GHz devices
char password[] = "HVpPptcx3DTE"; //Password for 6.08 Lab 2.4 GHz devices

const uint8_t LOOP_PERIOD = 10; //milliseconds
uint32_t primary_timer = 0;
uint32_t posting_timer = 0;
float x,y,z; //variables for grabbing x,y,and z values

const char USER[] = "test_user";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const int POSTING_PERIOD = 6000; //periodicity of getting a number fact.

const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response


float old_acc_mag;
float older_acc_mag;  //

int steps;


void setup(){
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set color of font to green foreground, black background
  Serial.begin(115200); //begin serial comms
  delay(100); //wait a bit (100 ms)

  WiFi.begin(network,password); //attempt to connect to wifi
  uint8_t count = 0; //count used for Wifi check times
  Serial.print("Attempting to connect to ");
  Serial.println(network);
  while (WiFi.status() != WL_CONNECTED && count<12) {
    delay(500);
    Serial.print(".");
    count++;
  }
  delay(2000);
  if (WiFi.isConnected()) { //if we connected then print our IP, Mac, and SSID we're on
    Serial.println("CONNECTED!");
    Serial.println(WiFi.localIP().toString() + " (" + WiFi.macAddress() + ") (" + WiFi.SSID() + ")");
    delay(500);
  } else { //if we failed to connect just Try again.
    Serial.println("Failed to Connect :/  Going to restart");
    Serial.println(WiFi.status());
    ESP.restart(); // restart the ESP (proper way)
  }
}


void loop(){
  if (millis()-posting_timer > POSTING_PERIOD){
    char body[100]; //for body
    sprintf(body,"user=%s&steps=%d",USER,1);//generate body, posting to User, 1 step
    int body_len = strlen(body); //calculate body length (for header reporting)
    sprintf(request_buffer,"POST http://iesc-s3.mit.edu/esp32test/stepcounter HTTP/1.1\r\n");
    strcat(request_buffer,"Host: iesc-s3.mit.edu\r\n");
    strcat(request_buffer,"Content-Type: application/x-www-form-urlencoded\r\n");
    sprintf(request_buffer+strlen(request_buffer),"Content-Length: %d\r\n", body_len); //append string formatted to end of request buffer
    strcat(request_buffer,"\r\n"); //new line from header to body
    strcat(request_buffer,body); //body
    strcat(request_buffer,"\r\n"); //header
    Serial.println(request_buffer);
    do_http_request("iesc-s3.mit.edu", request_buffer, response_buffer, OUT_BUFFER_SIZE, RESPONSE_TIMEOUT,true);
    Serial.println(response_buffer); //viewable in Serial Terminal
    steps=0;
    //LCD Display:
    char output[80];
    tft.drawString("Check Serial Monitor!!",0,10,1);
    posting_timer = millis();
  }
   
  while (millis()-primary_timer<LOOP_PERIOD); //wait for primary timer to increment
  primary_timer =millis();
}
