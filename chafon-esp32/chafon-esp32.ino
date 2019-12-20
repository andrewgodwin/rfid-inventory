
#include <SPI.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#include "passwords.h"

#define SERIAL_PASSTHROUGH false

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define BUTTON_GROUND 5
#define BUTTON_INPUT 19
#define PIN_RESET 26

#define STATUS_NO_TAG 0xfb

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
WiFiMulti WiFiMulti;

String tags[100];
uint8_t rssis[100];
uint8_t tagsPointer = 0;

void setup() {
  
  Serial.begin(57600);

  // Debugging mode
  if (SERIAL_PASSTHROUGH) {
    Serial1.begin(57600);
    for (;;) {
      if (Serial.available()) Serial1.write(Serial.read());
      if (Serial1.available()) Serial.write(Serial1.read());
    }
  }

  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Connect to the reader
  Serial1.begin(57600);

  // Connect to WiFi
  Serial.println("Connecting to WiFi...");
  printString("[WiFi...]");
  WiFi.mode(WIFI_AP_STA);
  WiFiMulti.addAP(ssid, password);
  while ((WiFiMulti.run() != WL_CONNECTED)) {
    Serial.print(".");
  }
  Serial.println(" connected");
  printString("[WiFi done]");

  pinMode(BUTTON_GROUND, OUTPUT);
  digitalWrite(BUTTON_GROUND, HIGH);

  // Set the power to max (30)
  uint8_t data[] = {30};
  sendCommand(0x2f, data, 1);
  uint8_t buffer[255];
  uint8_t bufferLength = readResponse(buffer);

  pinMode(BUTTON_INPUT, INPUT);
  printString("[Idle]");

}

void loop() {
  int sensorVal = digitalRead(BUTTON_INPUT);
  if (sensorVal == HIGH) {
    tagsPointer = 0;
    scan();
    sync();
    printString("[Idle]");
  }
  WiFiMulti.run();
}

// Runs a tag scan and returns EPCs
void scan() {
  // Do scan
  uint8_t status = 0x03;
  printString("[Scan...]");
  uint8_t data[] = {0x04, 0xff};
  sendCommand(0x01, data, 2);
  while (status == 0x03) {
    uint8_t buffer[255];
    uint8_t bufferLength = readResponse(buffer);
    Serial.println(" Got response");
    // Decode response
    status = buffer[2];
    // NO_TAG is the only "error" status code we allow
    if (status == STATUS_NO_TAG) return;
    if (status >= 0xf0) printError("RFID Error");
    if (status > 0x04) printError("Bad status");
    // Decode the tags
    uint8_t numTags = buffer[4];
    uint8_t bufferPointer = 5;
    for (uint8_t i = 0; i < numTags; i++) {
      uint8_t epcLength = buffer[bufferPointer++];
      String epc = String();
      for (uint8_t j = 0; j < epcLength; j++) {
        uint8_t epcByte = buffer[bufferPointer++];
        if (epcByte < 0x10) {
          epc.concat("0");
        }
        epc.concat(String(epcByte, HEX));
      }
      // Fetch RSSI
      uint8_t rssi = buffer[bufferPointer++];
      // Ensure the tag isn't already seen
      bool tagSeen = false;
      for (uint8_t j = 0; j < tagsPointer; j++) {
        if (epc.equals(tags[j])) {
          tagSeen = true;
        }
      }
      if (!tagSeen) {
        tags[tagsPointer] = epc;
        rssis[tagsPointer++] = rssi;
      }
    }
    // Verify things lined up
    if (bufferPointer != bufferLength) printError("Buffer mismatch");
  }
}

void sync() {
  // Send it
  WiFiClientSecure *client = new WiFiClientSecure;
  setWifiMessage("[HTTP -->]");
  if (client) {
    {
      // Scoping block for HTTPClient
      HTTPClient https;
  
      Serial.println("[HTTPS] Begin");
      if (https.begin(*client, url)) {  // HTTPS
        Serial.print("[HTTPS] POST ");
        Serial.println(url);
        // start connection and send HTTP header
        String body = String("{\"token\":\"") + token + String("\",\"tags\":[");
        for (uint8_t i = 0; i < tagsPointer; i++) {
          body.concat(String("\"epc:") + tags[i] + "/" + rssis[i] + "\"");
          if (i < tagsPointer - 1) {
            body.concat(",");
          }
        }
        body.concat("]}");
        Serial.println(body);
        int httpCode = https.POST(body.c_str());
  
        // httpCode will be negative on error
        if (httpCode > 0) {
          setWifiMessage("[HTTP OK]");
          // HTTP header has been sent and Server response header has been handled
          Serial.printf("[HTTPS] Status: %d\n", httpCode);
          // All good!
          if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
            String payload = https.getString();
            Serial.println(payload);
          } else {
            setWifiMessage("[HTTP BAD]");
            Serial.printf("[HTTPS] Bad status code: %s\n", https.errorToString(httpCode).c_str());
          }
        } else {
          setWifiMessage("[HTTP ERR]");
          Serial.printf("[HTTPS] Failed: %s\n", https.errorToString(httpCode).c_str());
        }
  
        https.end();
      } else {
        Serial.printf("[HTTPS] Unable to connect\n");
      }

      // End extra scoping block
    }
  
    delete client;
    delay(1000);
    printString("[Idle]");
  } else {
    Serial.println("Unable to create client");
  }
}
