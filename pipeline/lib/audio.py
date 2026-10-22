"""Original music bed + audio assembly.

No third-party samples: everything is synthesised with numpy from a fixed seed, so
the bed is CC0 and reproducible. SoX is then used for the trim/fade/stat work that
the chain documents (see skills/base/sox/SKILL.md).
"""
from __future__ import annotations

import math
import wave
from pathlib import Path

import numpy as np

SR = 48000
BPM = 90
SEED = 20261022


def _env(n: int, attack: float, decay: float) -> np.ndarray:
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-t / max(decay, 1e-4))
    return a * d


def _pluck(freq: float, dur: float, amp: float = 0.3) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * freq * t) * 0.6
           + np.sin(2 * np.pi * freq * 2 * t) * 0.25
           + np.sin(2 * np.pi * freq * 3.01 * t) * 0.12)
    return sig * _env(n, 0.004, dur * 0.28) * amp


def _kick(dur: float = 0.28, amp: float = 0.5) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 92 * np.exp(-t * 26) + 44
    sig = np.sin(2 * np.pi * np.cumsum(freq) / SR)
    return sig * np.exp(-t * 14) * amp


def _shaker(dur: float = 0.09, amp: float = 0.12) -> np.ndarray:
    rng = np.random.default_rng(SEED)
    n = int(dur * SR)
    noise = rng.standard_normal(n)
    # cheap high-pass: difference of consecutive samples
    hp = np.diff(noise, prepend=noise[0])
    return hp * np.exp(-np.arange(n) / SR * 55) * amp


def build_bed(seconds: float = 30.0, bpm: int = BPM, seed: int = SEED) -> np.ndarray:
    """90 BPM pentatonic bed: plucks on the beat, soft kick on 1 & 3, shaker on 8ths."""
    rng = np.random.default_rng(seed)
    total = int(seconds * SR)
    buf = np.zeros((total, 2), dtype=np.float64)
    beat = 60.0 / bpm
    # D minor pentatonic-ish, kept low so it sits under a voice-over later
    scale = [146.83, 174.61, 196.00, 220.00, 261.63, 293.66]
    pattern = [0, 2, 4, 2, 3, 5, 4, 1]

    def place(sig: np.ndarray, at: float, gain: float = 1.0, pan: float = 0.0):
        start = int(at * SR)
        if start >= total:
            return
        n = min(len(sig), total - start)
        left = gain * (1 - max(0.0, pan))
        right = gain * (1 + min(0.0, pan))
        buf[start:start + n, 0] += sig[:n] * left
        buf[start:start + n, 1] += sig[:n] * right

    steps = int(seconds / (beat / 2)) + 1
    for i in range(steps):
        at = i * beat / 2
        if i % 2 == 0:  # quarter notes: melodic pluck
            note = scale[pattern[(i // 2) % len(pattern)]]
            place(_pluck(note, 1.1, 0.22), at, 1.0, pan=rng.uniform(-0.3, 0.3))
            place(_pluck(note * 2, 0.7, 0.07), at, 1.0, pan=rng.uniform(-0.4, 0.4))
        if i % 4 == 0:  # kick on 1 and 3
            place(_kick(), at, 0.5)
        if i % 2 == 1:  # shaker on the off-beat
            place(_shaker(), at, 0.5, pan=0.25)

    # low pad for warmth
    t = np.arange(total) / SR
    pad = (np.sin(2 * np.pi * 73.42 * t) * 0.5 + np.sin(2 * np.pi * 110.0 * t) * 0.25)
    pad *= np.clip(t / 2.0, 0, 1) * np.clip((seconds - t) / 2.5, 0, 1) * 0.10
    buf[:, 0] += pad
    buf[:, 1] += pad

    peak = np.max(np.abs(buf)) or 1.0
    return (buf / peak * 0.55).astype(np.float32)


def write_wav(path: Path, data: np.ndarray, sr: int = SR) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = np.clip(data, -1.0, 1.0)
    ints = (clipped * 32767).astype("<i2")
    with wave.open(str(path), "wb") as fh:
        fh.setnchannels(ints.shape[1] if ints.ndim > 1 else 1)
        fh.setsampwidth(2)
        fh.setframerate(sr)
        fh.writeframes(ints.tobytes())
    return path


def read_wav(path: Path):
    with wave.open(str(path), "rb") as fh:
        n, ch, sr = fh.getnframes(), fh.getnchannels(), fh.getframerate()
        raw = np.frombuffer(fh.readframes(n), dtype="<i2").astype(np.float32) / 32768.0
    return raw.reshape(-1, ch), sr
