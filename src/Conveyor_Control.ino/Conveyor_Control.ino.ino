#include <MFRC522.h>
#include <MFRC522Extended.h>
#include <deprecated.h>
#include <require_cpp11.h>
#include <SPI.h>
#include <MFRC522.h>
#include <List.hpp>

#define RST_PIN         9      
#define SS_PIN          10        

const int motor_1 = 3;
const int motor_2 = 5;
const int motor_flag = 4;
int speed = 0;// 속도값
int stop =0; //멈춤 flag
int count =0;
int robot_arm = 0;
MFRC522 mfrc522(SS_PIN, RST_PIN); 

void setup() {
  Serial.begin(9600);
  pinMode(motor_1, OUTPUT);
  pinMode(motor_2, OUTPUT);
  pinMode(motor_flag, INPUT);

  SPI.begin();
  mfrc522.PCD_Init(); // Init MFRC522
  Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
}

void loop() {
  robot_arm = digitalRead(motor_flag);
  // Serial.println(stop);
  if (robot_arm == 1 && stop ==0) {
    stop = 1;
    Serial.println("stopped");
  }

  if (stop == 1) {
    count += 1;
    speed = 0;
    Serial.println("stopped");
    // Serial.println(count);
    if (count == 500) {
      count = 0;
      stop = 0;
    }
  }

  if (stop != 1) {
    speed = 120;
    Serial.println("is working");
  }

  analogWrite(motor_1, speed);
  digitalWrite(motor_2, LOW);
}