#define MM_TO_STEPS (4672) //with 64 microstepping

//FD100,100; * 2 with MM_ = 1000 == 6mm
// time = 2000 spd = 10000 steps = 20000/0.006 = 
char c;
/*
mode 0 - waiting
 mode 1 - reading direction (U/D)
 mode 2 - reading distance (number of um)
 mode 3 - reading speed (mm/s)
 */

int mode;

int dir;
unsigned long steps;
unsigned int spd;
int avg = 0;

void setup() {
  mode = 0;
  dir = 0;
  steps = 0;
  spd = 0;
  Serial.begin(9600);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  delay(100);
}

void run_motor() {
  //some pin for dir

    //edge and delay for each step
  
  if (dir == 1) {
    digitalWrite(9, HIGH);
  } else if (dir == -1) {
    digitalWrite(9, LOW);
    if (spd > 100) {
      Serial.print("F");
      return;
    }
  }

  unsigned long runTime = (1000*steps)/spd;
  
  if (runTime == 0) {
    Serial.print("F");
    return;
  }

  tone(8, int(46.72*spd), runTime);
  
  if (runTime >= 10) {
    long sum = 0;
    for (int i = 0; i < 10; i++) {
      sum = sum + analogRead(0);
      delay(int(runTime/10));
    } 
    avg = sum/10;
  } else {
    delay(runTime + 5);
    avg = 0;
  }
  Serial.print("A");
}
//155mm 10000 1000
//160mm 10000 1000
//170mm 
void loop() {
  if (Serial.available()) {
    c = Serial.read();
    if (c == 'K') {
      noTone(8);
    } else if (c == 'P') {
      Serial.print(avg);
      Serial.print("A");
    }
    
    if (mode > 0) {
      if (c == ';') {
        run_motor();
        dir = 0;
        steps = 0;
        spd = 0;
        mode = 0;
      } 
      else {
        switch(mode) {
        case 1:
          if (c == 'U') {
            dir = 1;
            mode = 2;
          } 
          else if (c == 'D') {
            dir = -1;
            mode = 2;
          }
          break;
        case 2:
          if (c >= '0' && c <= '9') {
            steps = steps * 10;
            steps = steps + c - '0';
          } 
          else if (c == ',') {
            mode = 3;
          }
          break;
        case 3:
          if (c >= '0' && c <= '9') {
            spd = spd * 10;
            spd = spd + c - '0';
          }
          break;
        default:
          mode = 0;
          break;
        };
      }
    } 
    else {
      if (c == 'F') {
        mode = 1;
      }
    }
  }
}

