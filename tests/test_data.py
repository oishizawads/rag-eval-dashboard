"""合成データ生成のテスト。"""

from __future__ import annotations

import src.data as data_mod
from src.data import build_corpus, load_eval_questions, rebuild_data


def test_rebuild_is_reproducible_with_same_seed() -> None:
    items_a, qs_a = rebuild_data(seed=42)
    items_b, qs_b = rebuild_data(seed=42)
    assert [i.id for i in items_a] == [i.id for i in items_b]
    assert [q.id for q in qs_a] == [q.id for q in qs_b]
    assert items_a[0].title == items_b[0].title


def test_corpus_has_unique_ids_and_nonempty_bodies() -> None:
    items = build_corpus()
    ids = [i.id for i in items]
    assert len(ids) == len(set(ids))
    assert all(i.body.strip() for i in items)
    assert all(i.keywords for i in items)


def test_eval_questions_reference_existing_faq_ids() -> None:
    items = build_corpus()
    questions = load_eval_questions()
    valid_ids = {i.id for i in items}
    for q in questions:
        assert q.relevant_ids, f"{q.id} に正解根拠がありません"
        for rid in q.relevant_ids:
            assert rid in valid_ids, f"{q.id} の正解 {rid} がコーパスに存在しません"


def test_ensure_data_files_creates_files(tmp_path) -> None:
    assert not (tmp_path / "data" / "faq.json").exists()
    build_corpus()
    assert (tmp_path / "data" / "faq.json").exists()
    assert (tmp_path / "data" / "eval_questions.json").exists()
