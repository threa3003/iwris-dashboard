-- schema.sql
-- Run this once against your Neon/Postgres database before loading data.

CREATE TABLE IF NOT EXISTS stations (
    station_code   TEXT PRIMARY KEY,
    station_name   TEXT,
    parameter      TEXT,        -- 'groundwater' or 'rainfall'
    state          TEXT,
    district       TEXT,
    tehsil         TEXT,
    block          TEXT,
    latitude       DOUBLE PRECISION,
    longitude      DOUBLE PRECISION,
    agency         TEXT,
    well_type      TEXT,
    aquifer_type   TEXT,
    well_depth     DOUBLE PRECISION,
    data_status    TEXT
);

CREATE TABLE IF NOT EXISTS readings (
    id             BIGSERIAL PRIMARY KEY,
    station_code   TEXT NOT NULL REFERENCES stations(station_code),
    date           DATE NOT NULL,
    parameter      TEXT NOT NULL,   -- 'groundwater_level_m' or 'rainfall_mm'
    value          DOUBLE PRECISION NOT NULL
);

-- Indexes that make the dashboard's queries fast:
-- "give me this station's full history" and "give me all stations for a state/date range"
CREATE INDEX IF NOT EXISTS idx_readings_station_date ON readings (station_code, date);
CREATE INDEX IF NOT EXISTS idx_readings_date ON readings (date);
CREATE INDEX IF NOT EXISTS idx_stations_state ON stations (state);
CREATE INDEX IF NOT EXISTS idx_stations_parameter ON stations (parameter);
