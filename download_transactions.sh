#!/bin/bash
# filepath: /Users/.../Desktop/repositories/google-lifetime-value/download_transactions.sh

# Set the data directory relative to the script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/data"

# Create data directory if it doesn't exist
mkdir -p "${DATA_DIR}"

# Check if file already exists
if [ -e "${DATA_DIR}/transactions.csv" ] || [ -e "${DATA_DIR}/transactions.csv.gz" ]
then
  echo "✅ Transactions file already exists in ${DATA_DIR}"
else
  echo "🔄 Downloading data from Kaggle..."
  
  # Navigate to data directory
  cd "${DATA_DIR}"
  
  # Download from Kaggle
  kaggle competitions download -c acquire-valued-shoppers-challenge

  # Extract only the transactions file
  echo "📦 Extracting transactions.csv.gz (this may take 10+ minutes)..."
  unzip -o acquire-valued-shoppers-challenge.zip transactions.csv.gz
  
  echo "🔄 Converting to CSV format..."
  gunzip -f transactions.csv.gz
  
  echo "✅ Download and extraction complete!"
  echo "📁 Data available at: ${DATA_DIR}/transactions.csv"
fi

# Return to original directory
cd "${SCRIPT_DIR}"