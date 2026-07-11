const int analogPin = 34;

const unsigned long samplingIntervalUs = 1000;
unsigned long previousSampleTime = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);

  delay(1000);

  Serial.println("timestamp_us,adc_value");
}

void loop() {
  unsigned long currentTime = micros();

  if (currentTime - previousSampleTime >= samplingIntervalUs) {
    previousSampleTime = currentTime;

    int adcValue = analogRead(analogPin);

    Serial.print(currentTime);
    Serial.print(",");
    Serial.println(adcValue);
  }
}