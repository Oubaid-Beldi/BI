#!/usr/bin/env python3
"""
Energy & Environmental Database - Python Data Loader
Alternative data loading script using Python and pandas
"""

import pandas as pd
from sqlalchemy import create_engine
import sys
from pathlib import Path

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'energy_environmental_db',
    'user': 'energy_user',
    'password': 'energy_pass_2025'
}

# Expected row counts for verification
EXPECTED_COUNTS = {
    'co2_emissions': 29384,
    'electricity_production': 6917,
    'oil_production': 750,
    'energy_prod_cons': 1113,
    'nymex_gas_prices': 1224
}

def create_db_engine():
    """Create SQLAlchemy engine for PostgreSQL"""
    connection_string = (
        f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(connection_string)

def load_dataset(engine, table_name, csv_file, data_dir='cleaned_data'):
    """Load a single CSV file into PostgreSQL table"""
    csv_path = Path(data_dir) / csv_file
    
    if not csv_path.exists():
        print(f"✗ File not found: {csv_path}")
        return False
    
    print(f"Loading {table_name}...", end=' ', flush=True)
    
    try:
        # Read CSV
        df = pd.read_csv(csv_path)
        
        # Convert data types for optimization
        if 'year' in df.columns:
            df['year'] = df['year'].astype('int16')
        if 'last_updated' in df.columns:
            df['last_updated'] = pd.to_datetime(df['last_updated'], errors='coerce')
        if 'is_net_exporter' in df.columns:
            df['is_net_exporter'] = df['is_net_exporter'].astype('bool')
        
        # Load to database
        df.to_sql(
            table_name, 
            engine, 
            if_exists='append',  # Use 'append' since tables are created via SQL
            index=False,
            chunksize=1000,
            method='multi'
        )
        
        print(f"✓ Loaded {len(df):,} rows")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def verify_data(engine):
    """Verify loaded data counts"""
    print("\n" + "="*50)
    print("Verifying Data Import")
    print("="*50)
    
    query = """
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
    """
    
    try:
        df = pd.read_sql(query, engine)
        
        print("\nActual vs Expected Row Counts:")
        print("-" * 50)
        
        all_match = True
        for _, row in df.iterrows():
            table = row['table_name']
            actual = row['row_count']
            expected = EXPECTED_COUNTS.get(table, 0)
            match = "✓" if actual == expected else "✗"
            
            print(f"{match} {table:25} {actual:>6,} / {expected:>6,}")
            
            if actual != expected:
                all_match = False
        
        return all_match
        
    except Exception as e:
        print(f"✗ Error verifying data: {e}")
        return False

def main():
    """Main execution"""
    print("="*50)
    print("Energy & Environmental Database Data Loader")
    print("Python + Pandas + SQLAlchemy")
    print("="*50)
    print()
    
    # Create database engine
    print("Connecting to PostgreSQL...")
    try:
        engine = create_db_engine()
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT version();")
            version = result.fetchone()[0]
            print(f"✓ Connected to PostgreSQL")
            print(f"  Version: {version.split(',')[0]}")
    except Exception as e:
        print(f"✗ Failed to connect to database: {e}")
        print("\nMake sure PostgreSQL is running:")
        print("  docker-compose up -d")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Loading Data Files")
    print("="*50)
    
    # Define datasets to load
    datasets = {
        'co2_emissions': 'co2_emissions_cleaned.csv',
        'electricity_production': 'electricity_production_cleaned.csv',
        'oil_production': 'oil_production_cleaned.csv',
        'energy_prod_cons': 'energy_prod_cons_cleaned.csv',
        'nymex_gas_prices': 'nymex_gas_prices_cleaned.csv'
    }
    
    # Load each dataset
    success_count = 0
    for table_name, csv_file in datasets.items():
        if load_dataset(engine, table_name, csv_file):
            success_count += 1
    
    print(f"\n✓ Successfully loaded {success_count}/{len(datasets)} datasets")
    
    # Verify data
    if verify_data(engine):
        print("\n✓ All data loaded successfully!")
    else:
        print("\n⚠ Warning: Row count mismatch detected")
    
    print("\n" + "="*50)
    print("Database Connection Info:")
    print("="*50)
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Password: {DB_CONFIG['password']}")
    print("\nConnect with:")
    print(f"  docker exec -it energy_db psql -U {DB_CONFIG['user']} -d {DB_CONFIG['database']}")
    print()

if __name__ == "__main__":
    main()
