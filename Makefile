.PHONY: install generate-data analyze export-tableau all clean

install:
	pip install -r requirements.txt

generate-data:
	python -m src.data.generate_all_data

analyze:
	python -m src.analysis.sales_analysis
	python -m src.analysis.customer_analysis
	python -m src.analysis.marketing_analysis
	python -m src.analysis.financial_analysis
	python -m src.analysis.supply_chain_analysis
	python -m src.analysis.hr_analysis
	python -m src.analysis.genai_analysis

export-tableau:
	python -m src.export_tableau_ready

all: install generate-data analyze export-tableau

clean:
	rm -rf data/*.csv
	rm -rf data/analysis/*.csv
	rm -rf data/tableau_ready/*.csv
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
