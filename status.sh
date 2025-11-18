#!/bin/bash

# Status Check Script - Quick health check for the database setup

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Database Status Check                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Docker
echo -n "Docker:                    "
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
fi

# Check Docker Compose
echo -n "Docker Compose:            "
if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Installed${NC}"
else
    echo -e "${RED}✗ Not installed${NC}"
fi

# Check if container is running
echo -n "PostgreSQL Container:      "
if docker ps | grep -q energy_db; then
    echo -e "${GREEN}✓ Running${NC}"
    CONTAINER_RUNNING=true
else
    echo -e "${RED}✗ Not running${NC}"
    CONTAINER_RUNNING=false
fi

# Check if database is accessible
if [ "$CONTAINER_RUNNING" = true ]; then
    echo -n "Database Connection:       "
    if docker exec energy_db pg_isready -U energy_user -d energy_environmental_db &> /dev/null; then
        echo -e "${GREEN}✓ Ready${NC}"
        DB_READY=true
    else
        echo -e "${RED}✗ Not ready${NC}"
        DB_READY=false
    fi
fi

# Check data files
echo -n "Cleaned Data Files:        "
if [ -d "cleaned_data" ] && [ $(ls -1 cleaned_data/*.csv 2>/dev/null | wc -l) -eq 5 ]; then
    echo -e "${GREEN}✓ All 5 files present${NC}"
else
    echo -e "${RED}✗ Missing files${NC}"
fi

# Check if data is loaded (only if DB is ready)
if [ "$DB_READY" = true ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Data Status"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    docker exec energy_db psql -U energy_user -d energy_environmental_db -t -c "
    SELECT 
        CASE 
            WHEN COUNT(*) = 29384 THEN '✓'
            ELSE '✗'
        END || ' co2_emissions: ' || COUNT(*)::text || ' rows (expected: 29,384)'
    FROM co2_emissions
    UNION ALL
    SELECT 
        CASE 
            WHEN COUNT(*) = 6917 THEN '✓'
            ELSE '✗'
        END || ' electricity_production: ' || COUNT(*)::text || ' rows (expected: 6,917)'
    FROM electricity_production
    UNION ALL
    SELECT 
        CASE 
            WHEN COUNT(*) = 750 THEN '✓'
            ELSE '✗'
        END || ' oil_production: ' || COUNT(*)::text || ' rows (expected: 750)'
    FROM oil_production
    UNION ALL
    SELECT 
        CASE 
            WHEN COUNT(*) = 1113 THEN '✓'
            ELSE '✗'
        END || ' energy_prod_cons: ' || COUNT(*)::text || ' rows (expected: 1,113)'
    FROM energy_prod_cons
    UNION ALL
    SELECT 
        CASE 
            WHEN COUNT(*) = 1224 THEN '✓'
            ELSE '✗'
        END || ' nymex_gas_prices: ' || COUNT(*)::text || ' rows (expected: 1,224)'
    FROM nymex_gas_prices
    " 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo ""
        total=$(docker exec energy_db psql -U energy_user -d energy_environmental_db -t -c "
        SELECT 
            (SELECT COUNT(*) FROM co2_emissions) +
            (SELECT COUNT(*) FROM electricity_production) +
            (SELECT COUNT(*) FROM oil_production) +
            (SELECT COUNT(*) FROM energy_prod_cons) +
            (SELECT COUNT(*) FROM nymex_gas_prices)
        " 2>/dev/null | tr -d ' ')
        
        echo "  Total Records: $total / 39,388"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Quick Actions"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ "$CONTAINER_RUNNING" = false ]; then
    echo ""
    echo "  To start the database:"
    echo "  $ make setup        (complete setup + load data)"
    echo "  $ make start        (just start container)"
elif [ "$DB_READY" = false ]; then
    echo ""
    echo "  Database is starting... wait a moment and check again"
    echo "  $ ./status.sh"
else
    echo ""
    echo "  Database is ready! You can:"
    echo "  $ make connect      (connect to database CLI)"
    echo "  $ make verify       (verify data integrity)"
    echo "  $ make logs         (view container logs)"
fi

echo ""
