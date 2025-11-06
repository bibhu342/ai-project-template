"""Model package init.

Import models so they register on Base.metadata when the package is imported.
Use relative imports to avoid any ambiguity with top-level package resolution
in different environments (e.g., CI images with conflicting packages).
"""

from .user import User  # noqa: F401
from .customer import Customer  # noqa: F401
from .note import Note  # noqa: F401
