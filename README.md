# 🎯 LTV Prediction with Deep Probabilistic Model

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Kaggle](https://img.shields.io/badge/Dataset-Kaggle-orange.svg)](https://www.kaggle.com/competitions/acquire-valued-shoppers-challenge/data)

Basic implementation of the [paper](https://research.google/pubs/a-deep-probabilistic-model-for-customer-lifetime-value-prediction/) on predicting Customer Lifetime Value (CLV) using deep probabilistic models.

## 📊 Dataset

This project uses the [Acquire Valued Shoppers Challenge dataset](https://www.kaggle.com/competitions/acquire-valued-shoppers-challenge/data) from Kaggle.

### Dataset Explanation

You are provided four relational files:

- **transactions.csv** - Contains transaction history for all customers for a period of at least 1 year prior to their offered incentive.
- **trainHistory.csv** - Contains the incentive offered to each customer and information about the behavioral response to the offer.
- **testHistory.csv** - Contains the incentive offered to each customer but does not include their response (you are predicting the `repeater` column for each id in this file).
- **offers.csv** - Contains information about the offers.

### Fields

All fields are anonymized and categorized to protect customer and sales information. The specific meanings of the fields will not be provided (so don't bother asking). Part of the challenge is learning the taxonomy of items in a data-driven way.

#### History
- `id` - A unique id representing a customer
- `chain` - An integer representing a store chain
- `offer` - An id representing a certain offer
- `market` - An id representing a geographical region
- `repeattrips` - The number of times the customer made a repeat purchase
- `repeater` - A boolean, equal to `repeattrips > 0`
- `offerdate` - The date a customer received the offer

#### Transactions
- `id` - See above
- `chain` - See above
- `dept` - An aggregate grouping of the Category (e.g., water)
- `category` - The product category (e.g., sparkling water)
- `company` - An id of the company that sells the item
- `brand` - An id of the brand to which the item belongs
- `date` - The date of purchase
- `productsize` - The amount of the product purchase (e.g., 16 oz of water)
- `productmeasure` - The units of the product purchase (e.g., ounces)
- `purchasequantity` - The number of units purchased
- `purchaseamount` - The dollar amount of the purchase

#### Offers
- `offer` - See above
- `category` - See above
- `quantity` - The number of units one must purchase to get the discount
- `company` - See above
- `offervalue` - The dollar value of the offer
- `brand` - See above

### Joins
- The transactions file can be joined to the history file by (`id`, `chain`).
- The history file can be joined to the offers file by (`offer`).
- The transactions file can be joined to the offers file by (`category`, `brand`, `company`).
- A negative value in `productquantity` and `purchaseamount` indicates a return.