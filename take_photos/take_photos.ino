#include "esp_camera.h"
#include "WiFi.h"
#include "HTTPClient.h"

#define CAMERA_MODEL_XIAO_ESP32S3 // Has PSRAM

#include "camera_pins.h"

unsigned long lastCaptureTime = 0; // Last shooting time
int imageCount = 1;                // File Counter
bool camera_sign = false;          // Check camera status

const char* ssid = "RZD FREE 2";  // Replace with your Wi-Fi SSID
const char* password = "nark1488";  // Replace with your Wi-Fi Password
const char* serverUrl = "http://192.168.187.152:5000/upload"; // Replace with your server endpoint
// const char* serverUrl = "http://127.0.0.1:5000/upload"; // Replace with your server endpoint
// Function to send photo to server
void sendPhoto(camera_fb_t *fb) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected");
        return;
    }

    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");

    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
        Serial.printf("Photo sent, response code: %d\n", httpResponseCode);
    } else {
        Serial.printf("Failed to send photo, error: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
}

void setup() {
    Serial.begin(115200);
    while (!Serial);

    // Initialize Wi-Fi
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWi-Fi connected");

    // Camera configuration
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.frame_size = FRAMESIZE_UXGA;
    config.pixel_format = PIXFORMAT_JPEG; // for streaming
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
    config.fb_location = CAMERA_FB_IN_PSRAM;
    config.jpeg_quality = 12;
    config.fb_count = 1;

    if (psramFound()) {
        config.jpeg_quality = 10;
        config.fb_count = 2;
        config.grab_mode = CAMERA_GRAB_LATEST;
    } else {
        config.frame_size = FRAMESIZE_SVGA;
        config.fb_location = CAMERA_FB_IN_DRAM;
    }

    // Initialize camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera init failed with error 0x%x\n", err);
        return;
    }

    camera_sign = true;
    Serial.println("Camera initialized.");
}

void loop() {
    if (camera_sign) {
        unsigned long now = millis();

        if ((now - lastCaptureTime) >= 10000) {
            // Take a photo
            camera_fb_t *fb = esp_camera_fb_get();
            if (!fb) {
                Serial.println("Failed to get camera frame buffer");
                return;
            }

            // Send photo to server
            sendPhoto(fb);

            // Release image buffer
            esp_camera_fb_return(fb);

            Serial.printf("Photo %d sent to server\n", imageCount);
            imageCount++;
            lastCaptureTime = now;
        }
    }
}
