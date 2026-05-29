"""1D KDE helpers for ridgeline analytical charts (numpy-only)."""

import numpy as np


def gaussian_kde_1d(values: np.ndarray, grid: np.ndarray) -> np.ndarray:
    """Evaluate Gaussian KDE on a fixed grid."""
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 2:
        return np.zeros_like(grid, dtype=float)

    std = float(values.std())
    if std < 1e-6:
        std = 1.0
    bandwidth = 1.06 * std * (len(values) ** (-1 / 5))
    bandwidth = max(bandwidth, 0.8)

    diff = (grid[:, None] - values[None, :]) / bandwidth
    density = np.exp(-0.5 * diff**2).sum(axis=1)
    density /= len(values) * bandwidth * np.sqrt(2 * np.pi)
    if density.max() > 0:
        density /= density.max()
    return density
