# Auto-loaded by Python if present on sys.path. Ensures the local 'app' package
# is used instead of any third-party package named 'app' that may be installed
# in the environment (notably on CI images).
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parent

# Prepend repo root to sys.path so local packages win
repo_str = str(REPO_ROOT)
if repo_str not in sys.path:
    sys.path.insert(0, repo_str)


def _is_local_app(mod: object) -> bool:
    try:
        mod_file = getattr(mod, "__file__", "") or ""
        return repo_str.replace("\\", "/") in mod_file.replace("\\", "/")
    except Exception:
        return False


# If a foreign 'app' is already imported, drop it
if "app" in sys.modules and not _is_local_app(sys.modules["app"]):
    del sys.modules["app"]

# Ensure our local 'app' package is importable as a proper package
if "app" not in sys.modules or not _is_local_app(sys.modules["app"]):
    app_init = REPO_ROOT / "app" / "__init__.py"
    if app_init.exists():
        spec = importlib.util.spec_from_file_location(
            "app", str(app_init), submodule_search_locations=[str(app_init.parent)]
        )
        if spec and spec.loader:
            app_module = importlib.util.module_from_spec(spec)
            sys.modules["app"] = app_module
            spec.loader.exec_module(app_module)
