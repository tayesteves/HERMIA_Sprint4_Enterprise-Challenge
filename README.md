# HERMIA_Sprint4_Enterprise-Challenge

### FIAP - Faculdade de Informática e Administração Paulista

# 🌐 HERMIA Sprint 4 — Enterprise Challenge FIAP / Hermes Reply

Equipe 

- **Carlos** - RM566487
- **Endrew** - RM563646
- **João** - RM565999
- **Tayná** - RM562491
- **Vinicius** - RM566269

📂 Estrutura do Repositório

- [`/sensors`](./sensors) → Código para ESP32 (modo simulado e real), configuração no PlatformIO/Wokwi e saída dos sensores.  
- [`/ingest`](./ingest) → Dados simulados de entrada (CSV) para popular o pipeline.  
- [`/db`](./db) → Scripts SQL para criação do esquema (schema.sql) e consultas (queries.sql).  
- [`/ml`](./ml) → Treinamento e execução de modelos de Machine Learning.  
- [`/dashboard`](./dashboard) → Aplicação Streamlit para visualização de métricas e alertas, com evidências em `/dashboard/screenshots`.  
- [`/docs/arquitetura`](./docs/arquitetura) → Diagramas e documentação do sistema.  

---


## Fluxo de Dados (ponta a ponta)

1. **Sensores / Simulação**  
   O ESP32 (em modo real ou simulado) gera leituras de temperatura, vibração, luminosidade e qualidade do ar.  
   Os dados são exportados para `saida_sensor.csv`.

2. **Ingestão**  
   A partir de `saida_sensor.csv`, é construído o `readings.csv` que alimenta a camada de ingestão.

3. **Persistência em Banco**  
   O arquivo `readings.csv` é importado para as tabelas do banco (via `schema.sql`).  
   A tabela `alerts` armazena sinais disparados pelo dashboard.

4. **Machine Learning**  
   Sobre os dados armazenados, treina-se um modelo simples que permite realizar previsões ou classificações (exibir métricas como MAE).  

5. **Dashboard & Alertas**  
   O app Streamlit exibe KPIs, séries temporais e dispara alertas baseados em regras configuráveis.  
   Todo alerta é registrado para auditoria.

6. **Documentação / Evidências**  
   O diagrama da arquitetura e screenshots das interfaces servem como comprovação do funcionamento e desenho do pipeline.

---

## ▶️ Como Executar

1. Clone o repositório  
   ```bash
   git clone https://github.com/tayesteves/HERMIA_Sprint4_Enterprise-Challenge.git
   cd HERMIA_Sprint4_Enterprise-Challenge

Caso queira rodar em modo simulado ou modo real (ESP32), siga as instruções no README da pasta sensors/
.
O resultado esperado é o arquivo ingest/readings.csv.

- Criar e popular o banco de dados (SQLite)
   ```bash
   sqlite3 hermia.db < db/schema.sql
   sqlite3 hermia.db < db/queries.sql


- Treinar / rodar modelo de Machine Learning
   ```bash
   cd ml
   python train_model.py

- Executar o dashboard (Streamlit)
 ```bash
   cd dashboard
   streamlit run streamlit_app.py
. 

- Evidências
Arquitetura do sistema: /docs/arquitetura/SPRINT4-hermia.drawio.png
Prints de execução no dashboard: /dashboard/screenshots/
Saída simulada dos sensores: /sensors/saida_sensor.csv


📢 Observações Finais
Este repositório evoluiu das entregas anteriores, combinando arquitetura planejada, simulação, modelagem e visualização em um MVP funcional.
A proposta central é evidenciar integração entre camadas, rastreabilidade dos dados e flexibilidade para evolução futura.
