const int emgPin = 34;
const unsigned long samplingIntervalUs = 1000;

unsigned long lastSampleUs = 0;

void setup() {
	Serial.begin(115200);
	analogReadResolution(12);
}

void loop() {
	unsigned long currentUs = micros();

	if (currentUs - lastSampleUs >= samplingIntervalUs) {
		lastSampleUs += samplingIntervalUs;

		int adcValue = analogRead(emgPin);

		Serial.println(adcValue);
	}
}