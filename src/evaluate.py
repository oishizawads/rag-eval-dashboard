"""検索結果の評価指標。recall@k / precision@k / MRR。"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.data import EvalQuestion
from src.search import SearchResult, Searcher


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """recall@k = |正解 ∩ 検索結果| / |正解|。正解が空なら 0。"""

    if not relevant_ids:
        return 0.0
    hit = len(set(retrieved_ids) & set(relevant_ids))
    return hit / len(set(relevant_ids))


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """precision@k = |正解 ∩ 検索結果| / k。k=0 のとき 0。"""

    if not retrieved_ids:
        return 0.0
    hit = len(set(retrieved_ids) & set(relevant_ids))
    return hit / len(retrieved_ids)


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """MRR = 1 / (最初の正解の順位)。正解が無ければ 0。"""

    rel_set = set(relevant_ids)
    for rank, rid in enumerate(retrieved_ids, start=1):
        if rid in rel_set:
            return 1.0 / rank
    return 0.0


@dataclass(frozen=True)
class QuestionEval:
    """1質問あたりの評価結果。"""

    question_id: str
    query: str
    retrieved_ids: list[str]
    relevant_ids: list[str]
    recall: float
    precision: float
    reciprocal_rank: float
    hit_ranks: list[int] = field(default_factory=list)


@dataclass(frozen=True)
class EvalSummary:
    """質問セット全体の評価サマリー。"""

    top_k: int
    mean_recall: float
    mean_precision: float
    mean_mrr: float
    per_question: list[QuestionEval]


def _hit_ranks(retrieved_ids: list[str], relevant_ids: list[str]) -> list[int]:
    rel_set = set(relevant_ids)
    return [rank for rank, rid in enumerate(retrieved_ids, start=1) if rid in rel_set]


def evaluate_retriever(
    searcher: Searcher,
    questions: list[EvalQuestion],
    top_k: int = 5,
) -> EvalSummary:
    """検索器を全質問で評価しサマリーを返す。空の質問セットでも落ちない。"""

    per_question: list[QuestionEval] = []
    for q in questions:
        results: list[SearchResult] = searcher.search(q.query, top_k=top_k)
        retrieved_ids = [r.faq_id for r in results]
        per_question.append(
            QuestionEval(
                question_id=q.id,
                query=q.query,
                retrieved_ids=retrieved_ids,
                relevant_ids=list(q.relevant_ids),
                recall=recall_at_k(retrieved_ids, q.relevant_ids),
                precision=precision_at_k(retrieved_ids, q.relevant_ids),
                reciprocal_rank=mrr(retrieved_ids, q.relevant_ids),
                hit_ranks=_hit_ranks(retrieved_ids, q.relevant_ids),
            )
        )

    n = max(len(per_question), 1)
    mean_recall = sum(p.recall for p in per_question) / n
    mean_precision = sum(p.precision for p in per_question) / n
    mean_mrr = sum(p.reciprocal_rank for p in per_question) / n
    return EvalSummary(
        top_k=top_k,
        mean_recall=mean_recall,
        mean_precision=mean_precision,
        mean_mrr=mean_mrr,
        per_question=per_question,
    )
