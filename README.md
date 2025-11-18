# Energy & Environmental Data ETL Pipeline

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Latest-green.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Extract, Transform, Load (ETL) pipeline for cleaning and analyzing energy and environmental datasets including CO2 emissions, electricity production, oil production, and energy trade data.

## 🚀 New to this Project?

**→ Start here: [GETTING_STARTED.md](GETTING_STARTED.md)**

Quick setup after cloning:

```bash
# Step 1: Clean the data
pip install pandas numpy
python3 et_analysis_and_execution.py

# Step 2: Load into database
./setup_database.sh
```

**Done! Database ready in ~40 seconds.**

## 📊 Project Overview

This project processes and cleans **39,388 records** across 5 major datasets spanning **1750-2024**, achieving a **99.2% data quality score** with **100% data retention**.

### Datasets Processed

- **CO2 Emissions**: 29,384 records (1750-2024) - Global Carbon Budget
- **Electricity Production**: 6,917 records (1985-2024) - Ember & Energy Institute
- **Oil Production**: 750 records (1900-2024) - Energy Institute & Shift Data Portal
- **Energy Production vs Consumption**: 1,113 records (1995-2020) - EXIOBASE
- **NYMEX Gas Prices**: 1,224 records (2017-2022) - NYMEX Daily Data

## ✨ Key Features

- ✅ **Automated ETL Pipeline** - 700-line Python script with full documentation
- ✅ **Comprehensive Data Quality Analysis** - 15+ issue types detected and resolved
- ✅ **Derived Analytics Columns** - Total electricity, renewable percentages, net trade
- ✅ **Database-Ready Output** - Cleaned CSVs with SQL import scripts
- ✅ **Complete Documentation** - 54-page analysis report + execution logs
- ✅ **100% Data Retention** - Zero critical data loss during cleaning

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.13+
pandas
numpy
Docker & Docker Compose (for database setup)
```

### Installation

```bash
# Clone the repository
git clone https://github.com/jasseurchibani/bi.git
cd bi

# Install dependencies
pip install pandas numpy

# Run the ETL pipeline
python et_analysis_and_execution.py
```

### Load Data into PostgreSQL (Docker)

```bash
# One-command setup (recommended)
./setup_database.sh

# Or using Makefile
make setup

# Check status
./status.sh
```

**See [DATABASE_SETUP.md](DATABASE_SETUP.md) for complete database setup instructions.**

## 📁 Project Structure

```
.
├── cleaned_data/                          # Output cleaned datasets
│   ├── co2_emissions_cleaned.csv          # 29,384 rows × 8 columns
│   ├── electricity_production_cleaned.csv  # 6,917 rows × 20 columns
│   ├── oil_production_cleaned.csv         # 750 rows × 8 columns
│   ├── energy_prod_cons_cleaned.csv       # 1,113 rows × 11 columns
│   ├── nymex_gas_prices_cleaned.csv       # 1,224 rows × 7 columns
│   ├── execution_log.json                 # Detailed operation log
│   └── cleaning_summary_report.txt        # Human-readable summary
│
├── sql/                                   # Database setup
│   └── 01_create_tables.sql               # PostgreSQL schema
│
├── et_analysis_and_execution.py           # Main ETL pipeline
├── et_plan.json                           # Machine-readable transformation plan
│
├── docker-compose.yml                     # Docker PostgreSQL setup
├── setup_database.sh                      # One-command database setup ⭐
├── load_data.sh                           # Bash data loader
├── load_data.py                           # Python data loader
├── status.sh                              # Health check script
├── Makefile                               # Convenient commands
│
├── DATABASE_SETUP.md                      # Complete database setup guide ⭐
├── COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md  # 54-page full analysis
├── DATABASE_LOADING_GUIDE.md              # Alternative loading methods
├── PROJECT_SUMMARY.md                     # Executive overview
│
├── annual-co2-emissions-per-country.csv   # Raw data
├── annual-co2-emissions-per-country.metadata.json
├── electricity-prod-source-stacked.csv
├── electricity-prod-source-stacked.metadata.json
├── oil-production-by-country.csv
├── oil-production-by-country.metadata.json
├── production-vs-consumption-energy.csv
├── production-vs-consumption-energy.metadata.json
└── NYMEX_DL_TTF1 1D.csv
```

## 📖 Documentation

- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Quick overview and deliverables
- **[COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md](COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md)** - Complete analysis with all sections:
  - A. Data Overview
  - B. Detected Issues
  - C. Cleaning Steps (per column)
  - D. Transformations
  - E. Final Schema
  - F. Assumptions & Clarifications
- **[DATABASE_LOADING_GUIDE.md](DATABASE_LOADING_GUIDE.md)** - PostgreSQL, MySQL, Python import instructions

## 🔧 Usage

### Run the ETL Pipeline

```python
python et_analysis_and_execution.py
```

The pipeline will:

1. Extract all CSV and JSON metadata files
2. Analyze data quality issues
3. Generate transformation plan
4. Execute cleaning and transformations
5. Save cleaned datasets and logs

### Load to Database

#### PostgreSQL Example

```bash
# Create database
createdb energy_environmental_db

# Import cleaned data
psql energy_environmental_db -c "\copy co2_emissions FROM 'cleaned_data/co2_emissions_cleaned.csv' CSV HEADER"
```

#### Python/Pandas Example

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/energy_db')

# Load cleaned data
co2 = pd.read_csv('cleaned_data/co2_emissions_cleaned.csv')
co2.to_sql('co2_emissions', engine, if_exists='replace', index=False)
```

### Analyze Data

```python
import pandas as pd

# Load cleaned datasets
co2 = pd.read_csv('cleaned_data/co2_emissions_cleaned.csv')
electricity = pd.read_csv('cleaned_data/electricity_production_cleaned.csv')

# Top CO2 emitters in 2024
top_emitters = co2[co2['year'] == 2024].nlargest(10, 'annual_co2_emissions')

# Renewable energy trends
renewable_trends = electricity[electricity['entity'] == 'United States'][
    ['year', 'pct_renewable', 'pct_fossil']
]
```

## 📊 Data Quality Metrics

| Dataset          | Completeness | Consistency | Accuracy       | Data Retention |
| ---------------- | ------------ | ----------- | -------------- | -------------- |
| CO2 Emissions    | 100%         | ✓ High     | ✓ Verified    | 100%           |
| Electricity      | 100%         | ✓ High     | ✓ Verified    | 100%           |
| Oil Production   | 100%         | ✓ High     | ✓ Verified    | 100%           |
| Energy Prod/Cons | 100%         | ✓ High     | ✓ Verified    | 100%           |
| NYMEX Prices     | 98.4%        | ✓ High     | ✓ Market Data | 100%           |

**Overall Data Quality Score: 99.2%**

## 🎯 Key Transformations

### Derived Columns Added

1. **Total Electricity Generation** - Sum across all sources (TWh)
2. **Renewable Percentage** - (Solar + Wind + Hydro + Bio) / Total × 100
3. **Fossil Percentage** - (Coal + Gas + Oil) / Total × 100
4. **Nuclear Percentage** - Nuclear / Total × 100
5. **Net Energy Trade** - Production - Consumption (TWh)
6. **Is Net Exporter** - Boolean flag for trade balance
7. **Entity Type** - Classification as 'country' or 'aggregate'
8. **Data Quality Flags** - Tracking and audit metadata

## 🔍 Sample Queries

### Top 10 CO2 Emitters (2024)

```sql
SELECT entity, annual_co2_emissions, code
FROM co2_emissions
WHERE year = 2024 AND entity_type = 'country'
ORDER BY annual_co2_emissions DESC
LIMIT 10;
```

### Renewable Energy Adoption Trends

```sql
SELECT entity, year, pct_renewable, pct_fossil
FROM electricity_production
WHERE entity IN ('United States', 'China', 'Germany', 'India')
  AND year >= 2000
ORDER BY entity, year;
```

### Net Energy Exporters

```sql
SELECT entity, production_based_energy, consumption_based_energy, net_energy_trade_twh
FROM energy_prod_cons
WHERE is_net_exporter = TRUE AND year = 2020
ORDER BY net_energy_trade_twh DESC
LIMIT 10;
```

## 📈 Results & Achievements

- ✅ **39,388 records** processed successfully
- ✅ **0 duplicates** found and removed
- ✅ **6,918 empty values** converted to proper NULLs
- ✅ **42 columns** standardized to snake_case
- ✅ **8 new analytical fields** created
- ✅ **100% type validation** - All numeric fields properly typed
- ✅ **Zero data loss** - 100% retention rate

## 🛠️ Technologies Used

- **Python 3.13** - Core programming language
- **Pandas** - Data manipulation and analysis
- **NumPy** - Numerical computing
- **JSON** - Metadata parsing
- **SQL** - Database integration (PostgreSQL/MySQL compatible)

## 📝 Data Sources

- **Global Carbon Budget (2025)** - CO2 emissions data
- **Ember (2025)** - Electricity generation statistics
- **Energy Institute - Statistical Review (2025)** - Energy production data
- **EXIOBASE v3.8.2** - Trade-adjusted energy consumption
- **NYMEX** - Natural gas futures prices (Dutch TTF)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

- **Author**: Jasseur Chibani && Oubaid Beldi

## 🙏 Acknowledgments

- Global Carbon Project for comprehensive emissions data
- Ember for detailed electricity generation statistics
- Energy Institute for long-term energy production data
- Our World in Data for data processing and standardization

---

**Last Updated**: November 18, 2025
**Pipeline Version**: 1.0
**Data Quality Certification**: PASSED ✓
