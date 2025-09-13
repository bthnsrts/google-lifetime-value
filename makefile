preprocess:
	python src/google_lifetime_value/preprocess/preprocess_transactions.py

download_data:
	chmod +x download_transactions.sh
	./download_transactions.sh