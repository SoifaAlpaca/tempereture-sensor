#include <Arduino.h>

// NTC XXXX Thermisthor
// fotmula for temp in Kelvin

#define IN_NTC 4
#define IN_LM35 2
#define VDD 3.3

void setup()
{
  int NTC_read;
  int LM35_read;
  float NTC_AFEOut;
  float LM35_AFEOut;
  pinMode(IN_NTC, INPUT);  // Set the ADC pin as input
  pinMode(IN_LM35, INPUT); // Set the ADC pin as input

  Serial.begin(115200);
  // put your setup code here, to run once:
}

void loop()
{
  int NTC_read = analogRead(IN_NTC);
  int LM35_read = analogRead(IN_LM35);
  float NTC_AFEOut = NTC_read * (3.3 / 4095);   // 3.3V is the reference voltage of ESP32 and 4095 is the maximum value of ADC (2^12 - 1)
  float LM35_AFEOut = LM35_read * (3.3 / 4095); // 3.3V is the reference voltage of ESP32 and 4095 is the maximum value of ADC (2^12 - 1)
  Serial.print("\nNTC Voltage: ");
  Serial.println(NTC_AFEOut);
  Serial.print("\nLM35 Voltage: ");
  Serial.println(LM35_AFEOut);

  delay(1000);
}