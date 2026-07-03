"""評価指標のテスト。"""

from __future__ import annotations

from src.data import build_corpus, load_eval_questions
from src.evaluate import (
    evaluate_retriever,
    mrr,
    precision_at_k,
    recall_at_k,
)
from src.search import SearchMethod, Searcher


def test_recall_perfect_and_zero() -> None:
    assert recall_at_k(["a", "b"], ["a", "b"]) == 1.0
    assert recall_at_k(["a"], ["a", "b"]) == 0.5
    assert recall_at_k(["c"], ["a", "b"]) == 0.0
    assert recall_at_k(["a"], []) == 0.0


def test_precision_perfect_and_zero() -> None:
    assert precision_at_k(["a", "b"], ["a", "b"]) == 1.0
    assert precision_at_k(["a", "c"], ["a", "b"]) == 0.5
    assert precision_at_k(["c", "d"], ["a", "b"]) == 0.0
    assert precision_at_k([], ["a"]) == 0.0


def test_mrr_values() -> None:
    assert mrr(["a", "b"], ["a"]) == 1.0
    assert mrr(["c", "a"], ["a"]) == 0.5
    assert mrr(["c", "d"], ["a"]) == 0.0
    assert mrr([], ["a"]) == 0.0


def test_evaluate_retriever_summary_ranges() -> None:
    corpus = build_corpus()
    questions = load_eval_questions()
    searcher = Searcher(corpus, SearchMethod.TFIDF)
    summary = evaluate_retriever(searcher, questions, top_k=5)
    assert summary.top_k == 5
    assert len(summary.per_question) == len(questions)
    assert 0.0 <= summary.mean_recall <= 1.0
    assert 0.0 <= summary.mean_precision <= 1.0
    assert 0.0 <= summary.mean_mrr <= 1.0


def test_evaluate_retriever_handles_empty_questions() -> None:
    corpus = build_corpus()
    searcher = Searcher(corpus, SearchMethod.TFIDF)
    summary = evaluate_retriever(searcher, [], top_k=5)
    assert summary.per_question == []
    assert summary.mean_recall == 0.0
    assert summary.mean_mrr == 0.0


def test_per_question_hit_ranks_are_consistent() -> None:
    corpus = build_corpus()
    questions = load_eval_questions()
    searcher = Searcher(corpus, SearchMethod.BM25)
    summary = evaluate_retriever(searcher, questions, top_k=5)
    for pq in summary.per_question:
        rel = set(pq.relevant_ids)
        expected = [r for r, rid in enumerate(pq.retrieved_ids, start=1) if rid in rel]
        assert pq.hit_ranks == expected
        assert pq.recall <= 1.0
