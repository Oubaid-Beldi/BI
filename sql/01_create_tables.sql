-- Energy & Environmental Database Schema
-- Created: 2025-11-18

-- CO2 Emissions Table
CREATE TABLE IF NOT EXISTS co2_emissions (
    entity VARCHAR(255) NOT NULL,
    code VARCHAR(3),
    year SMALLINT NOT NULL,
    annual_co2_emissions DOUBLE PRECISION NOT NULL,
    data_source VARCHAR(50),
    data_quality_flag VARCHAR(20),
    last_updated DATE,
    entity_type VARCHAR(20),
    PRIMARY KEY (entity, year)
);

-- Electricity Production Table
CREATE TABLE IF NOT EXISTS electricity_production (
    entity VARCHAR(255) NOT NULL,
    code VARCHAR(3),
    year SMALLINT NOT NULL,
    other_renewables_twh DOUBLE PRECISION,
    bioenergy_twh DOUBLE PRECISION,
    solar_twh DOUBLE PRECISION,
    wind_twh DOUBLE PRECISION,
    hydro_twh DOUBLE PRECISION,
    nuclear_twh DOUBLE PRECISION,
    oil_twh DOUBLE PRECISION,
    gas_twh DOUBLE PRECISION,
    coal_twh DOUBLE PRECISION,
    total_electricity_twh DOUBLE PRECISION,
    pct_renewable DOUBLE PRECISION,
    pct_fossil DOUBLE PRECISION,
    pct_nuclear DOUBLE PRECISION,
    data_source VARCHAR(50),
    data_quality_flag VARCHAR(20),
    last_updated DATE,
    entity_type VARCHAR(20),
    PRIMARY KEY (entity, year)
);

-- Oil Production Table
CREATE TABLE IF NOT EXISTS oil_production (
    entity VARCHAR(255) NOT NULL,
    code VARCHAR(3),
    year SMALLINT NOT NULL,
    oil_production_twh DOUBLE PRECISION NOT NULL,
    data_source VARCHAR(50),
    data_quality_flag VARCHAR(20),
    last_updated DATE,
    entity_type VARCHAR(20),
    PRIMARY KEY (entity, year)
);

-- Energy Production vs Consumption Table
CREATE TABLE IF NOT EXISTS energy_prod_cons (
    entity VARCHAR(255) NOT NULL,
    code VARCHAR(3) NOT NULL,
    year SMALLINT NOT NULL,
    consumption_based_energy DOUBLE PRECISION NOT NULL,
    production_based_energy DOUBLE PRECISION NOT NULL,
    net_energy_trade_twh DOUBLE PRECISION,
    is_net_exporter BOOLEAN,
    data_source VARCHAR(50),
    data_quality_flag VARCHAR(20),
    last_updated DATE,
    entity_type VARCHAR(20),
    PRIMARY KEY (entity, year)
);

-- NYMEX Gas Prices Table
CREATE TABLE IF NOT EXISTS nymex_gas_prices (
    time VARCHAR(50) PRIMARY KEY,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume INTEGER,
    volume_ma DOUBLE PRECISION
);

-- Create indexes for better query performance
-- CO2 Emissions Indexes
CREATE INDEX IF NOT EXISTS idx_co2_code ON co2_emissions(code);
CREATE INDEX IF NOT EXISTS idx_co2_year ON co2_emissions(year);
CREATE INDEX IF NOT EXISTS idx_co2_entity_type ON co2_emissions(entity_type);

-- Electricity Production Indexes
CREATE INDEX IF NOT EXISTS idx_elec_code ON electricity_production(code);
CREATE INDEX IF NOT EXISTS idx_elec_year ON electricity_production(year);
CREATE INDEX IF NOT EXISTS idx_elec_renewable ON electricity_production(pct_renewable);

-- Oil Production Indexes
CREATE INDEX IF NOT EXISTS idx_oil_code ON oil_production(code);
CREATE INDEX IF NOT EXISTS idx_oil_year ON oil_production(year);

-- Energy Prod/Cons Indexes
CREATE INDEX IF NOT EXISTS idx_energy_code ON energy_prod_cons(code);
CREATE INDEX IF NOT EXISTS idx_energy_year ON energy_prod_cons(year);
CREATE INDEX IF NOT EXISTS idx_energy_exporter ON energy_prod_cons(is_net_exporter);

-- NYMEX Indexes
CREATE INDEX IF NOT EXISTS idx_nymex_time ON nymex_gas_prices(time);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO energy_user;
