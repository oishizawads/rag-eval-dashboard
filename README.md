# RAG 評価ダッシュボード

RAG（検索拡張生成）の品質を **検索結果・回答・根拠・評価指標** で比較できる、公開用の小型アプリです。「RAG は作るだけでなく評価すること」を示すことを目的にしています。

> **注意:** 本アプリの FAQ データはすべて **合成データ** であり、実在の精度・効果を示すものではありません。

## 目的

- 検索方式（TF-IDF / BM25 風）の違いでランキングがどう変わるかを可視化する
- Top-K の根拠ドキュメントと、それに基づく回答文をセットで提示する
- recall@k / precision@k / MRR で検索品質を定量的に評価する

## 主要機能

- 質問セット選択（架空 SaaS サポート FAQ に対する評価クエリ）
- 検索方式の切り替え：TF-IDF（cosine 類似度）/ BM25 風スコアリング
- 回答結果一覧（テンプレート生成）
- 根拠ドキュメント表示（Top-K）
- 指標サマリー（平均 Recall@K / Precision@K / MRR）と質問別グラフ
- カスタムクエリの入力（空クエリ・未知語でも落ちない）

## 使用技術

- Python 3.11+
- Streamlit（UI）
- scikit-learn（TF-IDF の特徴抽出）
- polars（結果の表組）
- Altair（指標グラフ、Streamlit 同梱）
- pytest（コアロジックのテスト）

## データの出所

- `data/faq.json` と `data/eval_questions.json` は **架空 SaaS「CloudFlow」の合成サポート FAQ** です
- 実在企業 FAQ のコピーではありません
- 乱数シード固定で生成されるため再現可能（`src/data.py` の `rebuild_data(seed=...)`）
- 初回起動時に `data/` が自動生成されます

## ローカル実行手順

```bash
# 依存関係のインストール（uv を推奨）
uv sync

# アプリの起動
uv run streamlit run app/streamlit_app.py

# テストの実行
uv run pytest
```

Python 3.11+ が必要です。`uv` を使わない場合は `pip install streamlit scikit-learn polars pytest` でも動きます。

## ディレクトリ構成

```
rag-eval-dashboard/
├── app/
│   └── streamlit_app.py      # Streamlit エントリ（UI は薄く）
├── src/
│   ├── data.py               # 合成 FAQ の生成と永続化
│   ├── search.py             # TF-IDF / BM25 風の検索
│   ├── evaluate.py           # recall@k / precision@k / MRR
│   └── answer.py             # テンプレート回答生成
├── tests/                    # src/ 関数の最低限のテスト
├── data/                     # 合成データ（自動生成）
├── assets/                   # スクリーンショット置き場
└── pyproject.toml
```

## スクリーンショット

`assets/` に配置してください（現在は空）。

![dashboard](assets/dashboard.png)

## 制限事項

- MVP であり、認証・DB・本番運用機能・課金は含みません
- 回答文はテンプレート生成であり、LLM による生成ではありません（API キー不要）
- トークナイザは文字 n-gram の簡易方式で、形態素解析は行いません
- TF-IDF と BM25 風でスコアのスケールが異なるため、信頼度は相対値として表示します
- **合成データであり、実在の検索精度・効果を示すものではありません**

## セキュリティ

- API キー等の秘密情報は使用しません（`.env` 不要で動作）
- `.env` が存在してもコミットされません（`.gitignore` で除外）
