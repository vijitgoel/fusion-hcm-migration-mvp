# Technical Design: Fusion SaaS REST-based “Already Loaded” Validation

## Overview
This document outlines an additive validation layer for the HCM-to-HDL conversion pipeline. The existing application validates legacy HCM extracts (Excel/CSV) and generates Fusion HDL load files. The new feature introduces a configurable REST-based existence check against the target Fusion SaaS instance for each record (Department, Employee, Location, etc.) prior to final HDL output.

**Critical Design Note:** This is strictly an *additive validation layer*. It does **not** replace existing validation logic. It does **not** alter the existing HDL generation contract unless a minimal change is required for rejection tagging. It simply injects an existence check against Fusion before final output is produced.

## Current Architecture
- Core logic resides in `fusion-app/main.py` and associated services under `fusion-app/services/`.
- Pipeline performs:
  1. Data ingestion from legacy extracts.
  2. Object-specific business/validation rules.
  3. HDL file generation for passing records.
  4. Production of validation summaries, rejection reports (`*.rejections.*`), and structured logs.
- Processing is object-aware (Department, Employee, Location under `InputData/`).
- No current integration with Fusion SaaS runtime APIs; all validation is offline/static.

## Problem Statement
Legacy migration runs risk creating duplicate records or load failures when data has been partially loaded into Fusion in prior runs. There is no mechanism to query the target Fusion instance at validation time to detect pre-existing records using natural/business keys.

## Proposed Solution
Add a pluggable, configuration-driven “already-loaded” check as a sequential step in the *existing* validation pipeline (not a parallel system). 

- For each record passing preliminary validation, construct and execute a targeted REST lookup against the configured Fusion endpoint.
- Decision (exists vs. new) feeds directly into the current rejection/tagging mechanism.
- Results are aggregated into existing summary, rejection, and logging outputs.
- Feature is toggleable via config; disabled by default to preserve current behavior.

## Central Configuration Design
All Fusion connectivity and mapping data lives in **one central location** (`fusion-app/config/fusion_config.yaml` or equivalent section in existing config).

```yaml
fusion:
  base_url: "https://<tenant>.fa.us2.oraclecloud.com"
  username: "migration.user"
  password: "..."                  # RECOMMEND: externalize via env/secret manager
  auth_type: "basic"               # or "oauth"
  timeout: 30
  retries: 3
  enable_already_loaded_check: true

  object_endpoints:
    Department:
      endpoint: "/hcmRestApi/resources/11.13.18.05/departments"
      query_template: "DepartmentName={DepartmentName}"
      unique_keys: ["DepartmentName"]
      exists_check: "items.length > 0"
      headers:
        "REST-Framework-Ctx": "effectiveDate=2025-01-01"
    
    Employee:
      endpoint: "/hcmRestApi/resources/11.13.18.05/employees"
      query_template: "PersonNumber={PersonNumber}"
      unique_keys: ["PersonNumber"]
      exists_check: "items.length > 0"
    
    Location:
      endpoint: "/hcmRestApi/resources/11.13.18.05/locations"
      query_template: "LocationCode={LocationCode}"
      unique_keys: ["LocationCode"]
      exists_check: "items.length > 0"
```

- Loaded once at application startup (`FusionConfig` singleton/service).
- Sensitive values should be overridden via environment variables at runtime.
- Schema supports per-object custom headers, query builders, and response evaluators.

## Object-Specific Endpoint Strategy
- Lookup is **entirely configuration-driven** and object-aware.
- Each object maps to:
  - REST resource endpoint (versioned HCM REST API).
  - Query template using Python-style `{FieldName}` substitution from the incoming record.
  - List of unique key fields used for both query construction and logging.
  - `exists_check` expression (simple JMESPath-style or Python eval against JSON response).
- Strategy supports both simple query-param lookups and more complex patterns (finder APIs, composite keys) via additional config fields if needed in future.
- No hard-coded endpoints in business logic — all routing flows through the central config.

## Validation Flow
1. Record ingested and passes **existing** validation rules (unchanged).
2. If `enable_already_loaded_check` is true:
   - Resolve object type → lookup config.
   - Substitute record values into `query_template`.
   - Execute authenticated GET to `{base_url}{endpoint}?{query}`.
   - Evaluate response against `exists_check`.
3. If record exists:
   - Tag with rejection reason `ALREADY_LOADED_IN_FUSION`.
   - Capture matching Fusion record details (ID, last update, etc.) for reporting.
4. Record proceeds through remaining pipeline stages (HDL generation skipped for rejections).
5. All steps reuse existing aggregation, summary, and logging infrastructure.

No second validation engine is created; the new check is a registered validator in the current `ValidationPipeline`.

## Error Handling and Fallback Behavior
- Transient errors (network, timeout, rate-limit): retry with exponential backoff (config-driven).
- Persistent errors (auth failure, 5xx): 
  - Configurable fallback policy — `fail_fast`, `treat_as_new`, or `reject_with_warning`.
  - Default: `reject_with_warning` + prominent log entry.
- Malformed config or missing endpoint mapping: fail at startup with clear error.
- Per-record failures logged with context (object, key values, HTTP status, response snippet).
- All HTTP calls wrapped in structured logging (`fusion_rest_call`, `already_loaded_decision`, etc.).

## Output/UX Impact
- **Validation Summary:** New counter `already_loaded_in_fusion` alongside existing metrics.
- **Rejection Output:** Records appear in rejection files with reason `ALREADY_LOADED_IN_FUSION`, plus Fusion match details (e.g., `fusion_record_id`, `match_criteria`).
- **Logs:** Detailed trace for every lookup (endpoint used, query, response time, decision). 
- **Dashboard (`fusion-dashboard/`):** New validation category badge and filter (if UI updated).
- **HDL Files:** Unchanged contract — only non-rejected records emitted.
- Clear separation in reports between “business validation failure” and “already exists in Fusion”.

## Testing Strategy
- **Unit:** Config loader, query template rendering, response evaluator, fallback logic (using `pytest`).
- **Integration:** Mocked Fusion REST endpoints (`responses` or `httpx_mock`) covering positive/negative/exists cases for each object.
- **E2E:** Run full pipeline against `sample.xlsx` with seeded “already loaded” test data; assert correct rejection tagging and HDL output.
- **Regression:** Explicit tests verifying existing validation rules and HDL generation remain identical when feature is disabled.
- **Error Path:** Simulate auth failures, timeouts, rate limits, malformed responses.
- **Performance:** Benchmark lookup overhead; add caching layer (LRU on unique key tuple) if needed.

## Implementation Notes
- Create `fusion-app/services/fusion_rest_client.py` and `fusion_app/services/already_loaded_validator.py`.
- Reuse or extend existing HTTP client (requests / httpx).
- Add config loading in `fusion-app/main.py` initialization path.
- Make validator implement the same interface as current validators for seamless pipeline insertion.
- Consider caching repeated lookups (same business key) within a single run.
- Credentials must never be committed; document use of `.env` or Vault.
- Initial implementation targets HCM REST resources under `/hcmRestApi/resources/11.13.18.05/`.
- Monitor Fusion API quotas; design supports batching where endpoints permit.
- Keep changes localized — core data transformation and HDL emitter logic should require zero or minimal modification.

This design ensures clean integration, full configurability, and zero regression of existing behavior while delivering the requested existence validation.