Ingestão de Dados – HERMIA Sprint 4

Esta pasta contém os arquivos responsáveis pela **coleta e ingestão de dados simulados** dos sensores no pipeline HERMIA.

## Arquivos

- **`readings.csv`**  
  Arquivo de exemplo com leituras simuladas, incluindo:  
  - `ts` → timestamp da leitura  
  - `temperature` → temperatura em °C  
  - `vibration` → vibração (0 a 1.5)  
  - `luminosity` → luminosidade em lux  
  - `air_q` → índice de qualidade do ar  

  Este arquivo serve como **ponto inicial de ingestão** para alimentar o dashboard.

---

## Integração com o pipeline

1. **Origem dos dados:** simulados (exemplo em `readings.csv`) ou coletados via ESP32.  
2. **Ingestão:** registros são salvos no `readings.csv`.  
3. **Consumo:** o arquivo é lido pelo dashboard (`/dashboard/streamlit_app.py`) para cálculo de KPIs, exibição de séries temporais e disparo de alertas.  



