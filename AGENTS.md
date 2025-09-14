# Repository Guidelines

## Project Structure & Module Organization
- `app.py` — Streamlit entrypoint and UI.
- `utils/` — core logic:
  - `unified_client.py` (OpenAI client; GPT-5 mini via Responses API + Web Search tool)
  - `broker_logic.py` (assistant orchestration; model-native web search)
  - `knowledge_base.py` (KB hooks)
- `prompts/` — system prompts for the assistant.
- `data/` — local KB/artifacts (safe to ignore in CI).
- `test_*.py` (root) — lightweight tests/health checks.
- `.streamlit/` — Streamlit config; `secrets.toml.example` for cloud.
- `.env` / `.env.example` — local configuration.
- `archive/` — experiments and older prototypes.

## Build, Test, and Development Commands
- Create env and install: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- Run locally: `streamlit run app.py`
- Health check: `python check_deployment.py`
- Tests: `pytest -q` (if installed) or `python test_multi_provider.py` and `python test_startup_performance.py`.
- CI: GitHub Actions workflow “Check App Health” runs imports and env validation on PRs.

## Coding Style & Naming Conventions
- Python 3.11; follow PEP 8; 4-space indentation; target line length ~100.
- Use type hints for public functions/classes; include concise docstrings.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Keep modules import-safe (no side effects); prefer small, focused functions.

## Testing Guidelines
- Prefer `pytest`; place tests as `test_*.py` at repo root (consistent with current files).
- Keep tests deterministic and fast; gate network/API tests on `OPENAI_API_KEY` presence.
- For search features, prefer the model-native Web Search tool (no extra deps) when using GPT-5 mini.

## Commit & Pull Request Guidelines
- Use Conventional Commits (seen in history): `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`; imperative, concise subject.
- Provide context in body (what/why), link issues (e.g., `Closes #123`).
- PRs should include: summary, screenshots for UI changes, test plan/steps, and notes on config/secrets changes.

## Security & Configuration Tips
- Required env: `OPENAI_API_KEY`. Optional: `MODEL_NAME`, `RAG_ENABLED`.
- Local: use `.env`; Cloud: use `.streamlit/secrets.toml`. Never commit secrets.
- If you add config, update `.env.example` and docs.

## Agent-Specific Instructions
- Scope: this file applies repo-wide; deeper `AGENTS.md` overrides.
- Make minimal, surgical changes; avoid adding dependencies unless essential.
- Keep style consistent; place new logic under `utils/` and tests as `test_*.py`.
- Update `README.md` when behavior or configuration changes.
