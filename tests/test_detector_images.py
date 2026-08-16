"""Close-safe detector-image loader tests.

These tests drive the shipped helper with injected fake handles. They do not
re-implement the close/copy contract and do not hard-code scientific values.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from saxsabs.io.detector_images import (
    close_image_handle,
    load_detector_header,
    load_detector_image,
    load_detector_pixels,
)


def test_load_detector_image_closes_handle_and_returns_owned_array():
    source = np.array([[1, 2]], dtype=np.int16)
    opened = SimpleNamespace(data=source, header={"ExposureTime": "1.0"}, close=Mock())

    loaded = load_detector_image("frame.tif", open_image_fn=lambda path: opened)
    source[0, 0] = 99
    opened.header["ExposureTime"] = "mutated"

    np.testing.assert_array_equal(loaded.data, np.array([[1.0, 2.0]]))
    assert loaded.data.dtype == np.float64
    assert loaded.header == {"ExposureTime": "1.0"}
    opened.close.assert_called_once_with()


def test_load_detector_image_closes_handle_after_missing_pixel_data():
    opened = SimpleNamespace(header={}, close=Mock())

    with pytest.raises(ValueError, match="no pixel data"):
        load_detector_image("empty.tif", open_image_fn=lambda path: opened)

    opened.close.assert_called_once_with()


def test_load_detector_image_closes_handle_after_data_access_failure():
    opened = SimpleNamespace(close=Mock())

    class BrokenData:
        @property
        def data(self):
            raise RuntimeError("broken detector data")

        header = {}
        close = opened.close

    with pytest.raises(RuntimeError, match="broken detector data"):
        load_detector_image("broken.tif", open_image_fn=lambda path: BrokenData())

    opened.close.assert_called_once_with()


def test_load_detector_pixels_preserves_source_dtype_when_requested():
    source = np.array([[1, 0]], dtype=np.uint8)
    opened = SimpleNamespace(data=source, header={}, close=Mock())

    pixels = load_detector_pixels(
        "mask.edf",
        dtype=None,
        open_image_fn=lambda path: opened,
    )
    source[0, 0] = 7

    np.testing.assert_array_equal(pixels, np.array([[1, 0]], dtype=np.uint8))
    assert pixels.dtype == np.uint8
    opened.close.assert_called_once_with()


def test_load_detector_header_closes_without_requiring_pixel_data():
    opened = SimpleNamespace(header={"Monitor": "100"}, close=Mock())

    header = load_detector_header("header-only.tif", open_image_fn=lambda path: opened)
    opened.header["Monitor"] = "mutated"

    assert header == {"Monitor": "100"}
    opened.close.assert_called_once_with()


def test_load_detector_header_closes_after_header_copy_failure():
    opened = SimpleNamespace(close=Mock())

    class BrokenHeader:
        def items(self):
            raise RuntimeError("broken header")

        def __iter__(self):
            raise RuntimeError("broken header")

    broken = SimpleNamespace(header=BrokenHeader(), close=opened.close)

    header = load_detector_header("bad-header.tif", open_image_fn=lambda path: broken)

    assert header == {}
    opened.close.assert_called_once_with()


def test_close_image_handle_ignores_objects_without_close():
    close_image_handle(SimpleNamespace(data=[[1]]))


def test_read_detector_image_delegates_to_shared_loader(monkeypatch):
    from saxsabs.workflows import bl19b2_abs2d as bl19b2

    opened = SimpleNamespace(data=np.array([[3, 4]], dtype=np.int16), close=Mock())
    fake_fabio = SimpleNamespace(open=lambda path: opened)
    monkeypatch.setitem(__import__("sys").modules, "fabio", fake_fabio)

    image = bl19b2.read_detector_image("frame.tif")
    opened.data[0, 0] = 99

    np.testing.assert_array_equal(image, np.array([[3.0, 4.0]]))
    assert image.dtype == np.float64
    opened.close.assert_called_once_with()


def test_default_opener_uses_injected_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    seen: list[str] = []

    class FakeFabio:
        @staticmethod
        def open(path):
            seen.append(str(path))
            return SimpleNamespace(
                data=np.array([[8, 9]], dtype=np.float64),
                header={"path": str(path)},
                close=Mock(),
            )

    monkeypatch.setitem(__import__("sys").modules, "fabio", FakeFabio)
    image_path = tmp_path / "frame.tif"
    loaded = load_detector_image(image_path)

    assert seen == [str(image_path)]
    np.testing.assert_array_equal(loaded.data, [[8.0, 9.0]])
    assert loaded.header["path"] == str(image_path)
