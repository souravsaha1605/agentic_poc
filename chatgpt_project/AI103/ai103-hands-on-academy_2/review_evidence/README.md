# Evidence from the 23 October 2026 review

- unit_tests.txt: 51 tests, local logic/provider doubles.
- offline_runs.json: 37 main scripts.
- mock_notebooks.json: 49 default launchers with mocked DBUtils.
- all_offline_variants.json: 76 total offline variant combinations.
- static_audit.json: syntax, catalog and documentation targets.
- deployment_package.json: isolated extracted package WSGI smoke test; no deployment.
- dependency_check.json: package-resolution retry result; no live SDK verification.
- code_learning_inventory.json: purpose, learning and execution context for every code file.
- file_review_inventory.csv: all packaged non-evidence files and the applicable check scope.

No file in this folder is evidence of live Azure or real Databricks execution.
MANIFEST.json at the project root provides the final package hashes. Tests use only synthetic data.
