"""検索方式の実装。TF-IDF（cosine 類似度）と BM25 風スコアリング。

両方式とも同じ文字 n-gram トークナイザを用いるため、検索方式の違いが
ランキングに与える影響を公平に比較できる。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.data import FaqItem


class SearchMethod(str, Enum):
    """検索方式。"""

    TFIDF = "tfidf"
    BM25 = "bm25"


@dataclass(frozen=True)
class SearchResult:
    """検索結果1件。"""

    rank: int
    faq_id: str
    score: float


def _document_text(item: FaqItem) -> str:
    """検索対象テキストを組み立てる。"""

    return f"{item.title} {item.body} {' '.join(item.keywords)}"


def _char_ngram_tokenizer(text: str) -> list[str]:
    """文字 2-3 gram の簡易トークナイザ。"""

    chars = list(text)
    tokens: list[str] = []
    for n in (2, 3):
        for i in range(len(chars) - n + 1):
            tokens.append("".join(chars[i : i + n]))
    return tokens


class Searcher:
    """コーパスから検索インデックスを構築しクエリを検索する。"""

    def __init__(self, corpus: list[FaqItem], method: SearchMethod = SearchMethod.TFIDF) -> None:
        if not corpus:
            raise ValueError("コーパスが空です")
        self._corpus = corpus
        self._ids = [item.id for item in corpus]
        self._method = method
        self._docs = [_document_text(item) for item in corpus]
        self._build_index()

    def _build_index(self) -> None:
        if self._method == SearchMethod.TFIDF:
            self._vectorizer = TfidfVectorizer(
                analyzer="char",
                ngram_range=(2, 3),
                lowercase=False,
                token_pattern=None,
            )
            self._doc_matrix = self._vectorizer.fit_transform(self._docs).toarray()
        elif self._method == SearchMethod.BM25:
            self._count_vectorizer = CountVectorizer(
                analyzer="char",
                ngram_range=(2, 3),
                lowercase=False,
                token_pattern=None,
            )
            self._count_matrix = self._count_vectorizer.fit_transform(self._docs).toarray()
            self._vocab = self._count_vectorizer.get_feature_names_out()
            self._doc_lens = self._count_matrix.sum(axis=1).astype(float)
            self._avgdl = float(self._doc_lens.mean()) if len(self._docs) else 1.0
            self._k1 = 1.5
            self._b = 0.75
            n_docs = len(self._docs)
            df = (self._count_matrix > 0).sum(axis=0).astype(float)
            df_safe = np.where(df == 0, 1e-9, df)
            self._idf = np.log((n_docs - df + 0.5) / (df_safe + 0.5) + 1.0)
        else:  # pragma: no cover - enum で到達不能
            raise ValueError(f"未知の検索方式: {self._method}")

    def _score_tfidf(self, query: str) -> np.ndarray:
        query_vec = self._vectorizer.transform([query]).toarray()[0]
        if query_vec.sum() == 0:
            return np.zeros(len(self._docs))
        doc_norms = np.linalg.norm(self._doc_matrix, axis=1)
        q_norm = np.linalg.norm(query_vec)
        denom = doc_norms * q_norm
        denom_safe = np.where(denom == 0, 1e-9, denom)
        return (self._doc_matrix @ query_vec) / denom_safe

    def _score_bm25(self, query: str) -> np.ndarray:
        query_vec = self._count_vectorizer.transform([query]).toarray()[0]
        if query_vec.sum() == 0:
            return np.zeros(len(self._docs))
        scores = np.zeros(len(self._docs))
        term_idx = np.where(query_vec > 0)[0]
        for idx in term_idx:
            tf = self._count_matrix[:, idx]
            denom = tf + self._k1 * (1 - self._b + self._b * self._doc_lens / max(self._avgdl, 1e-9))
            term_scores = self._idf[idx] * (tf * (self._k1 + 1)) / np.where(denom == 0, 1e-9, denom)
            scores += term_scores
        return scores

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """クエリを検索し Top-K を返す。空クエリや未知語でも空リストを返す。"""

        if query is None or not query.strip():
            return []
        if top_k <= 0:
            return []

        if self._method == SearchMethod.TFIDF:
            scores = self._score_tfidf(query)
        else:
            scores = self._score_bm25(query)

        if scores.sum() == 0:
            return []

        order = np.argsort(-scores)
        results: list[SearchResult] = []
        for rank, doc_idx in enumerate(order, start=1):
            if rank > top_k:
                break
            score = float(scores[doc_idx])
            if not math.isfinite(score) or score <= 0:
                continue
            results.append(SearchResult(rank=rank, faq_id=self._ids[doc_idx], score=score))
        return results
