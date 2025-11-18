# 🚀 How to Run This Project

Complete instructions to set up and run the Energy & Environmental Data ETL Pipeline with PostgreSQL database.

---

## 📋 What You Need

- **Python 3.13+**
- **Docker & Docker Compose**
- **pandas and numpy** (Python packages)

---

## ⚡ Quick Start (2 Steps)

### Step 1: Run the ETL Pipeline

```bash
# Install dependencies
pip install pandas numpy

# Run the ETL pipeline to clean the data
python3 et_analysis_and_execution.py
```

This will:
- Load 5 raw CSV files
- Clean and transform the data
- Generate 5 cleaned CSV files in `cleaned_data/`
- Create execution logs and reports

**Time: ~10 seconds**

### Step 2: Load Data into PostgreSQL Database

```bash
# One-command setup
./setup_database.sh
```

This will:
- Start PostgreSQL in Docker
- Create database and tables
- Load all cleaned data (39,388 rows)
- Verify everything worked

**Time: ~30 seconds**

**Done! Your database is ready to use.**

---

## 🎯 Detailed Instructions

### Part 1: Data Cleaning (ETL)

1. **Install Python dependencies:**
   ```bash
   pip install pandas numpy
   ```

2. **Run the ETL pipeline:**
   ```bash
   python3 et_analysis_and_execution.py
   ```

3. **Verify output:**
   ```bash
   ls -lh cleaned_data/
   ```
   
   You should see:
   - `co2_emissions_cleaned.csv` (29,384 rows)
   - `electricity_production_cleaned.csv` (6,917 rows)
   - `oil_production_cleaned.csv` (750 rows)
   - `energy_prod_cons_cleaned.csv` (1,113 rows)
   - `nymex_gas_prices_cleaned.csv` (1,224 rows)

### Part 2: Database Setup

1. **Install Docker** (if not already installed):
   - Ubuntu/Debian: `sudo apt-get install docker.io docker-compose`
   - macOS: `brew install docker docker-compose`
   - Or download from: https://docs.docker.com/get-docker/

2. **Run the database setup:**
   ```bash
   ./setup_database.sh
   ```

3. **Check everything is working:**
   ```bash
   ./status.sh
   ```

### Part 3: Access Your Data

**Connect to database:**
```bash
make connect
```

**Run a sample query:**
```sql
SELECT entity, annual_co2_emissions, code
FROM co2_emissions
WHERE year = 2024 AND entity_type = 'country'
ORDER BY annual_co2_emissions DESC
LIMIT 10;
```

**Use Python:**
```python
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('postgresql://energy_user:energy_pass_2025@localhost:5432/energy_environmental_db')
df = pd.read_sql('SELECT * FROM co2_emissions LIMIT 10', engine)
print(df)
```

---

## 📊 What You Get

### After ETL:
- 5 cleaned CSV files (39,388 total rows)
- Execution logs and reports
- Data quality: 99.2%

### After Database Setup:
- PostgreSQL database running on `localhost:5432`
- 5 tables with all cleaned data loaded
- Indexes for fast queries
- Ready for analysis!

---

## 🛠️ Common Commands

```bash
# ETL
python3 et_analysis_and_execution.py    # Run data cleaning

# Database Management
./setup_database.sh                     # Complete database setup
./status.sh                             # Check database health
make start                              # Start database
make stop                               # Stop database
make connect                            # Connect to database
make verify                             # Verify data loaded
make backup                             # Backup database
make help                               # See all commands

# Data Analysis
make connect                            # Open SQL prompt
```

---

## 🔍 Verify Everything Works

### Check ETL Output:
```bash
ls -lh cleaned_data/
cat cleaned_data/cleaning_summary_report.txt
```

### Check Database:
```bash
./status.sh
make verify
```

Expected output shows all tables with correct row counts.

---

## 📚 Documentation

- **DATABASE_SETUP.md** - Complete database setup guide
- **PROJECT_SUMMARY.md** - Project overview and achievements
- **COMPREHENSIVE_ET_PLAN_AND_EXECUTION_REPORT.md** - Detailed ETL documentation
- **README.md** - Full project documentation

---

## 🆘 Troubleshooting

### ETL Issues:

**Missing dependencies:**
```bash
pip install pandas numpy
```

**File not found:**
```bash
# Make sure you're in the project directory
cd /path/to/bi
```

### Database Issues:

**Docker not installed:**
```bash
# See installation instructions in DATABASE_SETUP.md
```

**Port 5432 in use:**
```bash
# Stop existing PostgreSQL
sudo systemctl stop postgresql
```

**Container won't start:**
```bash
# Check logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

**Data not loading:**
```bash
# Make sure ETL ran first
python3 et_analysis_and_execution.py

# Then reload data
./load_data.sh
```

---

## ✅ Success Checklist

- [ ] Python 3.13+ installed
- [ ] pandas and numpy installed
- [ ] Docker and Docker Compose installed
- [ ] Ran `python3 et_analysis_and_execution.py`
- [ ] Cleaned data files exist in `cleaned_data/`
- [ ] Ran `./setup_database.sh`
- [ ] Database is running (check with `./status.sh`)
- [ ] Can connect to database (try `make connect`)
- [ ] Data verified (39,388 total rows)

**All checked? You're ready to analyze! 🎉**

---

## 💡 Quick Tips

1. **Run ETL first** - Always clean the data before loading to database
2. **Use `make` commands** - They're shortcuts for common tasks
3. **Check status regularly** - Run `./status.sh` to verify everything is running
4. **Backup before experiments** - Use `make backup` before testing queries
5. **Read the docs** - Check DATABASE_SETUP.md for detailed information

---

## 🎯 Next Steps

1. **Explore the data** - Try the sample queries in DATABASE_SETUP.md
2. **Build visualizations** - Connect to Tableau, Power BI, or use Python
3. **Analyze trends** - CO2 emissions, renewable energy adoption, etc.
4. **Create dashboards** - Build interactive data applications
5. **Advanced analytics** - Time series analysis, predictions, ML models

---

**Questions? Check the documentation files or the troubleshooting sections.**

**Ready to start? → Run:** `python3 et_analysis_and_execution.py`
