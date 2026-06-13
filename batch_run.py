"""ITeM 批量迁移：补齐 movedroid 已跑但 ITeM 缺失的实验。

每个任务独立 subprocess 调用 run_task.py，避免 Appium session 冲突。
"""
import os, shutil, subprocess, sys, time, traceback
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_executor import TestExecutor
from test_migrator import TestMigrator

DATASET = (Path(__file__).resolve().parent.parent / "moveDroid_text" / "ITeM_Dataset").resolve()
GPT_TRACE = Path("assets/GPT_Trace")

# 需要补的实验：browser (a13) + news (a61)，限 Android 6.0
CATEGORIES = {
    "browser": {"src": "a13", "funcs": ["b11", "b12"], "targets": ["a11", "a12", "a14", "a15"]},
    "news":    {"src": "a61", "funcs": ["b61", "b62"], "targets": ["a62", "a63", "a64", "a65"]},
}


def is_completed(src, func, tgt):
    return (GPT_TRACE / f"{src}_{func}_{tgt}").exists()


def has_trace(src, func):
    trace_dir = Path("assets/Trace") / src / func
    return trace_dir.exists() and any(trace_dir.iterdir())


def has_intention(src, func):
    return (Path("assets/Intention") / func / f"{src}.txt").exists()


def ensure_trace_and_intent(src, func):
    """Stage 1+2: 只在缺失时跑，已在则跳过。"""
    if has_trace(src, func) and has_intention(src, func):
        print(f"  [1/2] {src}/{func} 已有 trace + intention")
        return True

    # 清理不完整的旧数据
    for d in [Path("assets/Trace") / src / func,
              Path("assets/Intention") / func / f"{src}.txt",
              Path("assets/Intention") / func / f"{src}_time.txt"]:
        p = Path(d)
        if p.exists():
            shutil.rmtree(p) if p.is_dir() else p.unlink()

    # DEBUG: 验证数据集能找到目标
    print(f"  [1/2] {src}/{func}: trace + intentions  ", end="", flush=True)
    t0 = time.perf_counter()
    try:
        executor = TestExecutor()
        available = list(executor.test_cases.get(src, {}).keys())
        if func not in available:
            print(f"\u274c 数据集无 {func}（可用: {available}）")
            return False
        executor.execute_test_case(src, func)
        migrator = TestMigrator()
        migrator.generate_test_intentions(src, func)
        print(f"\u2705 ({time.perf_counter()-t0:.1f}s)")
        return True
    except Exception as e:
        print(f"\u274c {str(e)[:80]}")
        traceback.print_exc()
        return False


def run_migration(src, func, tgt):
    """Stage 3+4: 用独立 subprocess 调用 run_task.py。"""
    label = f"{src}_{func}_{tgt}"
    if is_completed(src, func, tgt):
        print(f"  \u23ed {label} 已完成，跳过")
        return True

    print(f"  [2/2] {func} \u2192 {tgt}  ", end="", flush=True)
    t0 = time.perf_counter()

    try:
        r = subprocess.run(
            ["python", "run_task.py", src, func, tgt, str(DATASET)],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True, text=True, timeout=600)

        out = {}
        if r.stdout.strip():
            import json
            try:
                out = json.loads(r.stdout)
            except json.JSONDecodeError:
                pass

        if out.get("status") == "success":
            print(f"\u2705 ({time.perf_counter()-t0:.1f}s)")
            return True

        err = out.get("error", r.stderr[:100] if r.stderr else "unknown")
        print(f"\u274c {err[:80]} ({time.perf_counter()-t0:.1f}s)")
        return False

    except subprocess.TimeoutExpired:
        print(f"\u274c timeout (600s)")
        return False
    except Exception as e:
        print(f"\u274c {str(e)[:80]}")
        traceback.print_exc()
        return False


def run_batch():
    start_at = datetime.now()
    print(f"[{start_at:%H:%M:%S}] 开始补齐 ITeM 实验")
    print(f"  数据集: {DATASET}")
    print(f"  将跳过已完成的 GPT_Trace\n")

    for cat_name, cfg in CATEGORIES.items():
        src = cfg["src"]
        print(f"\n{'='*50}")
        print(f">>> {cat_name}: {src}")
        print(f"{'='*50}")

        for func in cfg["funcs"]:
            ok = ensure_trace_and_intent(src, func)
            if not ok:
                print(f"  \u274c {src}/{func} trace/intent 失败，跳过本功能")
                continue

            for tgt in cfg["targets"]:
                run_migration(src, func, tgt)

    end_at = datetime.now()
    elapsed = (end_at - start_at).total_seconds()
    print(f"\n{'='*50}")
    print(f"[{end_at:%H:%M:%S}] 全部完成，耗时 {elapsed/60:.1f} 分钟")


if __name__ == "__main__":
    run_batch()
