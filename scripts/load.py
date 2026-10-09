#!/usr/bin/env python3
"""Convenience script for loading the transformed data into SQLite."""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.transform import transform_cases


if __name__ == "__main__":
    transform_cases()
