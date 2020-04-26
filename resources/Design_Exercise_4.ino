#include <SPI.h>
#include <TFT_eSPI.h>
TFT_eSPI tft = TFT_eSPI();

const int PERIOD = 250;
int render_period;
int raw_reading;
float sample_rate = 800; //Hz
float sample_period = (int)(1e6 / sample_rate);
float UP_THRESHOLD = 1900;
float DOWN_THRESHOLD = 1300;

float avg_reading, old_reading, older_reading, oldest_reading, boomer_reading;

uint32_t transition_timer;
uint32_t clap_timer;
uint8_t state;
uint8_t claps;
bool toggle = true;


#define IDLE 0
#define UP 1
#define DOWN 2


void setup() {
  Serial.begin(115200);
  pinMode(14, OUTPUT);
  digitalWrite(14, 1);
  render_period = millis();
  tft.init();  //init screen
  tft.setRotation(2); //adjust rotation
  tft.setTextSize(1); //default    font size
  tft.fillScreen(TFT_GREEN); //fill background
  tft.setTextColor(TFT_GREEN, TFT_BLACK); //set col
//  tft.drawString("Hello World!", 0, 0, 1); 
  transition_timer = millis();
  clap_timer = millis();
  state = IDLE;
  claps = 0;
}

void loop() {
  raw_reading = analogRead(A0);

  avg_reading = (raw_reading + old_reading + older_reading + oldest_reading + boomer_reading) / 5.0;
  boomer_reading = oldest_reading;
  oldest_reading = older_reading;
  older_reading = old_reading;
  old_reading = raw_reading;

  //  Serial.println(avg_reading);
  switch (state) {
    case IDLE:
      //      Serial.println("IDLE");
      if (millis() - clap_timer >= 1000 and claps >= 1) {
        claps = 0;
      }

      if (avg_reading > UP_THRESHOLD) {
        if (millis() - clap_timer <= 250 and claps >= 1) {
          claps = 0;
        }
        transition_timer = millis();

        state = UP;
      }
      break;
    case UP:
      //      Serial.println("UP");
      if (avg_reading < DOWN_THRESHOLD) {
        state = DOWN;
        transition_timer = millis();
      } else if (millis() - transition_timer > 250) {
        claps = 0;
        state = IDLE;
      }
      break;
    case DOWN:
      //      Serial.println("DOWN");
      if (avg_reading > DOWN_THRESHOLD and avg_reading < UP_THRESHOLD) {
        state = IDLE;
        transition_timer = millis();
        clap_timer = millis();
        claps++;
        if (claps == 2) {
          toggle = !toggle;
          claps = 0;
          //          Serial.println("Double Clap!!!");
          if (toggle == true) {
            digitalWrite(14, 1);
          } else {
            digitalWrite(14, 0);
          }
        }

      }
      break;
  }
  Serial.println(claps);
}
