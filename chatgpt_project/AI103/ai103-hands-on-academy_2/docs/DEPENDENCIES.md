# Installing and recording dependencies

Offline core lessons use Python's standard library; native/service SDKs install only for live
notebooks. SDK ranges in requirements/ are compatibility intentions, not a fully tested lockfile.
This review environment could not access package distributions, so it could not verify dependency
resolution. Do not interpret that limitation as a package-not-found result in Azure.

1. Use the notebook's exact requirements file; do not install all optional SDKs into one session.
2. If pip reports a conflict, retain the full package-name/version error (no secrets), start a fresh
   compatible compute/session, and retry the exact file. Do not force-install incompatible packages.
3. Restart Python once after a successful install. Run the final cell. environment.json records
   package versions for every successful run. Copy a successful environment to a personal tested
   requirements lock only after testing live calls with that exact Databricks Runtime.
4. Pin those validated versions for a scheduled job or release. Re-run tests/evaluations before
   updating SDKs, runtime, model or API generation. Avoid hidden cluster-wide package changes.
5. Native Speech and ODBC have OS dependencies that pip cannot supply; use azure_execution fallbacks.

The source package is designed to run from its checkout/extracted directory. Do not build a wheel
and assume bundled data/config are included: production packaging should move those assets into
explicit package resources or a governed data store and add packaging tests.
