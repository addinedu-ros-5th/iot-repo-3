#include <Servo.h>
#include <SoftwareSerial.h>

SoftwareSerial A_Serial(7,8);
const int motor_1 = 3;
const int motor_2 = 5;
const int motor_flag = 4;
const int servo_1_pin = 9;
const int servo_2_pin = 10;
const int servo_3_pin = 11;

int speed = 0; // DC 모터 속도
int stop =0; // 멈춤 flag
int count =0;
int robot_arm = 0;

Servo servo_1;
Servo servo_2;
Servo servo_3;

void setup() {
  A_Serial.begin(9600);
  Serial.begin(9600);
  pinMode(motor_1, OUTPUT);
  pinMode(motor_2, OUTPUT);
  pinMode(motor_flag, INPUT);

  servo_1.attach(servo_1_pin); // 서보 모터 1에 핀 연결
  servo_2.attach(servo_2_pin); // 서보 모터 2에 핀 연결
  servo_3.attach(servo_3_pin); // 서보 모터 3에 핀 연결
  
  servo_1.write(0); // 초기 위치로 설정
  servo_2.write(0);
  servo_3.write(0);
}

void loop() {
  // robot_arm = digitalRead(motor_flag);
  // Serial.println(stop);
  // if (robot_arm == 1 && stop == 0) {
  //   stop = 1;
  //   Serial.println("stopped");
  // }



  if(A_Serial.available()){
    char input = A_Serial.read();
    
    if (input == '1') {
      servo_2.write(0); // 2번 서보 모터 초기화
      servo_3.write(0); // 3번 서보 모터 초기화
      moveServo(servo_1, 90, 2000); // 1번을 누르면 90도로 2초 후에 180도로 이동
      Serial.println(input);
    }
    else if (input == '2') {
      servo_1.write(0); // 1번 서보 모터 초기화
      servo_3.write(0); // 3번 서보 모터 초기화
      moveServo(servo_2, 90, 4000); // 2번을 누르면 90도로 4초 후에 180도로 이동
      Serial.println(input);
    }
    else if (input == '3') {
      servo_1.write(0); // 1번 서보 모터 초기화
      servo_2.write(0); // 2번 서보 모터 초기화
      moveServo(servo_3, 90, 6000); // 3번을 누르면 90도로 6초 후에 180도로 이동
      Serial.println(input);
    }

    else if (input =='4'){
      stop = 1;
      Serial.println(input);
      // Serial.println("idasjflasjlf");
    }
  }


  if (stop == 1) {
    count += 1;
    speed = 0;
    Serial.println("stopped");
    if (count == 500) {
      count = 0;
      stop = 0;
    }
  }

  if (stop != 1) {
    speed = 200;
    // Serial.println("is working");
  }

  analogWrite(motor_1, speed); // DC 모터 제어
  digitalWrite(motor_2, LOW);  // DC 모터 정지
}

void moveServo(Servo servo, int angle, int delay_time) {
  servo.write(angle); // 목표 각도로 이동
  delay(delay_time); // 일정 시간 대기
  servo.write(180); // 180도로 이동
  delay(2000); // 2초 대기
  servo.write(0); // 초기 위치로 이동
}