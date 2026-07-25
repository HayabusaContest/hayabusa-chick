"""
hayabusa-chick: 実行エンジン

問題文をBPEトークン単位で1トークンずつ少しずつ読み上げるように表示し(逐次入力)、
そのたびに agent.predict_answer() を呼び出して、その時点での回答を
「入力に対する回答」として表示します。正解かどうかの自動判定は行いません。

各ステップの「No / 逐次入力 / 回答」は、config.yml の output 設定に従って
data/output/csv/ と data/output/jsonl/ に実行ごとのファイルとして保存します。

このファイルは基本的に改造不要です。
挙動を変えたい場合は agent.py を編集してください。
"""

import csv
import json
import os
import re
import time
from datetime import datetime
from typing import List

import tiktoken

from agent import predict_answer
from config_loader import load_config

# 問題文をトークン化するエンコーディング(BPEトークナイザー)
_ENCODING = tiktoken.get_encoding("o200k_base")


def _tokenize(question_text: str) -> List[int]:
    return _ENCODING.encode(question_text)


class _Recorder:
    """各ステップの結果を data/output/{csv,jsonl}/ に保存する。

    config.yml の output.enabled が false の場合は何もしない。
    ファイル名は <モデル名>_<タイムスタンプ> で、csv/jsonl で共通のベース名。
    """

    def __init__(self, config: dict):
        out = config.get("output") or {}
        self._files = []
        self._csv = None
        self._jsonl = None
        if not out.get("enabled", True):
            return

        base_dir = out.get("dir", "data/output")
        formats = out.get("formats") or ["csv", "jsonl"]

        llm_type = (config.get("llm") or {}).get("type", "openai")
        self._model = str((config.get(llm_type) or {}).get("model", llm_type))
        self._stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        safe_model = re.sub(r"[^\w.-]", "_", self._model)
        base_name = f"{safe_model}_{self._stamp}"

        if "csv" in formats:
            d = os.path.join(base_dir, "csv")
            os.makedirs(d, exist_ok=True)
            f = open(os.path.join(d, base_name + ".csv"), "w", encoding="utf-8-sig", newline="")
            self._files.append(f)
            self._csv = csv.writer(f)
            self._csv.writerow(["No", "逐次入力", "回答"])

        if "jsonl" in formats:
            d = os.path.join(base_dir, "jsonl")
            os.makedirs(d, exist_ok=True)
            f = open(os.path.join(d, base_name + ".jsonl"), "w", encoding="utf-8")
            self._files.append(f)
            self._jsonl = f

    def write(self, no: str, partial_input: str, answer: str) -> None:
        if self._csv is not None:
            self._csv.writerow([no, partial_input, answer])
        if self._jsonl is not None:
            self._jsonl.write(json.dumps({
                "no": no,
                "partial_input": partial_input,
                "answer": answer,
                "model": self._model,
                "timestamp": self._stamp,
            }, ensure_ascii=False) + "\n")

    def close(self) -> None:
        for f in self._files:
            f.close()


def run(csv_path: str) -> None:
    config = load_config()
    reveal_delay = float((config.get("llm") or {}).get("sleep_time", 0.1))

    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    recorder = _Recorder(config)
    try:
        for row in rows:
            print(f"\n--- 問題 {row['No']} ---")
            token_ids = _tokenize(row["問題文"])

            for i in range(1, len(token_ids) + 1):
                partial_question = _ENCODING.decode(token_ids[:i])
                print(f"逐次入力: {partial_question}")

                answer = predict_answer(partial_question)
                print(f"入力に対する回答: {answer if answer else ''}")

                recorder.write(row["No"], partial_question, answer or "")
                time.sleep(reveal_delay)
    finally:
        recorder.close()
