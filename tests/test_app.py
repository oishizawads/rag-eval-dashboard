"""Streamlit アプリがヘッドレスでエラー無くレンダリングできるか検証する。"""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app" / "streamlit_app.py"


def test_app_renders_without_exception() -> None:
    at = AppTest.from_file(str(APP_PATH), default_timeout=120)
    at.run()
    assert not at.exception, f"アプリで例外が発生: {at.exception}"
    # 指標サマリーとタイトルが描画されていること
    assert at.title
    assert at.metric


def test_app_custom_query_empty_state() -> None:
    """カスタムクエリ未入力でも落ちず、空状態メッセージが出ること。"""

    at = AppTest.from_file(str(APP_PATH), default_timeout=120)
    at.run()
    at.sidebar.radio(key="mode_radio").set_value("カスタムクエリを入力")
    at.run()
    assert not at.exception
    assert at.info  # 空クエリ時の案内メッセージ
