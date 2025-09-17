import os
import numpy as np
import pandas as pd
import tqdm
import pathlib
from datetime import datetime
from google_lifetime_value.utils.logger import setup_logger

logger = setup_logger()

def load_data(company):

    """Load and filter transaction data for a specific company."""
    repo_root = pathlib.Path('').resolve() 
    trx_data_filename = repo_root / 'data' / 'transactions.csv.gz'

    processed__trx_dir = repo_root / 'data' / 'processed' / 'transactions'
    processed__trx_dir.mkdir(parents=True, exist_ok=True)

    one_company_data_filename = processed__trx_dir / f'transactions_company_{company}.csv'
    
    if os.path.isfile(one_company_data_filename):
        logger.info(f"Loading existing filtered data for company {company} from {one_company_data_filename}")
        df = pd.read_csv(one_company_data_filename)
    else:
        logger.info(f"Filtering transactions for company {company} from {trx_data_filename}")
        data_list = []
        chunksize = 10**6  # Process 1 million rows at a time

        if not os.path.isfile(trx_data_filename):
            msg = f"Transactions file not found at {trx_data_filename}. Run the download_transactions.sh script first."
            logger.error(msg)
            raise FileNotFoundError(msg)
    
        # Process in chunks to handle large file
        for chunk in tqdm.tqdm(pd.read_csv(trx_data_filename, compression='gzip', chunksize=chunksize)):        
            # Filter for the specified company
            company_chunk = chunk.query(f"company=={company}")          
            if not company_chunk.empty:
                data_list.append(company_chunk)

        # Combine all chunks and save
        if data_list:
               df = pd.concat(data_list, axis=0)
               logger.info(f"Saving filtered data for company {company} to {one_company_data_filename}")
               df.to_csv(one_company_data_filename, index=None)
        else:
            msg = f"No transactions found for company {company} in the dataset."
            logger.error(msg)
            raise ValueError(msg)

    logger.info(f"Loaded {len(df)} transactions for company {company}")
    
    return df

def preprocess(df):
    """Preprocess transaction data to create customer-level features."""
    # Create copy of input dataframe to avoid SettingWithCopyWarning
    orig_df = df.copy()
    
    # Count returns once and keep this information
    returns_by_id = orig_df.loc[orig_df['purchaseamount'] < 0].groupby('id').size().reset_index()
    returns_by_id.columns = ['id', 'return_count']
    
    # Filter out negative purchase amounts
    df = orig_df[orig_df['purchaseamount'] > 0].copy()
    
    # Convert date once
    df.loc[:,'date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    
    # Create a dictionary to store all customer-level aggregations
    customer_data = {}
    
    # Calculate start date for each customer
    start_dates = df.groupby('id')['date'].min()
    df = df.join(start_dates.rename('start_date'), on='id')
    
    # Identify calibration rows (first purchase date)
    calibration_mask = df['date'] == df['start_date']
    calibration_rows = df[calibration_mask]
    
    # Compute calibration values
    calibration_values = calibration_rows.groupby('id')['purchaseamount'].sum()
    customer_data['calibration_value'] = calibration_values
    customer_data['log_calibration_value'] = np.log(calibration_values).astype('float32')
    
    # Calculate holdout values (purchases within one year after start date)
    holdout_mask = ((df['date'] > df['start_date']) & 
                    (df['date'] <= df['start_date'] + np.timedelta64(365, 'D')))
    holdout_values = df[holdout_mask].groupby('id')['purchaseamount'].sum()
    customer_data['holdout_value'] = holdout_values
    
    # Compute calibration attributes (using the highest purchase within first day)
    categorical_features = ['chain', 'dept', 'category', 'brand', 'productmeasure']
    
    # Get first purchase attributes - use first() after sorting by purchaseamount
    calibration_attributes = (calibration_rows
                             .sort_values(['id', 'purchaseamount'], ascending=[True, False])
                             .groupby('id')[categorical_features]
                             .first())
    
    # Combine all customer data into one DataFrame
    result = pd.DataFrame(index=customer_data['calibration_value'].index)
    
    # Add numeric features
    for col, series in customer_data.items():
        result[col] = series
    
    # Add categorical features 
    result = result.join(calibration_attributes)
    
    # Add returns data through merge
    result = result.reset_index().merge(returns_by_id, on='id', how='left').assign(return_count=lambda x: x['return_count'].fillna(0).astype('int64'))
    
    # Fill missing values
    result['holdout_value'] = result['holdout_value'].fillna(0.)
    result[categorical_features] = result[categorical_features].fillna('UNKNOWN')
    
    # Convert to appropriate data types
    result['label'] = result['holdout_value'].astype('float32')
    for col in categorical_features:
        result[col] = result[col].astype('category')
    
    return result

def process(company):    
    """Process transaction data for a company and save customer-level features."""
    logger.info(f"Processing company {company}")
    
    # Load transaction data for this company
    transaction_level_data = load_data(company)
    
    # Process to customer level
    customer_level_data = preprocess(transaction_level_data)
    
    # Set paths relative to repository structure
    repo_root = pathlib.Path('').resolve()
    processed__customers_dir = repo_root / 'data' / 'processed' / 'customers'
    processed__customers_dir.mkdir(parents=True, exist_ok=True)
    
    # Save customer level data
    customer_level_data_file = processed__customers_dir / f'customer_level_data_company_{company}.csv'
    customer_level_data.to_csv(customer_level_data_file, index=None)
    
    logger.info(f"Customer data saved to: {customer_level_data_file}")
    
    return customer_level_data
