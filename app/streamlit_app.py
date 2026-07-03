"""RAG 評価ダッシュボードの Streamlit エントリポイント。

UI は薄く保ち、計算ロジックは src/ の関数に委ねる。
"""

from __future__ import annotations

import sys
from pathlib import Path

import altair as alt
import polars as pl
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.answer import build_answer
from src.brand import apply_brand, hero
from src.data import FaqItem, build_corpus, load_eval_questions
from src.evaluate import evaluate_retriever
from src.search import SearchMethod, Searcher

st.set_page_config(
    page_title="RAG 評価ダッシュボード",
    page_icon="🔎",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_corpus() -> list[FaqItem]:
    return build_corpus()


@st.cache_data(show_spinner=False)
def load_questions() -> list:
    return load_eval_questions()


@st.cache_resource(show_spinner=False)
def get_searcher(method: str) -> Searcher:
    return Searcher(load_corpus(), SearchMethod(method))


def render_sidebar() -> dict:
    st.sidebar.title("RAG 評価ダッシュボード")
    st.sidebar.caption("合成データのデモ（実在の精度・効果を示すものではありません）")

    method = st.sidebar.radio(
        "検索方式",
        options=[("TF-IDF（cosine）", "tfidf"), ("BM25 風", "bm25")],
        format_func=lambda x: x[0],
        index=0,
        key="method_radio",
    )[1]

    top_k = st.sidebar.slider(
        "Top-K（根拠表示件数）",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        key="top_k_slider",
    )

    mode = st.sidebar.radio(
        "質問の選び方",
        options=["質問セットから選ぶ", "カスタムクエリを入力"],
        index=0,
        key="mode_radio",
    )

    custom_query = ""
    selected_id: str | None = None
    if mode == "質問セットから選ぶ":
        questions = load_questions()
        options = {q.id: f"{q.id}: {q.query}" for q in questions}
        selected_id = st.sidebar.selectbox(
            "質問を選択",
            options=list(options.keys()),
            format_func=lambda qid: options[qid],
            key="question_select",
        )
    else:
        custom_query = st.sidebar.text_area(
            "カスタムクエリ",
            value="",
            placeholder="例: パスワードを忘れた",
            height=80,
        )

    return {
        "method": method,
        "top_k": top_k,
        "mode": mode,
        "selected_id": selected_id,
        "custom_query": custom_query,
    }


def render_metric_summary(summary) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("評価質問数", len(summary.per_question))
    col2.metric("平均 Recall@K", f"{summary.mean_recall:.3f}")
    col3.metric("平均 Precision@K", f"{summary.mean_precision:.3f}")
    col4.metric("平均 MRR", f"{summary.mean_mrr:.3f}")


def render_per_question_chart(summary) -> None:
    if not summary.per_question:
        st.info("評価対象の質問がありません。")
        return
    df = pl.DataFrame(
        {
            "質問ID": [p.question_id for p in summary.per_question],
            "クエリ": [p.query for p in summary.per_question],
            "Recall@K": [p.recall for p in summary.per_question],
            "Precision@K": [p.precision for p in summary.per_question],
            "MRR": [p.reciprocal_rank for p in summary.per_question],
        }
    )
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("質問ID:O", sort=None, title="質問ID"),
            y=alt.Y("Recall@K:Q", scale=alt.Scale(domain=[0, 1]), title="Recall@K (0..1)"),
            tooltip=["質問ID", "クエリ", "Recall@K", "Precision@K", "MRR"],
        )
        .properties(width="container", height=280)
    )
    st.altair_chart(chart, width="stretch")


def render_results(
    query: str,
    results: list,
    corpus_map: dict[str, FaqItem],
    relevant_ids: list[str] | None,
    top_k: int,
) -> None:
    if not query.strip():
        st.warning("質問またはクエリを入力してください。")
        return
    if not results:
        st.info("該当するFAQが見つかりませんでした（未知語・空クエリでも落ちない設計）。")
        return

    answer = build_answer(query, results, corpus_map)
    st.subheader("生成回答（テンプレート）")
    conf = answer.confidence
    st.markdown(f"**信頼度（相対）:** `{conf:.2f}` ｜ 根拠: `{answer.source_id}` / {answer.source_title}")
    st.info(answer.text)

    st.subheader(f"根拠ドキュメント（Top-{top_k}）")
    rows = []
    for r in results:
        item = corpus_map.get(r.faq_id)
        is_relevant = relevant_ids is not None and r.faq_id in relevant_ids
        rows.append(
            {
                "順位": r.rank,
                "FAQ ID": r.faq_id,
                "タイトル": item.title if item else "（不明）",
                "カテゴリ": item.category if item else "—",
                "スコア": round(r.score, 4),
                "正解根拠": "○" if is_relevant else "",
            }
        )
    st.dataframe(pl.DataFrame(rows), width="stretch", hide_index=True)

    for r in results:
        item = corpus_map.get(r.faq_id)
        if item is None:
            continue
        with st.expander(f"#{r.rank} {item.title} （スコア {r.score:.4f}）"):
            st.markdown(f"**ID:** {item.id} ｜ **カテゴリ:** {item.category}")
            st.write(item.body)
            st.caption(f"キーワード: {', '.join(item.keywords)}")


def main() -> None:
    apply_brand(st)
    cfg = render_sidebar()
    corpus = load_corpus()
    questions = load_questions()
    corpus_map = {item.id: item for item in corpus}

    searcher = get_searcher(cfg["method"])
    top_k = cfg["top_k"]

    hero(
        st,
        "RAG Evaluation",
        "RAG 評価ダッシュボード",
        "検索方式（TF-IDF / BM25 風）を切り替えて、検索結果・回答・根拠・評価指標を比較します。",
    )

    st.subheader("指標サマリー（質問セット全体）")
    summary = evaluate_retriever(searcher, questions, top_k=top_k)
    render_metric_summary(summary)
    render_per_question_chart(summary)

    st.divider()

    if cfg["mode"] == "質問セットから選ぶ":
        question = next((q for q in questions if q.id == cfg["selected_id"]), None)
        if question is None:
            st.warning("質問が選択されていません。")
            return
        st.subheader(f"選択中の質問: {question.id}")
        st.markdown(f"**クエリ:** {question.query}")
        st.markdown(f"**正解根拠:** {', '.join(question.relevant_ids) if question.relevant_ids else '（なし）'}")
        results = searcher.search(question.query, top_k=top_k)
        render_results(question.query, results, corpus_map, question.relevant_ids, top_k)
    else:
        st.subheader("カスタムクエリ評価")
        query = cfg["custom_query"]
        if not query.strip():
            st.info("サイドバーにカスタムクエリを入力すると、検索結果と回答が表示されます。")
            return
        results = searcher.search(query, top_k=top_k)
        render_results(query, results, corpus_map, None, top_k)


if __name__ == "__main__":
    main()
