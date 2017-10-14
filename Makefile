ro: run
	open .
run:
	python3 pixiv2bg.py
install:
	pip3 install -r requirements.txt
clean:
	rm -rf __pycache__
cleanall: clean
	rm -rf pictures
