"""
hayabusa-chick CLI エントリーポイント

使い方:
    python main.py data/sample_questions.csv
"""

import sys

from engine import run


def main() -> None:
    if len(sys.argv) < 2:
        print("使い方: python main.py <CSVファイルパス>")
        sys.exit(1)

    # APIキー(.env)と設定(config.yml)の読み込みは config_loader が行います。
    run(sys.argv[1])


if __name__ == "__main__":
    main()
