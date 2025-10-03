-- Quantidade total de leituras
SELECT COUNT(*) AS n_readings FROM readings;

-- KPIs simples
SELECT ROUND(AVG(vibration), 3) AS avg_vibration FROM readings;
SELECT ROUND(AVG(air_q), 1)    AS avg_air_q     FROM readings;

-- Últimas 5 leituras (evidência)
SELECT ts, temperature, vibration, luminosity, air_q
FROM readings
ORDER BY id DESC
LIMIT 5;

-- Top 10 alertas mais recentes
SELECT ts, rule, value, severity, status
FROM alerts
ORDER BY id DESC
LIMIT 10;
