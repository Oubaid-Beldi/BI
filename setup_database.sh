#!/bin/bash

# Quick Start Script for PostgreSQL Database Setup
# This script automates the entire database setup and data loading process

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Energy & Environmental Database - Quick Setup            ║"
echo "║  PostgreSQL + Docker                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}✗ Docker is not installed!${NC}"
        echo "Please install Docker first: https://docs.docker.com/get-docker/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is installed${NC}"
}

# Check if Docker Compose is installed
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo -e "${RED}✗ Docker Compose is not installed!${NC}"
        echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker Compose is installed${NC}"
}

# Check if cleaned data files exist
check_data_files() {
    echo -e "${BLUE}Checking for data files...${NC}"
    
    required_files=(
        "cleaned_data/co2_emissions_cleaned.csv"
        "cleaned_data/electricity_production_cleaned.csv"
        "cleaned_data/oil_production_cleaned.csv"
        "cleaned_data/energy_prod_cons_cleaned.csv"
        "cleaned_data/nymex_gas_prices_cleaned.csv"
    )
    
    missing_files=0
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}✗ Missing: $file${NC}"
            missing_files=$((missing_files + 1))
        else
            echo -e "${GREEN}✓ Found: $file${NC}"
        fi
    done
    
    if [ $missing_files -gt 0 ]; then
        echo -e "${RED}✗ Missing $missing_files required data files!${NC}"
        echo "Please run the ETL pipeline first: python3 et_analysis_and_execution.py"
        exit 1
    fi
}

# Start Docker containers
start_docker() {
    echo ""
    echo -e "${BLUE}Starting PostgreSQL container...${NC}"
    
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PostgreSQL container started${NC}"
    else
        echo -e "${RED}✗ Failed to start container${NC}"
        exit 1
    fi
}

# Wait for database to be ready
wait_for_db() {
    echo ""
    echo -e "${YELLOW}⏳ Waiting for database to be ready...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker exec energy_db pg_isready -U energy_user -d energy_environmental_db > /dev/null 2>&1; then
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

# Load data
load_data() {
    echo ""
    echo -e "${BLUE}Loading data into database...${NC}"
    
    ./load_data.sh
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Data loaded successfully!${NC}"
    else
        echo -e "${RED}✗ Failed to load data${NC}"
        exit 1
    fi
}

# Display connection info
show_connection_info() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  Setup Complete! Database is Ready                        ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}Database Connection Information:${NC}"
    echo "  Host:     localhost"
    echo "  Port:     5432"
    echo "  Database: energy_environmental_db"
    echo "  User:     energy_user"
    echo "  Password: energy_pass_2025"
    echo ""
    echo -e "${YELLOW}Quick Access Commands:${NC}"
    echo ""
    echo "  # Connect to database CLI:"
    echo "  docker exec -it energy_db psql -U energy_user -d energy_environmental_db"
    echo ""
    echo "  # View container logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "  # Stop database:"
    echo "  docker-compose down"
    echo ""
    echo "  # Full documentation:"
    echo "  cat DATABASE_SETUP.md"
    echo ""
    echo -e "${GREEN}✓ Ready to analyze data!${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}Step 1: Checking prerequisites...${NC}"
    check_docker
    check_docker_compose
    check_data_files
    
    echo ""
    echo -e "${BLUE}Step 2: Starting Docker container...${NC}"
    start_docker
    
    echo ""
    echo -e "${BLUE}Step 3: Waiting for database...${NC}"
    wait_for_db
    
    echo ""
    echo -e "${BLUE}Step 4: Loading data...${NC}"
    load_data
    
    show_connection_info
}

# Run main function
main
