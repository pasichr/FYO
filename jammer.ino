#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define LED_PIN8 PB14
#define LED_PIN7 PB15

RF24 radio(PB10,PB11); // CE, CSN

void setup() {
  Serial.begin(9600);  // Start serial communication at 9600 bps
  
  pinMode(LED_PIN7, OUTPUT);  // Set the LED pin as output
  pinMode(LED_PIN8, OUTPUT);  // Set the LED pin as output
    pinMode(PB10, OUTPUT);  // Set the LED pin as output
  pinMode(PB11, OUTPUT);  // Set the LED pin as output

  digitalWrite(PB11,LOW);
  digitalWrite(PB10,LOW);
  randomSeed(analogRead(0));  // Initialize random seed
  
  radio.begin();
  radio.setPALevel(RF24_PA_MAX); // Set power level
  radio.setDataRate(RF24_2MBPS); // data rate
}

void loop() {
  if (Serial.available()) {  // If data is available to read
    char command = Serial.read(); // Read the next character
    if (command == '1') {
      digitalWrite(LED_PIN8, LOW); 
      
      
      for (uint8_t channel = 0; channel <= 125; channel++) { 

      digitalWrite(LED_PIN7, HIGH);
      
      
      radio.setChannel(channel); // Set the channel
       byte randomData[32]; // Maximum payload size for nRF24L01 is 32 bytes

        for (int i = 0; i < 32; i++) {
          randomData[i] = random(0, 255); // Fill array with random bytes
        }

        radio.write(&randomData, sizeof(randomData));
      }

      //delay(100); // Small delay between loops
      digitalWrite(LED_PIN7, LOW); // Turn the LED off
    } 
    else if (command == '0') {
      digitalWrite(LED_PIN7, LOW);
      digitalWrite(LED_PIN8, HIGH);   // Turn the red LED on
                  // Wait for another second
      Serial.println("Jammer Stopped SuccessFully"); 
    }
  }
}
