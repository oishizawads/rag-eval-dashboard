"""検索ロジックのテスト。"""

from __future__ import annotations

import pytest

from src.data import build_corpus, load_eval_questions
from src.search import SearchMethod, Searcher


@pytest.fixture()
def corpus():
    return build_corpus()


@pytest.fixture()
def questions():
    return load_eval_questions()


@pytest.mark.parametrize("method", [SearchMethod.TFIDF, SearchMethod.BM25])
def test_empty_query_returns_empty(method, corpus) -> None:
    searcher = Searcher(corpus, method)
    assert searcher.search("", top_k=5) == []
    assert searcher.search("   ", top_k=5) == []
    assert searcher.search(None, top_k=5) == []  # type: ignore[arg-type]


@pytest.mark.parametrize("method", [SearchMethod.TFIDF, SearchMethod.BM25])
def test_unknown_tokens_do_not_crash(method, corpus) -> None:
    searcher = Searcher(corpus, method)
    results = searcher.search("qwxy zzzz 12345", top_k=5)
    # 未知語でも例外は起きない。結果が空またはスコア0件のみでよい。
    assert isinstance(results, list)


@pytest.mark.parametrize("method", [SearchMethod.TFIDF, SearchMethod.BM25])
def test_top_k_bounds_and_ranks(method, corpus) -> None:
    searcher = Searcher(corpus, method)
    results = searcher.search("パスワード リセット", top_k=3)
    assert len(results) <= 3
    assert [r.rank for r in results] == list(range(1, len(results) + 1))


def test_top_k_zero_returns_empty(corpus) -> None:
    searcher = Searcher(corpus, SearchMethod.TFIDF)
    assert searcher.search("パスワード", top_k=0) == []


@pytest.mark.parametrize("method", [SearchMethod.TFIDF, SearchMethod.BM25])
def test_relevant_faq_appears_in_topk(method, corpus, questions) -> None:
    searcher = Searcher(corpus, method)
    q = next(q for q in questions if q.id == "q_01")  # パスワードリセット
    results = searcher.search(q.query, top_k=5)
    retrieved_ids = [r.faq_id for r in results]
    assert q.relevant_ids[0] in retrieved_ids


def test_methods_can_produce_different_rankings(corpus, questions) -> None:
    """検索方式の違いで順位が変化するケースが少なくとも1つ存在することを確認。"""

    tfidf = Searcher(corpus, SearchMethod.TFIDF)
    bm25 = Searcher(corpus, SearchMethod.BM25)
    differs = False
    for q in questions:
        a = [r.faq_id for r in tfidf.search(q.query, top_k=5)]
        b = [r.faq_id for r in bm25.search(q.query, top_k=5)]
        if a and b and a != b:
            differs = True
            break
    assert differs, "TF-IDF と BM25 風で順位が全問一致した（方式比較の意味がない）"


def test_empty_corpus_raises() -> None:
    with pytest.raises(ValueError):
        Searcher([], SearchMethod.TFIDF)
