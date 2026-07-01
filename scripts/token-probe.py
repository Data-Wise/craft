#!/usr/bin/env python3
"""Compare token counts between two file-set globs -- a relative, not exact,
comparison tool for "should we merge/split X" questions.

Generalizes the disposable one-off probe from
docs/plans/2026-06-30-namespace-token-probe.md (which measured the namespace
refactor's flat-vs-consolidated command layout, 243 -> 77 tokens, 68.3%
reduction, see docs/specs/SPEC-refactor-namespace-2026-06-29.md). This script
is the reusable version: point it at any two globs and it tells you the
token-count delta between them.

Caveat (state this whenever citing a result from this tool): it uses
tiktoken's cl100k_base encoding, which approximates Claude's actual
tokenizer but is not it -- Claude uses a different vocabulary. cl100k_base is
a real, consistent tokenizer, good enough for a *relative* comparison between
two layouts. Do not report its output as an exact Claude token count.

Usage:
    python3 scripts/token-probe.py --before <glob> --after <glob> [--encoding cl100k_base] [--json]

Examples:
    # Compare a set of flat command files against one consolidated file
    python3 scripts/token-probe.py \\
        --before 'commands/docs/{guide,quickstart,website}.md' \\
        --after 'commands/docs.md'

    # Compare a command file before/after a thin-shim extraction (two snapshots)
    python3 scripts/token-probe.py --before /tmp/before/refine.md --after commands/workflow/refine.md

Exit codes:
    0 - comparison ran and printed a result (this tool has no pass/fail
        threshold -- it reports, it doesn't gate)
    1 - one or both globs matched no files
"""
import argparse
import glob
import sys


def _resolve(pattern):
    """Glob a pattern; brace-expansion ({a,b,c}) isn't supported by glob.glob,
    so fall back to Python's braceexpand-free behavior -- if the pattern
    contains braces and glob finds nothing, expand it manually."""
    matches = sorted(glob.glob(pattern, recursive=True))
    if matches:
        return matches
    if "{" in pattern and "}" in pattern:
        prefix, rest = pattern.split("{", 1)
        options, suffix = rest.split("}", 1)
        expanded = []
        for opt in options.split(","):
            expanded.extend(_resolve(prefix + opt + suffix))
        return sorted(set(expanded))
    return matches


def count_tokens(paths, encoding_name):
    import tiktoken

    enc = tiktoken.get_encoding(encoding_name)
    total = 0
    per_file = []
    for p in paths:
        try:
            text = open(p, encoding="utf-8").read()
        except OSError as e:
            print(f"! could not read {p}: {e}", file=sys.stderr)
            continue
        n = len(enc.encode(text))
        total += n
        per_file.append((p, n))
    return total, per_file


def main():
    parser = argparse.ArgumentParser(
        description="Compare token counts between two file-set globs (relative comparison, not exact Claude token count).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--before", required=True, help="Glob pattern for the 'before' file set")
    parser.add_argument("--after", required=True, help="Glob pattern for the 'after' file set")
    parser.add_argument("--encoding", default="cl100k_base",
                         help="tiktoken encoding name (default: cl100k_base -- an approximation of "
                              "Claude's tokenizer, used for relative comparison only)")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    before_paths = _resolve(args.before)
    after_paths = _resolve(args.after)

    if not before_paths:
        print(f"! --before glob matched no files: {args.before}", file=sys.stderr)
        sys.exit(1)
    if not after_paths:
        print(f"! --after glob matched no files: {args.after}", file=sys.stderr)
        sys.exit(1)

    before_total, before_files = count_tokens(before_paths, args.encoding)
    after_total, after_files = count_tokens(after_paths, args.encoding)

    delta = before_total - after_total
    delta_pct = (delta / before_total) * 100 if before_total else 0.0

    if args.json:
        import json
        print(json.dumps({
            "encoding": args.encoding,
            "before": {"glob": args.before, "files": len(before_files), "total_tokens": before_total},
            "after": {"glob": args.after, "files": len(after_files), "total_tokens": after_total},
            "delta_tokens": delta,
            "delta_pct": round(delta_pct, 1),
            "direction": "reduction" if delta > 0 else "increase" if delta < 0 else "no change",
        }, indent=2))
        return

    print(f"Token-probe comparison (encoding={args.encoding})")
    print("=" * 70)
    print(f"Before ({len(before_files)} file(s), glob={args.before!r}): {before_total} tokens")
    print(f"After  ({len(after_files)} file(s), glob={args.after!r}): {after_total} tokens")
    direction = "reduction" if delta > 0 else "increase" if delta < 0 else "no change"
    print(f"Delta: {delta} tokens ({delta_pct:.1f}% {direction})")
    print()
    print("Caveat: cl100k_base approximates Claude's tokenizer; treat this as a "
          "relative comparison, not an exact Claude token count.")


if __name__ == "__main__":
    main()
