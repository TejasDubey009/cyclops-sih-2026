"""CYCLOPS — Cyclone Observation, Prediction & Explainability System."""
from __future__ import annotations

import sys
import types

__version__ = "0.2.0-mvp"

# Windows Smart App Control / WDAC compatibility for unsigned SciPy C-extensions in Python 3.14
if "scipy.interpolate._interpnd" not in sys.modules:
    try:
        import scipy.interpolate._interpnd  # noqa: F401
    except Exception:
        _stub = types.ModuleType("scipy.interpolate._interpnd")
        _stub.LinearNDInterpolator = type("LinearNDInterpolator", (), {})
        _stub.NDInterpolatorBase = type("NDInterpolatorBase", (), {})
        _stub.CloughTocher2DInterpolator = type("CloughTocher2DInterpolator", (), {})
        _stub._ndim_coords_from_arrays = lambda *a, **k: None
        sys.modules["scipy.interpolate._interpnd"] = _stub
