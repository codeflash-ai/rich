from __future__ import annotations

from typing import IO


def get_fileno(file_like: IO[str]) -> int | None:
    """Get fileno() from a file, accounting for poorly implemented file-like objects.

    Args:
        file_like (IO): A file-like object.

    Returns:
        int | None: The result of fileno if available, or None if operation failed.
    """
    # Use try/except directly; avoids attribute lookups and unnecessary getattr
    try:
        return file_like.fileno()
    except Exception:
        # `fileno` is documented as potentially raising a OSError
        # Alas, from the issues, there are so many poorly implemented file-like objects,
        # that `fileno()` can raise just about anything.
        return None
