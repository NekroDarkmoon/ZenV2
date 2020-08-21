init:
	python3.8 -m pip install -r requirements.txt

test:
	nosetests tests
