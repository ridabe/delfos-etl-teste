CREATE TABLE IF NOT EXISTS data (
    timestamp TIMESTAMP NOT NULL,
    wind_speed DOUBLE PRECISION NOT NULL,
    power DOUBLE PRECISION NOT NULL,
    ambient_temprature DOUBLE PRECISION NOT NULL
);

INSERT INTO data (timestamp, wind_speed, power, ambient_temprature)
SELECT ts,
       3 + 5 * random(),
       100 + 200 * random(),
       15 + 10 * random()
FROM generate_series('2025-12-01'::timestamp, '2025-12-10 23:59:00'::timestamp, interval '1 minute') ts;
