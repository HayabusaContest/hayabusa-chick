# ローカル / セルフホスト LLM の設定

[README](../README.md) の補足です。`config/config.yml` の書き方をまとめています。ローカル/セルフホストは3通りで、追加の重い依存(torch など)が要るのは HuggingFace だけです。各バックエンドの**起動手順や Colab での動かし方**は [run-local.md](run-local.md) を参照してください。

## ollama

```yaml
llm:
  type: ollama
ollama:
  model: llama3.1
  base_url: http://localhost:11434
```

## OpenAI互換サーバー(vLLM / LM Studio / Together / Groq など)

OpenAI互換APIを出すサーバーは、`openai` プロバイダの `base_url` を向けるだけで使えます(追加依存もコード変更も不要)。

```yaml
llm:
  type: openai            # OpenAI 互換なので openai を使う
openai:
  model: <サーバーで配信中のモデル名>
  base_url: http://localhost:8000/v1
```

ローカルの vLLM / LM Studio はキー不要(ダミーで可)。Together / Groq などクラウドの互換サービスは `config/.env` の `OPENAI_API_KEY` にそのキーを入れます。

## HuggingFace(transformers をプロセス内で直接実行)

```yaml
llm:
  type: huggingface
huggingface:
  model: gpt2
  device: -1            # -1: CPU / 0: GPU(cuda:0)
  max_new_tokens: 64
  temperature: 0.7
```

`uv sync --extra huggingface` で依存を追加します(起動手順は [run-local.md](run-local.md))。なお素の `gpt2` は指示追従の学習がされていないため、この用途では小型のinstruct系モデルの方が向いています。
