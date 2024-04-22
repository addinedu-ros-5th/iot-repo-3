#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above

MFRC522 rc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
MFRC522::StatusCode checkAuth(int index);
MFRC522::MIFARE_Key key;
MFRC522::StatusCode writeData(int index, byte* data, int length);
MFRC522::StatusCode readData(int index, byte* data);
MFRC522::StatusCode status;
void handleCommand(char* recv_buffer, int recv_size, int index);

void setup() {
  Serial.begin(115200);   // Initialize serial communications with the PC
  SPI.begin();      // Init SPI bus
  rc522.PCD_Init();   // Init MFRC522
  for (int i = 0; i < 6; i++)
  {
    key.keyByte[i] = 0xFF;
  }
}

void loop() {
  SPI.begin();      // Init SPI bus
  rc522.PCD_Init();   // Init MFRC522
  int recv_size = 0;
  char recv_buffer[16];
  while (Serial.available() > 0)
  {
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 16);
  }
  if (!rc522.PICC_IsNewCardPresent()) {
    return;
  }
  if (!rc522.PICC_ReadCardSerial()){
    return;
  }

  if (recv_size > 0)
  {
    char cmd[3];
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 2);
    if (strncmp(cmd, "Iw", 2) == 0)
    {
        int index = 52;
        handleCommand(recv_buffer, recv_size, index);
    }
    else if (strncmp(cmd, "Nw", 2) == 0)
    {
        int index = 53;
        handleCommand(recv_buffer, recv_size, index);
    }
    else if (strncmp(cmd, "nw", 2) == 0)
    {
        int index = 54;
        handleCommand(recv_buffer, recv_size, index);
    }
    else if (strncmp(cmd, "Re", 2) == 0)
    {
      byte data_id[16];
      memset(data_id, 0x00, sizeof(data_id));
      status = readData(52, data_id);
      Serial.print("Ir");
      Serial.write(data_id, 14);
      Serial.println("");
      byte data_name[16];
      memset(data_name, 0x00, sizeof(data_name));
      status = readData(53, data_name);
      Serial.print("Nr");
      Serial.write(data_name, 14);
      Serial.println("");
      byte data_num[16];
      memset(data_num, 0x00, sizeof(data_num));
      status = readData(54, data_num);
      Serial.print("nr");
      Serial.write(data_num, 14);
      Serial.println("");
    }
    else
    {
        Serial.println("unknown");
        status = MFRC522::STATUS_ERROR;
    }
  }
}


MFRC522::StatusCode checkAuth(int index)
{
  MFRC522::StatusCode status = 
    rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid));
  return status;
}
MFRC522::StatusCode writeData(int index, byte* data, int length)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }
  byte buffer[14];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, data, length);

  status = rc522.MIFARE_Write(index, buffer, 16);
  return status;
}
MFRC522::StatusCode readData(int index, byte* data)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    Serial.println(status);
    return status;
  }
  byte buffer[18];
  byte length = 18;
  status = rc522.MIFARE_Read(index, buffer, &length);
  if (status == MFRC522::STATUS_OK)
  {
    memcpy(data, buffer, 18);
  }
  return status;
}
void handleCommand(char* recv_buffer, int recv_size, int index)
{    
    byte data[16];
    memset(data, 0x00, sizeof(data));
    status = writeData(index, data, sizeof(data));
    memcpy(data, recv_buffer + 2, recv_size - 2);
    status = writeData(index, data, sizeof(data));
    Serial.write(data, sizeof(data));
}

    
