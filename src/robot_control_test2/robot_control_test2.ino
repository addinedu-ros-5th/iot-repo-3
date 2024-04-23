#include <Servo.h>
#include <MFRC522.h>
#include <MFRC522Extended.h>
#include <deprecated.h>
#include <require_cpp11.h>
#include <SPI.h>
#include <List.hpp>
#include <SoftwareSerial.h>

#define RST_PIN         9
#define SS_PIN          10

#define MOTOR_PIN_LEFT_RIGHT    (2)   // D6 pin
#define MOTOR_PIN_UP_DOWN       (3)  // D10 pin
#define MOTOR_PIN_TONGS         (4)  // D11 pin

#define DEGREE_MIN    (0)
#define DEGREE_MAX    (180)

#define DEFAULT_DEGREE_LEFT_RIGHT    (0) //55
#define DEFAULT_DEGREE_UP_DOWN       (140) //70
#define DEFAULT_DEGREE_TONGS         (120) //80
#define NOMOV    (255)

SoftwareSerial A_Serial(7,8);
// const int motor_1 = 5;
// const int motor_2 = 6;
// const int motor_flag = 7;

const int stop_flag= 5;
MFRC522 mfrc522(SS_PIN, RST_PIN);

// int speed = 0;// 속도값
// int stop =0; //멈춤 flag
// int count =0;
// int robot_arm = 0;
bool isInitialPosition = true;


class Motor {
  private:
    class SpeedControlParam {
      public:
        int fromDegree;
        int toDegree;
        int currDegree;
        int delta;
        int momentaryDelay;

        SpeedControlParam(int fromDegree, int toDegree) {
            if (toDegree == NOMOV || fromDegree == toDegree) {
              this->currDegree = NOMOV;
              this->toDegree = NOMOV;
              return;
            }

            this->fromDegree = fromDegree;
            this->toDegree = toDegree;
            this->delta = (fromDegree < toDegree) ? 1 : -1; 
            this->currDegree = fromDegree + this->delta;
            this->momentaryDelay = -1;
            
            checkLimit(&this->toDegree);
        }

        void checkLimit(int *degree) {
            if (*degree > DEGREE_MAX) {
                *degree = DEGREE_MAX;
            }
            else if (*degree < DEGREE_MIN) {
                *degree = DEGREE_MIN;
            }
        }
    };
  
  private:
    static Servo *leftRightMotor;
    static Servo *upDownMotor;
    static Servo *tongsMotor;  

    void initialize() {
        leftRightMotor = new Servo();
        upDownMotor = new Servo();
        tongsMotor = new Servo();
        
        leftRightMotor->attach(MOTOR_PIN_LEFT_RIGHT);
        upDownMotor->attach(MOTOR_PIN_UP_DOWN);
        tongsMotor->attach(MOTOR_PIN_TONGS);         
    }



    int getMomentaryDelayByGauss(int fromDegree, int toDegree, int currDegree) {
        if (fromDegree == toDegree) {
          return 0;
        }
        if (fromDegree < toDegree) {
          currDegree = (currDegree > toDegree) ? toDegree : currDegree;
          currDegree = (currDegree < fromDegree) ? fromDegree : currDegree;
        }
        else {
          currDegree = (currDegree > fromDegree) ? fromDegree : currDegree;
          currDegree = (currDegree < toDegree) ? toDegree : currDegree;
        }
      
        float x = ((float)currDegree - fromDegree) / (toDegree - fromDegree);  // Min-Max Normalize

        const float MOMENTARY_DELAY_MS_MAX = 20.0;
        const float MOMENTARY_DELAY_MS_MIN = 5.0;
        const float MOMENTARY_DELAY_MS_DIFF = MOMENTARY_DELAY_MS_MAX - MOMENTARY_DELAY_MS_MIN;
        const float ROTATE_DEGREE_MAX = 180.0;
        const float B = 0.5;
        const float C = 0.235;
        
        float y = MOMENTARY_DELAY_MS_MAX - MOMENTARY_DELAY_MS_DIFF * exp(- ((x - B) * (x - B)) / (C * C)) * (abs(fromDegree-toDegree) / ROTATE_DEGREE_MAX);
        
        return round(y);
    }    

    void moveWithSpeed(Servo *servo, int toDegree, Servo *servo2 = NULL, int toDegree2 = NOMOV, Servo *servo3 = NULL, int toDegree3 = NOMOV) {
        SpeedControlParam sv(servo->read(), toDegree);
        SpeedControlParam sv2(servo2->read(), toDegree2);
        SpeedControlParam sv3(servo3->read(), toDegree3);

        for (int ms = 0; ms < 999999; ms++) {
            if (sv.currDegree != sv.toDegree && sv.momentaryDelay < 0) {
                servo->write(sv.currDegree);
                sv.momentaryDelay = getMomentaryDelayByGauss(sv.fromDegree, sv.toDegree, sv.currDegree);
                sv.currDegree += sv.delta;
            }
            if (sv2.currDegree != sv2.toDegree && sv2.momentaryDelay < 0) {
                servo2->write(sv2.currDegree);
                sv2.momentaryDelay = getMomentaryDelayByGauss(sv2.fromDegree, sv2.toDegree, sv2.currDegree);
                sv2.currDegree += sv2.delta;
            }
            if (sv3.currDegree != sv3.toDegree && sv3.momentaryDelay < 0) {
                servo3->write(sv3.currDegree);
                sv3.momentaryDelay = getMomentaryDelayByGauss(sv3.fromDegree, sv3.toDegree, sv3.currDegree);
                sv3.currDegree += sv3.delta;
            }

            if (sv.currDegree == sv.toDegree && sv2.currDegree == sv2.toDegree && sv3.currDegree == sv3.toDegree) {
                break;            
            }

            delay(1);
            sv.momentaryDelay = (sv.momentaryDelay >= 0) ? sv.momentaryDelay-1 : sv.momentaryDelay;
            sv2.momentaryDelay = (sv2.momentaryDelay >= 0) ? sv2.momentaryDelay-1 : sv2.momentaryDelay;
            sv3.momentaryDelay = (sv3.momentaryDelay >= 0) ? sv3.momentaryDelay-1 : sv3.momentaryDelay;
        }
    }
    
  protected:
    Motor() {
        if (leftRightMotor == NULL) {
            initialize();
        }
    }

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
    
    void rotateTongs(int toDegree) {
        moveWithSpeed(tongsMotor, toDegree);
    }
    void rotateTongsCloseByCurrPos(int toDegree) {
        moveWithSpeed(tongsMotor, tongsMotor->read()+toDegree);
    }
    void rotateTongsOpenByCurrPos(int toDegree) {
        moveWithSpeed(tongsMotor, tongsMotor->read()-toDegree);
    }
};
Servo* Motor::leftRightMotor = NULL;
Servo* Motor::upDownMotor = NULL;
Servo* Motor::tongsMotor = NULL;  


class GrabMotion : public Motor {
  protected:
    GrabMotion() {
    
    }

  public:
    virtual void grab() = 0;
};


class Robot {
  private:
    static Robot *_instance;
    GrabMotion *grabMotion;
    Robot() {
      grabMotion = NULL; 
    }

  public:
    static Robot* getInstance() {
        if (_instance == NULL) {
            _instance = new Robot();
        }
        return _instance;
    }
    
    void setGrabMotion(GrabMotion *grabMotion) {
        if (this->grabMotion != NULL) {
            delete this->grabMotion;
        }
        this->grabMotion = grabMotion;
    }

    void doGrab() {
        grabMotion->grab();
    }

    void setGrabMotionAndDo(GrabMotion *grabMotion) {
        setGrabMotion(grabMotion);
        doGrab();
    }
};
Robot* Robot::_instance = NULL;


class DefaultPosition : public GrabMotion {
  public:
    void grab() override {
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN);
        rotateTongs(DEFAULT_DEGREE_TONGS);  
    }
};
// 출고
class F1_1_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 80, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(110, 80, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(110, 60, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(110, 80, false); // 들어 올리고
        delay(400);
        rotateMotor(140, 80, false); // 공통 위치로 이동
        delay(1000);
        rotateMotor(140, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false); // 목표지점 이동
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F1_2_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 80, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(120, 80, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(120, 60, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(120, 80, false); // 들어 올리고
        delay(400);
        rotateMotor(140, 80, false); // 공통 위치로 이동
        delay(1000);
        rotateMotor(140, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false); // 목표지점 이동
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F1_3_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);                                     
        rotateMotor(140, 80, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(170, 80, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(170, 60, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(170, 80, false); // 들어 올리고
        delay(400);
        rotateMotor(140, 80, false); // 공통 위치로 이동
        delay(1000);
        rotateMotor(140, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false); // 목표지점 이동
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F1_4_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 80, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(170, 80, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(170, 60, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(170, 80, false); // 들어 올리고
        delay(400);
        rotateMotor(140, 80, false); // 공통 위치로 이동
        delay(1000);
        rotateMotor(140, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 140, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false); // 목표지점 이동
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_1_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 130, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(100, 130, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(100, 110, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(100, 130, false); // 들어 올리고
        delay(400);
        // rotateMotor(140, 140, false); // 공통 위치로 이동
        // delay(1000);
        rotateMotor(10, 90, false); // 목표지점 이동
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_2_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 130, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(120, 130, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(120, 110, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(120, 130, false); // 들어 올리고
        delay(400);
        // rotateMotor(140, 140, false); // 공통 위치로 이동
        // delay(1000);
        rotateMotor(10, 130, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false);
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_3_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 130, false); // 층 선택 1층(110) 
        delay(1000);
        rotateMotor(150, 130, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(150, 110, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(150, 130, false); // 들어 올리고
        delay(400);
        // rotateMotor(140, 140, false); // 공통 위치로 이동
        // delay(1000);
        rotateMotor(10, 130, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false);
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_4_out : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(140, 140, false); // 공통위치로 이동 (좌우, 위아래, 절대좌표)
        delay(1000);
        rotateMotor(140, 130, false); // 층 선택 2층(110) 
        delay(1000);
        rotateMotor(170, 130, false); // 구역 이동 (오른쪽 100) 왼쪽(140)
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(170, 110, false); // 물건을 집기 위해서 하강
        
        delay(1000);
        rotateTongsCloseByCurrPos(40);// 그리퍼 닫고
        delay(1000);
        rotateMotor(170, 130, false); // 들어 올리고
        delay(400);
        // rotateMotor(140, 140, false); // 공통 위치로 이동
        // delay(1000);
        rotateMotor(10, 130, false); // 목표지점 이동
        delay(1000);
        rotateMotor(10, 90, false);
        delay(1000);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열어서 물건 놓기
        delay(1000);
        rotateMotor(10,110, false);  // 머리들고 
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫아서 원상 복구
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

//입고
class F1_1_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(50); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(50); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 140, false); //2층 입구 도착
        delay(500);
        rotateMotor(140, 140, false); // 2층 공통입구 도착
        delay(500);
        rotateMotor(140, 80, false); // 1층으로 이동
        delay(500);
        rotateMotor(100, 80, false);
        delay(500);
        rotateMotor(100, 60, false);
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(100, 80, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(140, 80, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F1_2_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(50); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(50); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 140, false); //2층 입구 도착
        delay(500);
        rotateMotor(140, 140, false); // 2층 공통입구 도착
        delay(500);
        rotateMotor(140, 80, false); // 1층으로 이동
        delay(500);
        rotateMotor(120, 80, false); //1-2 구역으로 이동
        delay(500);
        rotateMotor(120, 60, false); // 하강
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(120, 80, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(140, 80, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F1_3_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(40); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 140, false); //2층 입구 도착
        delay(500);
        rotateMotor(140, 140, false); // 2층 공통입구 도착
        delay(500);
        rotateMotor(140, 80, false); // 1층으로 이동
        delay(500);
        rotateMotor(170, 80, false);
        delay(500);
        rotateMotor(170, 60, false);
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(170, 80, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(140, 80, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_1_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(40); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 130, false); //2층 입구 도착
        delay(500);
        rotateMotor(100, 130, false); // 2-1지점 도착
        delay(500);
        rotateMotor(100, 110, false); // 놓기 위해 하강
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(100, 130, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(80, 130, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_2_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(40); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 130, false); //2층 입구 도착
        delay(500);
        rotateMotor(120, 130, false); // 2-2지점 도착
        delay(500);
        rotateMotor(120, 110, false); // 놓기 위해 하강
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(100, 130, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(80, 130, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

class F2_3_stock : public GrabMotion {
  public:
    void grab() override {        
        rotateMotor(0, 110, false); // 목표지점 이동
        delay(1000);
        rotateMotor(0, 95, false); // 하강
        delay(1000);
        rotateTongsOpenByCurrPos(40); // 그리퍼 열고
        delay(200);
        rotateMotor(0, 70, false); // 하강
        delay(200);
        rotateTongsCloseByCurrPos(40); // 그리퍼 닫기
        delay(200);
        rotateMotor(0, 90, false); // 상승
        delay(500);
        rotateMotor(80, 130, false); //2층 입구 도착
        delay(500);
        rotateMotor(160, 130, false); // 2-3지점 도착
        delay(500);
        rotateMotor(160, 110, false); // 놓기 위해 하강
        delay(500);
        rotateTongsOpenByCurrPos(30); // 그리퍼 열고
        delay(500);
        rotateMotor(160, 130, false); // 상승
        delay(500);
        rotateTongsCloseByCurrPos(30); // 그리퍼 닫고
        delay(500);
        rotateMotor(80, 130, false); // 1층 입구로 이동
        delay(500);
        rotateMotor(140, 140, false); // 공통 위치로 이동(2층)
        delay(500);
        rotateMotor(10, 140, false); // 빠져나가기
        delay(500);
        rotateMotor(DEFAULT_DEGREE_LEFT_RIGHT, DEFAULT_DEGREE_UP_DOWN); // 초기 
      }
};

void setup() {
    Serial.begin(9600);
    A_Serial.begin(9600);
    while (!Serial);
    // Serial.println("[i] Start !");
    // pinMode(motor_1, OUTPUT);
    // pinMode(motor_2, OUTPUT);
    // pinMode(motor_flag, INPUT);
    pinMode(stop_flag, OUTPUT);
    SPI.begin();
    mfrc522.PCD_Init(); // Init MFRC522
    // Serial.println(F("Scan PICC to see UID, SAK, type, and data blocks..."));
    Robot *robot = Robot::getInstance();
    robot->setGrabMotionAndDo(new DefaultPosition());
    isInitialPosition = true;
    delay(2000);

    // Serial.println("[i] setup() completed.");
}
bool input_flag = false;
bool arm_flag = false;
bool isTaskCompleted = false;
String command;
bool out_flag = false;
void loop()
{
  if (mfrc522.PICC_IsNewCardPresent() && out_flag == false) {
    isTaskCompleted = false;
    if (input_flag == true) //출고
    {
      // digitalWrite(stop_flag, HIGH);
      // delay(100);
      // digitalWrite(stop_flag, LOW);
      // A_Serial.write("4");
      Serial.println("출고");
      command = "1";
      Serial.println(command);
      arm_flag = true;
      input_flag = false;
      Serial.println("인식 완료");
      delay(1000);
      
    }
    else  //입고
    {
      A_Serial.write('4');
      command = "a";
      Serial.println("입고");
      Serial.println(command);
      
      arm_flag = true;
      input_flag = true;
      Serial.println("인식 완료");
      delay(1000);
    }
    
    // Serial.println("stopped");
  }

  Robot *robot = Robot::getInstance();

  if (!isInitialPosition)
  {
    robot->setGrabMotionAndDo(new DefaultPosition());
    isInitialPosition = true;
  }

  // 2. 원하는 동작 수행
  if (arm_flag == true)
  {
    // Serial.println("in");
    // char command = Serial.read();
    if (command == "1" && !isTaskCompleted && out_flag == false)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      // robot->setGrabMotionAndDo(new F1_1_out());
      // A_Serial.write("4");
      arm_flag = false;
      out_flag = true;
      isTaskCompleted = true; 
      Serial.println("Task completed"); 
    }
    else if (command == "2" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F1_2_out());
      isTaskCompleted = true;
      Serial.println("Task completed"); 
    }
    else if (command == "3" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F1_3_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "4" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F1_4_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "5" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_1_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "6" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_2_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "7" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_3_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "8" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_4_out());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == "a" && !isTaskCompleted)
    {
      // int serial_input = 1;
      // digitalWrite(stop_flag, HIGH);
      // delay(100);
      // digitalWrite(stop_flag, LOW);
      // robot->setGrabMotionAndDo(new F1_1_stock());
      isTaskCompleted = true;
      arm_flag = false;
      Serial.println("Task completed"); 
    }
    else if (command == "b" && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F1_2_stock());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == 'c' && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F1_3_stock());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    } 
    else if (command == 'd' && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_1_stock());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == 'e' && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_2_stock());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
    else if (command == 'f' && !isTaskCompleted)
    {
      digitalWrite(stop_flag, HIGH);
      delay(100);
      digitalWrite(stop_flag, LOW);
      robot->setGrabMotionAndDo(new F2_3_stock());
      isTaskCompleted = true;
      // Serial.println("Task completed"); 
    }
  }

  else if (!isInitialPosition)
  {
    robot->setGrabMotionAndDo(new DefaultPosition());
    isInitialPosition = true;
  } 

  if (out_flag == true)
  {
    if (mfrc522.PICC_IsNewCardPresent())
    {
      A_Serial.write('3');
      Serial.println("배송중");
      delay(2000);
      out_flag = false;
    }
  }


}
