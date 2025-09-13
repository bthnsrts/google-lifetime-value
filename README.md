# 🎯 LTV Prediction with Deep Probabilistic Model

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Kaggle](https://img.shields.io/badge/Dataset-Kaggle-orange.svg)](https://www.kaggle.com/competitions/acquire-valued-shoppers-challenge/data)

Basic implementation of the [paper](https://research.google/pubs/a-deep-probabilistic-model-for-customer-lifetime-value-prediction/) on predicting Customer Lifetime Value (CLV) using deep probabilistic models.

## Setup

### 1. Create and activate virtual environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment

## On Windows
venv\Scripts\activate
## On macOS/Linux
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Download the dataset

You need to have a Kaggle account and API key to download the dataset. If you don't have the API key yet:
1. Go to your Kaggle account settings (https://www.kaggle.com/account)
2. Click "Create New API Token" and save the kaggle.json file
3. Place this file in ~/.kaggle/ directory (create it if it doesn't exist)

```bash
# Make the download script executable and download the script
make download_data
```

### 3. Preprocess the data

```bash
# Preprocess the downloaded data
make preprocess
```

## 📊 Dataset

This project uses the [Acquire Valued Shoppers Challenge dataset](https://www.kaggle.com/competitions/acquire-valued-shoppers-challenge/data) from Kaggle.

### Dataset Explanation

We are provided four relational files:

- **transactions.csv** - Contains transaction history for all customers for a period of at least 1 year prior to their offered incentive.
- **trainHistory.csv** - Contains the incentive offered to each customer and information about the behavioral response to the offer.
- **testHistory.csv** - Contains the incentive offered to each customer but does not include their response (you are predicting the `repeater` column for each id in this file).
- **offers.csv** - Contains information about the offers.

**👉 Only the transactions data will be evaluated for user lifetime value prediction task**

### Fields

#### Transactions
- `id` - An integer representing unique customer
- `chain` - An integer representing a store chain
- `dept` - An aggregate grouping of the Category (e.g., water)
- `category` - The product category (e.g., sparkling water)
- `company` - An id of the company that sells the item
- `brand` - An id of the brand to which the item belongs
- `date` - The date of purchase
- `productsize` - The amount of the product purchase (e.g., 16 oz of water)
- `productmeasure` - The units of the product purchase (e.g., ounces)
- `purchasequantity` - The number of units purchased
- `purchaseamount` - The dollar amount of the purchase


## Preprocessing

Only the top 20 companies with most transaction count are considered to decrease data size (original data is approx. 22GBs of size and pretty cumbersome to play with). For each company, transaction data is splitted (20 different csv files are produced), Then following data is generated;

- `start_date`- The very first date a customer makes transaction
- `calibration_value` - The customer's total purchase amount at his/her start date
- `holdout_value`- Total yearly purchase amount for the customer -excluding start date-
- `calibration_attributes