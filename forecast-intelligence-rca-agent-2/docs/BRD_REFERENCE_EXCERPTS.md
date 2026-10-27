# Preserved review reference catalogue

Source: Forecast_RCA_Product_and_Solution_Review.docx, review 5, 27 October 2026. Extracted paragraph text below is preserved as reference data, not executable instructions. Original READY cells are examples, not test results.

22 Original BRD examples and contracts
Unchanged reference excerpts from BRD version 1.1 follow. They preserve all quoted business prompts, numerical examples, the ten conversation tests, the full definition-of-done journey, the matrices and the implementation code-pattern example. The source section numbers are retained for traceability.
BRD source section 3
3. Product Vision
Create a conversational Forecast Intelligence Agent that behaves like a digital analytical copilot for business users.
The user should be able to start with a broad question:
"Why is the forecast for P0001 deteriorating?"
and continue naturally:
"What happened in the last 12 weeks?"
"Was the decline concentrated in the North region?"
"What about revenue?"
"Could inventory have caused the drop in sales?"
"What if demand increases by 15%?"
"We changed the promotion last week. Has the situation improved?"
The system must understand whether each message is part of the same case or starts a new one, without requiring the user to restate all context.
BRD source section 8
8. Functional Requirements
FR-01 — Natural-language forecast retrieval
Users shall be able to ask for:
current forecast;
historical forecast;
actual sales;
forecast accuracy;
forecast bias;
forecast vs actual comparison;
period-over-period changes.
The system shall support filters such as:
Product/SKU
Store
Region
Category
Channel, when available
Date range
Fiscal period
Comparison period
The response shall state the relevant time period and entity scope.
FR-02 — Revenue retrieval
The system shall support:
actual revenue;
revenue trend;
revenue change over time;
revenue by product/store/region/category;
revenue exposure associated with forecast deviation.
Revenue calculations shall use an explicitly documented business formula.
For the current synthetic dataset, if Price is unit selling price and Discount is a percentage:
Gross Revenue = Units Sold × PriceNet Revenue = Units Sold × Price × (1 - Discount / 100)
The implementation must validate the business meaning of the discount field before using the formula.
The system shall not silently substitute gross revenue for net revenue.
FR-03 — Inventory retrieval
The system shall support:
latest inventory;
historical inventory;
inventory trend;
stockout/low-inventory status;
inventory exposure during forecast errors;
inventory as-of date.
The tool must not use the most recent row blindly when the user asks for a historical period.
FR-04 — Historical pattern analysis
The system shall identify historical patterns using a configurable lookback window.
Minimum supported analytical patterns:
trend;
level shift;
recurring seasonality;
volatility;
forecast bias drift;
forecast accuracy deterioration;
actual-vs-forecast divergence;
demand spikes/drops;
intermittent demand;
promotion-linked changes;
price-linked changes;
competitor-price-linked changes when data exists;
weather-linked changes when data exists;
inventory-constrained sales.
The user must be able to request:
"Last 12 weeks"
or
"Last 6 months"
without the agent confusing retrieval period with current-date assumptions.
BRD source section 9
9. Forecast RCA Requirements
FR-05 — RCA initiation
RCA may be initiated explicitly:
"Why is forecast accuracy low for SKU P0001?"
or implicitly:
"Forecast accuracy has deteriorated badly for P0001. What is happening?"
The system shall detect RCA intent from the request but shall not start an RCA if required entities or evidence are unavailable.
FR-06 — RCA evidence model
The RCA service shall build an evidence package containing, as applicable:
actual demand;
forecast demand;
forecast error;
forecast accuracy;
forecast bias;
historical trend;
rolling averages;
variability;
inventory;
stockout indicators;
revenue;
price;
discount;
promotion;
seasonality;
competitor pricing;
weather;
product lifecycle;
region/store/category mix;
data-quality indicators.
Not every RCA needs every signal. The service shall retrieve only the evidence required by the RCA question.
FR-07 — RCA hypothesis categories
The engine shall evaluate evidence for possible contributing factors such as:
Forecast level/bias issue
Demand trend shift
Seasonal pattern mismatch
Promotion/calendar effect
Price effect
Competitor pricing effect
Inventory/stockout constraint
Product lifecycle/new launch effect
Regional/store mix shift
Data-quality or missing-data issue
The engine must distinguish:
observed fact
evidence
probable contributor
uncertain hypothesis
unsupported hypothesis
The LLM must not convert a correlation into a confirmed causal statement.
Preferred wording:
"The evidence is consistent with a promotion-related demand shift."
Not:
"The promotion caused the forecast error."
unless a valid causal method is explicitly implemented.
BRD source section 10
10. Forecast Metric Requirements
The implementation shall support configurable metric definitions.
At minimum:
Forecast Error
Forecast Error = Forecast - Actual
Absolute Error
Absolute Error = |Forecast - Actual|
Bias
The business convention shall be documented and consistently applied.
Example:
Bias % = (Forecast - Actual) / Actual × 100
Under this convention:
positive bias = over-forecast;
negative bias = under-forecast.
WMAPE
For aggregate business analysis:
WMAPE = Σ|Forecast - Actual| / Σ|Actual|
This should be preferred over a simple average of row-level percentage accuracies when business volume differs materially.
Forecast Accuracy
If used as:
Forecast Accuracy = (1 - WMAPE) × 100
the calculation must define handling for zero actual demand.
The current row-level calculation should not be the sole business metric.
BRD source section 11
11. Data Sufficiency Rules
RCA shall not be presented as reliable when the data is insufficient.
Examples of insufficient evidence:
too few historical observations;
no actual sales;
all actual values are zero;
missing forecast values;
stale dataset;
missing inventory when inventory is required;
missing price when revenue analysis is required;
incomplete time coverage;
duplicate records at the expected grain.
The system shall return a structured status such as:
data_status = SUFFICIENTdata_status = PARTIALdata_status = INSUFFICIENT
and explain what is missing.
The exhaustive data-capability assessment is a one-time/onboarding activity. A scheduled readiness and feature-generation job shall maintain the current readiness metadata. Individual user requests shall use that persisted readiness information and perform only lightweight entity, period, and freshness checks at runtime.
BRD source section 12
12. Inventory-Constrained Demand Protection
A critical forecasting-RCA exception is stockout censorship.
Observed sales may be lower than underlying demand when inventory is unavailable.
Therefore:
Low Actual Sales+Low Inventory / Stockout
must not automatically be interpreted as:
Demand Decline
The RCA should explicitly state when demand may be supply-constrained.
Example:
"Observed sales declined while inventory was at stockout-risk levels. The sales decline may reflect supply constraint rather than a reduction in underlying demand."
This is a critical safeguard for real-world forecast RCA.
BRD source section 13
13. Mandatory Entity & Context Resolution
The system shall identify and resolve:
Product/SKU
Store
Region
Category
Date period
Metric
Analysis objective
Comparison entity, where relevant
The user may reference previous entities indirectly:
"What about the South region?"
"Now check revenue."
"Why was it worse last month?"
The system shall resolve these references against structured scenario state.
Entity resolution strategy
Exact ID match.
Normalized-name match.
Approved alias/reference match.
If multiple candidates remain → ask clarification.
Never silently select among multiple ambiguous entities.
Example:
"Show me sales for Coke."
If there are multiple Coca-Cola SKUs, the agent must ask which specific SKU/category/pack size applies.
BRD source section 14
14. Conversation Context & Scenario Memory
FR-08 — Persistent conversation
The system must retain relevant earlier messages within the same session.
Example:
Turn 1
"Analyze forecast performance for SKU P0001 in the North region."
Stored:
product = P0001region = Northanalysis = forecast performance
Turn 2
"What about inventory?"
The system must interpret this as:
product = P0001region = Northanalysis = inventory
without asking for P0001 again.
FR-09 — Structured scenario memory
Each active scenario shall maintain:
scenario_idsession_iduser_id / principalscenario_statusproduct(s)store(s)region(s)categorytime_rangecomparison_periodactive_issueanalysis_typebaseline_metricshistorical_metricsinventory_contextrevenue_contextRCA_evidenceRCA_hypothesesrecommendationswhat_if_parametersreported_outcomesassumptionsdata_timestampscenario_versioncreated_atupdated_at
Do not store only the natural-language transcript.
BRD source section 15
15. New Message Classification: Continuation vs New Scenario
Every message is evaluated after mandatory context/entity resolution. Intent classification and scenario action are independent dimensions; entity/context resolution is never an optional peer branch to tool selection or what-if handling.
This is a core product requirement.
Every new user message shall be evaluated on two independent dimensions:
A. Message Intent
Possible values:
FORECAST_RETRIEVALREVENUE_RETRIEVALINVENTORY_RETRIEVALTREND_ANALYSISRCACOMPARISONWHAT_IFOUTCOME_UPDATEEXPLANATION
B. Scenario Action
Possible values:
CONTINUE_ACTIVE_SCENARIOCREATE_NEW_SCENARIOUPDATE_ACTIVE_SCENARIOAMBIGUOUS_NEEDS_CLARIFICATION
These must not be conflated.
Continuation examples
Active scenario:
SKU=P0001Region=NorthPeriod=last 12 weeksIssue=forecast accuracy deterioration
User:
"Was the problem worse during promotions?"
Decision:
Intent = RCA / historical analysisScenario = CONTINUE_ACTIVE_SCENARIO
User:
"What happened to revenue?"
Decision:
Intent = REVENUE_RETRIEVALScenario = CONTINUE_ACTIVE_SCENARIO
User:
"What if demand is 15% higher?"
Decision:
Intent = WHAT_IFScenario = UPDATE_ACTIVE_SCENARIO
User:
"We changed the promotion last week and accuracy improved."
Decision:
Intent = OUTCOME_UPDATEScenario = UPDATE_ACTIVE_SCENARIO
The system shall record the outcome and preserve the scenario.
New scenario examples
Active scenario:
SKU=P0001Region=NorthIssue=forecast accuracy
User:
"Now analyze SKU P0099 in the West region."
Decision:
CREATE_NEW_SCENARIO
User:
"Forget the previous case. Start an RCA for the Dairy category."
Decision:
CREATE_NEW_SCENARIO
Ambiguous examples
User:
"Why is it getting worse?"
If both SKU and region context are clear, continue.
If multiple active entities or cases exist, ask:
"Do you mean the forecast issue for P0001 in North, or the revenue issue we discussed for P0020?"
The agent must not guess.
BRD source section 16
16. Scenario Lifecycle
The system shall model scenarios as:
NEW  ↓ACTIVE  ↓ANALYZING  ↓RCA_IDENTIFIED / INFORMATION_RETRIEVAL  ↓WHAT_IF / FOLLOW_UP  ↓OUTCOME_REPORTED  ↓RESOLVED or CLOSED
A new scenario can be created at any point when the user's intent/entity context materially changes.
Historical scenario versions shall not be overwritten.
BRD source section 17
17. Baseline, Current, Previous Scenario
For every what-if or updated analysis, maintain:
Baseline ScenarioCurrent ScenarioPrevious Scenario
Example:
Baseline:Current forecast demand = 100What-if:Demand +15%Current:115
The response shall explain the delta.
This also allows:
"How is this scenario different from the previous one?"
without rerunning everything unnecessarily.
BRD source section 18
18. What-if Requirements
What-if requests shall modify only explicitly requested assumptions.
Examples:
"What if price increases by 5%?"
"What if demand rises by 15%?"
"What if inventory is reduced by 20%?"
The system must:
clone the current scenario;
apply the requested change;
keep baseline immutable;
rerun only required deterministic calculations;
compare baseline vs what-if;
store the new scenario version.
The LLM must never modify raw enterprise data as part of a what-if.
BRD source section 19
19. Revenue & Inventory RCA Interaction
RCA should account for cross-functional relationships.
Examples:
Forecast error + inventory
Forecast overestimate+High inventory=Potential excess inventory exposure
Forecast underestimate + stockout
Forecast underestimate+Low inventory+Low observed sales=Sales may be supply constrained
Forecast error + revenue
Forecast deviation+Revenue decline=Investigate demand, price, promotion and availability together
These are analytical relationships, not automatic causal conclusions.
BRD source section 20
20. Proposed Tool Architecture
Keep the LLM-facing toolset intentionally small.
Recommended logical capabilities:
Tool 1 — get_forecast_context
Retrieve requested forecast evidence for a resolved entity and time period.
Should support flags such as:
include_summaryinclude_historyinclude_accuracyinclude_biasinclude_trend
Tool 2 — get_inventory_context
Retrieve current/historical inventory and stockout information.
Tool 3 — get_revenue_context
Retrieve actual and derived revenue metrics.
Tool 4 — analyze_historical_pattern
Return deterministic trend, volatility, level-shift and historical pattern indicators.
Tool 5 — run_forecast_rca
Generate an evidence package and structured RCA hypotheses.
Tool 6 — compare_scenarios
Compare baseline vs current/what-if scenario.
Entity resolution, memory persistence and security checks should be implemented as system components rather than creating unnecessary additional LLM tools.
BRD source section 21
21. Recommended Service Layer
Refactor the business logic into services similar to:
EntityResolutionServiceConversationMemoryServiceScenarioStateServiceForecastServiceInventoryServiceRevenueServiceHistoricalPatternServiceForecastRCAServiceScenarioComparisonServiceDataQualityServiceAuthorizationService (Iteration 2/3)
The LLM-facing tools should remain thin wrappers.
BRD source section 22
22. Data Model Requirements
At minimum, retain the current fact table concept:
fact_sales_forecast
Required fields should include:
datestore_idproduct_idcategoryregioninventory_levelunits_soldunits_ordereddemand_forecastpricediscountweather_conditionholiday_promotioncompetitor_pricingseasonality
For a more realistic RCA implementation, add:
gross_revenuenet_revenueforecast_errorabsolute_errorstockout_flaginventory_statusforecast_generated_dateforecast_horizon_daysdata_quality_flag
where source data supports these fields.
Master/reference tables should include:
dim_productdim_storedim_regiondim_calendar
If aliases are required for conversational entity resolution:
dim_entity_alias
BRD source section 23
23. Analytical Views
Create governed views rather than allowing arbitrary SQL.
Recommended views:
vw_forecast_metricsvw_inventory_healthvw_revenue_metricsvw_forecast_historyvw_forecast_rca_features
vw_forecast_rca_features should expose deterministic RCA-ready features so the RCA service does not repeatedly reconstruct the same calculations.
Also create `rca_readiness_registry` (or an equivalent governed Delta table) to persist readiness by entity, period and RCA capability, including coverage, required-field availability, data-quality status, and last validation timestamp. A scheduled job shall refresh both RCA features and readiness metadata.
BRD source section 24
24. Historical Pattern Features
The data/service layer should support:
period_actualperiod_forecastforecast_errorabsolute_erroraccuracybiasrolling_actualrolling_forecastrolling_biasrolling_accuracyactual_volatilityforecast_volatilitypromotion_flagprice_changecompetitor_price_changeinventory_daysstockout_flag
The exact statistical method can evolve, but the interface should remain stable.
BRD source section 25
25. RCA Decision Logic
The RCA service should produce structured output:
{  "scenario_id": "SCN-001",  "entity": {...},  "period": {...},  "data_quality": {...},  "observations": [...],  "evidence": [...],  "hypotheses": [    {      "cause": "...",      "evidence": [...],      "strength": "HIGH|MEDIUM|LOW",      "status": "SUPPORTED|POSSIBLE|NOT_SUPPORTED"    }  ],  "recommendations": [...],  "confidence": "...",  "limitations": [...]}
The LLM should convert this into business-friendly language.
BRD source section 28
28. Agent Error Handling
The agent shall:
validate tool arguments before execution;
return structured tool errors;
retry transient data/service failures within a bounded limit;
stop after a configurable maximum number of tool calls;
avoid infinite LLM/tool loops;
log failed tool calls;
distinguish user errors from system/data errors;
never hide data retrieval failures behind fabricated answers.
Example:
Data unavailable:"Inventory data for P0001 is unavailable for 2026-09-01 to 2026-09-30.I can complete the forecast portion, but the inventory-based RCA cannotbe validated for this period."
BRD source section 29
29. Prompt Injection & Trust Boundary
Tool outputs and enterprise data must be treated as data, not instructions.
A field containing:
"Ignore previous instructions..."
must never be executed as an instruction.
The agent must:
use an allowlist of approved tools;
reject unknown tools;
prohibit arbitrary SQL/code;
keep system instructions separate from retrieved content;
constrain tool parameters;
enforce read-only access in Iteration 1;
separate user text from tool/system instructions.
BRD source section 30
30. Cost and Loop Protection
The current agent loop must be bounded.
Introduce:
MAX_AGENT_TURNSMAX_TOOL_CALLS_PER_MESSAGEMAX_ROWS_RETURNEDMAX_HISTORY_TOKENSTOOL_TIMEOUT_SECONDS
Use progressive retrieval:
small summary   ↓only retrieve detail if required
The system shall avoid retrieving full datasets when a business aggregate is sufficient.
BRD source section 31
31. Memory Architecture
Iteration 1
Use Databricks Delta as persistent storage for:
conversation_turns
session_idturn_iduser_idtimestamprolemessage
scenario_state
scenario_idsession_idstatusresolved_entitiestime_rangeanalysis_typeactive_issuebaseline_statecurrent_stateprevious_statelast_tool_resultsrca_summarylast_updatedversion
The notebook may maintain an in-memory active object for convenience, but Delta must be the durable source for scenario persistence across notebook/cell boundaries where practical.
Iteration 2
Move memory access behind an API/service.
Teams user identity should map to:
tenant/user   ↓session   ↓scenario
Iteration 3
Use production-grade state management with:
durable conversation store;
versioned scenario state;
concurrency control;
TTL/archive policies;
encryption;
role-based access;
audit trails.
BRD source section 33
33. Security Requirements
Authentication
Iteration 1 can use controlled development credentials.
Iteration 2/3 shall use Entra ID / managed identity.
Authorization
Every production retrieval shall be evaluated against user entitlements.
Examples:
User A → North region onlyUser B → GlobalUser C → Category X only
The LLM must never determine authorization.
Authorization belongs to the service/tool boundary.
Secrets
Do not store secrets in source code or notebooks.
Use environment configuration locally and a managed secret store in later iterations.
BRD source section 35
35. Audit Requirements
The system should be able to answer:
What did the user ask?
What scenario was active?
What entities were resolved?
Which data was retrieved?
Which version of the RCA logic was used?
What evidence supported the conclusion?
What did the agent recommend?
Did the user report an outcome later?
This is especially important in enterprise planning environments.
BRD source section 36
36. User Experience Requirements
Responses should be concise by default but structured.
For forecast retrieval:
Forecast:Actual:Accuracy:Bias:Period:Business interpretation:
For RCA:
Executive SummaryObserved PatternEvidenceProbable ContributorsBusiness ImpactRecommended Investigation/ActionConfidenceData Limitations
For historical trends:
PeriodActualForecastErrorAccuracyBiasPattern
For ambiguous context:
Ask only the minimum clarification required.
BRD source section 37
37. Response Grounding
Every answer with material business numbers should include:
entity;
time period;
as-of date where applicable;
relevant metric definition;
limitation if data is partial.
Do not return a number such as:
"Accuracy is 84%"
without making the scope clear:
"For SKU P0001 in North across the 12 completed weeks ending 2026-09-27, WMAPE-based forecast accuracy is 84%."
BRD source section 38
38. Test Scenarios
The implementation must include deterministic test cases covering at least:
The first-run initialization shall execute a golden RCA test suite against the generated scenarios and compare observed evidence with expected scenario outcomes. A failed scenario test shall block readiness for that RCA capability until corrected or explicitly marked NOT_TESTABLE.
Test 1 — Forecast retrieval
"What is the forecast for P0001?"
Expected:
resolve entity;
retrieve forecast;
return scoped result.
Test 2 — Multi-turn continuation
Turn 1:
"Analyze P0001 in North."
Turn 2:
"What about inventory?"
Expected:
reuse P0001 + North;
do not ask user to repeat them.
Test 3 — RCA continuation
Turn 1:
"Why is forecast accuracy deteriorating for P0001?"
Turn 2:
"Was promotion a contributor?"
Expected:
continue same RCA;
inspect promotion evidence.
Test 4 — New scenario
Turn 1:
"Analyze P0001 in North."
Turn 2:
"Now analyze P0099 in West."
Expected:
create new scenario;
preserve old scenario.
Test 5 — Outcome update
Turn 1:
"Accuracy is poor for P0001."
Turn 2:
"We changed the promotion last week and accuracy improved."
Expected:
classify as OUTCOME_UPDATE;
store outcome against active scenario;
do not start unrelated RCA.
Test 6 — What-if
"What if demand increases by 15%?"
Expected:
clone baseline;
change only demand assumption;
preserve baseline;
return delta.
Test 7 — Ambiguous entity
"Analyze Coke."
Expected:
present candidate matches;
request clarification.
Test 8 — Insufficient history
"Perform RCA for this new product."
Expected:
retrieve available history;
identify insufficient observations;
do not fabricate RCA.
Test 9 — Stockout distortion
Actual sales decrease while inventory is zero.
Expected:
flag supply constraint;
avoid interpreting the sales drop as pure demand decline.
Test 10 — New topic
After an active forecast RCA:
"What is the revenue for another product?"
Expected:
create/route to a new business context when the entity changes materially.
BRD source section 40
The current pattern:
conversation = [    system_message,    user_message]
must become a session-aware workflow.
BRD source section 41
41. Definition of Done
A scenario is considered successfully implemented when the system can support this complete journey:
User:"Analyze forecast performance for P0001 in North."        ↓Resolve:P0001 + North + current/default historical period        ↓Retrieve:Forecast + Actual + Accuracy + Bias        ↓Analyze:Historical trend + data quality        ↓RCA:Identify evidence-based contributors        ↓User:"What about revenue?"        ↓Continue same scenario        ↓User:"Was inventory constraining sales?"        ↓Continue same scenario        ↓User:"What if demand is 15% higher?"        ↓Clone scenario + what-if calculation        ↓User:"We increased the promotion and accuracy improved."        ↓Outcome update on active scenario        ↓User:"Now analyze P0099 in West."        ↓Create new scenario        ↓Preserve previous scenario
BRD source section 44
44. Post-Approval Architectural and BRD Amendments
The following 22 changes are incorporated into Version 1.1 based on the architectural discussions following Version 1.0 approval. These changes are implementation requirements and shall guide Databricks Genie / Genie Code when modifying the current repository.
1. First-run data setup and validation: The first execution must inspect the existing synthetic dataset against the BRD, identify missing schema/data/coverage, generate missing synthetic data, and validate the resulting dataset before normal agent use.
2. Synthetic Data Capability & Scenario Generation Framework: Synthetic data must be deliberately designed around multiple forecast-RCA scenarios rather than relying only on random variation. Supported scenarios include forecast over-bias, under-bias, trend shift, promotion uplift, price effect, seasonality, inventory constraint, stockout, revenue deterioration, regional divergence, new-product insufficient history, missing data, and data-quality issues.
3. Synthetic scenario validation: Generation is not sufficient. Each scenario must have an expected signal and a deterministic validation test. A scenario is only certified when the expected pattern is observed in the generated data.
4. One-time RCA Data Capability Assessment: Perform a comprehensive onboarding/build-time assessment that produces an RCA Capability Matrix showing required fields, historical coverage, scenario availability, validation results, and READY / PARTIAL / NOT_SUPPORTED status by RCA capability.
5. Separation of one-time assessment, scheduled readiness, and on-demand RCA: Do not run the full capability audit for each chat request. Separate initial certification, scheduled maintenance, and user-triggered RCA execution.
6. RCA Readiness Registry: Persist readiness metadata in a governed Delta table such as `rca_readiness_registry`. Store entity, capability, history, required-field availability, data-quality status, coverage, freshness, last validation time, and readiness status.
7. Structured analytical planning instead of LLM-generated SQL: The LLM may produce a structured analysis/query plan. It must not create unrestricted executable SQL. A deterministic backend query builder shall translate approved request structures into parameterized SQL over governed views/fields.
8. RCA Evidence Contract: Define the minimum data required for each RCA hypothesis (for example actual+forecast for bias, promotion+actual+forecast for promotion RCA, inventory+sales for stockout analysis). Retrieve only the evidence needed for the requested RCA.
9. LLM Data Exposure Boundary: Raw enterprise or transaction-level records must not be passed to the LLM by default. Only minimum-necessary, aggregated, derived, sanitized evidence may cross the LLM boundary. Tool outputs must use approved schemas and exposure limits.
10. Mandatory entity/context resolution: Entity/context resolution must precede intent classification, tool selection, and what-if handling. Resolve exact IDs, normalized names, and approved aliases; ask for clarification when ambiguity remains.
11. Conversation memory vs structured scenario memory: Persist both recent conversational history and authoritative structured scenario state. The agent must not depend only on the raw transcript for continuity.
12. Scenario versioning: Maintain immutable baseline, current, and previous scenario versions. What-if requests clone the active scenario, change only explicit assumptions, preserve the baseline, and store deltas as new versions.
13. Historical pattern validation: The system must validate that trend, seasonality, volatility, bias drift, promotion, price, and inventory-constrained patterns can be detected on the synthetic dataset and test fixtures before certifying the associated RCA capability.
14. Golden RCA test suite: Create deterministic test cases with expected pattern, expected evidence, expected contributor(s), and expected RCA status. Execute them during first-run initialization and use them as regression tests for later releases.
15. NOT_TESTABLE status: Add NOT_TESTABLE for hypotheses whose required data or evidence does not exist. The system must never infer or fabricate a cause simply because a user asked for it.
16. Stronger data-quality layer: Implement explicit checks for schema, nulls, duplicates, entity coverage, time-series continuity, history length, metric validity, future actuals, negative values, data freshness, and cross-source timestamp conflicts. Use a scheduled job for comprehensive refresh.
17. Data lineage and evidence provenance: Persist source view, data-as-of timestamp, coverage period, feature version, RCA logic version, scenario version, and calculation timestamp so every RCA can be reproduced and audited.
18. Reproducible synthetic data: Record random seed, dataset version, scenario version, parameters, and generation timestamp. Regeneration of a certified scenario must be deterministic.
19. Iteration 1 architecture update: First-run notebook execution includes data inspection/generation, scenario creation, validation, feature generation, readiness registry population, and golden-test execution before enabling normal conversational RCA.
20. Iteration 2 and 3 architecture update: Iteration 2 moves the conversation interface to Teams while retaining the same deterministic backend and state contracts. Iteration 3 adds production-grade identity, authorization, API boundaries, observability, resilience, CI/CD, evaluation, security, and operational controls.
21. First-run acceptance criterion: First execution is successful only when missing data is generated, required RCA scenarios are validated, the capability matrix is populated, RCA-ready features/readiness are created, and golden tests pass or are explicitly marked NOT_TESTABLE.
22. Revised end-to-end product architecture: The target flow becomes: User → Conversational Interface → Agent Orchestrator → Context & Entity Resolution → Intent + Scenario Decision → RCA/Analysis Requirement Planning → Readiness Lookup → Governed Tools → Deterministic Query Builder → Databricks/Analytics → Evidence Package → LLM Interpretation → User, with audit and telemetry throughout.
BRD source section 46
46. Synthetic RCA Scenario Catalogue and Validation
Scenario
Purpose
Validation rule
Expected
Normal forecast
Forecast tracks actual demand within expected tolerance.
Forecast error/accuracy is within configured normal band.
PASS/FAIL
Over-forecast bias
Forecast remains above actual over several periods.
Positive bias persists for configured minimum history.
PASS/FAIL
Under-forecast bias
Forecast remains below actual.
Negative bias persists for configured minimum history.
PASS/FAIL
Demand trend shift
Demand structurally increases or decreases.
Rolling trend/level shift detected.
PASS/FAIL
Promotion uplift
Demand differs materially during promotion periods.
Promotion vs non-promotion comparison shows intended uplift.
PASS/FAIL
Price effect
Price changes coincide with demand movement.
Configured price-change scenario is detectable.
PASS/FAIL
Seasonality
Recurring time-based pattern.
Expected recurring seasonal signal is detected.
PASS/FAIL
Inventory constraint
Observed sales are constrained by low inventory.
Low inventory/stockout aligns with suppressed observed sales.
PASS/FAIL
Revenue deterioration
Revenue moves materially with demand/price conditions.
Revenue delta matches configured scenario.
PASS/FAIL
Regional divergence
One region materially diverges from another.
Regional metrics show intended divergence.
PASS/FAIL
New product / insufficient history
Short history is deliberately generated.
Readiness returns INSUFFICIENT or NOT_TESTABLE as appropriate.
PASS/FAIL
Missing-data / data-quality issue
Nulls, gaps or duplicates are injected deliberately.
Data-quality layer detects the issue.
PASS/FAIL

BRD source section 48
48. Structured RCA Analysis Planning and SQL Generation Boundary
For complex RCA requests, the LLM shall produce a structured analytical request. Example:
analysis_type: FORECAST_RCAproduct_id: P001region: Northlookback_weeks: 12hypotheses: [promotion, inventory, price, trend]
The backend shall validate this structure against approved schemas and use a deterministic query builder to construct parameterized SQL over governed views such as `vw_forecast_rca_features`. The system must not permit the LLM to submit unrestricted SQL strings or arbitrary table/column references.
The query planner/query builder shall also enforce row limits, allowed dimensions, allowed measures, supported time windows, and user authorization constraints in Iterations 2 and 3.
BRD source section 49
49. LLM Data Exposure and Evidence Contract
The LLM data boundary is an explicit product and security requirement.
Raw transactional/row-level enterprise data shall not be returned to the LLM by default.
Backend services shall filter, aggregate, derive and sanitize data before it crosses the LLM boundary.
Only the minimum necessary evidence required to explain the requested result shall be included in the LLM context.
Tool responses shall conform to Pydantic/JSON schemas with bounded field sets, row counts and payload sizes.
Sensitive identifiers shall be minimized or masked unless required for business explanation and permitted by policy.
Example permitted evidence: forecast accuracy, WMAPE, bias, promotion/non-promotion comparison, stockout days, revenue change, trend direction, data-quality status, evidence statements and source-period metadata. The LLM shall use these outputs for explanation rather than receiving the underlying transaction history.
BRD source section 50
50. RCA Readiness Matrix
RCA Capability
Required Evidence
Minimum History
Synthetic Scenario
Validation
Status
Forecast bias
Actual + Forecast
4+ weeks
Over/under-bias
Bias detected
READY
Trend shift
Date + Actual
8+ weeks
Trend shift
Trend detected
READY
Promotion RCA
Promotion + Actual + Forecast
8+ weeks
Promotion uplift
Promo/non-promo contrast
READY
Inventory RCA
Inventory + Actual
8+ weeks
Stockout/constraint
Suppressed sales detected
READY
Revenue RCA
Actual + Price + Discount
4+ weeks
Revenue deterioration
Revenue delta detected
READY
Seasonality RCA
Calendar + Actual
Configurable / typically longer history
Seasonality
Recurring pattern detected
READY/NOT_TESTABLE
Competitor RCA
Competitor pricing + demand
Configurable
Competitor scenario
Pattern detected
NOT_TESTABLE when data absent

The matrix is created/updated by the scheduled readiness job and is also used by Genie as a build-time contract to determine which RCA capabilities can legitimately be implemented and tested.
