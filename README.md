# Python Jenkins Selenium Project

## Executive summary
This repository is a **Python-based remake** of an existing **Java + TestNG + Maven** Selenium project that was designed to run in CI (Jenkins-style), producing machine-readable results and human-readable reports.

The remake keeps the **same functional intent** (UI automation against LambdaTest’s sample Todo application) while modernising the stack to:

- **pytest** (test runner)
- **selenium** (Remote WebDriver)
- **LambdaTest Selenium Grid** (cloud execution)
- **pytest-xdist** (parallel execution)
- **JUnit XML + HTML reports** (CI-friendly outputs)

Target application under test: `https://lambdatest.github.io/sample-todo-app/`

---

## Scope and inputs
### Original project characteristics (source baseline)
- Test framework: TestNG
- Build runner: Maven Surefire
- Suite control: TestNG suite XML files (single / parallel / mobile)
- Typical CI outputs: Surefire/TestNG HTML + XML reports

### Remade project characteristics (this repo)
- Test framework: pytest
- Dependency management: pip requirements
- Suite control: pytest markers (replacing TestNG suite XML)
- Parallelism: pytest-xdist (replacing TestNG parallel suite config)
- CI outputs: JUnit XML + HTML report (Jenkins-friendly)

---

## Repository structure
```
.
├─ tests/
│  ├─ test_todo_1.py
│  ├─ test_todo_2.py
│  ├─ test_todo_3.py
│  └─ test_todo_mobile.py
├─ config/
│  └─ capabilities.py
├─ conftest.py
├─ pytest.ini
├─ requirements.txt
└─ README.md
```

---

## Test design summary
- Each test module mirrors the intent of the original Java test classes:
  - navigate to the sample Todo app
  - select pre-existing items
  - add new items
  - assert the final added item text appears as expected

- Driver lifecycle mirrors TestNG’s `@BeforeMethod / @AfterMethod`:
  - a pytest fixture creates a **RemoteWebDriver session** on LambdaTest
  - the same fixture quits the session after each test

---

## Execution model
### Environment variables
LambdaTest credentials are read from environment variables:

- `LT_USERNAME`
- `LT_ACCESS_KEY`

Optional:
- `LT_BUILD_NAME` (defaults to a sensible value if unset)
- `LT_PROJECT_NAME` (defaults to a sensible value if unset)

---

## Installation
### 1) Create and activate a virtual environment
```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
```

### 2) Install dependencies
```
pip install -r requirements.txt
```

---

## Running tests
All examples below assume `LT_USERNAME` and `LT_ACCESS_KEY` are set.

### Single suite equivalent
Runs the tests marked as `single`:
```
pytest -m single
```

### Mobile suite equivalent (lightweight)
Runs the tests marked as `mobile`.

Note: this implementation uses **mobile emulation-style settings** inside a standard Selenium session (not Appium), to stay lightweight:
```
pytest -m mobile
```

### Parallel suite equivalent
Runs the tests marked as `regression` in parallel workers:
```
pytest -m regression -n auto
```

---

## Reports and CI outputs
### Generate JUnit XML (for Jenkins)
```
pytest --junitxml=reports/junit.xml
```

### Generate HTML report
```
pytest --html=reports/report.html --self-contained-html
```

### Combine (recommended for CI)
```
pytest -m regression -n auto --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html
```

The `reports/` directory is gitignored by default.

---

## Gaps and assumptions vs the original Java/Jenkins pipeline
This remake intentionally simplifies or changes a few areas while keeping the same testing intent:

1. **Suite XML files are not used**
   - Test selection is implemented with **pytest markers** instead of TestNG suite XML (`single.xml`, `parallel.xml`, `mobile.xml`).

2. **Mobile is lightweight, not full Appium**
   - The “mobile” flow is represented using browser-side configuration intended to be lightweight.
   - If full device cloud coverage is required, the mobile capabilities can be upgraded to Appium-based execution.

3. **Report formats differ**
   - Maven Surefire/TestNG reports are replaced with:
     - JUnit XML (`--junitxml`)
     - pytest HTML (`--html`)
   - These are typically sufficient for Jenkins pipelines, but will not match Surefire report HTML exactly.

4. **No legacy build outputs included**
   - Java build output folders (e.g., `target/`, `surefire-reports/`, `maven-status/`, `test-classes/`) are intentionally **not** included to keep the repo Python-only.

---

## Suggested next improvements (optional)
- Add a Jenkinsfile that:
  - installs dependencies
  - exports LT env vars via Jenkins credentials
  - runs suite/marker selection based on job params
  - archives `reports/` artifacts
- Add a small CLI wrapper (or Makefile) to standardize commands:
  - `make single`, `make mobile`, `make parallel`
- Add page objects for cleaner test code organization if the suite grows

---

## Appendix: Quick checklist for CI readiness
- [ ] `LT_USERNAME` and `LT_ACCESS_KEY` available in CI environment
- [ ] Network access to LambdaTest hub endpoint
- [ ] Reports written to `reports/` and archived by CI
- [ ] Parallel worker count tuned for account concurrency
