"""ITeM batch runner — same migration pairs as moveDroid.
Uses moveDroid's API config (deepseek-v4-flash).

Usage:
    python run_item_comparison.py [--skip-trace] [--dry-run]

Stages per migration:
    1. Trace (execute source test case)
    2. Generate Intentions
    3. Migrate GUI Events
    4. Migrate Oracles (Assertions)
"""
import sys
import json
import time
from datetime import datetime

from test_executor import TestExecutor
from test_migrator import TestMigrator

# Same migration pairs as moveDroid (excluding mail, which is non-functional)
EXPERIMENTS = [
    # (label, src, func, [targets...])
    # ("browser",     "a11", "b11", ["a12", "a13", "a14", "a15"]),
    # ("browser",     "a11", "b12", ["a12", "a13", "a14", "a15"]),
    # ("todo",        "a21", "b21", ["a22", "a23", "a24", "a25"]),
    # ("todo",        "a21", "b22", ["a22", "a23", "a24", "a25"]),
    # ("shopping",    "a31", "b31", ["a32", "a33", "a34", "a35"]),
    # ("shopping",    "a31", "b32", ["a32", "a33", "a34", "a35"]),
    # ("tip",         "a51", "b51", ["a52", "a53", "a54", "a55"]),
    # ("tip",         "a51", "b52", ["a52", "a53", "a54", "a55"]),
    # ("news",        "a61", "b61", ["a62", "a63", "a64", "a65"]),
    # ("news",        "a61", "b62", ["a62", "a63", "a64", "a65"]),
    # ("music",       "a71", "b71", ["a75"]),
    ("music",       "a71", "b72", ["a72", "a73", "a74", "a75"]),
]

RESULTS_FILE = "experiment_results.txt"


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(RESULTS_FILE, "a") as f:
        f.write(line + "\n")


def run():
    skip_trace = "--skip-trace" in sys.argv
    dry_run = "--dry-run" in sys.argv

    with open(RESULTS_FILE, "w") as f:
        f.write(f"ITeM Comparison Run\nStarted: {datetime.now()}\n{'=' * 80}\n\n")

    total_migrations = sum(len(tgts) for _, _, _, tgts in EXPERIMENTS)
    log(f"Total migration tasks: {total_migrations}")
    log(f"Skip trace: {skip_trace}")
    if dry_run:
        log("DRY RUN — no execution")
        for label, src, func, targets in EXPERIMENTS:
            log(f"  {label}: {src}/{func} -> {', '.join(targets)}")
        return

    overall_t0 = time.perf_counter()
    results = []

    for label, src, func, targets in EXPERIMENTS:
        log(f"\n{'=' * 60}")
        log(f"START: {label} ({src}/{func} -> {', '.join(targets)})")
        log(f"{'=' * 60}")

        # Stage 1: Trace
        if not skip_trace:
            log(f"[Stage 1/4] Tracing: {src} {func}")
            t0 = time.perf_counter()
            try:
                executor = TestExecutor()
                executor.execute_test_case(src, func)
                log(f"  [OK] Trace completed ({time.perf_counter() - t0:.1f}s)")
            except Exception as e:
                log(f"  [FAIL] Trace: {e}")
                log(f"  SKIPPING {label}")
                continue
        else:
            log(f"[Stage 1/4] Skipping trace (--skip-trace)")

        # Stage 2: Intentions
        log(f"[Stage 2/4] Generating intentions: {src} {func}")
        t0 = time.perf_counter()
        try:
            migrator = TestMigrator()
            migrator.generate_test_intentions(src, func)
            log(f"  [OK] Intentions completed ({time.perf_counter() - t0:.1f}s)")
        except Exception as e:
            log(f"  [FAIL] Intentions: {e}")
            log(f"  SKIPPING {label}")
            continue

        # Stage 3-4: Migrate per target
        for tgt in targets:
            label_tgt = f"{src}/{func} -> {tgt}"
            log(f"  --- {label_tgt} ---")

            # Stage 3: Migrate GUI Events
            log(f"  [Stage 3/4] Migrating events: {label_tgt}")
            t0 = time.perf_counter()
            try:
                migrator = TestMigrator()
                migrator.perform_test_intentions(src, func, tgt)
                log(f"    [OK] Events migrated ({time.perf_counter() - t0:.1f}s)")
            except Exception as e:
                log(f"    [FAIL] Events: {e}")
                results.append({"label": label, "src": src, "func": func, "tgt": tgt,
                                "status": "failed", "stage": "migrate_events"})
                continue

            # Stage 4: Migrate Oracles
            log(f"  [Stage 4/4] Migrating oracles: {label_tgt}")
            t0 = time.perf_counter()
            try:
                migrator = TestMigrator()
                migrator.migration_test_oracles(src, func, tgt, execution=False)
                log(f"    [OK] Oracles migrated ({time.perf_counter() - t0:.1f}s)")
                results.append({"label": label, "src": src, "func": func, "tgt": tgt,
                                "status": "success"})
            except Exception as e:
                log(f"    [FAIL] Oracles: {e}")
                results.append({"label": label, "src": src, "func": func, "tgt": tgt,
                                "status": "failed", "stage": "migrate_oracles"})

    overall_elapsed = time.perf_counter() - overall_t0
    successes = sum(1 for r in results if r.get("status") == "success")
    failures = sum(1 for r in results if r.get("status") == "failed")

    log(f"\n{'=' * 60}")
    log(f"ALL COMPLETED ({overall_elapsed:.1f}s)")
    log(f"{'=' * 60}")
    log(f"  Success: {successes}")
    log(f"  Failed:  {failures}")
    log(f"  Total:   {len(results)}")

    # Save results summary
    summary_path = "experiment_summary.json"
    with open(summary_path, "w") as f:
        json.dump({
            "started": str(datetime.now()),
            "elapsed_sec": round(overall_elapsed, 1),
            "success": successes,
            "failed": failures,
            "total": len(results),
            "results": results,
        }, f, indent=2)
    log(f"Summary saved to {summary_path}")


if __name__ == "__main__":
    run()
