# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Administração Paulista" width="40%"></a>
</p>

<br>

# Nome do projeto
Fase 6 - Colheita de soluções inteligentes - Transformando dados em ações / Enterprise Challenge - Sprint 4 - Reply

## Nome do grupo
Equipe Fiap

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/company/inova-fusca">**Carlos** - RM566487</a>
- <a href="https://www.linkedin.com/company/inova-fusca">**Endrew** - RM563646</a>
- <a href="https://www.linkedin.com/company/inova-fusca">**João** - RM565999</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">**Tayná** - RM562491</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">**Vinicius** - RM566269</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">André Godoi Chiovato</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Lucas Gomes Moreirar</a>

---

## 📜 Descrição

O **HERMIA** é um MVP de **Indústria 4.0** que integra:
- **Sensores IoT (ESP32)** em modo real ou simulado,
- **Ingestão** de dados em CSV,
- **Banco relacional (SQLite)**,
- **Machine Learning** (treino/inferência),
- **Dashboard (Streamlit)** com KPIs, gráficos e **alertas** com log de evidências.

O objetivo é demonstrar um **pipeline ponta a ponta**: coleta → ingestão → persistência → análise → visualização/alertas, com foco em **observabilidade e reprodutibilidade**.

---

## 📂 Estrutura do Repositório

![Estrutura do Repositório]("C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\estrutura_diretorios.png")

- [`/sensors`](./sensors) → Código para ESP32 (modo simulado e real), configuração no PlatformIO/Wokwi e saída dos sensores.  
- [`/ingest`](./ingest) → Dados simulados de entrada (CSV) para popular o pipeline.  
- [`/db`](./db) → Scripts SQL para criação do esquema (schema.sql) e consultas (queries.sql).  
- [`/ml`](./ml) → Treinamento e execução de modelos de Machine Learning.  
- [`/dashboard`](./dashboard) → Aplicação Streamlit para visualização de métricas e alertas, com evidências em `/dashboard/screenshots`.  
- [`/docs/arquitetura`](./docs/arquitetura) → Diagramas e documentação do sistema.  

---

## 🔄 Fluxo de Dados (ponta a ponta)

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

## 🗄️ Modelo de Dados

📌 **Diagrama da Arquitetura do Sistema:**  
<p align="center">
  <img src="C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\SPRINT4-hermia.drawio.png" alt="Arquitetura do Sistema" width="70%">
</p>

---

### Estrutura Geral das Tabelas

- **Tabela `MAQUINA_AUTONOMA`**
  - Armazena informações das máquinas monitoradas.
  - **Chave primária:** `ID_MAQUINA`
![MAQUINA_AUTONOMA](C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\banco_dados\08_t_maquina_autonoma.png)


- **Tabela `LEITURA_SENSORES`**
  - Centraliza as leituras enviadas pelos sensores.  
  - Temperatura, vibração, luminosidade, qualidade do ar etc.
  ![LEITURA_SENSORES](C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\banco_dados\04_t_leitura_sensores.png)


- **Tabela `FUNCIONARIO`**
  - Registra responsáveis por manutenção.
    ![FUNCIONARIO](C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\banco_dados\02_t_funcionario.png)


- **Tabela `MANUTENCAO`**
  - Registra eventos de manutenção preventiva ou corretiva.
    ![MANUTENCAO](C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\figs\banco_dados\06_t_manutencao.png)


- **Tabela `ALERTS`**
  - Mantém o log de alertas disparados pelo dashboard.
  

---

## 🖼️ Evidências

📌 **Dashboard - KPIs e Alertas:**  
    ![DASHBOARD 1]("C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\dashboards\dashboard_enriquecidos.html")
    
    ![DASHBOARD 2](""C:\Users\CarlosSouza\PycharmProjects\PythonProject1\Enterprise_Challenge_Sprint_4_Reply\dados_saida\dashboards\dashboard.html"")
---

## ▶️ Como Executar

1. Clone o repositório  
   ```bash
   git clone https://github.com/tayesteves/HERMIA_Sprint4_Enterprise-Challenge.git
   cd HERMIA_Sprint4_Enterprise-Challenge
