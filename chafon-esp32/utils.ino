char * mainMessage;
char * wifiMessage;


void printString(char const * message) {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println(message);
  display.setCursor(100,30);
  display.setTextSize(2);
  display.println(tagsPointer);
  display.display();
}

void setWifiMessage(char const * message) {
  //strcpy(wifiMessage, message);
  printString(message);
}

void printError(char const * message) {
  printString(message);
  Serial.println(message);
  delay(3000);
  
  pinMode(PIN_RESET, OUTPUT);
  digitalWrite(PIN_RESET, LOW);
}
