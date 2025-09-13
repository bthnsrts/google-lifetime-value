import os
import numpy as np
import pandas as pd
import tqdm
import pathlib
from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
from google_lifetime_value.utils.logger import setup_logger
    
# top 20 companies with most transactions
COMPANYS = [
    10000,
    101200010, 101410010, 101600010, 102100020, 102700020,
    102840020, 103000030, 103338333, 103400030, 103600030,
    103700030, 103800030, 104300040, 104400040, 104470040,
    104900040, 105100050, 105150050, 107800070
]

logger = setup_logger()

def load_data(company):
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
            company_chunk = chunk.query("company=={}".format(company))          

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
  df = df.query('purchaseamount>0').copy()
  df.loc[:,'date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
  df.loc[:,'start_date'] = df.groupby('id')['date'].transform('min')

  # Compute calibration values
  calibration_value = (
      df.query('date==start_date').groupby('id')
      ['purchaseamount'].sum().reset_index())
  calibration_value.columns = ['id', 'calibration_value']

  # Compute holdout values
  one_year_holdout_window_mask = (
      (df['date'] > df['start_date']) &
      (df['date'] <= df['start_date'] + np.timedelta64(365, 'D')))
  holdout_value = (
      df[one_year_holdout_window_mask].groupby('id')
      ['purchaseamount'].sum().reset_index())
  holdout_value.columns = ['id', 'holdout_value']

  # Compute calibration attributes
  calibration_attributes = (
      df.query('date==start_date').sort_values(
          'purchaseamount', ascending=False).groupby('id')[[
              'chain', 'dept', 'category', 'brand', 'productmeasure'
          ]].first().reset_index())

  # Merge dataframes
  customer_level_data = (
      calibration_value.merge(calibration_attributes, how='left',
                              on='id').merge(
                                  holdout_value, how='left', on='id'))
  customer_level_data['holdout_value'] = (
      customer_level_data['holdout_value'].fillna(0.))
  categorical_features = ([
      'chain', 'dept', 'category', 'brand', 'productmeasure'
  ])
  customer_level_data[categorical_features] = (
      customer_level_data[categorical_features].fillna('UNKNOWN'))

  # Specify data types
  customer_level_data['log_calibration_value'] = (
      np.log(customer_level_data['calibration_value']).astype('float32'))
  customer_level_data['chain'] = (
      customer_level_data['chain'].astype('category'))
  customer_level_data['dept'] = (customer_level_data['dept'].astype('category'))
  customer_level_data['brand'] = (
      customer_level_data['brand'].astype('category'))
  customer_level_data['category'] = (
      customer_level_data['category'].astype('category'))
  customer_level_data['label'] = (
      customer_level_data['holdout_value'].astype('float32'))
  return customer_level_data

# %%
def process(company):    
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

with ThreadPool() as p:
    _ = p.map(process, COMPANYS)


