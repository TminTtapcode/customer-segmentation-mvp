"""Tìm đường dẫn dữ liệu từ REES46_DATA_ROOT hoặc data/ trong repository.

Chỉ tính đường dẫn; không tạo thư mục, đọc dataset hoặc xác nhận dữ liệu hợp lệ.
Đường dẫn cấu hình tương đối luôn được tính từ repository, không từ terminal cwd.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def data_root() -> Path:
    configured = os.environ.get("REES46_DATA_ROOT", "").strip()
    root = Path(configured).expanduser() if configured else PROJECT_ROOT / "data"
    if not root.is_absolute():
        root = PROJECT_ROOT / root
    return root.resolve()


def observation_path() -> Path:
    return data_root() / "cleaned" / "observation_events.parquet"


if __name__ == "__main__":
    observation = observation_path()
    print(json.dumps({"data_root": str(data_root()), "observation_path": str(observation),
                      "observation_exists": observation.is_file(),
                      "note": "Path inspection only; existence is not data acceptance."}))
