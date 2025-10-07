# Repository Guidelines

## Project Structure & Module Organization
- `core/` orchestrates CESAR agents (memory, learning bridge, screen recorder, background managers).
- `agents/` houses specialized automation agents (reporting, CRM, UI-TARS, Cursor).
- `simple_web_ui.py` + `static/` deliver the FastAPI desktop shell; `static/index.html` is the main dashboard.
- Core pytest entry points live alongside the source in `td_manager_agent/test_*.py`; the legacy Atlas snapshot keeps mirror tests at the repo root.
- `scripts/runtime_benchmark.py` exercises orchestration loops.
- The personal assistant bridge lives under `AgentC/terry_assistant/`; launch `AgentC/run_terry_bridge.py` for local-only use, or leave `ENABLE_TERRY_ASSISTANT` unset to keep CESAR unaware of it.
- To keep Terry separate, run `AgentC/install_terry_launchagent.sh` (creates `~/Library/LaunchAgents/com.terry.assistant.plist`) or double-click `AgentC/start_terry.command` for an on-demand desktop launcher.
- Nightly recursive cognition is configured through `AgentC/install_terry_reflection_launchagent.sh`, which registers a 03:00 self-reflection job writing insights to `~/.terry_delmonaco`.
- A standalone desktop UI lives at `AgentC/terry_desktop.py`. Double-click `AgentC/TerryDesktop.command` (or the copy in `~/Downloads/Terry_UI.command`) and it will silently start the bridge if needed, launch the Tkinter window in the background, and display a macOS notification.
- Configuration defaults sit in `utils/config.py`; runtime artifacts (logs, `.memory.json`) are written to the current working directory by default (`Path.cwd()`), or to the folder specified via `CESAR_DATA_DIR`.

## Build, Test, and Development Commands
- `python3 -m venv .venv && source .venv/bin/activate` (macOS/Linux) sets up an isolated environment.
- `pip install -r requirements.txt` installs FastAPI, async orchestration, and agent dependencies.
- `uvicorn simple_web_ui:app --reload` starts the desktop interface at `http://localhost:8000` with hot reload.
- `python3 -m pytest` runs the full suite; add `-k <pattern>` for focused runs.
- `PYTHONPATH=. python3 scripts/runtime_benchmark.py` smoke-tests task delegation and shutdown flow.

## Coding Style & Naming Conventions
- Python modules use 4-space indentation, type hints, and snake_case for functions/variables; CamelCase reserved for classes.
- Prefer async/await for I/O; wrap blocking calls with `asyncio.to_thread` (see `core/memory_manager.py`).
- Log through `utils.logger.setup_logger` to keep structured output consistent.
- New agents live under `agents/` with filenames `<capability>_agent.py` and subclasses of `BaseAgent`.

## Testing Guidelines
- Pytest is the project standard; name files `test_<feature>.py` and async tests with `async def` + `pytest.mark.asyncio` if needed.
- Validate new background jobs with unit tests plus the `runtime_benchmark` script to catch event-loop stalls.
- Target parity with existing coverage (all critical orchestration paths exercised); add fixture data under `tests/fixtures/` if required.

## Commit & Pull Request Guidelines
- Follow conventional, action-oriented commit subjects (`feat: add hybrid memory metrics`, `fix: guard background git commands`).
- PRs should include: summary of changes, verification steps (commands run), screenshots/GIFs for UI updates, and linked issue/task IDs.
- Ensure CI (pytest) passes before requesting review; highlight any follow-up work in a "Next Steps" subsection of the PR description.

## Security & Configuration Tips (Optional)
- Never commit secrets; configure API keys via environment variables or `.env` excluded from Git.
- When testing background agents, set `CESAR_DATA_DIR` to a sandbox directory to avoid polluting the repo root.
- Grant macOS screen-recording permission to the Python interpreter to enable UI-TARS capture flows.
- To enable Terry locally, set `ENABLE_TERRY_ASSISTANT=true` and optionally configure `TERRY_BRIDGE_URL`, `TERRY_BRIDGE_PORT`, and `QUEN_MODEL_PATH`.
