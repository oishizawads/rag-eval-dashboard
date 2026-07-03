"""RAG 評価ダッシュボードのコアロジック。"""

from src.data import build_corpus, load_eval_questions
from src.search import Searcher, SearchMethod
from src.evaluate import evaluate_retriever, recall_at_k, precision_at_k, mrr
from src.answer import build_answer

__all__ = [
    "build_corpus",
    "load_eval_questions",
    "Searcher",
    "SearchMethod",
    "evaluate_retriever",
    "recall_at_k",
    "precision_at_k",
    "mrr",
    "build_answer",
]
