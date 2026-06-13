# ITeM — Intention-based GUI Test Migration

Research prototype. ISSTA 2025 paper. Migrates Android GUI tests between apps using LLMs.

## Code / naming conventions

- Apps: `a{cat}{idx}` (e.g. `a11` = browser app 1, `a71` = music app 1). 7 categories: browser, todo, shopping, mail, tip, news, music.
- Functionalities: `b{cat}{idx}` (e.g. `b11`, `b72`).
- Migration task labelled `{src_app}_{func}_{tgt_app}` (e.g. `a11_b11_a12`).

## Pipeline (4 ordered stages)

Each stage modifies its own `main_*.py` entrypoint with the desired args, then runs it.

| Stage | Entrypoint | Key method call | Output |
|---|---|---|---|
| 1. Trace | `main_trace.py` | `executor.execute_test_case('a11', 'b11')` | `assets/Trace/{app}/{func}/` (screenshots, XML, action_trace.json) |
| 2. Intentions | `main_generate_intentions.py` | `migrator.generate_test_intentions('a11', 'b11')` | `assets/Intention/{func}/{app}.txt` |
| 3. Migrate events | `main_migrate_intentions.py` | `migrator.perform_test_intentions('a11', 'b11', 'a12')` | `assets/GPT_Trace/{src}_{func}_{tgt}/` |
| 4. Migrate oracles | `main_migrate_oracles.py` | `migrator.migration_test_oracles('a11', 'b11', 'a12', False)` | `assets/Oracle/{src}_{func}_{tgt}/oracle.txt` |

Stage 4 must always be run *after* Stage 3 for the same task (needs GPT_Trace). If GPT_Trace is missing or was deleted, pass `execution=True` to regenerate it inline.

## Batch runners (preferred over manual entrypoints)

```bash
# Run all experiments
python run_item_comparison.py

# Skip trace stage (if traces already exist)
python run_item_comparison.py --skip-trace

# Dry run (print what would run)
python run_item_comparison.py --dry-run

# Batch-run specific gap-filling tasks
python batch_run.py
```

## LLM API config

Uses `openai` v0.28.0 (legacy `ChatCompletion.create`). API config loaded from `../moveDroid_text/config/agent_api.json` (field: `llm.model`, `llm.api_key`, `llm.base_url`). Falls back to `gpt-4-turbo` with empty key.

To change API key/model, edit that JSON file (preferred) or `gpt_client.py:23` `_load_api_config()`.

## Infrastructure

```bash
# Prerequisites
pip install -r requirements.txt
# Start Appium server
appium
# Verify emulator
adb devices
```

- Appium server at `http://localhost:4723`
- `config/env.yaml` — Appium caps (`platformVersion: '6.0'` default, `'11.0'` for a7 music apps)
- `config/app.yaml` — per-app APK path, package, activity, noReset flag
- Catalogs a1–a6 run on Android 6.0; a7 on Android 11.0
- APKs live in `ITeM_Dataset/subject_apps/{category}/`
- Resource: paper DOI `10.1145/3728978`, dataset DOI `10.5281/zenodo.15174071`

## Required asset directories (created on first run, but safe to pre-create)

```
assets/{GPT_Guidance,GPT_Trace,Intention,Oracle,Trace}
```

## Thresholds

- `threshold.py:1` — `EXPLORATION_LIMIT = 5` (max LLM exploration steps per intention)
- `GPTClient.ACTION_SLEEP_INTERVAL = 20` and `TestExecutor.ACTION_SLEEP_INTERVAL = 5` (seconds between actions)

## Testing

No automated test suite. Verification is empirical — inspect `assets/` output or rerun batch runners.
