#include <Arduino.h>

#define IN_NTC 4
#define IN_LM35 2

void setup()
{
  pinMode(IN_NTC, INPUT);  // Set the ADC pin as input
  pinMode(IN_LM35, INPUT); // Set the ADC pin as input

  Serial.begin(115200);
  // put your setup code here, to run once:
}

void loop()
{
  int NTC_VALUE = analogRead(IN_NTC);
  int LM35_VALUE = analogRead(IN_LM35);
  float voltage_NTC = NTC_VALUE * (3.3 / 4095);   // 3.3V is the reference voltage of ESP32 and 4095 is the maximum value of ADC (2^12 - 1)
  float voltage_LM35 = LM35_VALUE * (3.3 / 4095); // 3.3V is the reference voltage of ESP32 and 4095 is the maximum value of ADC (2^12 - 1)
  Serial.print("\nNTC Voltage: ");
  Serial.println(voltage_NTC);
  Serial.print("\nLM35 Voltage: ");
  Serial.println(voltage_LM35);

  delay(1000);
}