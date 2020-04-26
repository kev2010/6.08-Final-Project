#include <WiFi.h> //Connect to WiFi Network
#include <TFT_eSPI.h> // Graphics and font library for ST7735 driver chip
#include <SPI.h> //Used in support of TFT Display
#include <string.h>  //used for some string handling and processing.
#include <mpu6050_esp32.h>
#include<math.h>

TFT_eSPI tft = TFT_eSPI();  // Invoke library, pins defined in User_Setup.h


char network[] = "MIT";  //SSID for 6.08 Lab
char password[] = ""; //Password for 6.08 Lab

bool first = true;

const uint8_t LOOP_PERIOD = 10; //milliseconds
uint32_t primary_timer = 0;
uint32_t posting_timer = 0;
uint32_t step_timer = 0;
float x, y, z; //variables for grabbing x,y,and z values
const char USER[] = "gchatz";

//Some constants and some resources:
const int RESPONSE_TIMEOUT = 6000; //ms to wait for response from host
const int POSTING_PERIOD = 6000; //periodicity of getting a number fact.
const uint16_t IN_BUFFER_SIZE = 1000; //size of buffer to hold HTTP request
const uint16_t OUT_BUFFER_SIZE = 1000; //size of buffer to hold HTTP response
char request_buffer[IN_BUFFER_SIZE]; //char array buffer to hold HTTP request
char response_buffer[OUT_BUFFER_SIZE]; //char array buffer to hold HTTP response

const uint8_t INPUT_PIN1 = 16; //pin connected to button
const uint8_t INPUT_PIN2 = 5; //pin connected to button

char out[20];

uint8_t state;  //system state for step counting
uint8_t post_state; //state of posting
bool last_out = true;

#define IDLE 0  //change if you'd like
#define DOWN 1  //change if you'd like
#define POST 2  //change if you'd like
#define UP 3
#define UPLOAD 4


MPU6050 imu; //imu object called, appropriately, imu

float old_acc_mag;
float older_acc_mag;  //

int steps;
int curr_steps;


void setup() {
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default font size
  tft.fillScreen(TFT_BLACK); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set color of font to green foreground, black background
  Serial.begin(115200); //begin serial comms
  delay(100); //wait a bit (100 ms)
  Wire.begin();
  delay(50); //pause to make sure comms get set up
  if (imu.setupIMU(1)) {
    Serial.println("IMU Connected!");
  } else {
    Serial.println("IMU Not Connected :/");
    Serial.println("Restarting");
    ESP.restart(); // restart the ESP (proper way)
  }

  pinMode(INPUT_PIN1, INPUT_PULLUP); //set input pin as an input!
  pinMode(INPUT_PIN2, INPUT_PULLUP); //set input pin as an input!

  state = IDLE;
  post_state = 0; //initialize to somethin!
}


void loop() {
  //GET INPUT INFORMATION:
  imu.readAccelData(imu.accelCount);
  float x, y, z;
//  x = imu.accelCount[0] * imu.aRes;
//  y = imu.accelCount[1] * imu.aRes;
  z = imu.accelCount[2] * imu.aRes;
  uint8_t button1 = digitalRead(INPUT_PIN1);
  uint8_t button2 = digitalRead(INPUT_PIN2);
//  float acc_mag = sqrt(x * x + y * y + z * z);
  float acc_mag = sqrt(z*z);
//  Serial.print(acc_mag);
  float avg_acc_mag = 1.0 / 3.0 * (acc_mag + old_acc_mag + older_acc_mag);
//  step_reporter_fsm(avg_acc_mag); //run step_reporter_fsm (from lab02a)
//  post_reporter_fsm(button1); //run post_reporter_fsm (written here)
//  lcd_display(button2); //update display (minimize pixels you change)
  while (millis() - primary_timer < LOOP_PERIOD); //wait for primary timer to increment
  primary_timer = millis();
  older_acc_mag = old_acc_mag;
  old_acc_mag = acc_mag;
}


//Post reporting state machine, uses button1 as input
//use post_state for your state variable!
void post_reporter_fsm(uint8_t button1) {
  switch (post_state){
    case IDLE:
      if (button1==0){
        post_state = DOWN;
      }
    break;
    case DOWN:
      if (button1==1){
        post_state = UPLOAD;
      }
    break;
    case UPLOAD:
      first = false;
      //make post request
      make_post_req();
      Serial.println("Made post request!");
      tft.fillScreen(TFT_BLACK);
      curr_steps = 0;
      post_state = IDLE;
    break;
  }
}

void make_post_req(){
  char body[100]; //for body
  sprintf(body,"user=%s&steps=%d",USER,steps);//generate body, posting to User
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
}


//Step Counting FSM from Lab02A.  (bring over and adapt global variables as needed!)
void step_reporter_fsm(float acc) {
  switch (state){
    case IDLE:
      if (acc>2){
        state = UP;
      }
    break;
    case UP:
      if (acc<1){
        state = DOWN;
      }
    break;

    case DOWN:
      steps++;
      curr_steps++;
      state = IDLE;
    break;
  }
}
//Display information on LED based on button value (stateless)
void lcd_display(uint8_t button2) {
  if (button2==0){
    if (last_out){
      tft.fillScreen(TFT_BLACK);
      last_out = false;
    }
    sprintf(out, "Steps: %d", steps);
    tft.drawString(out, 0, 0, 1);
  } else {
    if (steps==0 and first){
      curr_steps = steps;
    }
    sprintf(out, "Current steps: %d", curr_steps);
    tft.drawString(out, 0, 0, 1);
    last_out = true;
  }
}
