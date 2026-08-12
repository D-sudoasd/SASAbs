#!/usr/bin/env python3
"""Capture the SASAbs Workbench for documentation and the JOSS paper.

The capture is window-scoped and written atomically.  It deliberately does not
fall back to a full-screen grab: a failed capture must never replace the paper
figure with unrelated desktop content.  The default output preserves the full
window so interface context remains visible and the screenshot can be audited.
"""

import argparse
import importlib.util
import os
import sys
import time
import tkinter as tk
from pathlib import Path

from PIL import ImageGrab

# We need to import the main script's directory
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))


def capture(output: Path, *, control_pane_only: bool = False) -> None:
    """Launch GUI, wait for render, capture screenshot, then destroy."""
    bootstrap_root = tk.Tk()
    bootstrap_root.withdraw()  # hide until module is loaded

    # Dynamically load SASAbs — keep __name__=="SASAbs" so loader is happy,
    # but patch __name__ after loading to prevent if __name__=="__main__" from running.
    module_spec = importlib.util.spec_from_file_location("SASAbs", str(ROOT / "SASAbs.py"))
    if module_spec is None or module_spec.loader is None:
        raise ImportError("could not load SASAbs.py")
    workbench_module = importlib.util.module_from_spec(module_spec)

    # Patch argparse to avoid consuming sys.argv
    original_parse_args = argparse.ArgumentParser.parse_args
    argparse.ArgumentParser.parse_args = lambda self, args=None, ns=None: original_parse_args(
        self, args=[], namespace=ns
    )

    try:
        module_spec.loader.exec_module(workbench_module)
    except SystemExit:
        pass
    finally:
        argparse.ArgumentParser.parse_args = original_parse_args

    bootstrap_root.destroy()

    # Re-create properly using the app's own main flow.
    app_root = tk.Tk()
    app_root.geometry("1280x800+50+50")
    workbench_module.SAXSAbsWorkbenchApp(app_root, language="en")
    app_root.deiconify()
    app_root.lift()
    app_root.update_idletasks()
    app_root.update()

    # Allow rendering to complete
    app_root.after(
        800,
        lambda: _do_capture(app_root, output, control_pane_only=control_pane_only),
    )
    app_root.mainloop()


def _do_capture(root: tk.Tk, output: Path, *, control_pane_only: bool) -> None:
    """Capture the native top-level window and close the application."""
    root.update_idletasks()
    root.update()
    time.sleep(0.3)

    temporary = output.with_name(f"{output.stem}.tmp{output.suffix}")
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        image = ImageGrab.grab(window=root.winfo_id())
        if control_pane_only:
            image = image.crop((0, 0, min(475, image.width), image.height))
        image.save(temporary, "PNG")
        temporary.replace(output)
        print(f"OK: {output} ({image.width}x{image.height})")
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        print(f"ERROR: window capture failed: {exc}", file=sys.stderr)
        root.destroy()
        raise SystemExit(1) from exc
    else:
        root.destroy()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "paper" / "fig_gui.png",
    )
    parser.add_argument(
        "--control-pane-only",
        action="store_true",
        help="save only the left control pane instead of the full application window",
    )
    args = parser.parse_args()
    capture(args.output.resolve(), control_pane_only=args.control_pane_only)
