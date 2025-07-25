.PHONY: test
test:
	uv run pytest -v

.PHONY: type
type:
	uv run pytype src
