run: build
	venv/bin/streamlit run "main.py"

venv:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt

build: venv
