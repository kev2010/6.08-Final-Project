float UP_THRESHOLD = 4;
float DOWN_THRESHOLD = 2;


#define IDLE 10
#define DOWN 11
#define UP 12

float x, y, z; //variables for grabbing x,y,and z values

uint8_t record_btn = 1;
uint8_t old_record_btn = 1;
uint32_t rep_timer = 0;
uint32_t cntd_timer = 0;

uint8_t pstate;  //system pstate for step counting
bool record = false;
bool started = false;
bool first = true;


float acc_mag;
float avg_acc_mag;
float old_acc_mag;
float older_acc_mag;

int push_ups;
int prev_push_ups;
uint8_t countdown;

void initialize() {
  push_ups = 0;
  pstate = IDLE;
  rep_timer = millis();
  record = false;
  countdown = 5;
  first = true;
  prev_push_ups = 10;
}

void push_up_game() {
  record_btn = digitalRead(PIN_1);
  if (record_btn != old_record_btn && record_btn == 1) {
    record = !record;
    if (record == true) {
      Serial.println("Starting to record ...");
    }
  }
  old_record_btn = record_btn;

  if (record == true) {
    if (countdown == 0) {
      tracker();
      push_up_reporter_fsm(avg_acc_mag);

      if (prev_push_ups != push_ups) {
        tft.fillScreen(TFT_BLACK);
        char a[5];
        sprintf(a, "%d", push_ups);
        tft.drawString(a, 70, 60, 2);
        prev_push_ups = push_ups;
      }

      if (millis() - rep_timer > 2000 and started == true) {
        Serial.println("Finished recording");
        post_push_ups();
        
        push_ups = 0;
        started = false;
        record = false;
        first = true;
        countdown = 5;
        
        state = PUSH_UP_GAME;
        flag = true;
      }
    } else {
      if (millis() - cntd_timer > 1000) {
        countdown--;
        tft.fillScreen(TFT_BLACK);
        tft.drawString("Counting down ...", 20, 60, 1);
        if (countdown == 0) {
          Serial.println("Go!!");
        } else {
          Serial.print("Begin in ");
          Serial.println(countdown);
        }

        cntd_timer = millis();
      }

    }

  } else {
    if (first == true) {
      tft.fillScreen(TFT_BLACK);
      tft.drawString("Press button on pin 16 to", 0, 40, 1);
      tft.drawString("start recording", 30, 50, 1);
      tft.drawString("You will have 5 seconds to", 0, 70, 1);
      tft.drawString("begin recording", 30, 80, 1);
      first = false;
    }
  }

}


void tracker() {
  //GET INPUT INFORMATION:
  imu.readAccelData(imu.accelCount);
  float x, y, z;
  x = imu.accelCount[0] * imu.aRes;
  y = imu.accelCount[1] * imu.aRes;
  z = imu.accelCount[2] * imu.aRes;

  //  float acc_mag = sqrt(x*x + y*y + z*z);
  acc_mag = sqrt(z * z);
  //    float avg_acc_mag = 1.0 / 2.0 * (acc_mag + old_acc_mag);
  avg_acc_mag = 1.0 / 3.0 * (acc_mag + old_acc_mag + older_acc_mag);
  avg_acc_mag = avg_acc_mag * 10;


  older_acc_mag = old_acc_mag;
  //  old_acc_mag = acc_mag;
}

//Step Counting FSM from Lab02A.  (bring over and adapt global variables as needed!)
void push_up_reporter_fsm(float acc) {
  switch (pstate) {
    case IDLE:
      if (acc < DOWN_THRESHOLD) {
        pstate = DOWN;
        //        Serial.println("Going Down");
      }

      break;
    case DOWN:
      if (acc > UP_THRESHOLD) {
        pstate = UP;
        //        Serial.println("Going Up");
      }
      break;
    case UP:
      if (acc > DOWN_THRESHOLD and acc < UP_THRESHOLD) {
        push_ups++;
        //        Serial.println("Going IDLE");
        Serial.println(push_ups);
        started = true;
        rep_timer = millis();
        pstate = IDLE;
      }
      break;
  }
}
