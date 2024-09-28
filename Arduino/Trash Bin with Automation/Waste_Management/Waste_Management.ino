#include <WiFi.h>
#include <FirebaseESP32.h>

// Set up your Firebase credentials
#define FIREBASE_HOST "iwms-v2-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "esdVYaMPGNYmO7lQxmIZXXpadQv6CHSZQzPt2JVe"

// Set up your WiFi credentials
const char* ssid = "Redmi";
const char* password = "876543210";

const int trigPin = 12;
const int echoPin = 14;
const int led1 = 26;
const int led2 = 25;
const int led3 = 33;
const int led4 = 32; // New LED

// Create Firebase objects
FirebaseData firebaseData1;
FirebaseConfig firebaseConfig;
FirebaseAuth firebaseAuth;

// Timer variables
unsigned long previousMillis = 0;
const long interval = 1000; // Read every 1 second

void setup() {
  Serial.begin(115200);
  pinMode(15, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  pinMode(led4, OUTPUT); // Set led4 as output

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
    digitalWrite(15, HIGH);
    delay(200);
    digitalWrite(15, LOW);
    delay(100);
  }
  Serial.println("Connected to WiFi");
  digitalWrite(15, HIGH);

  // Initialize Firebase
  firebaseConfig.host = FIREBASE_HOST;
  firebaseConfig.signer.tokens.legacy_token = FIREBASE_AUTH;
  Firebase.begin(&firebaseConfig, &firebaseAuth);
  Firebase.reconnectWiFi(true); // Ensure WiFi reconnects automatically
}

void loop() {
  unsigned long currentMillis = millis();

  // Call the ultrasonic reading function every second
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    ultrasonic_reading();
  }

  // Control LEDs based on Firebase values
  controlLEDs();
}

void ultrasonic_reading() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.0343 / 2;
  if (distance >= 1000) {
    distance = 0;
  }

  Serial.print("Distance: ");
  Serial.println(distance);

  // Send the distance value to Firebase only if changed
  static int lastDistance = 0;
  if (distance != lastDistance) {
    Firebase.setInt(firebaseData1, "/Trash-Bin/Bin-1/", distance);
    lastDistance = distance;
  }
}

// Function to control LEDs based on Firebase values
void controlLEDs() {
  // Control LEDs based on Firebase values with checks
  controlLED(led1, "/Automation/Led-1");
  controlLED(led2, "/Automation/Led-2");
  controlLED(led3, "/Automation/Led-3");
  controlLED(led4, "/Automation/Led-4");
}

void controlLED(int ledPin, const char* path) {
  if (Firebase.getInt(firebaseData1, path)) {
    int ledState = firebaseData1.intData();
    digitalWrite(ledPin, ledState); // Turn LED on/off
    Serial.print("LED at ");
    Serial.print(path);
    Serial.print(": ");
    Serial.println(ledState ? "ON" : "OFF");
  }
}
