import importlib.util, pathlib
spec = importlib.util.spec_from_file_location(
    "otr", pathlib.Path(__file__).parent.parent / "scripts" / "orchestrate-token-report.py")
otr = importlib.util.module_from_spec(spec); spec.loader.exec_module(otr)

def test_cost_weighted_applies_per_type_weights():
    usage = {"input_tokens": 100, "output_tokens": 10,
             "cache_creation_input_tokens": 40, "cache_read_input_tokens": 200}
    # 100*1 + 10*5 + 40*1.25 + 200*0.1 = 100 + 50 + 50 + 20 = 220
    assert otr.cost_weighted(usage) == 220.0

def test_cost_weighted_tolerates_missing_fields():
    assert otr.cost_weighted({"input_tokens": 10}) == 10.0

import pathlib
FX = pathlib.Path(__file__).parent / "fixtures" / "token_report" / "session.jsonl"

def test_iter_usages_slices_by_timestamp():
    usages = otr.iter_usages(str(FX), "2026-06-17T10:00:00Z", "2026-06-17T10:30:00Z")
    assert len(usages) == 2
    assert sum(u["input_tokens"] for u in usages) == 150

def test_iter_usages_no_window_returns_all():
    assert len(otr.iter_usages(str(FX), None, None)) == 3
