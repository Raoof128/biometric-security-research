.PHONY: help install install-dev test test-cov lint format clean docker run status docs

.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Biometric Security Research System - Makefile Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	@echo "$(GREEN)Installation complete!$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e ".[dev]"
	@echo "$(GREEN)Development installation complete!$(NC)"

setup: ## Initial project setup
	@echo "$(BLUE)Setting up project...$(NC)"
	./install.sh
	@echo "$(GREEN)Setup complete!$(NC)"

test: ## Run tests
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v
	@echo "$(GREEN)Tests complete!$(NC)"

test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	pytest --cov=. --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/$(NC)"

test-fast: ## Run tests in parallel
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	pytest -n auto
	@echo "$(GREEN)Tests complete!$(NC)"

lint: ## Run linters
	@echo "$(BLUE)Running linters...$(NC)"
	black --check .
	isort --check-only --profile black .
	pylint biometric attacks defenses evaluation reporting utils config.py || true
	mypy biometric attacks defenses evaluation reporting utils --ignore-missing-imports || true
	@echo "$(GREEN)Linting complete!$(NC)"

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	black .
	isort --profile black .
	@echo "$(GREEN)Code formatted!$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	safety check --continue-on-error || true
	bandit -r . -ll -i -x ./tests,./venv || true
	pip-audit || true
	@echo "$(GREEN)Security scan complete!$(NC)"

clean: ## Clean build artifacts and cache
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .eggs/ .tox/
	@echo "$(GREEN)Cleanup complete!$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	docker build -t biometric-security-research:2.0.0 .
	@echo "$(GREEN)Docker image built!$(NC)"

docker-run: ## Run Docker container
	@echo "$(BLUE)Running Docker container...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Container started!$(NC)"

docker-stop: ## Stop Docker container
	@echo "$(BLUE)Stopping Docker container...$(NC)"
	docker-compose down
	@echo "$(GREEN)Container stopped!$(NC)"

docker-shell: ## Open shell in Docker container
	@echo "$(BLUE)Opening shell in container...$(NC)"
	docker-compose exec biometric-security /bin/bash

run: ## Run the application
	@echo "$(BLUE)Running application...$(NC)"
	python main.py

status: ## Show system status
	@echo "$(BLUE)Checking system status...$(NC)"
	python cli_enhanced.py status

enroll: ## Enroll a user (requires USER_ID and IMAGES)
	@echo "$(BLUE)Enrolling user...$(NC)"
	python cli_enhanced.py enroll --user-id $(USER_ID) --modality face --images $(IMAGES)

attack: ## Generate attacks (requires IMAGE)
	@echo "$(BLUE)Generating attacks...$(NC)"
	python cli_enhanced.py attack --image $(IMAGE) --attack-types photo,mask,patch,fgsm

report: ## Generate enhanced report (requires RESULTS_FILE)
	@echo "$(BLUE)Generating report...$(NC)"
	python cli_enhanced.py enhanced-report --results-file $(RESULTS_FILE) --output reports/dashboard.html

docs: ## Generate documentation
	@echo "$(BLUE)Documentation available in docs/ directory$(NC)"
	@echo "$(GREEN)- README.md: Main documentation$(NC)"
	@echo "$(GREEN)- README_V2.md: v2.0 features$(NC)"
	@echo "$(GREEN)- docs/FEATURES_V2.md: Detailed features$(NC)"
	@echo "$(GREEN)- CONTRIBUTING.md: Contribution guidelines$(NC)"
	@echo "$(GREEN)- SECURITY.md: Security policy$(NC)"

version: ## Show version information
	@echo "$(BLUE)Biometric Security Research System$(NC)"
	@echo "Version: 2.0.0"
	@python --version

check-deps: ## Check for outdated dependencies
	@echo "$(BLUE)Checking dependencies...$(NC)"
	pip list --outdated

update-deps: ## Update dependencies (be careful!)
	@echo "$(RED)Warning: This will update all dependencies!$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		pip install --upgrade -r requirements.txt; \
		echo "$(GREEN)Dependencies updated!$(NC)"; \
	fi

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) test
	@echo "$(GREEN)Pre-commit checks complete!$(NC)"

build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	python -m build
	@echo "$(GREEN)Build complete! Packages in dist/$(NC)"

publish-test: ## Publish to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(NC)"
	python -m twine upload --repository testpypi dist/*

publish: ## Publish to PyPI (use with caution!)
	@echo "$(RED)Warning: This will publish to PyPI!$(NC)"
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python -m twine upload dist/*; \
		echo "$(GREEN)Published to PyPI!$(NC)"; \
	fi

all: ## Run complete CI pipeline locally
	@echo "$(BLUE)Running complete CI pipeline...$(NC)"
	$(MAKE) clean
	$(MAKE) install-dev
	$(MAKE) format
	$(MAKE) lint
	$(MAKE) security
	$(MAKE) test-cov
	@echo "$(GREEN)All checks passed!$(NC)"

# Example usage commands
.PHONY: example-enroll example-attack example-test example-report

example-enroll: ## Example: Enroll a user
	@echo "$(BLUE)Example: Enrolling user 'alice'$(NC)"
	@echo "Command: python cli_enhanced.py enroll --user-id alice --modality face --image-dir data/alice/"
	@echo "$(GREEN)Modify and run this command with your own data$(NC)"

example-attack: ## Example: Generate attacks
	@echo "$(BLUE)Example: Generating attacks$(NC)"
	@echo "Command: python cli_enhanced.py attack --image data/face.jpg --attack-types photo,mask,patch,fgsm"
	@echo "$(GREEN)Modify and run this command with your own data$(NC)"

example-test: ## Example: Run vulnerability test
	@echo "$(BLUE)Example: Running vulnerability test$(NC)"
	@echo "Command: python main.py vulnerability-test --test-dir data/test_samples --attack-source-dir data/enrolled_users"
	@echo "$(GREEN)Modify and run this command with your own data$(NC)"

example-report: ## Example: Generate report
	@echo "$(BLUE)Example: Generating enhanced report$(NC)"
	@echo "Command: python cli_enhanced.py enhanced-report --results-file data/results/vulnerability_test.json --output reports/dashboard.html"
	@echo "$(GREEN)Modify and run this command with your own data$(NC)"
