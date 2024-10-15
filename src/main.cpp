#include <Arduino.h>
// #include <lut.h> // LUT for non-linear correction of ESP32 ADC
#include <OneWire.h>
#include <DallasTemperature.h>

// NTC Thermisthor
// formula for temp in Kelvin
// T = 1/ (A + Bln(R_NTC) + C(ln(R_NTC))^3)

#define IN_NTC 4
#define IN_LM35 2
#define ONE_WIRE_BUS 5
#define RELAY 18

OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

#define VREF 3.3     // 3.3V is the reference voltage of ESP32
#define ADC_RES 4096 // maximum value of ADC is 4095 (2^12 - 1)
#define R1 9100
#define RF 10000
#define R2 12000
#define R3 8200
#define VOFFSET (VREF * (RF / (double)R1))                       // 3.53
#define GAINNTC (1 + RF * ((1 / (double)R1) + (1 / (double)R2))) // 2.92 //
#define GAINLM 7.5                                               // 7.8 valor real                                               // ajustado no digital era 7.8 no dimensionamento
#define T0 273.15
#define SAMPLES 6000
long int delaymicros = 10; // ms
long int previousMicros = 0;
int contador = 0;
double NTC_read = 0;
double LM35_read = 0;
double tempC = 0;
double Tntc = 0;
double Tlm35 = 0;
// NTC Models
#define BETA 3965
#define R0 10000
#define T0K 298.15
#define A 0.001384522703     // 0.0012
#define B 0.0001924505126    // 0.00021
#define C 0.0000002520860441 // 0.00000013

String relay_status = "RELAY_OFF";
String relay_mode = "AUTIMATIC";
// Command strings
String command = "RELAY_OFF";

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

  double TLin = Rntc * -0.001994945011 + 47.25190165;
  // Serial.print("\nTLin: ");
  // Serial.println(TLin);

  // Serial.print("\nRntc: ");
  // Serial.println(Rntc);
  // double TntcK = BETA / (BETA / (double)T0K + log(Rntc / R0));
  double TntcK = 1 / (A + B * log(Rntc) + C * pow(log(Rntc), 3));
  //    Serial.print("\nTntck: ");
  //    Serial.println(TntcK);
  // double TntcK = (Vntc - 1.56) / -0.005;
  double Tntc = TntcK - T0;

  // Serial.print("\nTntc: ");
  // Serial.println(Tntc);
  // Tntc = ((ntc_AFEOut + 3.6264) / 2.932 + 0.0350474) / -12.2884;
  return TLin;
}

double calculateTlm35(double lm35_AFEOut)
{
  double Vlm35 = lm35_AFEOut / GAINLM;
  // Serial.print("\nVlm35: ");
  // Serial.println(Vlm35);
  double Tlm35 = Vlm35 * 100;
  return Tlm35;
}

void relayTempControl(double tempC)
{
  if (tempC >= 25.00 && tempC < 40.00)
  {

    if (relay_status == "RELAY_OFF")
    {
      digitalWrite(RELAY, HIGH);
      // Serial.println("Relay is ON");
      relay_status = "RELAY_ON";
      delay(50);
    }
    else
    {
      // Serial.println("Relay is ON");
    }
  }
  else
  {
    if (relay_status == "RELAY_ON")
    {
      digitalWrite(RELAY, LOW);
      // Serial.println("Relay is OFF");
      relay_status = "RELAY_OFF";
      delay(50);
    }
    else
    {
      // Serial.println("Relay is OFF");
    }
  }
}

void relayGUIControl()
{
  if (command == "AUTOMATIC")
  {
    relayTempControl(tempC);
    // Serial.println("Automatic mode");
    relay_mode = "AUTOMATIC";
  }
  if (command == "MANUAL")
  {
    relay_mode = "MANUAL";
    // Serial.println("Manual mode");
  }
  if (command == "RELAY_ON")
  {
    // Turn the relay ON
    digitalWrite(RELAY, HIGH);

    //  Serial.println("Relay is ON");
    relay_status = "RELAY_ON";
    delay(1000);
  }
  if (command == "RELAY_OFF")
  {
    // Turn the relay OFF
    digitalWrite(RELAY, LOW);
    delay(50);
    //  Serial.println("Relay is OFF");
    relay_status = "RELAY_OFF";
    delay(1000);
  }
  // Clear the command string for the next command
  command = "";
}

void setup()
{

  pinMode(IN_NTC, INPUT);  // Set the ADC pin as input
  pinMode(IN_LM35, INPUT); // Set the ADC pin as input
  pinMode(ONE_WIRE_BUS, INPUT);
  pinMode(RELAY, OUTPUT);
  digitalWrite(RELAY, LOW);
  digitalWrite(ONE_WIRE_BUS, LOW);

  // Start up the library
  sensors.begin();
  relay_status = "RELAY_OFF";
  command = "RELAY_OFF";
  relay_mode = "MANUAL";
  Serial.begin(115200);
  // put your setup code here, to run once:
}

void loop()
{

  if (micros() - previousMicros >= delaymicros) // obtain the input analog value from the ADC every 10ms
  {
    // Serial.println((double)analogRead(IN_NTC) * VREF / (double)ADC_RES);
    // Serial.println((double)analogRead(IN_LM35) * VREF / (double)ADC_RES);
    NTC_read += (double)analogRead(IN_NTC) * VREF / (double)ADC_RES;
    LM35_read += (double)analogRead(IN_LM35) * VREF / (double)ADC_RES;

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
      tempC = sensors.getTempCByIndex(0);

      Serial.print(Tntc);
      Serial.print(",");
      Serial.print(Tlm35);
      Serial.print(",");
      Serial.println(tempC);

      // relayTempControl(tempC);

      contador = 0;
      NTC_read = 0;
      LM35_read = 0;
    }
    previousMicros = micros(); // save the current time
  }
  // Check if data is available on the serial port
  if (Serial.available() > 0)
  {
    // Read the incoming byte
    char incomingChar = Serial.read();

    // Append the received character to the command string
    if (incomingChar != '\n')
    {
      command += incomingChar;
    }
    else
    {
      // If the command is complete, process it
      relayGUIControl();
    }
  }
}
