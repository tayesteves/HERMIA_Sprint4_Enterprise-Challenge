Sensores – HERMIA Sprint 4

Esta pasta contém o código e arquivos de configuração utilizados para simular ou coletar dados de sensores em um **ESP32**, compondo a etapa de **coleta/ingestão** do pipeline HERMIA.
---

## Arquivos

- **`main.cpp`** → Código principal do ESP32 (Arduino/PlatformIO).  
  - Permite alternar entre **modo simulado** (`USE_REAL_SENSORS = 0`) e **modo real** (`USE_REAL_SENSORS = 1`).  
  - Sensores reais suportados:  
    - DHT22 (temperatura/umidade)  
    - LDR (luminosidade)  
    - MQ135 (qualidade do ar)  
    - Sensor de vibração  
  - Em modo simulado, gera valores **aleatórios mas realistas**, com ciclos de variação para temperatura, umidade e luminosidade, além de picos ocasionais de vibração.

- **`platformio.ini`** → Configuração do projeto no PlatformIO (placa `esp32dev`, bibliotecas da Adafruit para DHT):contentReference[oaicite:4]{index=4}.
- **`wokwi.toml`** → Arquivo de configuração da simulação no Wokwi (firmware gerado pelo PlatformIO):contentReference[oaicite:5]{index=5}.
- **`diagram.json`** → Diagrama do circuito no Wokwi, incluindo a placa ESP32 e conexões de TX/RX com o Serial Monitor:contentReference[oaicite:6]{index=6}.
- **`saida_sensor.csv`** → Exemplo de saída coletada do Serial Monitor (timestamp + valores dos sensores).

---

## ▶️ Como rodar

### 🖥️ Modo simulado (sem hardware)
1. Abra o projeto no **PlatformIO (VSCode)**.  
2. No `main.cpp`, garanta que:
   ```cpp
   #define USE_REAL_SENSORS 0
Compile e rode a simulação no Wokwi.

Veja os valores sendo exibidos no Serial Monitor a cada 2 segundos.

🔧 Modo real (com hardware ESP32)
Monte o circuito com:
DHT22 no pino GPIO4
LDR no GPIO35
Sensor de vibração no GPIO34
MQ135 no GPIO32

No main.cpp, altere para:
cpp
Copiar código
#define USE_REAL_SENSORS 1
Compile e faça upload para a placa via USB.

Acompanhe as leituras no Serial Monitor (115200 baud).

 Integração com o pipeline
Os dados gerados aqui (simulados ou reais) podem ser exportados para CSV (saida_sensor.csv).
Esse CSV alimenta a pasta /ingest, servindo como fonte inicial de dados para o pipeline.
A partir daí, o fluxo segue para banco de dados → ML → dashboard/alertas.

📸 Evidências
saida_sensor.csv → demonstra os dados capturados/simulados.

Esses dados coletados (reais ou simulados) são o ponto inicial do fluxo do projeto HERMIA, sendo integrados ao banco de dados (pasta /db) e posteriormente consumidos pelo ML e pelo dashboard (pasta /dashboard)
