"""Basic dermatoglyphic feature helpers (pattern cues + ridge/minutiae approximations)."""

from __future__ import annotations

import cv2
import numpy as np


def estimate_ridge_density(gray: np.ndarray) -> float:
    """Rough ridge-density score from binary ridge skeleton length."""
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    binary = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2
    )
    skeleton = _skeletonize(binary)
    return float(np.count_nonzero(skeleton) / skeleton.size)


def approximate_minutiae_count(gray: np.ndarray) -> dict[str, int]:
    """
    Lightweight minutiae approximation for reporting/demo.
    Not a forensic-grade extractor — document this limitation in the report.
    """
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2
    )
    skeleton = _skeletonize(binary) // 255
    endings = 0
    bifurcations = 0
    h, w = skeleton.shape
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if skeleton[y, x] == 0:
                continue
            neighborhood = skeleton[y - 1 : y + 2, x - 1 : x + 2]
            ones = int(neighborhood.sum() - 1)
            if ones == 1:
                endings += 1
            elif ones == 3:
                bifurcations += 1
    return {"ridge_endings": endings, "bifurcations": bifurcations}


def _skeletonize(binary: np.ndarray) -> np.ndarray:
    """Zhang-Suen-like thinning via OpenCV morphology iterate."""
    img = binary.copy()
    skeleton = np.zeros_like(img)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skeleton = cv2.bitwise_or(skeleton, temp)
        img = eroded.copy()
        if cv2.countNonZero(img) == 0:
            break
    return skeleton
