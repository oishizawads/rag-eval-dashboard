"""テンプレートベースの回答生成。LLM を呼ばず、根拠FAQから回答文を組み立てる。"""

from __future__ import annotations

from dataclasses import dataclass

from src.data import FaqItem
from src.search import SearchResult


@dataclass(frozen=True)
class AnswerOutput:
    """回答生成結果。"""

    text: str
    source_id: str | None
    source_title: str | None
    confidence: float


def _confidence(results: list[SearchResult]) -> float:
    """トップと2番目のスコア比から相対信頼度(0..1)を出す。"""

    if not results:
        return 0.0
    top = results[0].score
    if len(results) == 1:
        return 1.0 if top > 0 else 0.0
    second = results[1].score
    denom = top + second
    if denom <= 0:
        return 0.0
    return max(0.0, min(1.0, top / denom))


def build_answer(
    query: str,
    results: list[SearchResult],
    corpus_map: dict[str, FaqItem],
) -> AnswerOutput:
    """クエリと検索結果から回答文を組み立てる。結果が空でも落ちない。"""

    if not query or not query.strip():
        return AnswerOutput(
            text="質問を入力してください。",
            source_id=None,
            source_title=None,
            confidence=0.0,
        )
    if not results:
        return AnswerOutput(
            text="関連するFAQが見つかりませんでした。別のキーワードでお試しください。",
            source_id=None,
            source_title=None,
            confidence=0.0,
        )

    top = results[0]
    item = corpus_map.get(top.faq_id)
    if item is None:
        return AnswerOutput(
            text="根拠ドキュメントが特定できませんでした。",
            source_id=None,
            source_title=None,
            confidence=0.0,
        )

    confidence = _confidence(results)
    text = (
        f"ご質問「{query}」について、最も関連する情報は「{item.title}」です。\n"
        f"{item.body}\n"
        f"（根拠: {item.id} / カテゴリ: {item.category}）"
    )
    return AnswerOutput(
        text=text,
        source_id=item.id,
        source_title=item.title,
        confidence=confidence,
    )
