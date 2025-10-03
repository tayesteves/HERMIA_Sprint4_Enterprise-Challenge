# HERMIA_Sprint4_Enterprise-Challenge

### FIAP - Faculdade de Informática e Administração Paulista

# 🌐 HERMIA Sprint 4 — Enterprise Challenge FIAP / Hermes Reply

Equipe 

- **Carlos** - RM566487
- **Endrew** - RM563646
- **João** - RM565999
- **Tayná** - RM562491
- **Vinicius** - RM566269

## 📖 Descrição do Projeto

O projeto **HERMIA (Hermes Reply Intelligent Assistant)** foi desenvolvido como parte do **Enterprise Challenge da FIAP** em parceria com a **Hermes Reply**.  
Trata-se de um **sistema inteligente de monitoramento industrial** que integra sensores IoT, banco de dados relacional, algoritmos de Machine Learning e um dashboard interativo para análise e tomada de decisão.  

A proposta é **detectar anomalias e disparar alertas em tempo real**, além de oferecer métricas históricas e previsões para apoiar gestores e operadores no chão de fábrica. O MVP integra todas as camadas essenciais de um pipeline moderno de Indústria 4.0: **coleta, ingestão, armazenamento, análise e visualização**.  

---

## Visão Geral

Este projeto entrega uma **solução integrada ponta a ponta** (MVP) que engloba:

- Simulação ou leitura real de sensores via ESP32  
- Ingestão de dados e persistência em banco relacional  
- Modelo de Machine Learning  
- Dashboard com KPIs, gráficos e alertas  
- Arquitetura documentada para futuro escalonamento  

O objetivo é demonstrar um pipeline funcional de Indústria 4.0, seguindo os requisitos do desafio (integrar entregas anteriores, observabilidade e reprodutibilidade).

---

## Estrutura do Repositório

| Pasta / Arquivo        | Descrição |
|-------------------------|-----------|
| `sensors/`              | Código do ESP32, configuração PlatformIO, simulação (Wokwi) e `saida_sensor.csv` como evidência |
| `ingest/`               | Dados simulados (`readings.csv`) e README explicando ingestão |
| `db/`                   | Schema SQL, queries de evidência e README com instruções de uso |
| `ml/`                   | Modelagem, inferência e visualizações (em desenvolvimento) |
| `dashboard/`             | App Streamlit com KPIs, gráficos e alertas |
| `docs/arquitetura/`     | Diagrama do fluxo integrado (draw.io + PNG) |
| `README.md` (raiz)      | Este arquivo, guia geral do projeto |

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

Prepare os dados de entrada
Caso queira rodar em modo simulado ou modo real (ESP32), siga as instruções no README da pasta sensors/.
O resultado esperado é o arquivo ingest/readings.csv.

Criar e popular o banco de dados (SQLite)
  bash
  Copiar código
  sqlite3 hermia.db < db/schema.sql
  sqlite3 hermia.db < db/queries.sql

Treinar / rodar modelo de Machine Learning
  bash
  Copiar código
  cd ml
  python train_model.py

Executar o dashboard (Streamlit)
  bash
  Copiar código
  cd dashboard
  streamlit run streamlit_app.py

Evidências
Arquitetura do sistema: /docs/arquitetura/SPRINT4-hermia.drawio.png
Prints de execução no dashboard: /dashboard/screenshots/
Saída simulada dos sensores: /sensors/saida_sensor.csv


📢 Observações Finais
Este repositório evoluiu das entregas anteriores, combinando arquitetura planejada, simulação, modelagem e visualização em um MVP funcional.
A proposta central é evidenciar integração entre camadas, rastreabilidade dos dados e flexibilidade para evolução futura.
