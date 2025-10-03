Banco de Dados – HERMIA Sprint 4

Esta pasta reúne os scripts e consultas SQL utilizadas no projeto.

## Arquivos

- **schema.sql** → Criação das tabelas principais:
  - `devices` → dispositivos (ex.: ESP32)  
  - `readings` → leituras dos sensores  
  - `alerts` → alertas gerados  

- **queries.sql** → Consultas de exemplo:
  - Quantidade total de leituras  
  - KPIs (média de vibração e qualidade do ar)  
  - Últimas 5 leituras registradas  
  - Top 10 alertas mais recentes  

## Como usar

1. Criar o banco e as tabelas:
   ```bash
   sqlite3 hermia.db < db/schema.sql
Importar os dados de leitura (arquivo ingest/readings.csv):

sql
Copiar código
.mode csv
.headers on
.import ingest/readings.csv readings
Rodar as consultas de evidência:

bash
Copiar código
sqlite3 hermia.db < db/queries.sql

🔗 Integração
Os dados simulados de sensores ficam em /ingest

São importados para a tabela readings

O dashboard consome essas informações para exibir métricas e alertas
