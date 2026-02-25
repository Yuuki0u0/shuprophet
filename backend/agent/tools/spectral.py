"""
频域分析工具
"""

import numpy as np
from scipy import signal


def fft_analysis(data: list) -> dict:
    """FFT spectrum analysis — extract dominant frequencies."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Remove mean (DC component)
    y_centered = y - np.mean(y)

    # FFT
    fft_vals = np.fft.rfft(y_centered)
    magnitudes = np.abs(fft_vals)
    freqs = np.fft.rfftfreq(n)

    # Skip DC (index 0)
    mag = magnitudes[1:]
    frq = freqs[1:]

    if len(mag) == 0:
        return {"tool": "fft_analysis", "dominant_periods": [], "spectral_energy": 0}

    # Top-5 dominant frequencies
    top_k = min(5, len(mag))
    top_idx = np.argsort(mag)[-top_k:][::-1]

    dominant = []
    for i in top_idx:
        if frq[i] > 0:
            dominant.append({
                "frequency": round(float(frq[i]), 6),
                "period": round(float(1.0 / frq[i]), 2),
                "magnitude": round(float(mag[i]), 4),
            })

    # Spectral entropy (measure of complexity)
    psd = mag ** 2
    psd_norm = psd / (psd.sum() + 1e-10)
    spectral_entropy = float(-np.sum(psd_norm * np.log(psd_norm + 1e-10)))

    return {
        "tool": "fft_analysis",
        "dominant_periods": dominant,
        "spectral_entropy": round(spectral_entropy, 4),
        "has_strong_periodicity": len(dominant) > 0 and dominant[0]["magnitude"] > np.mean(mag) * 3,
    }


def wavelet_decomposition(data: list, max_level: int = 4) -> dict:
    """DWT multi-scale decomposition using Haar wavelet (no PyWavelets dependency)."""
    y = np.array(data, dtype=float)
    n = len(y)

    # Simple Haar wavelet decomposition
    levels = []
    approx = y.copy()
    for lv in range(1, max_level + 1):
        if len(approx) < 4:
            break
        # Truncate to even length
        m = len(approx) - (len(approx) % 2)
        a = approx[:m]
        # Haar: approx = (a[::2]+a[1::2])/sqrt(2), detail = (a[::2]-a[1::2])/sqrt(2)
        new_approx = (a[::2] + a[1::2]) / np.sqrt(2)
        detail = (a[::2] - a[1::2]) / np.sqrt(2)

        detail_energy = float(np.sum(detail ** 2))
        levels.append({
            "level": lv,
            "detail_energy": round(detail_energy, 4),
            "detail_std": round(float(np.std(detail)), 4),
            "detail_len": len(detail),
        })
        approx = new_approx

    total_energy = sum(lv["detail_energy"] for lv in levels) + float(np.sum(approx ** 2))
    for lv in levels:
        lv["energy_ratio"] = round(lv["detail_energy"] / (total_energy + 1e-10), 4)

    return {
        "tool": "wavelet_decomposition",
        "levels": levels,
        "total_energy": round(total_energy, 4),
        "dominant_scale": max(levels, key=lambda x: x["detail_energy"])["level"] if levels else 0,
    }


def periodogram(data: list) -> dict:
    """Welch periodogram for robust spectral density estimation."""
    y = np.array(data, dtype=float)
    n = len(y)
    nperseg = min(256, n // 2) if n > 8 else n

    freqs, psd = signal.welch(y, fs=1.0, nperseg=max(4, nperseg))

    # Skip DC
    freqs, psd = freqs[1:], psd[1:]
    if len(psd) == 0:
        return {"tool": "periodogram", "peaks": []}

    # Find peaks
    peak_idx, props = signal.find_peaks(psd, height=np.mean(psd))
    top_k = min(5, len(peak_idx))
    sorted_peaks = sorted(peak_idx, key=lambda i: psd[i], reverse=True)[:top_k]

    peaks = []
    for i in sorted_peaks:
        if freqs[i] > 0:
            peaks.append({
                "frequency": round(float(freqs[i]), 6),
                "period": round(float(1.0 / freqs[i]), 2),
                "power": round(float(psd[i]), 4),
            })

    return {
        "tool": "periodogram",
        "peaks": peaks,
        "total_power": round(float(np.sum(psd)), 4),
    }


# --- Tool Registry ---
SPECTRAL_TOOLS = {
    "fft_analysis": {
        "fn": fft_analysis,
        "description": "FFT spectrum analysis to extract dominant frequencies and periodicity. Use for periodic or seasonal data.",
        "triggers": ["frequency", "fft", "periodic", "cycle"],
    },
    "wavelet_decomposition": {
        "fn": wavelet_decomposition,
        "description": "Haar wavelet multi-scale decomposition. Use for multi-resolution analysis of complex signals.",
        "triggers": ["wavelet", "multiscale", "resolution"],
    },
    "periodogram": {
        "fn": periodogram,
        "description": "Welch periodogram for robust spectral density estimation. Use to confirm periodicity findings.",
        "triggers": ["periodogram", "spectral_density", "power_spectrum"],
    },
}
