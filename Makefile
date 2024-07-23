.DEFAULT: help

help:
	@echo "make help"
	@echo "    display this help statement"
	@echo "make run"
	@echo "    run the application in devel"
	@echo "make test"
	@echo "    run associated test suite with pytest"
	@echo "make lint"
	@echo "    lint project files using the black linter"

run:
	export ENVIRONMENT=devel; \
	python -c 'import lambda_function; lambda_function.lambda_handler(None, None)'

test:
	pytest tests -W ignore::DeprecationWarning

lint:
	black ./ --check --exclude="(env/)|(tests/)"