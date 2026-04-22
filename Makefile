.PHONY: docs lint format sanity install-dev clean

# Install development dependencies
install-dev:
	pip install -r dev-requirements.txt
	pre-commit install

# Run ruff lint
lint:
	ruff check plugins/

# Run ruff format
format:
	ruff format plugins/

# Build docs
docs:
	@echo "Generating per-module RST with antsibull-docs..."
	antsibull-docs --config-file docs/antsibull-docs.cfg collection --use-current --cleanup everything --dest-dir docs/ civo.cloud
	@echo "Building Sphinx HTML..."
	sphinx-build -j auto -b html docs/ docs/_build/html
	@echo "Docs available at docs/_build/html/index.html"

# Run ansible-lint
ansible-lint:
	ansible-lint --project-dir .

# Run ansible-test sanity (requires the collection to be installed)
sanity:
	ansible-test sanity --docker -v --color

clean:
	rm -rf docs/_build/ docs/collections/
