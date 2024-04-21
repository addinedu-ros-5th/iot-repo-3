#include <SPI.h>
#include <MFRC522.h>

#define RST_PIN         9          // Configurable, see typical pin layout above
#define SS_PIN          10         // Configurable, see typical pin layout above

struct TagData
{
  unsigned int id;    //2
  char name[14];      //14
  long total;         //4
  long payment;       //4
  char addf[8];       //8
  char addt[16];       //16
};

MFRC522 rc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
MFRC522::StatusCode checkAuth(int index);
MFRC522::StatusCode writeTagData(int index, TagData data);
MFRC522::StatusCode readTagData(int index, TagData& data);
MFRC522::MIFARE_Key key;
MFRC522::StatusCode writeData(int index, byte* data, int length);
MFRC522::StatusCode readData(int index, byte* data);

void setup() {
  Serial.begin(9600);   // Initialize serial communications with the PC
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
  // String cmd = "";
  int recv_size = 0;
  char recv_buffer[16];
  while (Serial.available() > 0)
  {
    //cmd = Serial.readStringUntil('\n');
    recv_size = Serial.readBytesUntil('\n', recv_buffer, 16);
  }
  if (!rc522.PICC_IsNewCardPresent()) {
    return;
  }
  if (!rc522.PICC_ReadCardSerial()){
    return;
  }


  MFRC522::StatusCode status;
  TagData t_data, id_data;
  String s_temp;

  if (recv_size > 0)
  {
    char cmd[2];
    memset(cmd, 0x00, sizeof(cmd));
    memcpy(cmd, recv_buffer, 2);
    
    if (strncmp(cmd, "Iw", 2) == 0)
    {
        Serial.println("ar : write");
        byte id[14];
        memset(id, 0x00, sizeof(id));
        status = writeData(52, id, sizeof(id));
        Serial.write(id, sizeof(id));
        memcpy(id, recv_buffer + 2, sizeof(id));
        Serial.write(id, sizeof(id));
        status = writeData(52, id, sizeof(id));
        /*
        t_data.id = 7885;
        s_temp = "kim";
        s_temp.toCharArray(t_data.name, s_temp.length() + 1);
        t_data.total = 5448;
        t_data.payment = 7888;
        s_temp = "seocho";
        s_temp.toCharArray(t_data.addf, s_temp.length() + 1);
        s_temp = "gasan";
        s_temp.toCharArray(t_data.addt, s_temp.length() + 1);
        status = writeTagData(56, t_data);
        */
        //rc522.PICC_DumpToSerial(&(rc522.uid));
    }
    else if (strncmp(cmd, "Ir", 2) == 0)
    {
        Serial.println("ar : read");
        byte id[16];
        memset(id, 0x00, sizeof(id));
        status = readData(52, id);
        Serial.write(id, sizeof(id));
        Serial.println("");
        /*
        Serial.println("");
        status = readTagData(56, t_data);
        Serial.print("ID : ");  Serial.println(t_data.id);
        Serial.println(String(t_data.name));
        Serial.println(t_data.total);
        Serial.println(t_data.payment);
        Serial.println(String(t_data.addf));
        Serial.println(String(t_data.addt));
        */
    }
    else 
    {
        Serial.println("unknown");
        status = MFRC522::STATUS_ERROR;
    }
  }
  
//  if (status == MFRC522::STATUS_OK)
//  {
//    Serial.println("success!");
//  }
}


MFRC522::StatusCode checkAuth(int index)
{
  MFRC522::StatusCode status = 
    rc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, index, &key, &(rc522.uid));
  return status;
}
MFRC522::StatusCode writeTagData(int index, TagData data)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }
  byte buffer[16];
  memset(buffer, 0x00, sizeof(buffer));
  memcpy(buffer, &data, sizeof(data));
  
  for (int i = 0; i < 1; i++)
  {
    status = rc522.MIFARE_Write(index + i, buffer + (i*16), 16);
  }

  return status;
}
MFRC522::StatusCode readTagData(int index, TagData& data)
{
  MFRC522::StatusCode status = checkAuth(index);
  if (status != MFRC522::STATUS_OK)
  {
    return status;
  }
  byte buffer[18];
  byte length = 18;

  for (int i = 0; i < 1; i++)
  {
    status = rc522.MIFARE_Read(index + i, buffer + (i*16), &length);
  }
  memcpy(&data, buffer, sizeof(data));
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
    return status;
  }
  byte buffer[16];
  byte length = 16;
  status = rc522.MIFARE_Read(index, buffer, &length);
  if (status == MFRC522::STATUS_OK)
  {
    memcpy(data, buffer, 16);
  }
  return status;
}
