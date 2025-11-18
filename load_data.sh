#!/bin/bash

# Energy & Environmental Database - Data Loading Script
# This script loads cleaned CSV files into PostgreSQL running in Docker

set -e

echo "=============================================="
echo "Energy & Environmental Database Data Loader"
echo "=============================================="
echo ""

# Configuration
CONTAINER_NAME="energy_db"
DB_NAME="energy_environmental_db"
DB_USER="energy_user"
PGPASSWORD="energy_pass_2025"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if container is running
check_container() {
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        echo -e "${RED}✗ Container $CONTAINER_NAME is not running!${NC}"
        echo "Please start it with: docker-compose up -d"
        exit 1
    fi
    echo -e "${GREEN}✓ Container $CONTAINER_NAME is running${NC}"
}

# Function to wait for database to be ready
wait_for_db() {
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec $CONTAINER_NAME pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Database is ready!${NC}"
            return 0
        fi
        attempt=$((attempt + 1))
        echo "  Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo -e "${RED}✗ Database did not become ready in time${NC}"
    exit 1
}

# Function to load a CSV file
load_csv() {
    local table_name=$1
    local csv_file=$2
    
    echo -e "${YELLOW}Loading $table_name...${NC}"
    
    docker exec -i $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "\COPY $table_name FROM '/data/$csv_file' WITH (FORMAT csv, HEADER true, NULL '');" 
    
    if [ $? -eq 0 ]; then
        # Get row count
        row_count=$(docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM $table_name;")
        echo -e "${GREEN}✓ Loaded $table_name: $row_count rows${NC}"
    else
        echo -e "${RED}✗ Failed to load $table_name${NC}"
        exit 1
    fi
}

# Function to verify data
verify_data() {
    echo ""
    echo "=============================================="
    echo "Verifying Data Import"
    echo "=============================================="
    
    docker exec $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME -c "
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
    SELECT 'nymex_gas_prices', COUNT(*) FROM nymex_gas_prices
    ORDER BY table_name;
    "
    
    echo ""
    echo -e "${GREEN}Expected row counts:${NC}"
    echo "  co2_emissions: 29,384"
    echo "  electricity_production: 6,917"
    echo "  energy_prod_cons: 1,113"
    echo "  nymex_gas_prices: 1,224"
    echo "  oil_production: 750"
}

# Main execution
echo "Step 1: Checking Docker container..."
check_container

echo ""
echo "Step 2: Waiting for database..."
wait_for_db

echo ""
echo "Step 3: Loading data files..."
echo "=============================================="

# Load each dataset
load_csv "co2_emissions" "co2_emissions_cleaned.csv"
load_csv "electricity_production" "electricity_production_cleaned.csv"
load_csv "oil_production" "oil_production_cleaned.csv"
load_csv "energy_prod_cons" "energy_prod_cons_cleaned.csv"
load_csv "nymex_gas_prices" "nymex_gas_prices_cleaned.csv"

echo ""
echo "Step 4: Verifying data..."
verify_data

echo ""
echo "=============================================="
echo -e "${GREEN}✓ Data loading completed successfully!${NC}"
echo "=============================================="
echo ""
echo "Database Connection Info:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Password: $PGPASSWORD"
echo ""
echo "Connect with: docker exec -it $CONTAINER_NAME psql -U $DB_USER -d $DB_NAME"
echo ""
