.PHONY: docs lint format sanity install-dev clean test-integration test-check

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

# Run full integration test suite (requires CIVO_TOKEN and civo CLI)
test-integration:
	ansible-playbook tests/integration/test_all.yml -v

# Run check-mode smoke tests (no live resources created; still requires CIVO_TOKEN)
test-check:
	ansible-playbook tests/integration/test_check_mode.yml -v

clean:
	rm -rf docs/_build/ docs/collections/
