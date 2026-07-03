"""テスト共通: data/ を一時ディレクトリに隔離して並列・反復安全性を担保する。"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolate_data_dir(tmp_path, monkeypatch):
    import src.data as data_mod

    data_dir = tmp_path / "data"
    monkeypatch.setattr(data_mod, "DATA_DIR", data_dir)
    monkeypatch.setattr(data_mod, "FAQ_PATH", data_dir / "faq.json")
    monkeypatch.setattr(data_mod, "EVAL_PATH", data_dir / "eval_questions.json")
    yield
