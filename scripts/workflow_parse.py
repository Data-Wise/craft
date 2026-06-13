#!/usr/bin/env python3
"""Deterministic workflow-engine parser/core for /craft:orchestrate:workflow.

Mechanical core (Increment 1): reads a WORKFLOW definition (YAML form or the
frozen shape-DSL form), compiles it to a canonical *wave plan*, structurally
validates agent outputs (D2 layer 1), computes cascade-aware cache keys (D4),
and does run-wide semaphore-file arithmetic (D5).

Determinism core (validation + hashing + semaphore) is pure stdlib — no
jsonschema, no node (D2/D3). YAML *input* reading uses PyYAML, already a craft
dependency; it is imported lazily inside parse_yaml() so the determinism core
never even touches it.
"""

import hashlib
import json
import os
import re

# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class WorkflowError(Exception):
    """Base class for all workflow-engine errors."""


class StructuralError(WorkflowError):
    """D2 layer-1 structural schema miss — a hard stop (gating)."""


class EmptyFanoutError(WorkflowError):
    """D6/FR8 — a fan-out bound to an empty upstream array aborts the run."""


# ---------------------------------------------------------------------------
# D2 layer 1 — structural output validator (gating, deterministic)
# ---------------------------------------------------------------------------

_SCALAR_TYPES = ("string", "number", "boolean")
_ARRAY_TYPES = ("string[]", "number[]", "boolean[]", "object[]")


def _scalar_ok(value, type_name):
    if type_name == "string":
        return isinstance(value, str)
    if type_name == "number":
        # bool is an int subclass — exclude it explicitly.
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if type_name == "boolean":
        return isinstance(value, bool)
    return False


def structural_errors(data, schema):
    """Return a list of structural error strings (empty == valid). Pure.

    Dialect (v1): every declared key is required; values are primitives
    (string/number/boolean) or homogeneous arrays (string[]/number[]/
    boolean[]/object[]). No oneOf, regex, or conditional subschemas (D2).
    """
    errors = []
    if not isinstance(data, dict):
        return [f"output must be an object, got {type(data).__name__}"]
    for key, type_spec in schema.items():
        if key not in data:
            errors.append(f"missing required key '{key}' ({type_spec})")
            continue
        value = data[key]
        if type_spec in _SCALAR_TYPES:
            if not _scalar_ok(value, type_spec):
                errors.append(
                    f"key '{key}': expected {type_spec}, got {type(value).__name__}"
                )
        elif type_spec in _ARRAY_TYPES:
            if not isinstance(value, list):
                errors.append(
                    f"key '{key}': expected {type_spec}, got {type(value).__name__}"
                )
                continue
            element_type = type_spec[:-2]  # strip "[]"
            # One error per offending key (first bad element is the evidence)
            # so the hard-stop message stays proportional to the schema, not
            # the data.
            for i, element in enumerate(value):
                if element_type == "object":
                    ok = isinstance(element, dict)
                else:
                    ok = _scalar_ok(element, element_type)
                if not ok:
                    errors.append(
                        f"key '{key}'[{i}]: expected {element_type}, "
                        f"got {type(element).__name__}"
                    )
                    break
        else:
            errors.append(f"key '{key}': unknown type spec '{type_spec}'")
    return errors


def validate_output(data, schema, stage="?"):
    """Gating check: raise StructuralError on any structural miss (D2).

    A structural miss is a HARD STOP — no silent parse-guessing.
    """
    errors = structural_errors(data, schema)
    if errors:
        raise StructuralError(
            f"stage '{stage}' output failed structural schema: " + "; ".join(errors)
        )
    return None


# ---------------------------------------------------------------------------
# D1 / D3 — definition parsing -> canonical wave plan
# ---------------------------------------------------------------------------


DEFAULT_CEILING = 16


def _canon_path(raw):
    """Normalize a binding string from either form to one canonical token.

    Both ``${stage.*.field}`` (YAML glob) and ``stage[].field`` (DSL) mean
    "map across the upstream collection and flatten one level" -> canonical
    ``stage[].field``. ``${stage.*}`` and ``stage[]`` both mean "all outputs
    of stage" -> canonical ``stage[]``.
    """
    if raw is None:
        return None
    s = raw.strip()
    if s.startswith("${") and s.endswith("}"):
        s = s[2:-1].strip()
    s = s.replace(".*.", "[].")
    if s.endswith(".*"):
        s = s[:-2] + "[]"
    return s


def parse(text, form="auto"):
    """Parse a WORKFLOW definition (YAML or shape-DSL) into a canonical plan."""
    if form == "auto":
        form = "dsl" if _looks_like_dsl(text) else "yaml"
    definition = parse_dsl(text) if form == "dsl" else parse_yaml(text)
    return compile_plan(definition)


def _looks_like_dsl(text):
    return re.match(r"\s*(pipeline|parallel|agent)\s*\(", text) is not None


def parse_file(path):
    """Read a WORKFLOW definition file and compile it to a wave plan."""
    with open(path, encoding="utf-8") as handle:
        return parse(handle.read())


_SHAPE_SIGNALS = {
    "decompose": ("decompose", "break down", "break it down", "split into", "dimensions", "for each"),
    "fanout": ("fan out", "fan-out", "in parallel", "parallel", "one per", "cover each", "per finding", "reviewers"),
    "verify": ("verify", "verifier", "double-check", "confirm each", "validate each"),
    "synthesize": ("synthesize", "synthesise", "aggregate", "summarize", "summarise", "roll up", "combine", "merge findings", "final report"),
}


def detects_workflow_shape(text):
    """Heuristic for D7: does this read like a coded decompose→cover→verify→
    synthesize shape worth SUGGESTING ``:workflow`` for?

    Deliberately conservative — fires only when ≥3 of the four stage categories
    appear (or the explicit decompose…synthesize chain). A lone "verify" or
    "parallel" must NOT trigger; auto-routing a task better served by improvised
    ``orchestrate`` is the accepted residual risk, so the router only ever
    SUGGESTS (confirm-before-switch), never silently hijacks.
    """
    low = text.lower()
    categories = sum(
        1
        for signals in _SHAPE_SIGNALS.values()
        if any(signal in low for signal in signals)
    )
    explicit = "decompose" in low and ("synthesize" in low or "synthesise" in low)
    return categories >= 3 or explicit


def dry_run_actions(plan):
    """Human-readable one-line-per-wave description of a plan (FR5 data).

    Statically-unknown fan-out width is shown symbolically (``xN``) — never a
    fabricated number — because data-driven width is only known at runtime
    (D1). The command wraps these lines in the shared dry-run box; this stays
    presentation-free so it is trivially testable and stdlib-pure.
    """
    lines = []
    for wave in plan["waves"]:
        role = wave.get("role") or "?"
        if wave["type"] == "parallel":
            fanout = wave["fanout"]
            fan_note = f", fan {fanout['fan']}" if fanout.get("fan", 1) != 1 else ""
            lines.append(
                f"{wave['id']}: parallel xN over ${{{fanout['over']}}}{fan_note} "
                f"-> {role}"
            )
        elif wave["type"] == "verify":
            command = wave.get("command") or "(auto-detected)"
            lines.append(
                f"{wave['id']}: verify-gate -> runs `{command}`, exit status authoritative"
            )
        else:
            lines.append(f"{wave['id']}: agent -> {role}")
    return lines


def gate_output(data, schema, stage="?", semantic_warning=None):
    """Hybrid D2 gate for one agent output (failure-isolating, non-raising).

    Structural validation is the gate (``ok=False`` on any miss → caller fails
    just that branch). The semantic warning is advisory: it is surfaced in the
    verdict but NEVER flips ``ok`` (blocking on LLM judgment would reintroduce
    the non-determinism D2 designed out).
    """
    errors = structural_errors(data, schema)
    return {
        "stage": stage,
        "ok": len(errors) == 0,
        "structural_errors": errors,
        "semantic_warning": semantic_warning,
    }


def parse_yaml(text):
    """Parse the YAML definition form into a normalized definition dict.

    Uses PyYAML for input reading only; the determinism-critical path
    (normalization below) is pure stdlib.
    """
    import yaml

    raw = yaml.safe_load(text) or {}
    stages = []
    for s in raw.get("stages", []):
        typ = s["type"]
        role = s.get("role")
        output_schema = s.get("output_schema")
        over = None
        fan = s.get("fan", 1)
        if typ == "parallel":
            agent_spec = s.get("agent", {})
            role = agent_spec.get("role", role)
            output_schema = agent_spec.get("output_schema", output_schema)
            over = _canon_path(s.get("over"))
        stages.append(
            {
                "id": s["id"],
                "type": typ,
                "role": role,
                "output_schema": output_schema,
                "over": over,
                "fan": fan,
                "input": _canon_path(s.get("input")),
                "command": s.get("command"),  # for type=verify (D8)
                "max_iter": s.get("max_iter"),  # for type=loop
            }
        )
    return {
        "name": raw.get("name"),
        "max_concurrent": raw.get("max_concurrent", DEFAULT_CEILING),
        "stages": stages,
    }


# --- frozen shape-DSL parser (D3): tokenizer + recursive descent, no eval ---


def _tokenize_dsl(text):
    """Tokenize the frozen DSL into (kind, value) tuples. Pure stdlib."""
    tokens = []
    i, n = 0, len(text)
    punct = set("(){},:")
    while i < n:
        c = text[i]
        if c.isspace() or c == ";":
            i += 1
            continue
        if c in ('"', "'"):
            j = i + 1
            while j < n and text[j] != c:
                j += 1
            if j >= n:
                raise WorkflowError("unterminated string in shape-DSL")
            tokens.append(("string", text[i + 1 : j]))
            i = j + 1
            continue
        if c in punct:
            tokens.append(("punct", c))
            i += 1
            continue
        if c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            tokens.append(("number", int(text[i:j])))
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (text[j].isalnum() or text[j] == "_"):
                j += 1
            tokens.append(("ident", text[i:j]))
            i = j
            continue
        raise WorkflowError(f"unexpected character {c!r} in shape-DSL")
    return tokens


class _DSLReader:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def _peek(self):
        return self.toks[self.i] if self.i < len(self.toks) else (None, None)

    def _next(self):
        tok = self._peek()
        self.i += 1
        return tok

    def _expect(self, value):
        kind, val = self._next()
        if val != value:
            raise WorkflowError(f"expected {value!r} in shape-DSL, got {val!r}")

    def program(self):
        kind, val = self._peek()
        if val == "pipeline":
            return self.pipeline()
        return [self.stage()]

    def pipeline(self):
        self._expect("pipeline")
        self._expect("(")
        stages = [self.stage()]
        while self._peek()[1] == ",":
            self._next()
            stages.append(self.stage())
        self._expect(")")
        return stages

    def stage(self):
        kind, val = self._peek()
        if val == "agent":
            return self.agent_stage()
        if val == "parallel":
            return self.parallel_stage()
        raise WorkflowError(f"unexpected stage {val!r} in shape-DSL")

    def parallel_stage(self):
        self._expect("parallel")
        self._expect("(")
        operator, val = self._next()[1], None  # operator name (map/flatMap)
        self._expect("(")
        path = self._string()
        self._expect(",")
        inner, fan = self.fan_inner()
        self._expect(")")  # close map/flatMap
        self._expect(")")  # close parallel
        flatten_path = "[]" in path
        if operator == "map" and flatten_path:
            raise WorkflowError(
                "map() binds a single array; a [] (flatten) path requires flatMap()/flatten()"
            )
        if operator in ("flatMap", "flatten") and not flatten_path:
            raise WorkflowError(f"{operator}() requires a [] (flatten) path")
        if operator not in ("map", "flatMap", "flatten"):
            raise WorkflowError(f"unknown fan-out operator {operator!r}")
        return {
            "id": inner["id"],
            "type": "parallel",
            "role": inner["role"],
            "output_schema": inner["output_schema"],
            "over": path,
            "fan": fan,
            "input": None,
        }

    def fan_inner(self):
        if self._peek()[1] == "fan":
            self._next()
            self._expect("(")
            kind, count = self._next()
            if kind != "number":
                raise WorkflowError("fan() expects a number")
            self._expect(",")
            agent = self.agent_stage()
            self._expect(")")
            return agent, count
        return self.agent_stage(), 1

    def agent_stage(self):
        self._expect("agent")
        self._expect("(")
        stage_id = self._string()
        self._expect(",")
        opts = self.obj()
        self._expect(")")
        return {
            "id": stage_id,
            "type": "agent",
            "role": opts.get("role"),
            "output_schema": opts.get("output_schema"),
            "over": None,
            "fan": 1,
            "input": _canon_path(opts.get("input")),
        }

    def obj(self):
        self._expect("{")
        result = {}
        while self._peek()[1] != "}":
            key_kind, key = self._next()
            if key_kind != "ident":
                raise WorkflowError(f"object key must be an identifier, got {key!r}")
            self._expect(":")
            result[key] = self.value()
            if self._peek()[1] == ",":
                self._next()
        self._expect("}")
        return result

    def value(self):
        kind, val = self._peek()
        if val == "{":
            return self.obj()
        kind, val = self._next()
        if kind == "string":
            return val
        if kind == "number":
            return val
        if kind == "ident" and val in ("true", "false"):
            return val == "true"
        raise WorkflowError(f"unexpected value {val!r} in shape-DSL")

    def _string(self):
        kind, val = self._next()
        if kind != "string":
            raise WorkflowError(f"expected a string, got {val!r}")
        return val


def parse_dsl(text):
    """Parse the frozen shape-DSL form into a normalized definition dict (D3)."""
    reader = _DSLReader(_tokenize_dsl(text))
    stages = reader.program()
    return {
        "name": None,
        "max_concurrent": DEFAULT_CEILING,
        "stages": stages,
    }


def _binding_source(over):
    """The upstream stage id a canonical binding reads from."""
    match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)", over)
    if not match:
        raise WorkflowError(f"invalid binding {over!r}")
    return match.group(1)


def _resolve_binding(over, upstream_outputs):
    """Walk a canonical binding (stage, [], .field) against real outputs."""
    source = _binding_source(over)
    if source not in upstream_outputs:
        raise WorkflowError(f"binding {over!r} references unknown stage {source!r}")
    value = upstream_outputs[source]
    rest = over[len(source):]
    pos = 0
    while pos < len(rest):
        if rest[pos:pos + 2] == "[]":
            pos += 2
            field_match = re.match(r"\.([A-Za-z_][A-Za-z0-9_]*)", rest[pos:])
            if field_match:
                field = field_match.group(1)
                pos += 1 + len(field)
                flattened = []
                for item in value:
                    if not isinstance(item, dict) or field not in item:
                        raise WorkflowError(
                            f"binding {over!r}: element missing field {field!r}"
                        )
                    flattened.extend(item[field])
                value = flattened
            else:
                value = list(value)
        elif rest[pos] == ".":
            field_match = re.match(r"\.([A-Za-z_][A-Za-z0-9_]*)", rest[pos:])
            if not field_match:
                raise WorkflowError(f"invalid binding segment in {over!r}")
            field = field_match.group(1)
            pos += 1 + len(field)
            if not isinstance(value, dict) or field not in value:
                raise WorkflowError(
                    f"binding {over!r}: missing field {field!r}"
                )
            value = value[field]
        else:
            raise WorkflowError(f"invalid binding segment in {over!r}")
    return value


def resolve_fanout(over, upstream_outputs):
    """Resolve a fan-out binding against real upstream outputs (runtime, D6).

    Returns the list of bound items. An empty result HARD-ABORTS with an
    EmptyFanoutError that names the upstream stage (D6/FR8) — empty fan-out
    is an upstream bug, not a silently-skipped stage.
    """
    items = _resolve_binding(over, upstream_outputs)
    if not isinstance(items, list):
        items = [items]
    if len(items) == 0:
        source = _binding_source(over)
        raise EmptyFanoutError(
            f"fan-out '{over}' resolved to an empty array — upstream stage "
            f"'{source}' produced no items to fan out over"
        )
    return items


def _sem_write(path, value):
    value = max(0, int(value))
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(str(value))
    return value


def sem_read(path):
    """Read the run-wide live-agent counter (0 if the file is absent)."""
    if not os.path.exists(path):
        return 0
    with open(path, encoding="utf-8") as handle:
        text = handle.read().strip()
    return int(text) if text else 0


def sem_acquire(path, ceiling):
    """Try to take one slot. Increment & return True if below the ceiling,
    else leave the counter untouched and return False (refuse dispatch)."""
    current = sem_read(path)
    if current >= ceiling:
        return False
    _sem_write(path, current + 1)
    return True


def sem_release(path):
    """Release one slot; decrement the counter (floored at 0). Returns new value."""
    return _sem_write(path, sem_read(path) - 1)


def sem_reconcile(path, live_count):
    """Reset the counter to the actual live-agent count at a wave boundary,
    healing leaks from a mid-run crash (D5 residual-risk mitigation)."""
    return _sem_write(path, live_count)


def cache_key(stage_block, resolved_input, role_prompt_version):
    """Content hash of the three D4 cache-key components.

    Key = sha256({resolved stage input + role-prompt version + definition
    stage block}). Any change to any of the three yields a different key —
    which is what lets cache reuse cascade downstream (a changed upstream
    output changes a stage's resolved input, hence its key).
    """
    payload = json.dumps(
        {
            "stage_block": stage_block,
            "input": resolved_input,
            "role_prompt_version": role_prompt_version,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_deps(plan):
    """Derive the stage dependency graph from a wave plan's bindings (D4).

    A wave depends on the upstream stage(s) its fan-out (``over``) and ``input``
    bindings read from. This is the bridge that lets ``cascade_invalidate`` run
    on a real plan — without it the cascade is untethered from the definition.
    Returns ``{stage_id: [upstream_ids]}``.
    """
    deps = {}
    for wave in plan["waves"]:
        upstream = set()
        fanout = wave.get("fanout", {})
        if fanout.get("kind") == "dynamic" and fanout.get("over"):
            upstream.add(_binding_source(fanout["over"]))
        if wave.get("input"):
            upstream.add(_binding_source(wave["input"]))
        deps[wave["id"]] = sorted(upstream)
    return deps


def cascade_invalidate(stages, changed, deps):
    """Given directly-changed stages, return the FULL invalidation set (D4).

    When a stage's own cache key changes it must re-run; because re-running it
    may produce a different output, every stage that *consumes* it (directly or
    transitively) must also re-run even if its own block/role/version is
    unchanged. That downstream propagation is "the cascade."

    Args:
        stages: stage ids in pipeline (topological) order.
        changed: set of stage ids whose own cache key changed (direct hits).
        deps: dict mapping stage id -> list of upstream stage ids it consumes.

    Returns:
        set of all stage ids that must re-run (direct hits + cascaded
        downstream). With ``changed`` empty, returns the empty set (full
        cache reuse).
    """
    # Approach A — pipeline-order propagation. `stages` is topologically
    # ordered, so every upstream is decided before its dependents and a single
    # forward pass suffices: a stage is invalid if it changed directly OR any
    # stage it consumes is already invalid.
    invalid = set(changed)
    for stage_id in stages:
        if any(dep in invalid for dep in deps.get(stage_id, [])):
            invalid.add(stage_id)
    return invalid


def compile_plan(definition):
    """Compile a normalized definition dict into the canonical wave plan.

    The wave plan is the deterministic normal form D1 reproduces: identical
    upstream definitions (and, for dynamic fan-out, identical upstream
    outputs) produce identical waves.
    """
    waves = []
    seen = set()
    for stage in definition["stages"]:
        # Fail fast: every binding must reference an EARLIER stage. A typo or a
        # forward reference is a definition bug, not a runtime surprise (E).
        for binding in (stage.get("over"), stage.get("input")):
            if binding:
                source = _binding_source(binding)
                if source not in seen:
                    raise WorkflowError(
                        f"stage '{stage['id']}' binds to '{binding}' but upstream "
                        f"stage '{source}' is not defined before it"
                    )
        if stage["type"] == "parallel":
            over = stage["over"]
            if over is None:
                raise WorkflowError(
                    f"parallel stage '{stage['id']}' has no fan-out binding (over)"
                )
            fanout = {
                "kind": "dynamic",
                "over": over,
                "flatten": "[]" in over,
                "fan": stage.get("fan", 1),
            }
        else:
            fanout = {"kind": "static", "count": 1}
        waves.append(
            {
                "id": stage["id"],
                "type": stage["type"],
                "fanout": fanout,
                "role": stage.get("role"),
                "output_schema": stage.get("output_schema"),
                "input": stage.get("input"),
                "command": stage.get("command"),  # set only for type=verify (D8)
                "max_iter": stage.get("max_iter"),  # set only for type=loop
            }
        )
        seen.add(stage["id"])
    return {
        "name": definition.get("name"),
        "max_concurrent": definition.get("max_concurrent", DEFAULT_CEILING),
        "waves": waves,
    }


# ---------------------------------------------------------------------------
# CLI — the executor skill calls this to obtain a wave plan from a file
# ---------------------------------------------------------------------------


def main(argv=None):
    """Emit the canonical wave plan (JSON) for a WORKFLOW definition file.

    The prompt-driven workflow-engine skill shells out to this to obtain the
    deterministic plan it then executes wave by wave. Exit 0 on success; exit 2
    with a structured message on stderr for any workflow/parse error.
    """
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        prog="workflow_parse",
        description="Compile a WORKFLOW definition (YAML or shape-DSL) to a wave plan.",
    )
    parser.add_argument("file", help="path to a WORKFLOW-*.yaml or shape-DSL file")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="print the wave plan (stages, fan-out, ceiling) without spawning agents",
    )
    args = parser.parse_args(argv)

    try:
        plan = parse_file(args.file)
    except WorkflowError as exc:
        print(f"workflow error: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError:
        print(f"no such file: {args.file}", file=sys.stderr)
        return 2

    if args.dry_run:
        name = plan.get("name") or "(unnamed)"
        print(f"DRY RUN: {name}  (run-wide ceiling: {plan['max_concurrent']})")
        for i, line in enumerate(dry_run_actions(plan), 1):
            print(f"  {i}. {line}")
        return 0

    print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
