# Database Loading Quick Reference Guide

## Files Ready for Database Import

All cleaned data files are located in: `cleaned_data/`

### File Inventory
```
✓ co2_emissions_cleaned.csv          - 29,384 rows, 8 columns
✓ electricity_production_cleaned.csv - 6,917 rows, 20 columns  
✓ oil_production_cleaned.csv         - 750 rows, 8 columns
✓ energy_prod_cons_cleaned.csv       - 1,113 rows, 11 columns
✓ nymex_gas_prices_cleaned.csv       - 1,224 rows, 7 columns
```

## Option 1: PostgreSQL Import (Recommended)

### Step 1: Create Database
```sql
CREATE DATABASE energy_environmental_db;
\c energy_environmental_db
```

### Step 2: Create Tables
```sql
-- CO2 Emissions Table
CREATE TABLE co2_emissions (
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
CREATE TABLE electricity_production (
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
CREATE TABLE oil_production (
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
CREATE TABLE energy_prod_cons (
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
CREATE TABLE nymex_gas_prices (
    time VARCHAR(50) PRIMARY KEY,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume INTEGER,
    volume_ma DOUBLE PRECISION
);
```

### Step 3: Import CSV Files
```bash
# From PostgreSQL command line or psql
\copy co2_emissions FROM 'cleaned_data/co2_emissions_cleaned.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy electricity_production FROM 'cleaned_data/electricity_production_cleaned.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy oil_production FROM 'cleaned_data/oil_production_cleaned.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy energy_prod_cons FROM 'cleaned_data/energy_prod_cons_cleaned.csv' WITH (FORMAT csv, HEADER true, NULL '');

\copy nymex_gas_prices FROM 'cleaned_data/nymex_gas_prices_cleaned.csv' WITH (FORMAT csv, HEADER true, NULL '');
```

### Step 4: Create Indexes for Performance
```sql
-- CO2 Emissions Indexes
CREATE INDEX idx_co2_code ON co2_emissions(code);
CREATE INDEX idx_co2_year ON co2_emissions(year);
CREATE INDEX idx_co2_entity_type ON co2_emissions(entity_type);

-- Electricity Production Indexes
CREATE INDEX idx_elec_code ON electricity_production(code);
CREATE INDEX idx_elec_year ON electricity_production(year);
CREATE INDEX idx_elec_renewable ON electricity_production(pct_renewable);

-- Oil Production Indexes
CREATE INDEX idx_oil_code ON oil_production(code);
CREATE INDEX idx_oil_year ON oil_production(year);

-- Energy Prod/Cons Indexes
CREATE INDEX idx_energy_code ON energy_prod_cons(code);
CREATE INDEX idx_energy_year ON energy_prod_cons(year);
CREATE INDEX idx_energy_exporter ON energy_prod_cons(is_net_exporter);

-- NYMEX Indexes
CREATE INDEX idx_nymex_time ON nymex_gas_prices(time);
```

### Step 5: Verify Import
```sql
-- Check row counts
SELECT 'co2_emissions' AS table_name, COUNT(*) AS row_count FROM co2_emissions
UNION ALL
SELECT 'electricity_production', COUNT(*) FROM electricity_production
UNION ALL
SELECT 'oil_production', COUNT(*) FROM oil_production
UNION ALL
SELECT 'energy_prod_cons', COUNT(*) FROM energy_prod_cons
UNION ALL
SELECT 'nymex_gas_prices', COUNT(*) FROM nymex_gas_prices;

-- Expected results:
-- co2_emissions: 29,384
-- electricity_production: 6,917
-- oil_production: 750
-- energy_prod_cons: 1,113
-- nymex_gas_prices: 1,224
```

## Option 2: Python with Pandas (Flexible)

```python
import pandas as pd
from sqlalchemy import create_engine

# Create database connection
engine = create_engine('postgresql://username:password@localhost:5432/energy_environmental_db')

# Or for SQLite (file-based, no server needed)
# engine = create_engine('sqlite:///energy_data.db')

# Load each cleaned CSV file
datasets = {
    'co2_emissions': 'co2_emissions_cleaned.csv',
    'electricity_production': 'electricity_production_cleaned.csv',
    'oil_production': 'oil_production_cleaned.csv',
    'energy_prod_cons': 'energy_prod_cons_cleaned.csv',
    'nymex_gas_prices': 'nymex_gas_prices_cleaned.csv'
}

for table_name, csv_file in datasets.items():
    df = pd.read_csv(f'cleaned_data/{csv_file}')
    
    # Convert types if needed
    if 'year' in df.columns:
        df['year'] = df['year'].astype('int16')
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'])
    
    # Load to database
    df.to_sql(table_name, engine, if_exists='replace', index=False, 
              chunksize=1000, method='multi')
    
    print(f"✓ Loaded {len(df):,} rows into {table_name}")

print("\n✓ All datasets loaded successfully!")
```

## Option 3: MySQL Import

```sql
-- Create database
CREATE DATABASE energy_environmental_db;
USE energy_environmental_db;

-- Create tables (use DOUBLE instead of DOUBLE PRECISION)
-- ... (similar to PostgreSQL but with MySQL syntax)

-- Load data
LOAD DATA LOCAL INFILE 'cleaned_data/co2_emissions_cleaned.csv'
INTO TABLE co2_emissions
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

-- Repeat for other tables...
```

## Option 4: Direct Analysis with Pandas (No Database)

```python
import pandas as pd

# Load all datasets into memory
co2 = pd.read_csv('cleaned_data/co2_emissions_cleaned.csv')
electricity = pd.read_csv('cleaned_data/electricity_production_cleaned.csv')
oil = pd.read_csv('cleaned_data/oil_production_cleaned.csv')
energy = pd.read_csv('cleaned_data/energy_prod_cons_cleaned.csv')
nymex = pd.read_csv('cleaned_data/nymex_gas_prices_cleaned.csv')

# Perform joins and analysis
integrated = co2.merge(
    electricity, 
    on=['entity', 'code', 'year'], 
    how='left', 
    suffixes=('_co2', '_elec')
)

# Continue analysis...
```

## Sample Analytical Queries

### Query 1: Top CO2 Emitters in 2024
```sql
SELECT entity, annual_co2_emissions, code
FROM co2_emissions
WHERE year = 2024 
  AND entity_type = 'country'
ORDER BY annual_co2_emissions DESC
LIMIT 10;
```

### Query 2: Renewable Energy Adoption Trends
```sql
SELECT entity, year, pct_renewable, pct_fossil
FROM electricity_production
WHERE entity IN ('United States', 'China', 'Germany', 'India')
  AND year >= 2000
ORDER BY entity, year;
```

### Query 3: Net Energy Exporters
```sql
SELECT entity, year, 
       production_based_energy,
       consumption_based_energy,
       net_energy_trade_twh
FROM energy_prod_cons
WHERE is_net_exporter = TRUE
  AND year = 2020
ORDER BY net_energy_trade_twh DESC
LIMIT 10;
```

### Query 4: Comprehensive Energy Profile
```sql
SELECT 
    co2.entity,
    co2.year,
    co2.annual_co2_emissions / 1000000 as co2_mt,
    elec.total_electricity_twh,
    elec.pct_renewable,
    oil.oil_production_twh,
    energy.net_energy_trade_twh
FROM co2_emissions co2
LEFT JOIN electricity_production elec 
    ON co2.entity = elec.entity AND co2.year = elec.year
LEFT JOIN oil_production oil
    ON co2.entity = oil.entity AND co2.year = oil.year
LEFT JOIN energy_prod_cons energy
    ON co2.entity = energy.entity AND co2.year = energy.year
WHERE co2.year = 2020
  AND co2.entity_type = 'country'
  AND co2.annual_co2_emissions > 0
ORDER BY co2.annual_co2_emissions DESC
LIMIT 20;
```

## Data Validation After Import

```sql
-- Test 1: Check for missing values in key columns
SELECT 
    'co2_emissions' as table_name,
    COUNT(*) as total_rows,
    SUM(CASE WHEN entity IS NULL THEN 1 ELSE 0 END) as null_entity,
    SUM(CASE WHEN year IS NULL THEN 1 ELSE 0 END) as null_year
FROM co2_emissions;

-- Test 2: Verify referential integrity (entity-code consistency)
SELECT entity, COUNT(DISTINCT code) as code_count
FROM co2_emissions
WHERE code IS NOT NULL
GROUP BY entity
HAVING COUNT(DISTINCT code) > 1;
-- Should return 0 rows

-- Test 3: Check data ranges
SELECT 
    MIN(year) as min_year,
    MAX(year) as max_year,
    MIN(annual_co2_emissions) as min_emissions,
    MAX(annual_co2_emissions) as max_emissions
FROM co2_emissions;

-- Test 4: Verify percentage calculations
SELECT entity, year,
    pct_renewable + pct_fossil + pct_nuclear as total_pct
FROM electricity_production
WHERE ABS((pct_renewable + pct_fossil + pct_nuclear) - 100) > 1
LIMIT 10;
-- Should return very few rows (only rounding differences)
```

## Troubleshooting

### Issue: Import fails with encoding errors
**Solution:** Specify UTF-8 encoding
```bash
# PostgreSQL
\copy table_name FROM 'file.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');
```

### Issue: NULL values not handled correctly
**Solution:** Explicitly define NULL representation
```bash
# PostgreSQL - empty strings as NULL
\copy table_name FROM 'file.csv' WITH (FORMAT csv, HEADER true, NULL '');
```

### Issue: Date format not recognized
**Solution:** Use COPY with proper date format or pre-process with Python
```python
df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%d')
```

## Performance Tips

1. **Use COPY instead of INSERT**: 10-100x faster for bulk loads
2. **Create indexes AFTER import**: Speeds up initial load
3. **Use transactions**: Wrap imports in BEGIN/COMMIT for rollback capability
4. **Partition large tables**: Consider partitioning by year for time-series data
5. **Use appropriate data types**: INT16 for years, FLOAT32 for metrics if precision allows

## Next Steps After Loading

1. ✓ Verify row counts match source files
2. ✓ Run validation queries
3. ✓ Create additional indexes based on query patterns
4. ✓ Set up backup and recovery procedures
5. ✓ Document database schema
6. ✓ Create views for common analytical queries
7. ✓ Set up user access controls
8. ✓ Configure automated data refresh procedures

---

**Questions?** Refer to:
- `COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md` - Full documentation
- `cleaned_data/execution_log.json` - Detailed transformation log
- `et_plan.json` - Machine-readable transformation plan
