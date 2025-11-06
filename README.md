# AI Project Template

## Structure

- `src/` — Python modules
- `notebooks/` — Jupyter work
- `data/` — **not committed** (raw, processed)
- `models/` — trained artifacts (ignored)
- `reports/` — exports/figures
- `scripts/` — helper scripts (setup, format, run)
- `tests/` — unit tests

## Development

**Prerequisites:** WSL, Git Bash, or a bash-compatible shell (required for Makefile targets).

1. **Create virtual environment and activate shell:**

   ```bash
   make venv && make shell
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start database, run migrations, and launch API:**

   ```bash
   make db && make migrate && make dev
   ```

4. **Run tests:**
   ```bash
   make test
   ```

The API will be available at `http://127.0.0.1:8000`. See the [Makefile](Makefile) for all available targets.

## Quickstart

```bash
make venv && make shell
pip install -r requirements.txt
make db && make migrate && make dev
```

API: http://127.0.0.1:8000/docs
