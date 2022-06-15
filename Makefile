build:
	python setup.py build

sdist:
	python setup.py sdist

upload_test_pypi:
	twine upload -r testpypi dist/*

upload_pypi:
	twine upload -r pypi dist/*
