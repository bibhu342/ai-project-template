# Ensure our local 'app' package is imported instead of any third-party package
# named 'app' that may be present in the environment (e.g., on CI images).
from __future__ import annotations

import sys
import os
from pathlib import Path
import importlib.util

# Set testing environment variable
os.environ["TESTING"] = "true"

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# If some foreign 'app' is already imported, drop it to avoid shadowing
if "app" in sys.modules:
    try:
        mod = sys.modules["app"]
        mod_file = getattr(mod, "__file__", "") or ""
        if str(PROJECT_ROOT).replace("\\", "/") not in mod_file.replace("\\", "/"):
            del sys.modules["app"]
    except Exception:
        del sys.modules["app"]

# Explicitly load our local 'app' package from path to guarantee resolution
app_init_path = PROJECT_ROOT / "app" / "__init__.py"
if app_init_path.exists():
    spec = importlib.util.spec_from_file_location(
        "app",
        str(app_init_path),
        submodule_search_locations=[str(app_init_path.parent)],
    )
    if spec and spec.loader:
        app_module = importlib.util.module_from_spec(spec)
        sys.modules["app"] = app_module
        spec.loader.exec_module(app_module)
