# ローカルLLMの起動方法(Colab含む)

[README](../README.md) の補足です。各ローカルバックエンドの立ち上げ方と、Google Colab での動かし方をまとめています。`config/config.yml` に何を書くか(設定値)は [local-models.md](local-models.md) を参照してください。

## ollama

1. **インストール** — [ollama公式](https://ollama.com/download) から。macOS / Linux はターミナルで下記、Windows は公式ページのインストーラ(.exe)を使ってください。
   ```bash
   # macOS / Linux
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **モデルを取得**:
   ```bash
   ollama pull llama3.1
   ```
3. **サーバー** — インストール後に自動でローカルサーバー(`http://localhost:11434`)が立ち上がります(立っていなければ `ollama serve`)。
4. `config.yml` を ollama に設定([local-models.md](local-models.md))して `uv run python main.py data/input/sample_questions.csv`。

## vLLM(OpenAI互換サーバー・Linux + NVIDIA GPU 前提)

1. **導入**(このリポジトリとは別の環境で。torch/CUDA を含む重量級):
   ```bash
   pip install vllm
   ```
2. **サーバー起動** — `http://localhost:8000/v1` で待ち受けます:
   ```bash
   vllm serve Qwen/Qwen2.5-1.5B-Instruct
   ```
3. `config.yml` を `openai` + `base_url` に設定([local-models.md](local-models.md))。

LM Studio など他の OpenAI互換サーバーも同様です(起動方法は各公式ドキュメントを参照)。

## HuggingFace(依存の追加)

プロセス内で直接実行するのでサーバーは不要。重い依存だけ追加します:

```bash
uv sync --extra huggingface
```

その後 `config.yml` を huggingface に設定([local-models.md](local-models.md))。`torch` が大きいため既定では入れていません。

## Google Colab(無料GPU)

手元にGPUが無くても、Colab の無料GPUで HuggingFace を試せます。

1. [Google Colab](https://colab.research.google.com/) で新しいノートブックを開き、**「ランタイム → ランタイムのタイプを変更 → T4 GPU」** を選択。
2. セルで取得と依存インストール:
   ```python
   !git clone https://github.com/iggy157/hayabusa-chick.git
   %cd hayabusa-chick
   !pip install uv
   !uv sync --extra huggingface
   ```
3. 左のファイルブラウザで `config/config.yml` を開き、`type: huggingface` と `device: 0`(GPU)に編集。
4. 実行:
   ```python
   !uv run python main.py data/input/sample_questions.csv
   ```

APIプロバイダ(Gemini など)を Colab で使う場合はGPUもHF依存も不要で、`!uv sync` だけでOK。`config/.env` にキーを入れて同じように実行できます。
