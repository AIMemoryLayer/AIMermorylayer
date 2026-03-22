.PHONY: install dev build-all format lint

# Install all dependencies (Node and Python)
install:
	pnpm install
	poetry install --no-root

# Run the development environment via Turbo
dev:
	pnpm run dev

# Build all packages via Turbo
build-all:
	pnpm run build

# Reformat code automatically
format:
	pre-commit run ruff-format --all-files
	pre-commit run prettier --all-files

# Run all linters and checks
lint:
	pre-commit run --all-files
