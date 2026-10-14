# Base de dados

Dataset: **Temperature Readings: IoT Devices** (Kaggle)
Link: https://www.kaggle.com/datasets/atulanandjha/temperature-readings-iot-devices

## Como baixar

1. Crie/entre na sua conta do Kaggle.
2. Abra o link acima e clique em **Download**.
3. Extraia o arquivo e salve como `data/IOT-temp.csv`.

O arquivo CSV não é versionado no Git (ver `.gitignore`) — o link acima é a fonte oficial.

## Colunas do CSV original

| Coluna        | Descrição                                   | Coluna na tabela |
|---------------|---------------------------------------------|------------------|
| `id`          | Identificador do registro de log            | `reading_id`     |
| `room_id/id`  | Sala onde o sensor está instalado           | `room_id`        |
| `noted_date`  | Data e hora da leitura (dd-mm-aaaa hh:mm)   | `noted_at`       |
| `temp`        | Temperatura em °C                           | `temperature`    |
| `out/in`      | Sensor externo (`Out`) ou interno (`In`)    | `location`       |
