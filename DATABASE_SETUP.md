# 🚀 PostgreSQL Database Setup Guide

Complete guide to load and run the Energy & Environmental database using Docker.

---

## ⚡ Quick Start (30 seconds)

**One command to set up everything:**

```bash
./setup_database.sh
```

This will automatically:
- ✓ Check Docker installation
- ✓ Verify data files exist
- ✓ Start PostgreSQL container
- ✓ Create database schema
- ✓ Load all 5 datasets (39,388 rows)
- ✓ Verify data integrity

**That's it! Your database is ready to use.**

---

## 📋 Prerequisites

- **Docker** and **Docker Compose** installed
- Cleaned CSV files in `cleaned_data/` directory (run ETL first if missing)
- ~500MB free disk space

### Install Docker (if needed)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# macOS
brew install docker docker-compose

# Or download from: https://docs.docker.com/get-docker/
```

---

## 🎯 Setup Methods

### Method 1: Automated Setup (Recommended)

```bash
./setup_database.sh
```

### Method 2: Using Makefile Commands

```bash
make setup      # Complete setup + data loading
make verify     # Verify data loaded correctly
make connect    # Connect to database CLI
```

See all commands:
```bash
make help
```

### Method 3: Manual Step-by-Step

```bash
# Step 1: Start PostgreSQL container
docker-compose up -d

# Step 2: Wait for database to initialize (10-15 seconds)
sleep 15

# Step 3: Load data (choose one)
./load_data.sh              # Bash script (fast)
python3 load_data.py        # Python script (requires: pip install pandas sqlalchemy psycopg2-binary)

# Step 4: Verify
./status.sh
```

---

## 📊 Database Details

### Connection Information

```
Host:     localhost
Port:     5432
Database: energy_environmental_db
User:     energy_user
Password: energy_pass_2025
```

### Tables Created

| Table | Rows | Description |
|-------|------|-------------|
| `co2_emissions` | 29,384 | Annual CO₂ emissions by country (1750-2024) |
| `electricity_production` | 6,917 | Electricity generation by source with % breakdowns |
| `oil_production` | 750 | Oil production by country (1900-2024) |
| `energy_prod_cons` | 1,113 | Energy production vs consumption with trade data |
| `nymex_gas_prices` | 1,224 | Daily natural gas prices (2017-2022) |
| **Total** | **39,388** | |

All tables include:
- Primary keys (entity, year)
- Proper indexes for fast queries
- Data quality flags and metadata
- Entity type classification (country vs aggregate)

---

## 🔌 Connecting to the Database

### PostgreSQL CLI

```bash
# Quick connect
make connect

# Or directly
docker exec -it energy_db psql -U energy_user -d energy_environmental_db
```

### Python (pandas)

```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://energy_user:energy_pass_2025@localhost:5432/energy_environmental_db')

# Query data
df = pd.read_sql('SELECT * FROM co2_emissions WHERE year = 2024 LIMIT 10', engine)
print(df)
```

### psql from Host (if PostgreSQL client installed)

```bash
psql -h localhost -p 5432 -U energy_user -d energy_environmental_db
# Password: energy_pass_2025
```

### GUI Tools

Use any PostgreSQL client:
- **pgAdmin**: https://www.pgadmin.org/
- **DBeaver**: https://dbeaver.io/
- **TablePlus**: https://tableplus.com/

Connection string:
```
postgresql://energy_user:energy_pass_2025@localhost:5432/energy_environmental_db
```

---

## 🔍 Verify Data Loaded

### Quick Check

```bash
./status.sh
```

### Or Using SQL

```bash
make connect
```

Then run:
```sql
-- Check row counts
SELECT 
    'co2_emissions' AS table_name, 
    COUNT(*) AS row_count 
FROM co2_emissions
UNION ALL
SELECT 'electricity_production', COUNT(*) FROM electricity_production
UNION ALL
SELECT 'oil_production', COUNT(*) FROM oil_production
UNION ALL
SELECT 'energy_prod_cons', COUNT(*) FROM energy_prod_cons
UNION ALL
SELECT 'nymex_gas_prices', COUNT(*) FROM nymex_gas_prices;
```

Expected output:
```
       table_name        | row_count 
-------------------------+-----------
 co2_emissions           |    29384
 electricity_production  |     6917
 energy_prod_cons        |     1113
 nymex_gas_prices        |     1224
 oil_production          |      750
```

---

## 📈 Sample Queries

### Top 10 CO₂ Emitters (2024)

```sql
SELECT entity, annual_co2_emissions, code
FROM co2_emissions
WHERE year = 2024 
  AND entity_type = 'country'
ORDER BY annual_co2_emissions DESC
LIMIT 10;
```

### Countries with Highest Renewable Energy %

```sql
SELECT entity, year, pct_renewable, total_electricity_twh
FROM electricity_production
WHERE year = 2024
  AND entity_type = 'country'
  AND total_electricity_twh > 100  -- Significant producers
ORDER BY pct_renewable DESC
LIMIT 10;
```

### Renewable Energy Trends

```sql
SELECT entity, year, pct_renewable, pct_fossil
FROM electricity_production
WHERE entity IN ('United States', 'China', 'Germany', 'India')
  AND year >= 2010
ORDER BY entity, year;
```

### Energy Trade Balance

```sql
SELECT 
    entity,
    production_based_energy,
    consumption_based_energy,
    net_energy_trade_twh,
    CASE WHEN is_net_exporter THEN 'Exporter' ELSE 'Importer' END as status
FROM energy_prod_cons
WHERE year = 2020
ORDER BY ABS(net_energy_trade_twh) DESC
LIMIT 15;
```

### Comprehensive Energy Profile (Joined Data)

```sql
SELECT 
    co2.entity,
    co2.year,
    co2.annual_co2_emissions / 1000000 as co2_millions_tonnes,
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
ORDER BY co2.annual_co2_emissions DESC
LIMIT 20;
```

---

## 🛠️ Management Commands

### Using Makefile (Recommended)

```bash
make help       # Show all available commands
make start      # Start database container
make stop       # Stop database container
make restart    # Restart database
make logs       # View container logs
make verify     # Verify data integrity
make backup     # Backup database to SQL file
make connect    # Connect to database CLI
make clean      # Remove everything (⚠️ destructive)
```

### Docker Commands

```bash
# Start database
docker-compose up -d

# Stop database
docker-compose down

# Stop and remove all data (⚠️ destructive)
docker-compose down -v

# View logs
docker-compose logs -f

# Check container status
docker ps

# Restart container
docker-compose restart
```

### Backup & Restore

```bash
# Create backup
make backup
# Or manually:
docker exec energy_db pg_dump -U energy_user energy_environmental_db > backup.sql

# Restore from backup
docker exec -i energy_db psql -U energy_user -d energy_environmental_db < backup.sql
```

---

## 🐛 Troubleshooting

### Port 5432 Already in Use

```bash
# Check what's using the port
sudo lsof -i :5432

# Stop existing PostgreSQL
sudo systemctl stop postgresql

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use different host port
```

### Container Won't Start

```bash
# View logs
docker-compose logs

# Remove old container and data, start fresh
docker-compose down -v
docker-compose up -d
```

### Data Files Not Found

```bash
# Check if files exist
ls -lh cleaned_data/*.csv

# If missing, run the ETL pipeline first
python3 et_analysis_and_execution.py
```

### Permission Denied on Scripts

```bash
chmod +x setup_database.sh load_data.sh status.sh
```

### Database Not Ready After Start

Wait a few more seconds for initialization:
```bash
# Check status
docker exec energy_db pg_isready -U energy_user -d energy_environmental_db

# Or just wait and try again
sleep 10
./load_data.sh
```

### Python Dependencies Missing (for load_data.py)

```bash
pip install pandas sqlalchemy psycopg2-binary
```

---

## 🔄 Common Workflows

### Start Database Daily

```bash
make start      # Start in morning
# ... do your work ...
make stop       # Stop when done
```

### Reload Data from Scratch

```bash
make clean      # Remove everything
make setup      # Fresh setup
```

### Reload Data Only (Keep Container)

```bash
# Truncate tables
docker exec -i energy_db psql -U energy_user -d energy_environmental_db << EOF
TRUNCATE TABLE co2_emissions CASCADE;
TRUNCATE TABLE electricity_production CASCADE;
TRUNCATE TABLE oil_production CASCADE;
TRUNCATE TABLE energy_prod_cons CASCADE;
TRUNCATE TABLE nymex_gas_prices CASCADE;
EOF

# Reload data
./load_data.sh
```

### Check Health Regularly

```bash
./status.sh     # Quick health check
make verify     # Detailed verification
```

---

## 📦 Files Overview

```
.
├── docker-compose.yml          # Docker configuration
├── setup_database.sh           # One-command setup ⭐
├── load_data.sh                # Bash data loader
├── load_data.py                # Python data loader
├── status.sh                   # Health check script
├── Makefile                    # Convenient commands
├── DATABASE_SETUP.md           # This file
├── .env.example                # Environment template
└── sql/
    └── 01_create_tables.sql    # Database schema
```

---

## 🔐 Security Notes

- **Default credentials are for development only**
- Change password in production: edit `docker-compose.yml`
- Consider using `.env` file for sensitive data
- Restrict network access in production environments
- Don't commit credentials to version control

---

## 🎓 Next Steps

1. ✅ **Setup Complete** - Your database is running!
2. 🔍 **Explore Data** - Try the sample queries above
3. 📊 **Build Visualizations** - Connect to Tableau, Power BI, or Python
4. 🤖 **Advanced Analytics** - Time series analysis, ML models, predictions
5. 📈 **Create Dashboards** - Build interactive data applications

---

## 📚 Additional Resources

- **ETL Documentation**: `COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md`
- **Project Overview**: `PROJECT_SUMMARY.md`
- **Original Loading Guide**: `DATABASE_LOADING_GUIDE.md`
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Docker Docs**: https://docs.docker.com/

---

## 💡 Tips

1. **Use indexes** - Already created for common queries
2. **EXPLAIN ANALYZE** - Use to optimize slow queries
3. **Materialized views** - Create for frequently-run complex queries
4. **Partition tables** - Consider partitioning by year for better performance
5. **Connection pooling** - Use for production applications

---

## ✅ Success Checklist

After setup, you should have:

- [x] PostgreSQL container running on port 5432
- [x] Database `energy_environmental_db` created
- [x] 5 tables with proper schemas and indexes
- [x] 39,388 rows of data loaded
- [x] Data verified and row counts match
- [x] Able to connect via CLI, Python, or GUI tools

---

**Database Setup Complete! Happy Analyzing! 🎉**

*Last Updated: November 18, 2025*
