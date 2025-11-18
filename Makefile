.PHONY: help setup start stop restart logs clean load verify connect backup

# Default target
help:
	@echo "═══════════════════════════════════════════════════════════"
	@echo "  Energy & Environmental Database - Available Commands"
	@echo "═══════════════════════════════════════════════════════════"
	@echo ""
	@echo "  make setup      - Complete setup: start DB + load data"
	@echo "  make start      - Start PostgreSQL container"
	@echo "  make stop       - Stop PostgreSQL container"
	@echo "  make restart    - Restart PostgreSQL container"
	@echo "  make logs       - View container logs"
	@echo "  make load       - Load data into database"
	@echo "  make verify     - Verify data integrity"
	@echo "  make connect    - Connect to database CLI"
	@echo "  make backup     - Backup database to file"
	@echo "  make clean      - Stop and remove all data (⚠️  destructive)"
	@echo ""

# Complete setup process
setup:
	@echo "🚀 Running complete database setup..."
	@./setup_database.sh

# Start Docker container
start:
	@echo "🐳 Starting PostgreSQL container..."
	@docker-compose up -d
	@echo "✓ Container started. Waiting for database to be ready..."
	@sleep 5
	@docker exec energy_db pg_isready -U energy_user -d energy_environmental_db || (echo "Database not ready yet, waiting..."; sleep 5)
	@echo "✓ Database is ready!"

# Stop container
stop:
	@echo "🛑 Stopping PostgreSQL container..."
	@docker-compose down
	@echo "✓ Container stopped"

# Restart container
restart:
	@echo "🔄 Restarting PostgreSQL container..."
	@docker-compose restart
	@sleep 3
	@echo "✓ Container restarted"

# View logs
logs:
	@docker-compose logs -f

# Load data into database
load:
	@echo "📊 Loading data into database..."
	@./load_data.sh

# Verify data integrity
verify:
	@echo "🔍 Verifying data integrity..."
	@docker exec energy_db psql -U energy_user -d energy_environmental_db -c "\
	SELECT \
	    'co2_emissions' AS table_name, \
	    COUNT(*) AS row_count, \
	    CASE WHEN COUNT(*) = 29384 THEN '✓' ELSE '✗' END AS status \
	FROM co2_emissions \
	UNION ALL \
	SELECT 'electricity_production', COUNT(*), CASE WHEN COUNT(*) = 6917 THEN '✓' ELSE '✗' END FROM electricity_production \
	UNION ALL \
	SELECT 'oil_production', COUNT(*), CASE WHEN COUNT(*) = 750 THEN '✓' ELSE '✗' END FROM oil_production \
	UNION ALL \
	SELECT 'energy_prod_cons', COUNT(*), CASE WHEN COUNT(*) = 1113 THEN '✓' ELSE '✗' END FROM energy_prod_cons \
	UNION ALL \
	SELECT 'nymex_gas_prices', COUNT(*), CASE WHEN COUNT(*) = 1224 THEN '✓' ELSE '✗' END FROM nymex_gas_prices \
	ORDER BY table_name;"

# Connect to database CLI
connect:
	@echo "🔗 Connecting to database..."
	@docker exec -it energy_db psql -U energy_user -d energy_environmental_db

# Backup database
backup:
	@echo "💾 Creating database backup..."
	@docker exec energy_db pg_dump -U energy_user energy_environmental_db > backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✓ Backup created: backup_$(shell date +%Y%m%d_%H%M%S).sql"

# Clean everything (destructive!)
clean:
	@echo "⚠️  WARNING: This will delete all data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🗑️  Removing containers and volumes..."; \
		docker-compose down -v; \
		echo "✓ Cleanup complete"; \
	else \
		echo "Cancelled"; \
	fi
