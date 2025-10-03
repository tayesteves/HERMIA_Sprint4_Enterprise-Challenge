#include <DHT.h>

// Defina USE_REAL_SENSORS como 1 para usar sensores reais, 0 para usar dados aleatórios
#define USE_REAL_SENSORS 0

#if USE_REAL_SENSORS == 1
  #define DHTPIN 4
  #define DHTTYPE DHT22
  #define LDR_PIN 35
  #define VIBRATION_PIN 34
  #define MQ135_PIN 32
  DHT dht(DHTPIN, DHTTYPE);
#endif

void setup() {
  Serial.begin(115200);
  
  #if USE_REAL_SENSORS == 1
    dht.begin();
    pinMode(LDR_PIN, INPUT);
    pinMode(VIBRATION_PIN, INPUT);
    pinMode(MQ135_PIN, INPUT);
    Serial.println("// Modo: Sensores reais");
  #else
    Serial.println("// Modo: Dados aleatórios para todos os sensores");
  #endif
  
  Serial.println("Timestamp,Temperatura,Umidade,Luminosidade,Vibracao,QualidadeAr");
}

void loop() {
  static unsigned long startTime = millis();
  static unsigned long lastRandomize = 0;
  static float baseTemperature = 25.0;  // Temperatura base
  static float baseHumidity = 60.0;     // Umidade base
  
  delay(2000);

  float temperature, humidity;
  int luminosity, vibration, airQuality;

  #if USE_REAL_SENSORS == 1
    // Lê dos sensores reais
    humidity = dht.readHumidity();
    temperature = dht.readTemperature();
    luminosity = analogRead(LDR_PIN);
    vibration = analogRead(VIBRATION_PIN);
    airQuality = analogRead(MQ135_PIN);

    if (isnan(humidity) || isnan(temperature)) {
      Serial.println("Erro na leitura do sensor DHT!");
      return;
    }
  #else
    // Gera dados aleatórios realistas para todos os sensores
    unsigned long currentTime = millis();
    
    // Aleatoriza a cada 10 segundos para padrões mais realistas
    if (currentTime - lastRandomize > 10000) {
      randomSeed(micros()); // Seed mais aleatória
      lastRandomize = currentTime;
    }

    // Simula variações lentas de temperatura ao longo do "dia"
    float dayCycle = sin(currentTime / 1200000.0); // Ciclo de 20 minutos
    float tempVariation = dayCycle * 8.0; // Variação de ±8°C
    float randomTemp = random(-10, 11) / 10.0; // Variação aleatória de ±1°C
    
    temperature = baseTemperature + tempVariation + randomTemp;
    temperature = constrain(temperature, 15.0, 35.0); // Entre 15°C e 35°C

    // Umidade correlacionada inversamente com temperatura
    float humidityVariation = -tempVariation * 1.5; // Quando temperatura sobe, umidade desce
    float randomHumidity = random(-15, 16) / 10.0; // Variação aleatória de ±1.5%
    
    humidity = baseHumidity + humidityVariation + randomHumidity;
    humidity = constrain(humidity, 30.0, 85.0); // Entre 30% e 85%

    // Luminosidade: varia ao longo do "dia" simulado
    int baseLight = 1500 + 1200 * sin(currentTime / 600000.0); // Ciclo de 10 minutos
    int lightNoise = random(-300, 301); // Ruído aleatório
    luminosity = baseLight + lightNoise;
    luminosity = constrain(luminosity, 0, 4095);
    
    // Vibração: geralmente baixa, com picos ocasionais
    if (random(100) < 8) { // 8% de chance de pico de vibração
      vibration = random(500, 1024);
      // Pequena correlação: quando há vibração, temperatura pode subir um pouco
      temperature += 0.5;
    } else {
      vibration = random(0, 80);
    }
    
    // Qualidade do ar: pior quando umidade está muito alta ou muito baixa
    float humidityFactor = abs(humidity - 50.0) / 50.0; // 0=ideal, 1=ruim
    int baseAirQuality = 100 + humidityFactor * 200; // Pior com umidades extremas
    int airNoise = random(-40, 41);
    airQuality = baseAirQuality + airNoise;
    airQuality = constrain(airQuality, 50, 450);
    
  #endif

  Serial.print(millis() - startTime);
  Serial.print(",");
  Serial.print(temperature, 1); // 1 casa decimal
  Serial.print(",");
  Serial.print(humidity, 1);   // 1 casa decimal
  Serial.print(",");
  Serial.print(luminosity);
  Serial.print(",");
  Serial.print(vibration);
  Serial.print(",");
  Serial.println(airQuality);
}