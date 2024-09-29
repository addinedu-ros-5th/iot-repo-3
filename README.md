# iot-repo-3
IoT 프로젝트 3조 저장소.

### 목적 및 방향
물류센터에서의 입고부터 출고, 고객 배송까지의 과정을 시스템을 구현\
시스템 관리를 위한 GUI 제작, Log 기록을 통한 관리, 동작 구현과 유기적인 시스템

### 동작 예시
크레인
```cpp
 void rotateMotor(int toDegree_LR, int toDegree_UD, bool isRelative=false) {
        if (isRelative) {
            toDegree_LR = (toDegree_LR == NOMOV) ? NOMOV : leftRightMotor->read() + toDegree_LR;
            toDegree_UD = (toDegree_UD == NOMOV) ? NOMOV : upDownMotor->read() - toDegree_UD;
        }

        // one motor
        if (toDegree_UD == NOMOV) {
            moveWithSpeed(leftRightMotor, toDegree_LR);
        }
        // two motors
        else {
            moveWithSpeed(leftRightMotor, toDegree_LR, upDownMotor, toDegree_UD);
        }
    }
```
RFID 통신모듈
```cpp
void handleCommand(char* recv_buffer, int recv_size, int index)
{    
    byte data[16];
    memset(data, 0x00, sizeof(data));
    status = writeData(index, data, sizeof(data));
    memcpy(data, recv_buffer, recv_size);
    status = writeData(index, data, sizeof(data));
    Serial.write(data, sizeof(data));
    Serial.println("");
}
```

### 개발 환경
언어 : C++, Python, QML\
환경 : VScode, PyQt5, MySQL, Arduino\
Tool : Jira, Confluence, Git, Github, AWS, UML

### 팀 소개
㈜ADI로보로지스틱스솔루션, High efficiency, Safety First, ECO-friendly
|이름|역할|담당|
|:---:|:---|:---|
|[한영철](https://github.com/OProcessing)|통신, 팀장|시리얼 통신, RFID 정보 입출력|
|[곽민기](https://github.com/Ignimkk)|제어|Crane 동작 제어, 관리자 GUI, DB 연동|
|[김민경](https://github.com/miggyo)|설계|하드웨어 설계&제작, Conveyor 동작 제어, 분류기|
|[박서연](https://github.com/seoyean)|UI/UX|고객 GUI, DB 구축, DB 연동|

#### 기간
2024년 04월 17일 ~ 2024년 04월 25일
