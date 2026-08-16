"""Close-safe detector-image loading.

FabIO image objects hold OS file handles. Every reader must copy pixels and
header out, then close the handle — including when the read later fails.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

OpenImageFn = Callable[[str | Path], Any]


@dataclass(frozen=True)
class DetectorImageLoad:
    """Owned detector pixels plus a copied header mapping."""

    data: np.ndarray
    header: dict[str, Any]


def close_image_handle(image: Any) -> None:
    """Close a FabIO-like image if it exposes a callable ``close``."""

    close = getattr(image, "close", None)
    if callable(close):
        close()


def copy_image_header(header: Any) -> dict[str, Any]:
    """Return a plain dict copy of a FabIO-like header mapping."""

    if header is None:
        return {}
    if isinstance(header, Mapping):
        return dict(header)
    try:
        return dict(header)
    except Exception:
        return {}


def _default_open_image(path: str | Path) -> Any:
    try:
        import fabio
    except ImportError as exc:
        raise ImportError("fabio is required for detector-image reading") from exc
    return fabio.open(str(path))


def load_detector_image(
    path: str | Path,
    *,
    dtype: np.dtype | type[np.generic] | None = np.float64,
    open_image_fn: OpenImageFn | None = None,
) -> DetectorImageLoad:
    """Open a detector image, copy pixels/header, and always close the handle.

    Parameters
    ----------
    path
        Image path passed to ``open_image_fn``.
    dtype
        Pixel dtype for the owned copy. ``None`` preserves the source dtype
        (used for masks). A concrete dtype always copies into C-order.
    open_image_fn
        Injectable opener returning an object with ``.data``, optional
        ``.header``, and optional ``.close``. Defaults to ``fabio.open``.
    """

    opener = open_image_fn if open_image_fn is not None else _default_open_image
    image = opener(path)
    try:
        raw = getattr(image, "data", None)
        if raw is None:
            raise ValueError(f"detector image has no pixel data: {path}")
        if dtype is None:
            data = np.array(raw, copy=True)
        else:
            data = np.array(raw, dtype=dtype, copy=True, order="C")
        header = copy_image_header(getattr(image, "header", None))
        return DetectorImageLoad(data=data, header=header)
    finally:
        close_image_handle(image)


def load_detector_pixels(
    path: str | Path,
    *,
    dtype: np.dtype | type[np.generic] | None = np.float64,
    open_image_fn: OpenImageFn | None = None,
) -> np.ndarray:
    """Return owned detector pixels and close the image handle."""

    return load_detector_image(path, dtype=dtype, open_image_fn=open_image_fn).data


def load_detector_header(
    path: str | Path,
    *,
    open_image_fn: OpenImageFn | None = None,
) -> dict[str, Any]:
    """Copy the image header and always close the handle.

    Header-only callers still go through the same close contract. Pixel data
    is not required; a missing ``.data`` attribute is ignored.
    """

    opener = open_image_fn if open_image_fn is not None else _default_open_image
    image = opener(path)
    try:
        return copy_image_header(getattr(image, "header", None))
    finally:
        close_image_handle(image)
