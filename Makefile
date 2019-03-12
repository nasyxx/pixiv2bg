open:
	open likes
	open /Users/Nasy/Documents/中二文件夹？/Pictures/Terminal\ BG
	open pictures

all: run
	open .
run:
	python3 pixiv2bg.py && python3 pixiv2bg.py
install:
	pip3 install -r requirements.txt
clean:
	rm -rf __pycache__
	rm -rf .mypy_cache
cleanall: clean
	rm -rf pictures
