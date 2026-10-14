-- Tabela principal com as leituras dos dispositivos IoT.
-- Origem: Kaggle "Temperature Readings: IoT Devices" (IOT-temp.csv)
CREATE TABLE IF NOT EXISTS temperature_readings (
    pk          BIGSERIAL PRIMARY KEY,
    reading_id  TEXT,                       -- coluna "id" do CSV (id do log)
    room_id     TEXT,                       -- coluna "room_id/id" do CSV
    location    TEXT NOT NULL,              -- coluna "out/in": 'In' (interno) ou 'Out' (externo)
    device_id   TEXT NOT NULL,              -- sensor lógico = room_id + '-' + location
    noted_at    TIMESTAMP NOT NULL,         -- coluna "noted_date" do CSV
    temperature NUMERIC(5,1) NOT NULL       -- coluna "temp" do CSV (°C)
);

CREATE INDEX IF NOT EXISTS idx_readings_noted_at ON temperature_readings (noted_at);
CREATE INDEX IF NOT EXISTS idx_readings_device   ON temperature_readings (device_id);
