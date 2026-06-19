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
