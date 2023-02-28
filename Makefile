all: build

build:
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/