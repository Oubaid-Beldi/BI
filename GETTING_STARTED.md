# 🚀 Getting Started

Quick guide to run this Energy & Environmental Data ETL Pipeline project after cloning.

---

## 📥 Clone the Repository

```bash
git clone https://github.com/Oubaid-Beldi/BI.git
cd BI
```

---

## ⚡ Quick Start (2 Steps)

### Step 1: Run ETL Pipeline (Clean the Data)

```bash
# Install Python dependencies
pip install pandas numpy

# Run the ETL pipeline
python3 et_analysis_and_execution.py
```

**What this does:**
- Loads 5 raw CSV files
- Cleans and transforms the data
- Creates `cleaned_data/` folder with 5 cleaned CSV files
- Generates execution logs and reports

**Time:** ~10 seconds

### Step 2: Set Up PostgreSQL Database

```bash
# Make scripts executable (first time only)
chmod +x setup_database.sh load_data.sh status.sh

# Run one-command setup
./setup_database.sh
```

**What this does:**
- Starts PostgreSQL container in Docker
- Creates database schema
- Loads all 39,388 rows of cleaned data
- Verifies data integrity

**Time:** ~30 seconds

**✅ Done! Your database is ready.**

---

## 📋 Prerequisites

Before running the project, make sure you have:

- **Python 3.13+** ([download](https://www.python.org/downloads/))
- **Docker & Docker Compose** ([install guide](https://docs.docker.com/get-docker/))
- **Git** (for cloning)

### Install Docker (if needed)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
sudo usermod -aG docker $USER  # Add your user to docker group
# Log out and back in for group changes to take effect
```

**macOS:**
```bash
brew install docker docker-compose
```

**Windows:**
- Download Docker Desktop from https://www.docker.com/products/docker-desktop

---

## 🔍 Verify Everything Works

### After Step 1 (ETL):
```bash
# Check cleaned data files
ls -lh cleaned_data/

# View summary report
cat cleaned_data/cleaning_summary_report.txt
```

You should see 5 CSV files:
- `co2_emissions_cleaned.csv` (29,384 rows)
- `electricity_production_cleaned.csv` (6,917 rows)
- `oil_production_cleaned.csv` (750 rows)
- `energy_prod_cons_cleaned.csv` (1,113 rows)
- `nymex_gas_prices_cleaned.csv` (1,224 rows)

### After Step 2 (Database):
```bash
# Check database status
./status.sh

# Or verify using Makefile
make verify
```

Expected output shows all 5 tables loaded with correct row counts.

---

## 🔌 Connect to the Database

### Method 1: PostgreSQL CLI

```bash
# Quick connect
make connect

# Or directly
docker exec -it energy_db psql -U energy_user -d energy_environmental_db
```

### Method 2: Python

```python
import pandas as pd
from sqlalchemy import create_engine

# Create connection
engine = create_engine('postgresql://energy_user:energy_pass_2025@localhost:5432/energy_environmental_db')

# Query data
df = pd.read_sql('SELECT * FROM co2_emissions LIMIT 10', engine)
print(df)
```

### Connection Details:
```
Host:     localhost
Port:     5432
Database: energy_environmental_db
User:     energy_user
Password: energy_pass_2025
```

---

## 📊 Try Some Sample Queries

After connecting (`make connect`), try:

```sql
-- Top 10 CO2 emitters in 2024
SELECT entity, annual_co2_emissions, code
FROM co2_emissions
WHERE year = 2024 AND entity_type = 'country'
ORDER BY annual_co2_emissions DESC
LIMIT 10;

-- Countries with highest renewable energy percentage
SELECT entity, year, pct_renewable, total_electricity_twh
FROM electricity_production
WHERE year = 2024 AND entity_type = 'country'
ORDER BY pct_renewable DESC
LIMIT 10;
```

More sample queries in `DATABASE_SETUP.md`

---

## 🛠️ Useful Commands

```bash
# ETL
python3 et_analysis_and_execution.py    # Run data cleaning

# Database Management
./setup_database.sh                     # Complete database setup
./status.sh                             # Check database health
make help                               # See all available commands
make start                              # Start database
make stop                               # Stop database
make connect                            # Connect to database
make verify                             # Verify data integrity
make backup                             # Backup database
```

---

## 🐛 Troubleshooting

### Problem: Python packages not found
```bash
pip install pandas numpy
# or
pip3 install pandas numpy
```

### Problem: Docker permission denied
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Problem: Port 5432 already in use
```bash
# Stop existing PostgreSQL
sudo systemctl stop postgresql

# Or change port in docker-compose.yml
ports:
  - "5433:5432"  # Use different port
```

### Problem: Scripts not executable
```bash
chmod +x setup_database.sh load_data.sh status.sh
```

### Problem: Container won't start
```bash
# View logs
docker-compose logs

# Restart
docker-compose down
docker-compose up -d
```

---

## 📁 Project Structure

```
BI/
├── cleaned_data/              # Output from ETL (created after Step 1)
├── sql/                       # Database schema
├── et_analysis_and_execution.py   # Main ETL pipeline ⭐
├── setup_database.sh          # Database setup script ⭐
├── load_data.sh               # Data loader (Bash)
├── load_data.py               # Data loader (Python)
├── status.sh                  # Health check script
├── docker-compose.yml         # Docker configuration
├── Makefile                   # Convenient commands
├── GETTING_STARTED.md         # This file ⭐
├── HOW_TO_RUN.md              # Detailed instructions
├── DATABASE_SETUP.md          # Database guide
└── README.md                  # Full documentation
```

---

## 📚 Documentation

- **GETTING_STARTED.md** (this file) - Quick start guide
- **HOW_TO_RUN.md** - Detailed step-by-step instructions
- **DATABASE_SETUP.md** - Complete database setup and usage guide
- **README.md** - Full project documentation
- **PROJECT_SUMMARY.md** - Executive summary of achievements

---

## ✅ Success Checklist

After cloning and setup, you should have:

- [x] Repository cloned
- [x] Python dependencies installed
- [x] ETL pipeline ran successfully
- [x] 5 cleaned CSV files in `cleaned_data/`
- [x] Docker container running
- [x] Database created and loaded
- [x] 39,388 rows of data accessible
- [x] Can connect to database
- [x] Can run queries

**All checked? You're ready to analyze! 🎉**

---

## 🎯 What's Next?

1. **Explore the data** - Try sample queries
2. **Build visualizations** - Connect to Tableau, Power BI, or Python
3. **Analyze trends** - CO2 emissions, renewable energy adoption
4. **Create dashboards** - Build interactive applications
5. **Advanced analytics** - Time series, predictions, ML models

---

## 🆘 Need Help?

- Check **DATABASE_SETUP.md** for detailed database instructions
- Check **HOW_TO_RUN.md** for detailed setup steps
- Review **README.md** for full project documentation
- Check troubleshooting section above

---

**Questions or Issues?** Open an issue on GitHub!

**Ready to start?** → Run: `python3 et_analysis_and_execution.py`
