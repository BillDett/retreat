/*
*  Arduino sketch for console puzzles.

Puzzles must be solved in following order:

1. Key switch
2. Tic Tac Toggle
3. Patch Panel

After all have been solved, send a message to Raspberry Pi to unlatch the door for final puzzle

*/

// Key Switch
const int keySwitchPin = 9;
const int keySwitchGreen = 11;
const int keySwitchRed = 10;

// Tic Tac Toggle
const int xSwitchPin = 7;
const int oSwitchPin = 8;
const int tictacGreen = 3;
const int tictacRed = 2;

// Patch Panel
const int patch1SwitchPin = 14; // Analog 0;
const int patch2SwitchPin = 15; // Analog 1;
const int patch3SwitchPin = 16; // Analog 2;
const int patch4SwitchPin = 17; // Analog 3;
const int patch5SwitchPin = 18; // Analog 4;
const int patch6SwitchPin = 19; // Analog 5;
const int patchGreen = 5;
const int patchRed = 4;

const int resetPin = 10;    // TODO: Set an interrupt for this pin- reset back to initial KEY state

enum puzzleState {
  KEY,
  TOGGLE,
  PATCH
};

enum puzzleState state;

void setup() {
  pinMode(keySwitchPin, INPUT);
  pinMode(keySwitchGreen, OUTPUT);
  pinMode(keySwitchRed, OUTPUT);
  
  pinMode(xSwitchPin, INPUT);
  pinMode(oSwitchPin, INPUT);  
  pinMode(tictacGreen, OUTPUT);
  pinMode(tictacRed, OUTPUT);

  pinMode(patch1SwitchPin, INPUT);  
  pinMode(patch2SwitchPin, INPUT);  
  pinMode(patch3SwitchPin, INPUT);  
  pinMode(patch4SwitchPin, INPUT);  
  pinMode(patch5SwitchPin, INPUT);  
  pinMode(patch6SwitchPin, INPUT);  
  pinMode(patchGreen, OUTPUT);
  pinMode(patchRed, OUTPUT);
  Serial.begin(9600);
  state = KEY;
}

void loop() {
  if ( state == KEY ) {
    Serial.println(digitalRead(keySwitchPin));
     if ( digitalRead(keySwitchPin) == HIGH ) {
       Serial.println("Yup");
       digitalWrite(keySwitchGreen, HIGH);
       //analogWrite(keySwitchGreen, 255);
       digitalWrite(keySwitchRed, LOW);
       //analogWrite(keySwitchRed, 0);
       delay(500);
       state = TOGGLE;
       // TODO: Tell the Pi to play a sound
     } else {
       Serial.println("Nope");
       digitalWrite(keySwitchGreen, LOW);
       //analogWrite(keySwitchGreen, 0);
       digitalWrite(keySwitchRed, HIGH);
       //analogWrite(keySwitchRed, 255);
     }
  } else if ( state == TOGGLE ) {
     if ( (digitalRead(xSwitchPin) == HIGH) && (digitalRead(oSwitchPin) == HIGH) ) {
       digitalWrite(tictacGreen, HIGH);
       digitalWrite(tictacRed, LOW);
       state = PATCH;
       // TODO: Tell the Pi to play a sound       
     } else {
       digitalWrite(tictacGreen, LOW);
       digitalWrite(tictacRed, HIGH);
     }    
  } else if ( state == PATCH ) {
     if ( (digitalRead(patch1SwitchPin) == HIGH)
           && (digitalRead(patch2SwitchPin) == HIGH) 
           && (digitalRead(patch3SwitchPin) == HIGH) 
           && (digitalRead(patch4SwitchPin) == HIGH) 
           && (digitalRead(patch5SwitchPin) == HIGH) 
           && (digitalRead(patch6SwitchPin) == HIGH) ) {
       digitalWrite(patchGreen, HIGH);
       digitalWrite(patchRed, LOW);
       // TODO: Notify the Pi!!
       
     } else {
       digitalWrite(patchGreen, LOW);
       digitalWrite(patchRed, HIGH);
     }      
  }
  

}
