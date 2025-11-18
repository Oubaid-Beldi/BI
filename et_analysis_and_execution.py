"""
Comprehensive ETL Analysis and Execution Plan
Data Cleaning and Transformation for Energy & Environmental Datasets
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PART 1: EXTRACT - Load all data and metadata
# ============================================================================

def load_data_and_metadata():
    """Load all CSV files and their corresponding JSON metadata"""
    
    data_dir = Path('.')
    
    datasets = {
        'co2_emissions': {
            'csv': 'annual-co2-emissions-per-country.csv',
            'metadata': 'annual-co2-emissions-per-country.metadata.json'
        },
        'electricity_production': {
            'csv': 'electricity-prod-source-stacked.csv',
            'metadata': 'electricity-prod-source-stacked.metadata.json'
        },
        'oil_production': {
            'csv': 'oil-production-by-country.csv',
            'metadata': 'oil-production-by-country.metadata.json'
        },
        'energy_prod_cons': {
            'csv': 'production-vs-consumption-energy.csv',
            'metadata': 'production-vs-consumption-energy.metadata.json'
        },
        'nymex_gas_prices': {
            'csv': 'NYMEX_DL_TTF1 1D.csv',
            'metadata': None  # No metadata file
        }
    }
    
    loaded_data = {}
    
    for key, files in datasets.items():
        print(f"\n{'='*60}")
        print(f"Loading: {key}")
        print(f"{'='*60}")
        
        # Load CSV
        try:
            df = pd.read_csv(files['csv'])
            print(f"✓ CSV loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Load metadata if exists
            metadata = None
            if files['metadata']:
                with open(files['metadata'], 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                print(f"✓ Metadata loaded")
            else:
                print(f"⚠ No metadata file available")
            
            loaded_data[key] = {
                'data': df,
                'metadata': metadata,
                'filename': files['csv']
            }
            
        except Exception as e:
            print(f"✗ Error loading {key}: {e}")
    
    return loaded_data


# ============================================================================
# PART 2: ANALYZE - Detect all data quality issues
# ============================================================================

def analyze_data_quality(loaded_data):
    """Comprehensive data quality analysis"""
    
    issues = {}
    
    for dataset_name, dataset in loaded_data.items():
        df = dataset['data']
        metadata = dataset['metadata']
        
        print(f"\n{'='*60}")
        print(f"ANALYZING: {dataset_name}")
        print(f"{'='*60}")
        
        dataset_issues = {
            'summary': {},
            'column_issues': {},
            'cross_column_issues': []
        }
        
        # Basic summary
        dataset_issues['summary'] = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'duplicate_rows': df.duplicated().sum()
        }
        
        print(f"\nDataset Summary:")
        print(f"  Rows: {dataset_issues['summary']['total_rows']:,}")
        print(f"  Columns: {dataset_issues['summary']['total_columns']}")
        print(f"  Duplicates: {dataset_issues['summary']['duplicate_rows']}")
        print(f"  Memory: {dataset_issues['summary']['memory_usage']:.2f} MB")
        
        # Per-column analysis
        print(f"\nColumn-by-Column Analysis:")
        print(f"{'Column':<40} {'Type':<15} {'Missing':<10} {'Unique':<10}")
        print("-" * 80)
        
        for col in df.columns:
            col_issues = analyze_column(df, col, metadata)
            dataset_issues['column_issues'][col] = col_issues
            
            print(f"{col[:38]:<40} {str(df[col].dtype):<15} {col_issues['missing_count']:<10} {col_issues['unique_count']:<10}")
        
        # Cross-column issues
        if 'Entity' in df.columns and 'Code' in df.columns:
            # Check entity-code consistency
            entity_code_map = df.groupby('Entity')['Code'].nunique()
            inconsistent = entity_code_map[entity_code_map > 1]
            if len(inconsistent) > 0:
                dataset_issues['cross_column_issues'].append({
                    'type': 'entity_code_mismatch',
                    'description': f'{len(inconsistent)} entities have multiple codes',
                    'affected_entities': inconsistent.index.tolist()[:10]
                })
        
        issues[dataset_name] = dataset_issues
    
    return issues


def analyze_column(df, col, metadata):
    """Analyze individual column for issues"""
    
    col_data = df[col]
    
    issues = {
        'column_name': col,
        'dtype': str(col_data.dtype),
        'missing_count': col_data.isna().sum(),
        'missing_percent': (col_data.isna().sum() / len(col_data)) * 100,
        'unique_count': col_data.nunique(),
        'zero_count': (col_data == 0).sum() if pd.api.types.is_numeric_dtype(col_data) else 0,
        'empty_string_count': (col_data == '').sum() if col_data.dtype == 'object' else 0,
        'issues': []
    }
    
    # Check for wrong dtype
    if metadata and 'columns' in metadata:
        for meta_col_name, meta_col_info in metadata['columns'].items():
            if meta_col_name in col or col in meta_col_name:
                expected_type = meta_col_info.get('type', '')
                if expected_type == 'Numeric' and col_data.dtype == 'object':
                    issues['issues'].append({
                        'type': 'wrong_dtype',
                        'expected': 'numeric',
                        'actual': str(col_data.dtype)
                    })
    
    # Check for outliers in numeric columns
    if pd.api.types.is_numeric_dtype(col_data):
        q1 = col_data.quantile(0.25)
        q3 = col_data.quantile(0.75)
        iqr = q3 - q1
        outliers = ((col_data < (q1 - 3 * iqr)) | (col_data > (q3 + 3 * iqr))).sum()
        if outliers > 0:
            issues['outliers'] = outliers
            issues['min'] = col_data.min()
            issues['max'] = col_data.max()
            issues['mean'] = col_data.mean()
            issues['median'] = col_data.median()
    
    # Check for special values
    if col_data.dtype == 'object':
        special_values = []
        if (col_data == 'NaN').any():
            special_values.append('string_NaN')
        if (col_data == 'nan').any():
            special_values.append('string_nan')
        if (col_data == 'null').any():
            special_values.append('string_null')
        if special_values:
            issues['special_values'] = special_values
    
    return issues


# ============================================================================
# PART 3: GENERATE ET PLAN
# ============================================================================

def generate_et_plan(loaded_data, issues):
    """Generate comprehensive Extract-Transform plan"""
    
    plan = {
        'metadata': {
            'plan_created': datetime.now().isoformat(),
            'total_datasets': len(loaded_data),
            'plan_version': '1.0'
        },
        'datasets': {}
    }
    
    print("\n" + "="*80)
    print("COMPREHENSIVE ET (EXTRACT + TRANSFORM) PLAN")
    print("="*80)
    
    for dataset_name, dataset in loaded_data.items():
        df = dataset['data']
        metadata = dataset['metadata']
        dataset_issues = issues[dataset_name]
        
        dataset_plan = generate_dataset_plan(df, metadata, dataset_issues, dataset_name)
        plan['datasets'][dataset_name] = dataset_plan
    
    # Generate integration plan
    plan['integration'] = generate_integration_plan(loaded_data)
    
    return plan


def generate_dataset_plan(df, metadata, dataset_issues, dataset_name):
    """Generate plan for individual dataset"""
    
    print(f"\n{'='*60}")
    print(f"PLAN FOR: {dataset_name.upper()}")
    print(f"{'='*60}")
    
    plan = {
        'extraction': {},
        'cleaning': {},
        'transformation': {},
        'validation': {},
        'final_schema': {}
    }
    
    # EXTRACTION
    plan['extraction'] = {
        'source_file': dataset_name,
        'encoding': 'utf-8',
        'rows': len(df),
        'columns': list(df.columns)
    }
    
    # CLEANING
    cleaning_steps = []
    
    # 1. Handle missing codes
    if 'Code' in df.columns:
        missing_codes = dataset_issues['column_issues']['Code']['empty_string_count']
        if missing_codes > 0:
            cleaning_steps.append({
                'step': 'fill_missing_codes',
                'column': 'Code',
                'action': 'Replace empty strings with NULL',
                'affected_rows': missing_codes,
                'reason': 'Regional aggregates (like "Africa", "World") do not have ISO codes'
            })
    
    # 2. Standardize column names
    cleaning_steps.append({
        'step': 'standardize_column_names',
        'action': 'Convert to snake_case, remove special characters',
        'columns': [col for col in df.columns if ' ' in col or '(' in col or '₂' in col]
    })
    
    # 3. Handle numeric columns with wrong dtype
    for col, col_issues in dataset_issues['column_issues'].items():
        if col_issues['issues']:
            for issue in col_issues['issues']:
                if issue['type'] == 'wrong_dtype':
                    cleaning_steps.append({
                        'step': 'convert_dtype',
                        'column': col,
                        'from': issue['actual'],
                        'to': 'float64',
                        'action': 'Convert to numeric, coerce errors to NaN'
                    })
    
    # 4. Handle special values
    for col, col_issues in dataset_issues['column_issues'].items():
        if 'special_values' in col_issues:
            cleaning_steps.append({
                'step': 'handle_special_values',
                'column': col,
                'special_values': col_issues['special_values'],
                'action': 'Replace string "NaN" with actual NaN'
            })
    
    # 5. Remove duplicates
    if dataset_issues['summary']['duplicate_rows'] > 0:
        cleaning_steps.append({
            'step': 'remove_duplicates',
            'action': 'Drop exact duplicate rows',
            'affected_rows': dataset_issues['summary']['duplicate_rows']
        })
    
    # 6. Date standardization
    if 'time' in df.columns:
        cleaning_steps.append({
            'step': 'standardize_dates',
            'column': 'time',
            'action': 'Parse ISO datetime to datetime64, extract date only',
            'target_format': 'YYYY-MM-DD'
        })
    elif 'Year' in df.columns:
        cleaning_steps.append({
            'step': 'validate_years',
            'column': 'Year',
            'action': 'Ensure all years are integers between 1750 and 2025',
            'current_range': f"{df['Year'].min()} to {df['Year'].max()}"
        })
    
    plan['cleaning'] = cleaning_steps
    
    # TRANSFORMATION
    transformation_steps = []
    
    # Add metadata-based transformations
    if metadata:
        transformation_steps.append({
            'step': 'add_metadata_columns',
            'action': 'Add source, citation, and data quality flags',
            'metadata_fields': ['citation', 'lastUpdated']
        })
    
    # Derive new columns
    if dataset_name == 'electricity_production':
        transformation_steps.append({
            'step': 'calculate_totals',
            'action': 'Sum all electricity sources to get total generation',
            'new_column': 'total_electricity_twh'
        })
        transformation_steps.append({
            'step': 'calculate_percentages',
            'action': 'Calculate percentage contribution of each source',
            'new_columns': ['pct_renewable', 'pct_fossil', 'pct_nuclear']
        })
    
    if dataset_name == 'energy_prod_cons':
        transformation_steps.append({
            'step': 'calculate_difference',
            'action': 'Calculate net trade (production - consumption)',
            'new_column': 'net_energy_trade_twh'
        })
    
    # Normalize entity names
    transformation_steps.append({
        'step': 'normalize_entities',
        'action': 'Standardize country names, flag aggregates vs individual countries',
        'new_column': 'entity_type'
    })
    
    plan['transformation'] = transformation_steps
    
    # VALIDATION
    if metadata and 'columns' in metadata:
        validation_rules = []
        for col_name, col_meta in metadata['columns'].items():
            if 'unit' in col_meta:
                validation_rules.append({
                    'column': col_name,
                    'rule': 'check_unit_consistency',
                    'expected_unit': col_meta['unit']
                })
            if 'timespan' in col_meta:
                validation_rules.append({
                    'column': 'Year',
                    'rule': 'check_timespan',
                    'expected_range': col_meta['timespan']
                })
        plan['validation'] = validation_rules
    
    # FINAL SCHEMA
    plan['final_schema'] = generate_final_schema(df, metadata, dataset_name)
    
    # Print summary
    print(f"\nCleaning Steps: {len(cleaning_steps)}")
    for i, step in enumerate(cleaning_steps, 1):
        print(f"  {i}. {step['step']}: {step['action']}")
    
    print(f"\nTransformation Steps: {len(transformation_steps)}")
    for i, step in enumerate(transformation_steps, 1):
        print(f"  {i}. {step['step']}: {step['action']}")
    
    return plan


def generate_final_schema(df, metadata, dataset_name):
    """Generate final cleaned schema"""
    
    schema = {}
    
    # Base columns (standardized)
    if 'Entity' in df.columns:
        schema['entity'] = {'type': 'string', 'nullable': False, 'description': 'Country or region name'}
    if 'Code' in df.columns:
        schema['code'] = {'type': 'string', 'nullable': True, 'description': 'ISO 3166-1 alpha-3 code'}
    if 'Year' in df.columns:
        schema['year'] = {'type': 'int16', 'nullable': False, 'description': 'Year of observation'}
    if 'time' in df.columns:
        schema['date'] = {'type': 'datetime64', 'nullable': False, 'description': 'Date of observation'}
    
    # Data columns (from metadata)
    if metadata and 'columns' in metadata:
        for col_name, col_meta in metadata['columns'].items():
            clean_name = col_name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            schema[clean_name] = {
                'type': 'float32' if col_meta.get('type') == 'Numeric' else 'string',
                'nullable': True,
                'unit': col_meta.get('unit', ''),
                'description': col_meta.get('descriptionShort', '')
            }
    
    return schema


def generate_integration_plan(loaded_data):
    """Generate plan for joining/merging datasets"""
    
    print(f"\n{'='*60}")
    print("INTEGRATION PLAN")
    print(f"{'='*60}")
    
    integration_plan = {
        'joins': [],
        'common_dimensions': [],
        'recommendations': []
    }
    
    # Identify common dimensions
    common_dims = {}
    for name, dataset in loaded_data.items():
        df = dataset['data']
        if 'Entity' in df.columns and 'Year' in df.columns:
            common_dims[name] = ['Entity', 'Year', 'Code']
    
    integration_plan['common_dimensions'] = common_dims
    
    # Suggest joins
    energy_datasets = ['co2_emissions', 'electricity_production', 'oil_production', 'energy_prod_cons']
    available_energy = [d for d in energy_datasets if d in loaded_data]
    
    if len(available_energy) >= 2:
        integration_plan['joins'].append({
            'type': 'inner_join',
            'datasets': available_energy,
            'on': ['entity', 'code', 'year'],
            'description': 'Join all energy datasets by country and year',
            'result_name': 'integrated_energy_data'
        })
    
    # Recommendations
    integration_plan['recommendations'] = [
        'Create a master dimension table for countries with codes and regions',
        'Create a time dimension table for years with metadata',
        'Consider star schema with fact tables for metrics',
        'NYMEX gas prices are time-series data at daily level - keep separate or aggregate to yearly'
    ]
    
    print("\nCommon Dimensions Found:")
    for dataset, dims in common_dims.items():
        print(f"  {dataset}: {', '.join(dims)}")
    
    print("\nRecommended Joins:")
    for join in integration_plan['joins']:
        print(f"  - {join['description']}")
        print(f"    Datasets: {', '.join(join['datasets'])}")
        print(f"    Join on: {', '.join(join['on'])}")
    
    return integration_plan


# ============================================================================
# PART 4: EXECUTE CLEANING AND TRANSFORMATION
# ============================================================================

def execute_et_plan(loaded_data, plan):
    """Execute the ET plan and clean all datasets"""
    
    print("\n" + "="*80)
    print("EXECUTING ET PLAN")
    print("="*80)
    
    cleaned_data = {}
    execution_log = []
    
    for dataset_name, dataset in loaded_data.items():
        print(f"\n{'='*60}")
        print(f"CLEANING: {dataset_name.upper()}")
        print(f"{'='*60}")
        
        df = dataset['data'].copy()
        dataset_plan = plan['datasets'][dataset_name]
        dataset_log = []
        
        # Execute cleaning steps
        for step in dataset_plan['cleaning']:
            try:
                df, step_log = execute_cleaning_step(df, step)
                dataset_log.append(step_log)
                print(f"✓ {step['step']}: {step_log['message']}")
            except Exception as e:
                error_log = {
                    'step': step['step'],
                    'status': 'error',
                    'message': str(e)
                }
                dataset_log.append(error_log)
                print(f"✗ {step['step']}: {e}")
        
        # Execute transformation steps
        for step in dataset_plan['transformation']:
            try:
                df, step_log = execute_transformation_step(df, step, dataset_name)
                dataset_log.append(step_log)
                print(f"✓ {step['step']}: {step_log['message']}")
            except Exception as e:
                error_log = {
                    'step': step['step'],
                    'status': 'error',
                    'message': str(e)
                }
                dataset_log.append(error_log)
                print(f"✗ {step['step']}: {e}")
        
        cleaned_data[dataset_name] = df
        execution_log.append({
            'dataset': dataset_name,
            'original_rows': len(dataset['data']),
            'cleaned_rows': len(df),
            'steps': dataset_log
        })
    
    return cleaned_data, execution_log


def execute_cleaning_step(df, step):
    """Execute individual cleaning step"""
    
    step_type = step['step']
    
    if step_type == 'fill_missing_codes':
        col = step['column']
        before = (df[col] == '').sum()
        df[col] = df[col].replace('', np.nan)
        return df, {
            'step': step_type,
            'status': 'success',
            'message': f"Replaced {before} empty strings with NaN in {col}"
        }
    
    elif step_type == 'standardize_column_names':
        old_cols = df.columns.tolist()
        new_cols = []
        for col in old_cols:
            # Convert to snake_case
            new_col = col.lower()
            # Remove special characters
            new_col = new_col.replace('₂', '2')
            new_col = new_col.replace('(', '').replace(')', '')
            new_col = new_col.replace(' - ', '_')
            new_col = new_col.replace(' ', '_')
            new_col = new_col.replace('-', '_')
            new_col = new_col.replace('__', '_')
            new_col = new_col.strip('_')
            new_cols.append(new_col)
        
        df.columns = new_cols
        return df, {
            'step': step_type,
            'status': 'success',
            'message': f"Standardized {len(old_cols)} column names"
        }
    
    elif step_type == 'convert_dtype':
        col = step['column']
        # Find the column with new name (after standardization)
        matching_cols = [c for c in df.columns if col.lower().replace(' ', '_') in c]
        if matching_cols:
            col = matching_cols[0]
            before_type = df[col].dtype
            df[col] = pd.to_numeric(df[col], errors='coerce')
            return df, {
                'step': step_type,
                'status': 'success',
                'message': f"Converted {col} from {before_type} to numeric"
            }
    
    elif step_type == 'handle_special_values':
        col = step['column']
        if col in df.columns:
            before = len(df)
            df[col] = df[col].replace(['NaN', 'nan', 'null', 'NULL'], np.nan)
            return df, {
                'step': step_type,
                'status': 'success',
                'message': f"Replaced special values in {col}"
            }
    
    elif step_type == 'remove_duplicates':
        before = len(df)
        df = df.drop_duplicates()
        removed = before - len(df)
        return df, {
            'step': step_type,
            'status': 'success',
            'message': f"Removed {removed} duplicate rows"
        }
    
    elif step_type == 'standardize_dates':
        col = step['column']
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            df['date'] = df[col].dt.date
            return df, {
                'step': step_type,
                'status': 'success',
                'message': f"Standardized dates in {col}, created 'date' column"
            }
    
    elif step_type == 'validate_years':
        col = 'year' if 'year' in df.columns else 'Year'
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            invalid = df[(df[col] < 1750) | (df[col] > 2025)][col].count()
            df = df[(df[col] >= 1750) & (df[col] <= 2025)]
            return df, {
                'step': step_type,
                'status': 'success',
                'message': f"Validated years, removed {invalid} invalid entries"
            }
    
    return df, {
        'step': step_type,
        'status': 'skipped',
        'message': 'Step not implemented or not applicable'
    }


def execute_transformation_step(df, step, dataset_name):
    """Execute individual transformation step"""
    
    step_type = step['step']
    
    if step_type == 'add_metadata_columns':
        df['data_source'] = dataset_name
        df['data_quality_flag'] = 'clean'
        df['last_updated'] = datetime.now().date()
        return df, {
            'step': step_type,
            'status': 'success',
            'message': 'Added metadata columns'
        }
    
    elif step_type == 'calculate_totals':
        # Find all electricity generation columns
        gen_cols = [c for c in df.columns if 'twh' in c and c not in ['oil_production_twh']]
        if gen_cols:
            df['total_electricity_twh'] = df[gen_cols].sum(axis=1)
            return df, {
                'step': step_type,
                'status': 'success',
                'message': f'Calculated total from {len(gen_cols)} sources'
            }
    
    elif step_type == 'calculate_percentages':
        if 'total_electricity_twh' in df.columns:
            renewable_cols = [c for c in df.columns if any(x in c for x in ['solar', 'wind', 'hydro', 'bioenergy', 'other_renewables'])]
            fossil_cols = [c for c in df.columns if any(x in c for x in ['coal', 'gas', 'oil'])]
            nuclear_cols = [c for c in df.columns if 'nuclear' in c]
            
            if renewable_cols:
                df['pct_renewable'] = (df[renewable_cols].sum(axis=1) / df['total_electricity_twh'] * 100).round(2)
            if fossil_cols:
                df['pct_fossil'] = (df[fossil_cols].sum(axis=1) / df['total_electricity_twh'] * 100).round(2)
            if nuclear_cols:
                df['pct_nuclear'] = (df[nuclear_cols].sum(axis=1) / df['total_electricity_twh'] * 100).round(2)
            
            return df, {
                'step': step_type,
                'status': 'success',
                'message': 'Calculated percentage contributions'
            }
    
    elif step_type == 'calculate_difference':
        if 'consumption_based_energy' in df.columns and 'production_based_energy' in df.columns:
            df['net_energy_trade_twh'] = (df['production_based_energy'] - df['consumption_based_energy']).round(2)
            df['is_net_exporter'] = df['net_energy_trade_twh'] > 0
            return df, {
                'step': step_type,
                'status': 'success',
                'message': 'Calculated net energy trade'
            }
    
    elif step_type == 'normalize_entities':
        if 'entity' in df.columns:
            # Flag aggregates vs countries
            aggregates = ['World', 'Africa', 'Asia', 'Europe', 'OECD', 'EU', 'ASEAN']
            df['entity_type'] = df['entity'].apply(
                lambda x: 'aggregate' if any(agg in str(x) for agg in aggregates) else 'country'
            )
            return df, {
                'step': step_type,
                'status': 'success',
                'message': 'Added entity_type classification'
            }
    
    return df, {
        'step': step_type,
        'status': 'skipped',
        'message': 'Step not implemented or not applicable'
    }


# ============================================================================
# PART 5: SAVE RESULTS AND GENERATE REPORTS
# ============================================================================

def save_cleaned_data(cleaned_data, execution_log):
    """Save cleaned datasets and generate reports"""
    
    print("\n" + "="*80)
    print("SAVING CLEANED DATA")
    print("="*80)
    
    output_dir = Path('./cleaned_data')
    output_dir.mkdir(exist_ok=True)
    
    for dataset_name, df in cleaned_data.items():
        output_file = output_dir / f"{dataset_name}_cleaned.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Saved: {output_file} ({len(df)} rows, {len(df.columns)} columns)")
    
    # Save execution log
    log_file = output_dir / 'execution_log.json'
    with open(log_file, 'w') as f:
        json.dump(execution_log, f, indent=2, default=str)
    print(f"✓ Saved: {log_file}")
    
    # Generate summary report
    generate_summary_report(cleaned_data, execution_log, output_dir)


def generate_summary_report(cleaned_data, execution_log, output_dir):
    """Generate comprehensive summary report"""
    
    report_file = output_dir / 'cleaning_summary_report.txt'
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("DATA CLEANING AND TRANSFORMATION SUMMARY REPORT\n")
        f.write("="*80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for log_entry in execution_log:
            f.write(f"\n{'='*60}\n")
            f.write(f"Dataset: {log_entry['dataset'].upper()}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Original rows: {log_entry['original_rows']:,}\n")
            f.write(f"Cleaned rows: {log_entry['cleaned_rows']:,}\n")
            f.write(f"Rows removed: {log_entry['original_rows'] - log_entry['cleaned_rows']:,}\n\n")
            
            f.write("Executed Steps:\n")
            for i, step in enumerate(log_entry['steps'], 1):
                status_icon = '✓' if step['status'] == 'success' else '✗' if step['status'] == 'error' else '⊘'
                f.write(f"  {i}. {status_icon} {step['step']}: {step['message']}\n")
            
            # Data sample
            df = cleaned_data[log_entry['dataset']]
            f.write(f"\nFinal columns ({len(df.columns)}):\n")
            for col in df.columns:
                f.write(f"  - {col} ({df[col].dtype})\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*80 + "\n")
    
    print(f"✓ Saved: {report_file}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function"""
    
    print("\n" + "="*80)
    print("DATA CLEANING AND TRANSFORMATION PIPELINE")
    print("Energy & Environmental Datasets ETL")
    print("="*80)
    
    # Step 1: Extract
    print("\n[STEP 1] EXTRACTING DATA...")
    loaded_data = load_data_and_metadata()
    
    # Step 2: Analyze
    print("\n[STEP 2] ANALYZING DATA QUALITY...")
    issues = analyze_data_quality(loaded_data)
    
    # Step 3: Generate Plan
    print("\n[STEP 3] GENERATING ET PLAN...")
    plan = generate_et_plan(loaded_data, issues)
    
    # Save plan
    with open('et_plan.json', 'w') as f:
        json.dump(plan, f, indent=2, default=str)
    print("\n✓ ET Plan saved to: et_plan.json")
    
    # Step 4: Execute
    print("\n[STEP 4] EXECUTING CLEANING AND TRANSFORMATION...")
    cleaned_data, execution_log = execute_et_plan(loaded_data, plan)
    
    # Step 5: Save
    print("\n[STEP 5] SAVING RESULTS...")
    save_cleaned_data(cleaned_data, execution_log)
    
    print("\n" + "="*80)
    print("✓ PIPELINE COMPLETED SUCCESSFULLY")
    print("="*80)
    print("\nCheck the 'cleaned_data' directory for:")
    print("  - Cleaned CSV files")
    print("  - Execution log (JSON)")
    print("  - Summary report (TXT)")
    print("\n")


if __name__ == "__main__":
    main()
