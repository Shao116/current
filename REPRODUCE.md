# Incremental v2.1 update / 增量升级

The current website explicitly requests `predictionMode: "weather"`. Published-reference pole/wire vulnerability, shared-location support associations, correlated sparse impact integration and restoration ensembles extend the existing v2 components. Existing explicit `quantity`, `upstream` or `failedNodes` requests keep their conditional-damage meaning unless weather mode is explicitly selected.

New authoritative method and measured reports are `reports/v21/Explanation-中英文.md` and `reports/v21/Validation-中英文.md`; the original v2 documentation below is retained as a historical reference. `risk.score` and calibrated unconditional probability remain null; useful reference-model values live in `impact.expectedAffectedPercentage`, its model sensitivity envelope, `riskAssessment`, `ert.perCustomer` and `ert.stages`. Published conductor repair references are explicitly distinguished from workbook labor. Unknown support coverage returns unavailable, never zero risk.

```sh
.venv/bin/python -m unittest discover -v
node test_frontend_demo.mjs
.venv/bin/python algorithms/benchmark_v21.py
.venv/bin/python algorithms/full_scope_v21.py
.venv/bin/python algorithms/report_v21.py
```

The frozen v2 comparison package is `algorithms/baseline_v2`; its manifest records original and path-normalized snapshot hashes. Large weather results use a bounded private gzip cache invalidated by model source, coefficient registry and environmental-input signatures. No new paid API or package is required. The served report links are `/reports/v21-explanation.html` and `/reports/v21-validation.html`.

---

# current v2 · Reproduce / 复现

Run from `/Users/tony/Desktop/AEP/outage-concierge`. The raw archives remain in `../materials/aep_challenge_hack26-main`. Raw/customer/precise infrastructure files stay under `private/`, never the web root. `network.pkl` is a trusted local build artifact; never load a pickle from an untrusted source.

## Environment

Python 3.12; dependencies pinned in `requirements-algorithms.lock`. On this Mac `.venv` uses the bundled Python plus its existing NumPy/pandas/openpyxl dependencies. For a clean environment:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-algorithms.lock
```

macOS XGBoost requires official Homebrew `libomp` (installed on this Mac). No paid API keys or cloud inference are used. Reports use Markdown 3.9. Core external sources are USGS/Open-Meteo and the previously downloaded Roanoke/OSM layers; service availability is not guaranteed. Source URLs, retrieval UTC and SHA256 are persisted next to new environmental files. Cached reanalysis/DEM are used for repeatability.

## Build, execute, test

```sh
.venv/bin/python algorithms/build_data.py
.venv/bin/python algorithms/acquire.py
.venv/bin/python server.py
```

In a second terminal:

```sh
.venv/bin/python -m unittest discover -v
node test_frontend_demo.mjs
.venv/bin/python algorithms/benchmark.py
.venv/bin/python algorithms/full_scope_check.py
.venv/bin/python algorithms/report.py
```

The benchmark computes 20 cases three times each with stable seeds and caches cleared, then measures a cached call. API/website integration tests expect port 8765. New server imports must be restarted after Python changes. `start.command` now uses `.venv/bin/python`.

## API compatibility and honest missing values

`POST /api/evaluate` keeps the existing JSON envelope `{ "scenario": {...} }`. Existing normalized fields remain; `risk.score` is now null rather than an arbitrary score. `restoration.low/high` may be null when a verified rate is absent. Frontend has been updated for these legitimate unknown values.

New fields: `impact`, `ert`, `physicsFeatures`, `equipmentFeatures`, `equipmentPredictions`, `model`, `performance`. `POST /api/impact` returns the canonical impact/ERT outputs; `GET /api/algorithm/status` exposes data/model/terrain evidence. Default scope is the selected circuit; `scope: "all"` returns rows for all 117,642 supplied customers. Only loopback access is accepted. Private source directories remain unserved.

Example body (engineering scenario, not an observed outage):

```json
{"scenario":{"contextType":"circuit","contextId":"C-001","asset":"transformer","quantity":3,"upstream":0,"crews":3,"date":"2025-09-27","historicalWeather":true,"seed":20261024,"trials":128,"correlation":0.35,"crewRange":[2,4],"accessDelayRange":[1,3]}}
```

Additional supported explicit inputs: `windDirection` (meteorological wind-from degrees), `rainMm`, `snowfallCm`, `snowDepthM`, `freezingRain` boolean, `failedNodes` (valid anonymous topology IDs), `components` (list of `{kind,quantity}`), `laborBasis` (`crew_hours` or `person_hours`), `crewSize`, and `repairHours` (explicit per-unit engineering override only when the workbook has no rate). `upstream` retains the legacy field but is now an extra assumed damage count; sequence is established by source-path energization, not an invented serial delay. `step` retains presentation compatibility; stages are computed from completed ancestor repairs.

Missing rain/snow/direction default to explicitly declared scenario assumptions; forecasts/reanalysis override them only when requested and available. `crewRange/accessDelayRange` determine scenario sensitivities, not confidence levels. Correlation is a declared simulation assumption. Known-node input means conditional on supplied failures, not externally verified utility outage status. Only calibrated-marginal simulation would expose unconditional per-customer probabilities, and those would still be conditional on asset coverage, model validity and correlation assumptions.

`ert.low/high` describe workload completion; customer restoration ranges are in `ert.perCustomer`. No verified connectivity means customer ERT is unavailable even when repair workload can be estimated. Default transformer labor assumes 50 kVA; the workbook does not establish actual ratings for every asset. No conductor rate is fabricated. Nine drawing references are catalogued in `algorithms/drawings.json`; caller must specify actual damaged components and quantities. Real backup supply is disabled without complete engineering verification; its constraint screen does not automatically alter customer energization.

## Training input and gate

No valid real training label table exists in this extract. Do not convert missing reports into negatives. Each training JSON row must include:

```json
{"asset_id":"verified-asset","event_id":"verified-event","timestamp":"2025-01-01T12:00:00Z","observed":true,"label":0,"features":["numeric values in algorithms.model.FEATURES order"]}
```

The example feature array is documentation, not a valid training row. Actual rows require numeric values/NaNs with the exact schema, at least 200 observed rows and 10 independent events with disjoint chronological partitions. Use `algorithms.model.vector` to generate the physical vector, preserving feature provenance. Training and candidate validation:

```sh
.venv/bin/python -m algorithms.model verified-exposures.json --out private/algorithm/model
```

A candidate failing the event-separated baseline gate cannot load. `candidate.joblib` is not an instruction to claim accuracy: review evidence provenance, label inspection, schema, geographic/asset coverage and independent test support before operational use. The synthetic plumbing test trains only in a temporary directory; no synthetic candidate is deployed. No actual calibrated model is currently present.

## Evidence

`reports/Report-1-Pipeline-中英文.md` and `reports/Report-2-Validation-中英文.md` are the requested bilingual reports. Their HTML counterparts are available locally at `/reports/report1.html` and `/reports/report2.html`. CSV/JSON files record actual inputs, results, seeds, timing, missing truth and failure reasons. Metrics describing source-path equality or synthetic model plumbing must never be presented as real outage accuracy.
