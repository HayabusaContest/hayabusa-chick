# プロバイダとモデルの設定

[README](../README.md) の補足です。設定は `config/` の2ファイルで行います。

- `config/config.yml` … 使うプロバイダ(`llm.type`)、モデル、プロンプト
- `config/.env` … APIキー(`YOUR_API_KEY` を自分のキーに置き換える)

`llm.type` に指定したプロバイダのブロックだけが使われます。APIキーは使うものだけ設定すればOK(ollama / huggingface はキー不要)。

## プロバイダとモデルの変更

`config/config.yml` を編集するだけで切り替えられます。

```yaml
llm:
  type: google          # openai / google / anthropic / ollama / huggingface
  sleep_time: 3       # 1トークン表示ごとの待機秒。レート制限が出たら上げる

openai:
  model: gpt-4o-mini
  temperature: 0.7
  reasoning_effort:      # GPT-5系のみ対応(none/low/medium/high/xhigh)。他は空欄

google:
  model: gemini-flash-lite-latest   # 無料枠のあるモデル。枠は変わるので 429 が出たら別の Flash 系に
  temperature: 0.7

anthropic:
  model: claude-haiku-4-5
  temperature: 0.7        # 新しいモデル(Sonnet 5 等)は温度非対応。その場合は行を削除
  max_tokens: 256

ollama:
  model: llama3.1
  temperature: 0.7
  base_url: http://localhost:11434
```

thinking / reasoning はプロバイダ固有です(統一スイッチは用意していません)。各ブロックにその名前で書けば渡ります — Gemini は `thinking_budget: 0` で off、Claude は `thinking: {type: disabled}`、OpenAI(GPT-5系)は `reasoning_effort`。`config.yml` にコメントアウトの例を置いてあるので、必要なら外して使ってください。

ollama・vLLM・HuggingFace などローカル/セルフホストの起動や依存は [local-models.md](local-models.md) を参照。

## プロンプト

システムプロンプトは `config/config.yml` の `prompt.system` で管理しています。回答の方針を変えたいときは、コードを触らずここを編集してください。

## 応答の保存(output)

各ステップの「No / 逐次入力 / 回答」を、実行ごとに1ファイルとして保存します(画面表示はそのまま)。

```yaml
output:
  enabled: true         # false で保存しない
  dir: data/output
  formats: [csv, jsonl] # 片方だけにするなら [csv] など
```

- 保存先: `data/output/csv/` と `data/output/jsonl/`。
- ファイル名は `<モデル名>_<タイムスタンプ>.csv` / `.jsonl`(csv と jsonl は同じベース名のペア)。jsonl には `model` と `timestamp` も記録します。
- `data/output/` は `.gitignore` 済みなので、保存結果は git に入りません(`data/input/sample_questions.csv` 以外の data は無視されます)。

## 仕組み・プロバイダの追加(改造したい人向け)

- `config_loader.py` が `config.yml` と `.env` を読み込み、`agent.py` が `llm.type` に応じてモデルを生成します。API系(openai/google/anthropic)と ollama は LangChain の `init_chat_model` で一元化、huggingface だけは `HuggingFacePipeline`(ローカル実行)で別扱いです。呼び出しは毎回 system+user だけの単発で、会話履歴は持ちません。
- 新しいAPI系プロバイダを足すには、`agent.py` の `_CHAT_PROVIDER_MAP` に `config.yml のキー: LangChain の model_provider 名` を1行追加します(対応する `langchain-xxx` パッケージが必要)。
- vLLM / LM Studio / Together / Groq などの **OpenAI互換エンドポイント**は、`openai` ブロックに `base_url` を足すだけでコード追加なしに使えます([local-models.md](local-models.md))。
