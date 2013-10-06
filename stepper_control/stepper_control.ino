#define MM_TO_STEPS (4672) //with 64 microstepping (73 on nothing)

char c;

int mode;


int dir;
unsigned int spd; // in um/sec
int avg = 0;
float inst;

void setup() {
  mode = 0;
  dir = 0;
  spd = 0;
  Serial.begin(9600);
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  delay(100);
}

void run_motor() {

  if (dir == 1) {
    digitalWrite(9, HIGH);
  } else if (dir == -1) {
    digitalWrite(9, LOW);
  }

  tone(8, int(46.72*spd));
  
  Serial.print("A");
}

//K kill, S speed
void loop() {
  if (Serial.available()) {
    c = Serial.read();
    if (c == 'K') {
      noTone(8);
    } else if (mode > 0) {
      if (c == ';') {
        run_motor();
        dir = 0;
        spd = 0;
        mode = 0;
      } else {
        switch(mode) {
        case 1:
          if (c == 'U') {
            dir = 1;
          } else if (c == 'D') {
            dir = -1;
          }
          mode = 2;
          break;
        case 2:
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
    } else if (c == 'F') {
        mode = 1;
      }
    }
}

