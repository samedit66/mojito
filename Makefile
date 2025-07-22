.PHONY: test
test:
	uv run pytest -v

.PHONY: mypy
mypy:
	uv run mypy src
