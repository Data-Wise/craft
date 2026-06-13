#!/usr/bin/env python3
"""
Test suite for scripts/workflow_parse.py — the deterministic workflow-engine core.

Covers Increment 1 of the workflow-engine plan (mechanical core):
  - Structural output validator (D2 layer 1, gating)
  - YAML form + shape-DSL form -> identical wave plan (D1, D3)
  - Empty fan-out hard error naming upstream (D6 / FR8)
  - Cache-key hash + downstream cascade invalidation (D4)
  - Run-wide semaphore-file arithmetic (D5 / FR7)

Pure stdlib core (no jsonschema, no node). YAML input reading uses PyYAML,
already a craft dependency.
"""

import os
import sys

import pytest

# Add parent directory to path to import the parser module from scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import workflow_parse as wp  # noqa: E402

from pathlib import Path  # noqa: E402

PLUGIN_DIR = Path(__file__).resolve().parent.parent

pytestmark = [pytest.mark.unit, pytest.mark.orchestrator]


# ---------------------------------------------------------------------------
# D2 layer 1 — structural output validator (gating, deterministic)
# ---------------------------------------------------------------------------

def test_valid_output_has_no_structural_errors():
    errors = wp.structural_errors({"dimensions": ["a", "b"]}, {"dimensions": "string[]"})
    assert errors == []


def test_missing_required_key_is_a_structural_error():
    errors = wp.structural_errors({}, {"dimensions": "string[]"})
    assert len(errors) == 1
    assert "dimensions" in errors[0]


def test_wrong_primitive_type_is_a_structural_error():
    errors = wp.structural_errors({"confirmed": "yes"}, {"confirmed": "boolean"})
    assert len(errors) == 1
    assert "confirmed" in errors[0]


def test_boolean_is_not_accepted_as_number():
    # bool is an int subclass in Python — the validator must reject it for `number`.
    errors = wp.structural_errors({"score": True}, {"score": "number"})
    assert len(errors) == 1


def test_scalar_where_array_expected_is_a_structural_error():
    errors = wp.structural_errors({"dimensions": "oops"}, {"dimensions": "string[]"})
    assert len(errors) == 1
    assert "dimensions" in errors[0]


def test_wrong_array_element_type_is_a_structural_error():
    errors = wp.structural_errors({"dimensions": [1, 2]}, {"dimensions": "string[]"})
    assert len(errors) == 1


def test_object_array_accepts_objects_rejects_scalars():
    assert wp.structural_errors({"findings": [{"x": 1}]}, {"findings": "object[]"}) == []
    assert len(wp.structural_errors({"findings": [1]}, {"findings": "object[]"})) == 1


def test_validate_output_raises_structural_error_on_miss():
    # The gating call: a structural miss is a HARD STOP (D2 layer 1).
    with pytest.raises(wp.StructuralError) as exc:
        wp.validate_output({}, {"dimensions": "string[]"}, stage="decompose")
    assert "decompose" in str(exc.value)


def test_validate_output_passes_silently_when_valid():
    # Returns None, raises nothing.
    assert wp.validate_output({"confirmed": True}, {"confirmed": "boolean"}, stage="verify") is None


# ---------------------------------------------------------------------------
# D1 / D3 — both definition forms compile to an identical wave plan
# ---------------------------------------------------------------------------

# The spec's canonical 5-dim review case, expressed in both forms. These are
# intended to be EQUIVALENT — the parser must normalize them to the same plan.

YAML_FORM = """
name: code-review-sweep
max_concurrent: 16
stages:
  - id: decompose
    type: agent
    role: task-analyzer
    output_schema: { dimensions: "string[]" }
  - id: cover
    type: parallel
    over: ${decompose.dimensions}
    agent: { role: reviewer, output_schema: { findings: "object[]" } }
  - id: verify
    type: parallel
    over: ${cover.*.findings}
    fan: 2
    agent: { role: verifier, output_schema: { confirmed: "boolean" } }
  - id: synthesize
    type: agent
    role: docs-architect
    input: ${verify.*}
"""

DSL_FORM = """
pipeline(
  agent("decompose", { role: "task-analyzer", output_schema: { dimensions: "string[]" } }),
  parallel(
    map("decompose.dimensions",
        agent("cover", { role: "reviewer", output_schema: { findings: "object[]" } }))),
  parallel(
    flatMap("cover[].findings",
            fan(2, agent("verify", { role: "verifier", output_schema: { confirmed: "boolean" } })))),
  agent("synthesize", { role: "docs-architect", input: "verify[]" })
);
"""


def test_yaml_single_agent_compiles_to_static_wave():
    plan = wp.parse("name: solo\nstages:\n  - id: only\n    type: agent\n    role: worker\n")
    assert len(plan["waves"]) == 1
    wave = plan["waves"][0]
    assert wave["id"] == "only"
    assert wave["type"] == "agent"
    assert wave["fanout"] == {"kind": "static", "count": 1}
    assert wave["role"] == "worker"


def test_both_forms_produce_identical_wave_plan():
    yaml_plan = wp.parse(YAML_FORM)
    dsl_plan = wp.parse(DSL_FORM)
    # D1: the execution-relevant wave structure is identical across forms.
    assert yaml_plan["waves"] == dsl_plan["waves"]


def test_parallel_fanout_normalizes_data_driven_binding():
    plan = wp.parse(YAML_FORM)
    waves = {w["id"]: w for w in plan["waves"]}

    cover = waves["cover"]
    assert cover["type"] == "parallel"
    assert cover["fanout"] == {
        "kind": "dynamic",
        "over": "decompose.dimensions",
        "flatten": False,
        "fan": 1,
    }
    assert cover["role"] == "reviewer"

    verify = waves["verify"]
    # ${cover.*.findings} normalizes to cover[].findings (flatten one level),
    # fan: 2 => two verifiers per finding.
    assert verify["fanout"] == {
        "kind": "dynamic",
        "over": "cover[].findings",
        "flatten": True,
        "fan": 2,
    }


def test_synthesize_input_binding_normalizes_collection_glob():
    # ${verify.*} (YAML) and "verify[]" (DSL) both mean "all of verify's outputs".
    yaml_plan = wp.parse(YAML_FORM)
    synth = [w for w in yaml_plan["waves"] if w["id"] == "synthesize"][0]
    assert synth["input"] == "verify[]"


def test_dsl_map_with_flatten_path_is_a_grammar_error():
    # map() binds a single array (no flatten); a [] path must use flatMap.
    bad = 'pipeline(parallel(map("cover[].findings", agent("x", { role: "r" }))))'
    with pytest.raises(wp.WorkflowError):
        wp.parse(bad)


# ---------------------------------------------------------------------------
# D6 / FR8 — empty fan-out is a hard error naming the upstream stage
# ---------------------------------------------------------------------------

def test_nonempty_fanout_resolves_to_bound_items():
    items = wp.resolve_fanout(
        "decompose.dimensions",
        {"decompose": {"dimensions": ["security", "perf"]}},
    )
    assert items == ["security", "perf"]


def test_flatten_fanout_collects_across_the_collection():
    upstream = {"cover": [{"findings": [1, 2]}, {"findings": [3]}]}
    assert wp.resolve_fanout("cover[].findings", upstream) == [1, 2, 3]


def test_collection_glob_resolves_to_all_outputs():
    upstream = {"verify": [{"confirmed": True}, {"confirmed": False}]}
    assert wp.resolve_fanout("verify[]", upstream) == [
        {"confirmed": True},
        {"confirmed": False},
    ]


def test_empty_fanout_hard_aborts_naming_upstream():
    with pytest.raises(wp.EmptyFanoutError) as exc:
        wp.resolve_fanout("decompose.dimensions", {"decompose": {"dimensions": []}})
    msg = str(exc.value)
    assert "decompose" in msg  # names the upstream stage that produced empty


def test_empty_flatten_fanout_also_hard_aborts():
    # Every upstream agent returned an empty findings array.
    upstream = {"cover": [{"findings": []}, {"findings": []}]}
    with pytest.raises(wp.EmptyFanoutError) as exc:
        wp.resolve_fanout("cover[].findings", upstream)
    assert "cover" in str(exc.value)


def test_heterogeneous_flatten_missing_field_is_a_workflow_error():
    # Agents returned different shapes: one {findings:[]}, one {notes:[]}.
    # Binding cover[].findings must fail as a structured WorkflowError,
    # not a bare KeyError/TypeError that aborts the whole resolver.
    upstream = {"cover": [{"findings": [1]}, {"notes": [2]}]}
    with pytest.raises(wp.WorkflowError) as exc:
        wp.resolve_fanout("cover[].findings", upstream)
    assert "findings" in str(exc.value)


def test_dot_field_missing_on_object_is_a_workflow_error():
    # A .field walk over an object that lacks the field (or a scalar)
    # must raise WorkflowError, not a bare KeyError/TypeError.
    upstream = {"decompose": {"dimensions": [1]}}
    with pytest.raises(wp.WorkflowError) as exc:
        wp.resolve_fanout("decompose.missing", upstream)
    assert "missing" in str(exc.value)


# ---------------------------------------------------------------------------
# D4 — cache-key hash (content hash of the three components)
# ---------------------------------------------------------------------------

def test_cache_key_is_deterministic_for_identical_inputs():
    block = {"id": "cover", "type": "parallel", "role": "reviewer"}
    a = wp.cache_key(block, {"target": "src/"}, "reviewer@v1")
    b = wp.cache_key(block, {"target": "src/"}, "reviewer@v1")
    assert a == b


def test_cache_key_is_insensitive_to_dict_ordering():
    a = wp.cache_key({"id": "x", "role": "r"}, {"a": 1, "b": 2}, "r@v1")
    b = wp.cache_key({"role": "r", "id": "x"}, {"b": 2, "a": 1}, "r@v1")
    assert a == b


def test_cache_key_changes_when_resolved_input_changes():
    block = {"id": "cover", "type": "parallel"}
    assert wp.cache_key(block, {"target": "src/"}, "r@v1") != wp.cache_key(
        block, {"target": "lib/"}, "r@v1"
    )


def test_cache_key_changes_when_role_prompt_version_changes():
    block = {"id": "cover", "type": "parallel"}
    assert wp.cache_key(block, {"target": "src/"}, "r@v1") != wp.cache_key(
        block, {"target": "src/"}, "r@v2"
    )


def test_cache_key_changes_when_definition_block_changes():
    assert wp.cache_key({"id": "cover", "role": "reviewer"}, {}, "r@v1") != wp.cache_key(
        {"id": "cover", "role": "auditor"}, {}, "r@v1"
    )


# ---------------------------------------------------------------------------
# D4 — downstream cascade invalidation
# ---------------------------------------------------------------------------

# The canonical 4-stage pipeline dependency structure.
PIPE_STAGES = ["decompose", "cover", "verify", "synthesize"]
PIPE_DEPS = {
    "decompose": [],
    "cover": ["decompose"],
    "verify": ["cover"],
    "synthesize": ["verify"],
}


def test_no_changes_means_full_cache_reuse():
    assert wp.cascade_invalidate(PIPE_STAGES, set(), PIPE_DEPS) == set()


def test_changing_a_stage_invalidates_only_itself_and_downstream():
    # 'verify' changed -> verify + synthesize re-run; decompose/cover stay cached.
    invalid = wp.cascade_invalidate(PIPE_STAGES, {"verify"}, PIPE_DEPS)
    assert invalid == {"verify", "synthesize"}


def test_changing_the_root_cascades_to_the_whole_pipeline():
    invalid = wp.cascade_invalidate(PIPE_STAGES, {"decompose"}, PIPE_DEPS)
    assert invalid == {"decompose", "cover", "verify", "synthesize"}


def test_cascade_handles_a_diamond_dependency():
    # synthesize consumes two independent upstreams; changing one cascades.
    stages = ["root", "left", "right", "synthesize"]
    deps = {
        "root": [],
        "left": ["root"],
        "right": ["root"],
        "synthesize": ["left", "right"],
    }
    invalid = wp.cascade_invalidate(stages, {"left"}, deps)
    assert invalid == {"left", "synthesize"}
    assert "right" not in invalid


# ---------------------------------------------------------------------------
# D5 / FR7 — run-wide semaphore as a counter FILE (survives compression)
# ---------------------------------------------------------------------------

def test_semaphore_reads_zero_when_file_absent(tmp_path):
    assert wp.sem_read(str(tmp_path / "semaphore.count")) == 0


def test_semaphore_acquire_increments_up_to_the_ceiling(tmp_path):
    path = str(tmp_path / "semaphore.count")
    assert wp.sem_acquire(path, ceiling=2) is True
    assert wp.sem_read(path) == 1
    assert wp.sem_acquire(path, ceiling=2) is True
    assert wp.sem_read(path) == 2


def test_semaphore_acquire_refuses_at_ceiling_without_mutating(tmp_path):
    path = str(tmp_path / "semaphore.count")
    wp.sem_acquire(path, ceiling=1)
    assert wp.sem_read(path) == 1
    # ceiling reached: refuse, and DO NOT increment past the ceiling.
    assert wp.sem_acquire(path, ceiling=1) is False
    assert wp.sem_read(path) == 1


def test_semaphore_release_decrements_and_floors_at_zero(tmp_path):
    path = str(tmp_path / "semaphore.count")
    wp.sem_acquire(path, ceiling=5)
    assert wp.sem_release(path) == 0
    # never goes negative even if released more than acquired.
    assert wp.sem_release(path) == 0


def test_semaphore_reconcile_resets_to_live_agent_count(tmp_path):
    # Residual-risk mitigation: a mid-run crash between increment and dispatch
    # leaks a count; reconcile against the live-agent manifest at wave boundary.
    path = str(tmp_path / "semaphore.count")
    wp.sem_acquire(path, ceiling=10)
    wp.sem_acquire(path, ceiling=10)  # counter says 2
    assert wp.sem_reconcile(path, live_count=1) == 1  # only 1 actually live
    assert wp.sem_read(path) == 1


# ---------------------------------------------------------------------------
# Increment 2 — executor support: file load, CLI emit, hybrid D2 gate
# ---------------------------------------------------------------------------

def test_parse_file_reads_a_workflow_definition(tmp_path):
    path = tmp_path / "WORKFLOW-x.yaml"
    path.write_text(YAML_FORM)
    plan = wp.parse_file(str(path))
    assert [w["id"] for w in plan["waves"]] == [
        "decompose",
        "cover",
        "verify",
        "synthesize",
    ]


def test_cli_emits_the_wave_plan_as_json(tmp_path, capsys):
    import json

    path = tmp_path / "WORKFLOW-x.yaml"
    path.write_text(YAML_FORM)
    rc = wp.main([str(path)])
    assert rc == 0
    plan = json.loads(capsys.readouterr().out)
    assert plan["waves"][0]["id"] == "decompose"


def test_cli_exits_nonzero_and_reports_an_invalid_definition(tmp_path, capsys):
    path = tmp_path / "WORKFLOW-bad.yaml"
    # parallel stage with no fan-out binding -> compile error
    path.write_text("name: bad\nstages:\n  - id: x\n    type: parallel\n    agent: { role: r }\n")
    rc = wp.main([str(path)])
    assert rc != 0
    err = capsys.readouterr().err.lower()
    assert "over" in err or "fan-out" in err


def test_gate_output_passes_structurally_valid_output():
    result = wp.gate_output({"confirmed": True}, {"confirmed": "boolean"}, stage="verify")
    assert result["ok"] is True
    assert result["structural_errors"] == []
    assert result["semantic_warning"] is None


def test_gate_output_fails_closed_on_structural_miss():
    # Failure isolation: returns ok=False (caller fails the branch), not raise.
    result = wp.gate_output({}, {"dimensions": "string[]"}, stage="decompose")
    assert result["ok"] is False
    assert any("dimensions" in e for e in result["structural_errors"])


def test_semantic_warning_is_surfaced_but_never_flips_the_gate():
    # D2: the LLM semantic check is ADVISORY — a warning must not block.
    result = wp.gate_output(
        {"findings": [{"x": 1}]},
        {"findings": "object[]"},
        stage="cover",
        semantic_warning="these read like TODOs, not findings",
    )
    assert result["ok"] is True  # structurally valid -> gate stays open
    assert result["semantic_warning"] == "these read like TODOs, not findings"


# ---------------------------------------------------------------------------
# Increment 3 — dry-run rendering (FR5): wave plan view, no agents spawned
# ---------------------------------------------------------------------------

def test_dry_run_actions_describe_each_wave():
    actions = wp.dry_run_actions(wp.parse(YAML_FORM))
    joined = "\n".join(actions)
    # one line per stage, in order
    assert len(actions) == 4
    assert actions[0].startswith("decompose")
    # data-driven fan-out shows it binds to the upstream array + the fan factor
    assert "decompose.dimensions" in joined
    assert "parallel" in joined
    assert "fan 2" in joined  # verify stage fans 2 per finding


def test_dry_run_actions_note_dynamic_width_is_runtime():
    actions = wp.dry_run_actions(wp.parse(YAML_FORM))
    cover_line = [a for a in actions if a.startswith("cover")][0]
    # statically-unknown fan-out width is shown symbolically, not a fake number
    assert "N" in cover_line


def test_cli_dry_run_prints_plan_without_json(tmp_path, capsys):
    path = tmp_path / "WORKFLOW-x.yaml"
    path.write_text(YAML_FORM)
    rc = wp.main(["--dry-run", str(path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "DRY RUN" in out
    assert "code-review-sweep" in out  # workflow name
    assert "16" in out  # run-wide ceiling surfaced
    assert "decompose" in out and "synthesize" in out


# ---------------------------------------------------------------------------
# Increment 4 / D7 — known-shape detection (router SUGGESTS, never switches)
# ---------------------------------------------------------------------------

def test_full_decompose_cover_verify_synthesize_shape_is_detected():
    text = (
        "decompose the review into dimensions, cover each dimension in parallel "
        "with a reviewer, verify each finding, then synthesize a report"
    )
    assert wp.detects_workflow_shape(text) is True


def test_parallel_verify_summarize_shape_is_detected():
    assert wp.detects_workflow_shape(
        "fan out reviewers in parallel, verify the findings, then summarize"
    ) is True


def test_ordinary_feature_request_does_not_trigger():
    assert wp.detects_workflow_shape("add a logout button to the navbar") is False


def test_a_lone_signal_does_not_trigger_false_positive():
    # D7 residual-risk guard: one signal word must NOT hijack to :workflow.
    assert wp.detects_workflow_shape("verify the login flow works") is False
    assert wp.detects_workflow_shape("review the architecture") is False
    assert wp.detects_workflow_shape("run the tests in parallel") is False


# ---------------------------------------------------------------------------
# Increment 5 / D8 — drive-engine verify-gate convergence
# ---------------------------------------------------------------------------

VERIFY_WORKFLOW = """
name: drive-convergence
stages:
  - id: implement
    type: agent
    role: coder
  - id: gate
    type: verify
    command: python3 tests/test_craft_plugin.py
"""


def test_verify_stage_compiles_to_a_static_gate_carrying_its_command():
    plan = wp.parse(VERIFY_WORKFLOW)
    gate = [w for w in plan["waves"] if w["id"] == "gate"][0]
    assert gate["type"] == "verify"
    assert gate["command"] == "python3 tests/test_craft_plugin.py"
    assert gate["fanout"] == {"kind": "static", "count": 1}


def test_drive_engine_verify_semantics_stay_reproducible_in_the_engine():
    # D8 convergence guard: the workflow `verify` primitive must keep
    # drive-engine's gate semantics — a real command whose EXIT STATUS is
    # authoritative, never a green transcript. If either skill drifts, fail.
    drive = (PLUGIN_DIR / "skills/orchestration/drive-engine/SKILL.md").read_text().lower()
    engine = (PLUGIN_DIR / "skills/orchestration/workflow-engine/SKILL.md").read_text().lower()
    for text in (drive, engine):
        assert "exit status" in text
        assert "authoritative" in text
        assert "green transcript" in text


def test_example_workflow_file_parses_to_the_canonical_five_stage_shape():
    example = PLUGIN_DIR / "examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml"
    plan = wp.parse_file(str(example))
    ids = [w["id"] for w in plan["waves"]]
    assert ids == ["decompose", "cover", "verify", "synthesize"]
    cover = [w for w in plan["waves"] if w["id"] == "cover"][0]
    assert cover["fanout"]["kind"] == "dynamic"


# ---------------------------------------------------------------------------
# Adversarial hardening (post-review): close real gaps the probes found
# ---------------------------------------------------------------------------

def test_dsl_flatten_operator_is_accepted_as_a_flatten_fanout():
    # D3 vocabulary lists map/flatMap/FLATTEN; flatten requires a [] path.
    plan = wp.parse(
        'pipeline('
        'agent("cover", { role: "reviewer" }), '
        'parallel(flatten("cover[].findings", agent("v", { role: "r" }))))'
    )
    wave = [w for w in plan["waves"] if w["id"] == "v"][0]
    assert wave["fanout"]["over"] == "cover[].findings"
    assert wave["fanout"]["flatten"] is True


def test_dsl_flatten_without_bracket_path_is_a_grammar_error():
    with pytest.raises(wp.WorkflowError):
        wp.parse('pipeline(parallel(flatten("decompose.dimensions", agent("v", { role: "r" }))))')


def test_build_deps_extracts_the_dependency_graph_from_bindings():
    # The missing link that makes the D4 cascade usable on a real plan.
    deps = wp.build_deps(wp.parse(YAML_FORM))
    assert deps == {
        "decompose": [],
        "cover": ["decompose"],
        "verify": ["cover"],
        "synthesize": ["verify"],
    }


def test_cascade_runs_end_to_end_from_a_plan():
    plan = wp.parse(YAML_FORM)
    deps = wp.build_deps(plan)
    order = [w["id"] for w in plan["waves"]]
    # editing 'cover' must re-run cover + verify + synthesize, not decompose
    invalid = wp.cascade_invalidate(order, {"cover"}, deps)
    assert invalid == {"cover", "verify", "synthesize"}


def test_binding_to_unknown_or_forward_stage_is_rejected_at_compile_time():
    bad = "name: b\nstages:\n  - id: cover\n    type: parallel\n    over: ${nope.items}\n    agent: { role: r }"
    with pytest.raises(wp.WorkflowError) as exc:
        wp.parse(bad)
    assert "nope" in str(exc.value)


def test_loop_stage_carries_max_iter_into_the_wave():
    plan = wp.parse("name: l\nstages:\n  - id: fix\n    type: loop\n    role: coder\n    max_iter: 5")
    wave = plan["waves"][0]
    assert wave["type"] == "loop"
    assert wave["max_iter"] == 5
