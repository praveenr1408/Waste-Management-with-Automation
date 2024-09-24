#include <WiFi.h>
#include <FirebaseESP32.h>
#include <EEPROM.h>

// Set up your Firebase credentials
#define FIREBASE_HOST "my-app-3de95-default-rtdb.firebaseio.com"
#define FIREBASE_AUTH "YwOotL0dOX4oiqAPoWYnik5Rn8fAq8nmkjOLmPXA"

// Set up your WiFi credentials
const char* ssid = "Redmi";
const char* password = "876543210";

const int trigPin = 12;
const int echoPin = 14;
const int totalValue = 20;  // Total value for percentage calculation

const int led1 = 26;
const int led2 = 25;
const int led3 = 33;

// EEPROM size
#define EEPROM_SIZE 3 // Store 3 bytes for the 3 LEDs

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

  // Initialize EEPROM
  EEPROM.begin(EEPROM_SIZE);

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

  // Load saved LED states from EEPROM and apply
  int led1State = EEPROM.read(0);
  int led2State = EEPROM.read(1);
  int led3State = EEPROM.read(2);
  digitalWrite(led1, led1State);
  digitalWrite(led2, led2State);
  digitalWrite(led3, led3State);

  Serial.print("LED1 State from EEPROM: ");
  Serial.println(led1State);
  Serial.print("LED2 State from EEPROM: ");
  Serial.println(led2State);
  Serial.print("LED3 State from EEPROM: ");
  Serial.println(led3State);
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
  Firebase.setInt(firebaseData1, "/WasteBox/Height(CM)/", distance);
}

// Function to control LEDs based on Firebase values
void controlLEDs() {
  // Check Firebase for led1 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led1")) {
    int led1State = firebaseData1.intData();
    digitalWrite(led1, led1State); // Turn led1 on/off
    Serial.print("led1: ");
    Serial.println(led1State ? "ON" : "OFF");
    
    // Save led1 state to EEPROM
    EEPROM.write(0, led1State);
    EEPROM.commit();
  }

  // Check Firebase for led2 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led2")) {
    int led2State = firebaseData1.intData();
    digitalWrite(led2, led2State); // Turn led2 on/off
    Serial.print("led2: ");
    Serial.println(led2State ? "ON" : "OFF");
    
    // Save led2 state to EEPROM
    EEPROM.write(1, led2State);
    EEPROM.commit();
  }

  // Check Firebase for led3 status
  if (Firebase.getInt(firebaseData1, "/Automation/Led3")) {
    int led3State = firebaseData1.intData();
    digitalWrite(led3, led3State); // Turn led3 on/off
    Serial.print("led3: ");
    Serial.println(led3State ? "ON" : "OFF");
    
    // Save led3 state to EEPROM
    EEPROM.write(2, led3State);
    EEPROM.commit();
  }
}
