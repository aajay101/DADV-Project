# Contributing to Bangalore Urban Intelligence Platform

Thank you for your interest in contributing. This document explains how to get started.

## Repository Setup

```bash
git clone https://github.com/aajay101/DADV-Project.git
cd DADV-Project/bangalore_intelligence
python -m venv .venv
.venv\Scripts\Activate.ps1    # Windows
# source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
bangalore_intelligence/
├── app.py              Entry point
├── config/             Theme, schema, page definitions
├── dashboards/         Chart modules and page modules
├── components/         Reusable UI building blocks
├── data_layer/         Transforms, bundles, governance
├── explainability/     Chart interpretation metadata
├── filters/            State reducers and interaction
├── services/           Chart handlers and detail content
├── utils/              Formatting, validation, theming
├── tests/              Test modules
└── scripts/            CLI tools
```

## Coding Standards

- **Python 3.11+** — use type hints on all function signatures
- **No business logic in chart functions** — transforms compute data, charts render it
- **No runtime AI calls** — explainability is pre-authored and validated at startup
- **Follow existing patterns** — mimic code style from neighbouring files
- **Security** — never log or commit secrets, API keys, or credentials

## Testing

```bash
# Run all tests
pytest bangalore_intelligence/tests/ -v

# Run a specific test module
pytest bangalore_intelligence/tests/test_chart_smoke.py -v
```

Every new chart, transform, or governance feature should include corresponding tests.

## Pull Request Process

1. Create a feature branch from `main`
2. Make focused, atomic commits — one logical change per commit
3. Run the full test suite before submitting
4. Write a clear PR description explaining **what** changed and **why**
5. Reference any related issues

## Commit Style

Use concise, imperative commit messages:

```
Add temperature scatter chart (A-08)
Fix fingerprint cache invalidation on schema change
Update explainability entries for speed threshold chart
```

## Reporting Issues

Open a GitHub issue with:
- Steps to reproduce
- Expected behaviour
- Actual behaviour
- Python version and OS

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
