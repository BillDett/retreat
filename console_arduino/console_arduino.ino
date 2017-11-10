

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

int completed = 0;  // Is puzzle completed (e.g. patch was solved)

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
  
  pinMode(xSwitchPin, INPUT_PULLUP);
  pinMode(oSwitchPin, INPUT_PULLUP);  
  pinMode(tictacGreen, OUTPUT);
  pinMode(tictacRed, OUTPUT);

  pinMode(patch1SwitchPin, INPUT_PULLUP);  
  pinMode(patch2SwitchPin, INPUT_PULLUP);  
  pinMode(patch3SwitchPin, INPUT_PULLUP);  
  pinMode(patch4SwitchPin, INPUT_PULLUP);  
  pinMode(patch5SwitchPin, INPUT_PULLUP);  
  pinMode(patch6SwitchPin, INPUT_PULLUP);  
  pinMode(patchGreen, OUTPUT);
  pinMode(patchRed, OUTPUT);

  Serial.begin(9600);
  state = KEY;
}

void loop() {
  if ( state == KEY ) {
     //Serial.println("Now Key");
     if ( digitalRead(keySwitchPin) == HIGH ) {
       digitalWrite(keySwitchGreen, HIGH);
       digitalWrite(keySwitchRed, LOW);
       digitalWrite(tictacRed, HIGH);       
       state = TOGGLE;
       // TODO: Tell the Pi to play a sound
     } else {
       digitalWrite(keySwitchGreen, LOW);
       digitalWrite(keySwitchRed, HIGH);
     }
  } else if ( state == TOGGLE ) {
     //Serial.println("Now Toggle");
     if ( (digitalRead(xSwitchPin) == LOW) && (digitalRead(oSwitchPin) == LOW) ) {
       digitalWrite(tictacGreen, HIGH);
       digitalWrite(tictacRed, LOW);
       digitalWrite(patchRed, HIGH);    
       state = PATCH;
       // TODO: Tell the Pi to play a sound       
     } else {
       digitalWrite(tictacGreen, LOW);
       digitalWrite(tictacRed, HIGH);
     }    
  } else if ( state == PATCH ) {
     //Serial.println("Now Patch");
     /*
     Serial.print("0: ");
     Serial.print(analogRead(patch1SwitchPin));
     Serial.print(" 1: ");
     Serial.print(analogRead(patch2SwitchPin));
     Serial.print(" 2: ");
     Serial.print(analogRead(patch3SwitchPin));
     Serial.print(" 3: ");
     Serial.print(analogRead(patch4SwitchPin));
     Serial.print(" 4: ");
     Serial.print(analogRead(patch5SwitchPin));
     Serial.print(" 5: ");
     Serial.print(analogRead(patch6SwitchPin));
     Serial.println("");
     */
//     delay(1000);

    if ( !completed ) {

       if ( (analogRead(patch1SwitchPin) >= 22 && analogRead(patch1SwitchPin) <= 24)
         &&  (analogRead(patch2SwitchPin) >= 34 && analogRead(patch2SwitchPin) <= 36)
         &&  (analogRead(patch3SwitchPin) >= 42 && analogRead(patch3SwitchPin) <= 44)
         &&  (analogRead(patch4SwitchPin) >= 41 && analogRead(patch4SwitchPin) <= 43)
         &&  (analogRead(patch5SwitchPin) >= 19 && analogRead(patch5SwitchPin) <= 21)
         &&  (analogRead(patch6SwitchPin) >= 54 && analogRead(patch6SwitchPin) <= 56) ) {
           digitalWrite(patchGreen, HIGH);
           digitalWrite(patchRed, LOW);
           Serial.print("Y"); 
           completed = 1;
         } else {
           digitalWrite(patchGreen, LOW);
           digitalWrite(patchRed, HIGH);
       }      
    }
  }
}
