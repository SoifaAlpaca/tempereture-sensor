#include <Arduino.h>
#include <lut.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// NTC XXXX Thermisthor
// fotmula for temp in Kelvin
// T = 1/ (A + Bln(R_NTC) + C(ln(R_NTC))^3)

// ESP ADC non-linear issue
#define ONE_WIRE_BUS 5
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

#define IN_NTC 4
#define IN_LM35 2
#define VREF 3.3              // 3.3V is the reference voltage of ESP32
#define ADC_RES 4095          // maximum value of ADC is 4095 (2^12 - 1)
#define A 0.001303923920      // 0.0012
#define B 0.0002143913551     // 0.00021
#define C 0.00000009659997359 // 0.00000013
#define R1 8200
#define RF 10000
#define R2 12000
#define R3 8000
#define VOFFSET (VREF * (RF / (double)R1))                       // 3.53
#define GAINNTC (1 + RF * ((1 / (double)R1) + (1 / (double)R2))) // 2.92 //
#define GAINLM 7.8
#define T0 273.15
long int delaymicros = 50; // ms
long int previousMicros = 0;
int contador = 0;
#define SAMPLES 1000
double NTC_read = 0;
double LM35_read = 0;
// double ntc_AFEOut = 0;
// double lm35_AFEOut = 0;
double Tntc = 0;
double Tlm35 = 0;
#define BETA 3799.42
float T0K = 298.15;
#define R0 10000

double calculateTntc(double ntc_AFEOut)
{
  // Serial.print("VOFFSET: ");
  // Serial.println(VOFFSET);
  // Serial.print("\nGAINNCT: ");
  // Serial.println(GAINNTC);
  double Vntc = (ntc_AFEOut + VOFFSET) / GAINNTC;
  // Serial.print("\nVntc: ");
  // Serial.println(Vntc);
  double Rntc = (Vntc * R3) / (VREF - Vntc);
  // Serial.print("\nRntc: ");
  // Serial.println(Rntc);
  // double TntcK = BETA / (BETA / T0K + log(Rntc / R0));
  double TntcK = 1 / (A + B * log(Rntc) + C * pow(log(Rntc), 3));
  // Serial.print("\nTntck: ");
  // Serial.println(TntcK);
  double Tntc = TntcK - T0;
  // Serial.print("\nTntc: ");
  // Serial.println(Tntc);
  return Tntc;
}

double calculateTlm35(double lm35_AFEOut)
{
  double Vlm35 = lm35_AFEOut / GAINLM;
  double Tlm35 = Vlm35 * 100;
  return Tlm35;
}

void setup()
{

  pinMode(IN_NTC, INPUT);  // Set the ADC pin as input
  pinMode(IN_LM35, INPUT); // Set the ADC pin as input

  // Start up the library
  sensors.begin();

  Serial.begin(115200);
  // put your setup code here, to run once:
}

void loop()
{

  if (micros() - previousMicros >= delaymicros)
  { // obtain the input analog value from the ADC every 10ms
    // obtain the input analog value from the ADC

    // Serial.println((double)analogRead(IN_NTC) * VREF / (double)ADC_RES);
    // Serial.println((double)analogRead(IN_LM35) * VREF / (double)ADC_RES);
    NTC_read += (double)analogRead(IN_NTC) * VREF / (double)ADC_RES;
    LM35_read += (double)analogRead(IN_LM35) * VREF / (double)ADC_RES;

    //  NTC_read = ADC_LUT[(int)analogRead(IN_NTC)];
    // NTC_read = ADC_LUT[(int)NTC_read];

    // ntc_AFEOut += NTC_read * (VREF / ADC_RES);
    // lm35_AFEOut += LM35_read * (VREF / ADC_RES);

    // non linear correction for ESP32 ADC
    contador++;

    if (contador == SAMPLES)
    {
      // Serial.println(NTC_read);
      // Serial.println(LM35_read);

      NTC_read = NTC_read / SAMPLES;
      LM35_read = LM35_read / SAMPLES;

      // Serial.print("NTC: ");
      // Serial.print(NTC_read);
      // Serial.print(" LM35: ");
      // Serial.println(LM35_read);

      Tntc = calculateTntc(NTC_read);
      Tlm35 = calculateTlm35(LM35_read);

      sensors.requestTemperatures(); // Send the command to get temperatures
      float tempC = sensors.getTempCByIndex(0);

      Serial.print(Tntc);
      Serial.print(",");
      Serial.print(Tlm35);
      Serial.print(",");
      Serial.println(tempC);

      contador = 0;
      NTC_read = 0;
      LM35_read = 0;
    }
    previousMicros = micros(); // save the current time
  }
}
