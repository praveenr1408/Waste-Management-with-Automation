#include <WiFi.h>
#include <FirebaseESP32.h>

// Set up your Firebase credentials
#define FIREBASE_HOST "iwms-v2-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "Um0c3b25OdguskNJF3OmT8XPbDXo4h2CDh6b5fzR"

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
  // Call the ultrasonic reading function (if needed)
  ultrasonic_reading();

  // Control LEDs based on Firebase values
  controlLEDs();
}

void ultrasonic_reading() {
  digitalWrite(trigPin, LOW);
  delay(1);
  digitalWrite(trigPin, HIGH);
  delay(1);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  int distance = duration * 0.0343 / 2;
  if (distance >= 1000) {
    distance = 0;
  }

  Serial.print("Distance: ");
  Serial.println(distance);

  // Send the distance value to Firebase
  Firebase.setInt(firebaseData1, "/Trash-Bin/Bin-1/", distance);
}

// Function to control LEDs based on Firebase values
void controlLEDs() {
  // Check Firebase for led1 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led-1")) {
    int led1State = firebaseData1.intData();
    digitalWrite(led1, led1State); // Turn led1 on/off
    Serial.print("led1: ");
    Serial.println(led1State ? "ON" : "OFF");
  }

  // Check Firebase for led2 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led-2")) {
    int led2State = firebaseData1.intData();
    digitalWrite(led2, led2State); // Turn led2 on/off
    Serial.print("led2: ");
    Serial.println(led2State ? "ON" : "OFF");
  }

  // Check Firebase for led3 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led-3")) {
    int led3State = firebaseData1.intData();
    digitalWrite(led3, led3State); // Turn led3 on/off
    Serial.print("led3: ");
    Serial.println(led3State ? "ON" : "OFF");
  }

  // Check Firebase for led4 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led-4")) {
    int led4State = firebaseData1.intData();
    digitalWrite(led4, led4State); // Turn led4 on/off
    Serial.print("led4: ");
    Serial.println(led4State ? "ON" : "OFF");
  }
}
