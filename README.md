# hayabusa-chick

早押しクイズエージェント作成用の最小構成テンプレートです。
自己完結型のエージェントでサーバ不要です。シングルエージェントのみ対応で、複数人でのクイズ大会を行いたい場合はhayabusa-quiz-agentをご利用ください。

問題文をBPEトークン(`tiktoken`)単位で1トークンずつ少しずつ読み上げるように表示し、そのたびにあなたのエージェント(`agent.py`)を呼び出して、その時点での回答をターミナルに表示します。表示されるのは「逐次入力」と「入力に対する回答」の2つだけで、正解かどうかの自動判定は行いません(表示された回答が正しいかは自分の目で確認してください)。

対応プロバイダは **OpenAI / Google (Gemini) / Anthropic (Claude) / ローカルLLM (ollama・HuggingFace)**。切り替えや詳しい設定は [docs/providers.md](docs/providers.md) を参照してください。

## 動作環境

Windows・macOS・Linux で動きます。まず次のコマンドで **uv** と **git** が入っているか確認してください(Python は uv が用意するので不要)。

```bash
uv --version
git --version
```

見つからないものがあれば、[docs/setup.md](docs/setup.md) に各OSのインストールコマンドをまとめています。

## クイックスタート

### 1. 取得と環境構築

```bash
git clone https://github.com/iggy157/hayabusa-chick.git
cd hayabusa-chick
uv sync
cp config/.env.example config/.env     # Windows は copy config\.env.example config\.env
```

`uv sync` で仮想環境の作成と依存インストールがまとめて行われます(`uv.lock` で固定されたバージョンが入るので、いつ・誰が実行しても同じ環境になります)。

### 2. プロバイダを選んで、使える状態にする

まず `config/config.yml` の `llm.type` で使うプロバイダを選びます(`openai` / `google` / `anthropic` / `ollama` / `huggingface`。モデルなどの細かい設定も同じファイルです)。

次に、選んだLLMを実行できるように準備します。

- **API系(openai / google / anthropic)** — `config/.env` に該当プロバイダのAPIキーを設定(例 `GOOGLE_API_KEY=...`)。無料で試すなら [Google AI Studio](https://aistudio.google.com/apikey) の Gemini が手軽です。
- **ローカル(ollama)** — ollama をローカルで起動しておきます。起動手順や vLLM・HuggingFace・Colab など他の構成は [docs/run-local.md](docs/run-local.md) を参照。

### 3. 実行

```bash
uv run python main.py data/input/sample_questions.csv
```

問題文とその下に回答が表示されれば成功です。引数の CSV パスを自分のファイルに差し替えれば、好きな問題で動かせます(`data/input/sample_questions.csv` は動作確認用のサンプル。自分の問題CSVは `data/input/` に置くと分かりやすいです)。

## 入力と出力(data/)

**入力** — 問題データは `data/input/` に CSV で置きます(サンプル: `data/input/sample_questions.csv`)。フォーマットは次の3列:

```csv
No,問題文,解答
1,問題文の本文,正答
```

**出力** — 実行結果は自動で `data/output/` に保存されます(1回の実行につき1ファイル。ファイル名は `<モデル名>_<タイムスタンプ>`)。

- `data/output/csv/` … `No / 逐次入力 / 回答` の表形式(Excelなどで開ける)
- `data/output/jsonl/` … 1行1レコード。`model` と `timestamp` も含む

保存の on/off や形式は `config/config.yml` の `output` で変更できます(詳細は [docs/providers.md](docs/providers.md))。サンプル以外の `data/` は git 管理外です。

## もっと詳しく

補足ドキュメントは `docs/` にあります。

- [docs/setup.md](docs/setup.md) — uv / git のインストールと環境構築
- [docs/providers.md](docs/providers.md) — プロバイダ・モデル・プロンプトの設定
- [docs/local-models.md](docs/local-models.md) — ローカル/セルフホスト LLM の設定
- [docs/run-local.md](docs/run-local.md) — ローカルLLMの起動方法(ollama・vLLM・HuggingFace・Colab)
