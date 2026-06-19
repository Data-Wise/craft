import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("qe", pathlib.Path(__file__).parent.parent/"scripts"/"quota_estimate.py")
qe = importlib.util.module_from_spec(spec); spec.loader.exec_module(qe)

def test_estimate_distribution():
    markers = [{"engine":"workflow","cost_weighted":c} for c in [100,120,110,130,90]]
    e = qe.estimate("workflow", markers)
    assert e["n"] == 5 and e["cold_start"] is False
    assert e["p05"] <= e["median"] <= e["p95"]

def test_estimate_cold_start():
    e = qe.estimate("workflow", [{"engine":"workflow","cost_weighted":100}])
    assert e["cold_start"] is True
