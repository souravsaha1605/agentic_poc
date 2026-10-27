# Databricks notebook source


# COMMAND ----------

# 02_golden_rca_tests.py - Golden RCA Test Suite (BRD 38)
import sys, os
sys.path.insert(0, '/Workspace/Users/sourav.saha26-10@iimv.ac.in/agentic_poc/forecast-intelligence-rca-agent-1')
from services.forecast_rca_service import (
    forecast_service, inventory_service, revenue_service,
    pattern_service, rca_service, comparison_service,
    entity_service, data_quality_service,
)
DB = 'workspace.forecast_db'
results = []
def record(name, passed, detail=''):
    status = 'PASS' if passed else 'FAIL'
    results.append((name, status, detail))
    print(f"  {'PASS' if passed else 'FAIL'} {name} - {detail}")
print('=' * 70)
print('  Golden RCA Test Suite (BRD 38)')
print('=' * 70)
# Test 1 - Forecast retrieval
print('\n[Test 1] Forecast Retrieval')
try:
    r = forecast_service.get_forecast_data('SKU-001', region='North', lookback_weeks=12)
    record('Forecast retrieval - entity resolved', r.get('success', True) and r.get('product_id') == 'SKU-001')
    record('Forecast retrieval - WMAPE calculated', r.get('wmape') is not None)
    record('Forecast retrieval - accuracy returned', r.get('forecast_accuracy') is not None)
except Exception as e:
    record('Forecast retrieval', False, str(e))
# Test 2 - Inventory retrieval (multi-turn continuation)
print('\n[Test 2] Inventory Retrieval')
try:
    inv = inventory_service.get_inventory_data('SKU-001', region='North', lookback_weeks=12)
    record('Inventory - same entity/region', inv.get('success', True) and inv.get('product_id') == 'SKU-001')
    record('Inventory - status returned', inv.get('inventory_status') is not None)
    record('Inventory - stockout flag', 'stockout_flag' in inv)
except Exception as e:
    record('Inventory retrieval', False, str(e))
# Test 3 - RCA with promotion hypothesis
print('\n[Test 3] RCA with hypothesis')
try:
    rca = rca_service.run_rca('SKU-001', region='North', lookback_weeks=12)
    record('RCA - evidence package', rca.get('success', True) and len(rca.get('evidence', [])) > 0)
    record('RCA - hypotheses structured', len(rca.get('hypotheses', [])) > 0)
    record('RCA - confidence assigned', rca.get('confidence') in ['HIGH', 'MEDIUM', 'LOW'])
    record('RCA - limitations included', len(rca.get('limitations', [])) > 0)
except Exception as e:
    record('RCA continuation', False, str(e))
# Test 4 - New scenario (different product)
print('\n[Test 4] New scenario detection')
try:
    r1 = forecast_service.get_forecast_data('SKU-001', region='North', lookback_weeks=12)
    r2 = forecast_service.get_forecast_data('SKU-009', region='North', lookback_weeks=12)
    record('New scenario - different product', r1.get('product_id') != r2.get('product_id'))
except Exception as e:
    record('New scenario', False, str(e))
# Test 5 - Outcome update
print('\n[Test 5] Outcome update persistence')
try:
    r = forecast_service.get_forecast_data('SKU-001', region='North', lookback_weeks=12)
    record('Outcome update - re-query works', r.get('success', True))
except Exception as e:
    record('Outcome update', False, str(e))
# Test 6 - What-if scenario comparison
print('\n[Test 6] What-if scenario comparison')
try:
    baseline = {'demand': 1000, 'revenue': 50000, 'inventory': 3000}
    what_if = {'demand_adjustment_pct': 15}
    current = {'demand': 1150, 'revenue': 57500, 'inventory': 3000}
    cmp = comparison_service.compare(baseline, current, what_if)
    record('What-if - deltas calculated', 'demand' in cmp.get('deltas', {}))
    record('What-if - delta_pct computed', cmp.get('deltas', {}).get('demand', {}).get('delta_pct') == 15.0)
    record('What-if - summary generated', len(cmp.get('summary', '')) > 0)
except Exception as e:
    record('What-if scenario', False, str(e))
# Test 7 - Ambiguous entity
print('\n[Test 7] Ambiguous entity resolution')
try:
    ctx = entity_service.resolve_product(product_name='Product')
    record('Ambiguous - multiple candidates', ctx.ambiguous and len(ctx.candidates) > 1)
    ctx2 = entity_service.resolve_product(product_id='SKU-001')
    record('Exact match - resolved', ctx2.resolved and ctx2.product_id == 'SKU-001')
except Exception as e:
    record('Ambiguous entity', False, str(e))
# Test 8 - Insufficient history
print('\n[Test 8] Insufficient history')
try:
    r = rca_service.run_rca('SKU-010', region='West', lookback_weeks=12)
    record('Insufficient history - handles gracefully', r.get('success') == False or r.get('data_quality', {}).get('data_status') in ['INSUFFICIENT', 'PARTIAL'])
except Exception as e:
    record('Insufficient history', False, str(e))
# Test 9 - Stockout distortion
print('\n[Test 9] Stockout distortion')
try:
    rca = rca_service.run_rca('SKU-007', region='South', lookback_weeks=26)
    inv_hyps = [h for h in rca.get('hypotheses', []) if 'INVENTORY' in h.get('cause', '')]
    record('Stockout - inventory hypothesis raised', len(inv_hyps) > 0)
    record('Stockout - supply constraint flagged', any('supply' in h.get('reasoning', '').lower() for h in inv_hyps))
except Exception as e:
    record('Stockout distortion', False, str(e))
# Test 10 - Revenue retrieval
print('\n[Test 10] Revenue retrieval')
try:
    rev = revenue_service.get_revenue_data('SKU-001', region='North', lookback_weeks=12)
    record('Revenue - gross calculated', rev.get('gross_revenue', 0) > 0)
    record('Revenue - net calculated', rev.get('net_revenue', 0) > 0)
except Exception as e:
    record('Revenue retrieval', False, str(e))
# Extra - Historical patterns
print('\n[Extra] Historical Pattern Analysis')
try:
    p = pattern_service.analyze_patterns('SKU-001', region='North', lookback_weeks=12)
    record('Pattern - trend detected', 'trend' in p.get('patterns', {}))
    record('Pattern - volatility calculated', 'volatility' in p.get('patterns', {}))
    record('Pattern - level shift checked', 'level_shift' in p.get('patterns', {}))
except Exception as e:
    record('Historical pattern', False, str(e))
# Extra - Data quality
print('\n[Extra] Data Quality Checks')
try:
    record('DQ - entity check', data_quality_service.check_entity('SKU-001').get('valid', False))
    record('DQ - date range', data_quality_service.check_date_range('SKU-001').get('valid', False))
    record('DQ - metrics valid', data_quality_service.check_metrics('SKU-001').get('valid', False))
except Exception as e:
    record('Data quality', False, str(e))
# Extra - Readiness registry
print('\n[Extra] Readiness Registry')
try:
    ready_count = spark.sql(f"SELECT COUNT(*) FROM {DB}.rca_readiness_registry WHERE status = 'READY'").collect()[0][0]
    record('Readiness - capabilities populated', ready_count >= 7, f'{ready_count} READY')
except Exception as e:
    record('Readiness registry', False, str(e))
# Summary
print('\n' + '=' * 70)
print('  GOLDEN TEST SUITE SUMMARY')
print('=' * 70)
passed = sum(1 for _, s, _ in results if s == 'PASS')
failed = sum(1 for _, s, _ in results if s == 'FAIL')
print(f'  Total tests: {len(results)}')
print(f'  Passed: {passed}')
print(f'  Failed: {failed}')
if results:
    print(f'  Pass rate: {passed / len(results) * 100:.1f}%')
if failed > 0:
    print('\n  FAILED TESTS:')
    for name, status, detail in results:
        if status == 'FAIL':
            print(f'    FAIL {name}: {detail}')
print('=' * 70)
print('  ALL TESTS PASSED' if failed == 0 else f'  {failed} TEST(S) FAILED')
print('=' * 70)