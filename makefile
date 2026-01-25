run:
	python ingest/ingest.py
	python transform/transform.py
	python gold/gold.py
	streamlit run app/dashboard.py
