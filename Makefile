# Customizing venv location:
# export UV_PROJECT_ENVIRONMENT="venv2"

PHONY: test
test:
	uv run pytest tests -vv

PHONY: lint
lint:
	uv run ruff format
	uv run ruff check --fix

PHONY: ty
ty:
	uv run ty check
