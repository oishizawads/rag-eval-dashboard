"""合成 SaaS サポート FAQ の生成と永続化。

実在企業 FAQ のコピーではなく、架空の SaaS「CloudFlow」のサポート FAQ を
乱数シード固定で合成する。生成物は ``data/`` 以下の JSON に保存され、
以降は同じ内容が再現される。
"""

from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FAQ_PATH = DATA_DIR / "faq.json"
EVAL_PATH = DATA_DIR / "eval_questions.json"


@dataclass(frozen=True)
class FaqItem:
    """FAQ 1件。"""

    id: str
    title: str
    body: str
    category: str
    keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class EvalQuestion:
    """評価用の検索クエリとその正解根拠。"""

    id: str
    query: str
    relevant_ids: list[str] = field(default_factory=list)


def _synthetic_faq(seed: int) -> list[FaqItem]:
    """乱数シード固定で架空 FAQ を生成する。"""

    rng = random.Random(seed)

    base: list[dict[str, Any]] = [
        {
            "id": "faq_001",
            "title": "アカウント登録の手順",
            "category": "アカウント",
            "keywords": ["アカウント", "登録", "サインアップ", "始め方"],
            "body": (
                "CloudFlow への登録は公式サイトの「無料ではじめる」ボタンから行えます。"
                "メールアドレスとパスワードを入力し、確認メールのリンクをクリックすると"
                "アカウントが有効化されます。"
            ),
        },
        {
            "id": "faq_002",
            "title": "パスワードを忘れた場合のリセット手順",
            "category": "アカウント",
            "keywords": ["パスワード", "リセット", "忘れた", "再設定", "ログイン"],
            "body": (
                "ログイン画面の「パスワードをお忘れですか？」から登録メールアドレスを入力すると、"
                "リセット用リンクが送信されます。リンクの有効期限は30分です。"
            ),
        },
        {
            "id": "faq_003",
            "title": "料金プランの変更とダウングレード",
            "category": "契約・請求",
            "keywords": ["料金", "プラン", "変更", "ダウングレード", "アップグレード", "課金"],
            "body": (
                "プラン変更は設定の「プランと請求」から行えます。アップグレードは即時反映、"
                "ダウングレードは次回更新日に適用されます。"
            ),
        },
        {
            "id": "faq_004",
            "title": "請求書と領収書のダウンロード",
            "category": "契約・請求",
            "keywords": ["請求書", "領収書", "ダウンロード", "インボイス", "pdf"],
            "body": (
                "過去の請求書は「プランと請求 > 請求履歴」から PDF 形式でダウンロードできます。"
                "領収書の宛名指定も同画面から編集可能です。"
            ),
        },
        {
            "id": "faq_005",
            "title": "API のレート制限とクォータ",
            "category": "API",
            "keywords": ["api", "レート制限", "上限", "クォータ", "429", "呼び出し回数"],
            "body": (
                "API の呼び出しはプランごとに1分あたりの上限が設定されています。"
                "上限に達すると HTTP 429 が返却され、Retry-After ヘッダーの秒数を待つ必要があります。"
            ),
        },
        {
            "id": "faq_006",
            "title": "データのエクスポート形式",
            "category": "データ",
            "keywords": ["エクスポート", "データ", "csv", "json", "書き出し"],
            "body": (
                "データは設定の「データエクスポート」から CSV または JSON 形式で出力できます。"
                "大容量の場合はバックグラウンド処理となり、完了後にダウンロードリンクが発行されます。"
            ),
        },
        {
            "id": "faq_007",
            "title": "二要素認証の設定手順",
            "category": "セキュリティ",
            "keywords": ["二要素認証", "2fa", "mfa", "ワンタイムパスワード", "認証アプリ"],
            "body": (
                "セキュリティ設定の「二要素認証」から認証アプリを登録できます。"
                "QRコードをアプリで読み取り、6桁のコードを入力して有効化します。"
            ),
        },
        {
            "id": "faq_008",
            "title": "チームメンバーの招待と権限",
            "category": "チーム管理",
            "keywords": ["チーム", "メンバー", "招待", "権限", "ロール", "ユーザー"],
            "body": (
                "チーム設定の「メンバー」からメールアドレスで招待できます。"
                "ロールは管理者・編集者・閲覧者の3種類で、プロジェクトごとに割り当て可能です。"
            ),
        },
        {
            "id": "faq_009",
            "title": "サードパーティ連携の追加",
            "category": "連携",
            "keywords": ["連携", "integration", "slack", "zapier", "webhook", "サードパーティ"],
            "body": (
                "連携マーケットから Slack や Zapier などを追加できます。"
                "連携ごとにスコープを限定したアクセストークンが発行されます。"
            ),
        },
        {
            "id": "faq_010",
            "title": "監査ログの取得期間",
            "category": "セキュリティ",
            "keywords": ["監査ログ", "操作履歴", "audit", "取得期間", "証跡"],
            "body": (
                "監査ログはエンタープライズプランで直近12ヶ月分を取得できます。"
                "CSV エクスポートも可能で、ユーザー・アクション・日時で絞り込めます。"
            ),
        },
        {
            "id": "faq_011",
            "title": "ダッシュボードのカスタマイズ",
            "category": "UI",
            "keywords": ["ダッシュボード", "カスタマイズ", "ウィジェット", "レイアウト", "表示"],
            "body": (
                "ダッシュボードはウィジェット単位で追加・移動が可能です。"
                "保存したレイアウトは個人のみに適用され、チーム共有は別途設定が必要です。"
            ),
        },
        {
            "id": "faq_012",
            "title": "通知設定とチャネル指定",
            "category": "通知",
            "keywords": ["通知", "アラート", "メール", "チャネル", "設定"],
            "body": (
                "通知はイベントごとにメール・Slack・アプリ内のチャネルを選択できます。"
                "重大度に応じて送信頻度を調整する設定も用意されています。"
            ),
        },
        {
            "id": "faq_013",
            "title": "データの保持期間と削除",
            "category": "データ",
            "keywords": ["保持期間", "削除", "データ", "ガバナンス", "保存"],
            "body": (
                "データの保持期間は既定で24ヶ月です。設定から短縮でき、"
                "削除リクエストは実行から30日後に物理削除されます。"
            ),
        },
        {
            "id": "faq_014",
            "title": "サポートへの問い合わせ方法",
            "category": "サポート",
            "keywords": ["サポート", "問い合わせ", "ヘルプ", "コンタクト", "対応"],
            "body": (
                "アプリ内のヘルプアイコンからチャットで問い合わせできます。"
                "エンタープライズプランでは専用メールと優先レスポンスが利用可能です。"
            ),
        },
        {
            "id": "faq_015",
            "title": "計画メンテナンスのスケジュール",
            "category": "運用",
            "keywords": ["メンテナンス", "停止", "スケジュール", "障害", "稼働時間"],
            "body": (
                "計画メンテナンスは月1回、日曜の深夜に実施し、ステータスページで事前告知します。"
                "影響範囲は読み取り機能の一時利用不可のみです。"
            ),
        },
    ]

    items: list[FaqItem] = []
    for entry in base:
        title = entry["title"]
        body = entry["body"]
        if rng.random() < 0.0:
            body = body
        items.append(
            FaqItem(
                id=entry["id"],
                title=title,
                body=body,
                category=entry["category"],
                keywords=list(entry["keywords"]),
            )
        )
    return items


def _synthetic_eval_questions() -> list[EvalQuestion]:
    """評価用クエリと正解根拠を定義する。"""

    return [
        EvalQuestion("q_01", "パスワードを忘れてログインできない", ["faq_002"]),
        EvalQuestion("q_02", "請求書を PDF でダウンロードしたい", ["faq_004"]),
        EvalQuestion("q_03", "API の呼び出し回数の上限を知りたい", ["faq_005"]),
        EvalQuestion("q_04", "データを CSV や JSON で書き出したい", ["faq_006"]),
        EvalQuestion("q_05", "二段階認証を有効にしたい", ["faq_007"]),
        EvalQuestion("q_06", "チームにメンバーを招待したい", ["faq_008"]),
        EvalQuestion("q_07", "Slack との連携を追加したい", ["faq_009"]),
        EvalQuestion("q_08", "過去の操作履歴を確認したい", ["faq_010"]),
        EvalQuestion("q_09", "プランを安いものに変更したい", ["faq_003"]),
        EvalQuestion("q_10", "通知をメール以外にしたい", ["faq_012"]),
        EvalQuestion("q_11", "データの保持期間はどれくらいか", ["faq_013"]),
        EvalQuestion("q_12", "メンテナンスで止まる時間を知りたい", ["faq_015"]),
    ]


def _ensure_data_files(seed: int = 42) -> None:
    """data/ に FAQ と評価質問が無ければ生成して保存する。"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not FAQ_PATH.exists():
        items = _synthetic_faq(seed)
        FAQ_PATH.write_text(
            json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if not EVAL_PATH.exists():
        qs = _synthetic_eval_questions()
        EVAL_PATH.write_text(
            json.dumps([asdict(q) for q in qs], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def build_corpus(seed: int = 42) -> list[FaqItem]:
    """FAQ コーパスを読み込み、無ければ生成して返す。"""

    _ensure_data_files(seed)
    raw = json.loads(FAQ_PATH.read_text(encoding="utf-8"))
    return [FaqItem(**entry) for entry in raw]


def load_eval_questions(seed: int = 42) -> list[EvalQuestion]:
    """評価用質問セットを読み込み、無ければ生成して返す。"""

    _ensure_data_files(seed)
    raw = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    return [EvalQuestion(**entry) for entry in raw]


def rebuild_data(seed: int = 42) -> tuple[list[FaqItem], list[EvalQuestion]]:
    """data/ を強制的に再生成する（テスト・再現用途）。"""

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    items = _synthetic_faq(seed)
    FAQ_PATH.write_text(
        json.dumps([asdict(i) for i in items], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    qs = _synthetic_eval_questions()
    EVAL_PATH.write_text(
        json.dumps([asdict(q) for q in qs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return items, qs
