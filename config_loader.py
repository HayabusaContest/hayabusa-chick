"""
設定の読み込み

config/config.yml(プロバイダ選択・モデル設定)と config/.env(APIキー)を
読み込みます。基本的にこのファイルを編集する必要はありません。
"""

from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

_CONFIG_DIR = Path(__file__).resolve().parent / "config"
_CONFIG_PATH = _CONFIG_DIR / "config.yml"
_ENV_PATH = _CONFIG_DIR / ".env"

_config_cache: Dict[str, Any] = {}


def load_config() -> Dict[str, Any]:
    """config/.env と config/config.yml を読み込んで設定辞書を返します。"""
    global _config_cache
    if _config_cache:
        return _config_cache

    # APIキーを環境変数へ読み込む(存在しなくてもエラーにはしない)。
    load_dotenv(_ENV_PATH)

    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"設定ファイルが見つかりません: {_CONFIG_PATH}\n"
            "config/config.yml を用意してください。"
        )

    with open(_CONFIG_PATH, encoding="utf-8") as f:
        _config_cache = yaml.safe_load(f) or {}

    return _config_cache
