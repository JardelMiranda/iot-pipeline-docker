-- ============================================================
-- View 1: média de temperatura por dispositivo
-- Compara os sensores (interno x externo): média, mínimo,
-- máximo e total de leituras de cada um.
-- ============================================================
CREATE OR REPLACE VIEW avg_temp_por_dispositivo AS
SELECT
    device_id,
    ROUND(AVG(temperature), 2) AS avg_temp,
    MIN(temperature)           AS min_temp,
    MAX(temperature)           AS max_temp,
    COUNT(*)                   AS total_leituras
FROM temperature_readings
GROUP BY device_id;

-- ============================================================
-- View 2: quantidade de leituras por hora do dia (0–23)
-- Mostra em quais horários os dispositivos mais enviam dados.
-- ============================================================
CREATE OR REPLACE VIEW leituras_por_hora AS
SELECT
    EXTRACT(HOUR FROM noted_at)::INT AS hora,
    COUNT(*)                         AS contagem
FROM temperature_readings
GROUP BY EXTRACT(HOUR FROM noted_at)
ORDER BY hora;

-- ============================================================
-- View 3: temperaturas máxima e mínima por dia
-- Série temporal diária para identificar picos e vales.
-- ============================================================
CREATE OR REPLACE VIEW temp_max_min_por_dia AS
SELECT
    noted_at::DATE   AS data,
    MAX(temperature) AS temp_max,
    MIN(temperature) AS temp_min
FROM temperature_readings
GROUP BY noted_at::DATE
ORDER BY data;
