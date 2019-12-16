
#include "Crc16.h"

Crc16 crc(true, true, 0x1021, 0xffff, 0x0000, 0x8000, 0xffff);

void sendByte(uint8_t data) {
  Serial1.write(data);
  crc.updateCrc(data);
  Serial.print(data, HEX); Serial.print(" ");
}

uint8_t readByte() {
  while (Serial1.available() == 0);
  uint8_t data = Serial1.read();
  crc.updateCrc(data);
  Serial.print(data, HEX); Serial.print(" ");
  return data;
}

void sendCommand(uint8_t command, uint8_t data[], uint8_t dataLength) {
  crc.clearCrc();
  Serial.print("Sending: ");
  // Send length
  Serial1.write(dataLength + 4);
  crc.updateCrc(dataLength + 4);
  Serial.print(dataLength + 4, HEX); Serial.print(" ");
  // Send address
  sendByte(0x00);
  // Send address
  sendByte(command);
  // Send data
  for (uint8_t i = 0; i < dataLength; i++) {
    sendByte(data[i]);
  }
  // Send CRC
  unsigned short crcValue = crc.getCrc();
  sendByte(crcValue & 0xff);
  sendByte(crcValue >> 8);
  Serial.println(" Done");
}

uint8_t readResponse(uint8_t buffer[]) {
  // Read length
  crc.clearCrc();
  Serial.print("Receiving: ");
  uint8_t length = readByte();
  // Read that much
  uint8_t data[length - 2];
  for (uint8_t i = 0; i < length - 2; i++) {
    data[i] = readByte();
  }
  // Check CRC
  unsigned short ourCrc = crc.getCrc();
  uint8_t lowCrc = readByte();
  uint8_t highCrc = readByte();
  unsigned short receivedCrc = ((highCrc) << 8) | lowCrc;
  if (receivedCrc != ourCrc) {
    Serial.print("// ");
    Serial.print(receivedCrc);
    Serial.print(" != ");
    Serial.print(ourCrc);
    printError(" CRC mismatch");
  }
  Serial.println(" Done");
  // Copy into the buffer
  for (uint8_t i = 0; i < length - 2; i++) {
    buffer[i] = data[i];
  }
  return length - 2;
}
