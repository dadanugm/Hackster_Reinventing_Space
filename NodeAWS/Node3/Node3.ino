#include "BLEDevice.h"
#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include "secrets_tokyo.h"

#define MQTT_ID "NODE3"
// The MQTT topics that this device should publish/subscribe
#define AWS_IOT_PUBLISH_TOPIC   "ESP32/pub"
#define AWS_IOT_SUBSCRIBE_TOPIC "ESP32/sub"

MQTTClient client = MQTTClient(256);
WiFiClientSecure net = WiFiClientSecure();
BLEScan* pBLEScan;

void connectAws(void);
void publishMessage(void);
void clean_addr(void);

StaticJsonDocument<200> doc;
char jsonBuffer[512];
char ble_addr[64];
char prev_addr[64];
std::string str;

void messageHandler(String &topic, String &payload) {
  Serial.println("incoming: " + topic + " - " + payload);

//  StaticJsonDocument<200> doc;
//  deserializeJson(doc, payload);
//  const char* message = doc["message"];
}

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    Serial.print("BLE Advertised Device found: ");
    Serial.print(advertisedDevice.getAddress().toString().c_str());
    //Serial.println(advertisedDevice.toString().c_str());
    Serial.print(" RSSI: ");
    Serial.println(advertisedDevice.getRSSI());
    Serial.print(" TX Power: ");
    Serial.println(advertisedDevice.getTXPower());
    // copy prev string
    advertisedDevice.getAddress().toString().copy(ble_addr,advertisedDevice.getAddress().toString().length(),0);
    // save previous address
    if (strcmp(prev_addr,ble_addr)!=0){
      strcpy(prev_addr,ble_addr);
      doc["NODE"] = MQTT_ID;
      doc["ADDR"] = ble_addr;//advertisedDevice.getAddress().toString().c_str();
      doc["RSSI"] = advertisedDevice.getRSSI();
      serializeJson(doc, jsonBuffer); // print to client
      publishMessage();
    }
  } 
};

void setup() {
  Serial.begin(115200);
  connectAws();
  //BLEDevice::init("NODE3");
}

void loop() {
  set_as_observer();
  //publishMessage();
  //WiFi.disconnect();
  //WiFi.mode(WIFI_OFF);
  delay(1000);
  clean_addr();
  delay(1000);
}

void set_as_observer(void)
{
    Serial.println("Starting Arduino BLE Client application...");
    BLEDevice::init("NODE3");
    doc.clear();
    //BLEDevice::setPower(ESP_PWR_LVL_P4);
    pBLEScan = BLEDevice::getScan(); //create new scan
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true);
    pBLEScan->setInterval(200);
    pBLEScan->setWindow(99); 
    pBLEScan->start(1, false);
    delay(2000);
    BLEDevice::deinit(0);
    delay(100);
}

void connectAws(void)
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.println("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  // Configure WiFiClientSecure to use the AWS IoT device credentials
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);

  // Connect to the MQTT broker on the AWS endpoint we defined earlier
  client.begin(AWS_IOT_ENDPOINT, 8883, net);

  // Create a message handler
  client.onMessage(messageHandler);

  Serial.print("Connecting to AWS IOT");

  while (!client.connect(THINGNAME)) {
    Serial.print(".");
    delay(100);
  }

  if(!client.connected()){
    Serial.println("AWS IoT Timeout!");
    return;
  }

  // Subscribe to a topic
  client.subscribe(AWS_IOT_SUBSCRIBE_TOPIC);

  Serial.println("AWS IoT Connected!");
}

void publishMessage(void)
{
    //StaticJsonDocument<200> doc;
    //doc["NODE"] = MQTT_ID;
    //doc["ADDR"] = analogRead(0);
    //char jsonBuffer[512];
    //serializeJson(doc, jsonBuffer); // print to client
    client.publish(AWS_IOT_PUBLISH_TOPIC, jsonBuffer);
}

void clean_addr(void)
{
  for (int i=0;i<sizeof(prev_addr);i++){
    prev_addr[i] = 0;
  }
}


