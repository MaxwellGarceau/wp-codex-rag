cov:
	coverage run -m pytest
	coverage html

test:
	ENV=test pytest tests -s

# Linting and formatting
lint:
	poetry run ruff check .

lint-fix:
	poetry run ruff check --fix .

format:
	poetry run black .

format-check:
	poetry run black --check .

type-check:
	poetry run mypy .

# Run all quality checks
quality: format-check lint type-check

# Fix all auto-fixable issues
fix: format lint-fix

# Install pre-commit hooks
install-hooks:
	poetry run pre-commit install
