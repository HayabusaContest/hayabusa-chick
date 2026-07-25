# セットアップ(uv / git のインストールと環境構築)

[README](../README.md) の補足です。uv・git の入れ方と、環境構築まわりの詳細だけをまとめています。

## uv

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

pip や Homebrew があれば `pip install uv` / `brew install uv` でも入ります。他の方法は [uv 公式](https://docs.astral.sh/uv/getting-started/installation/) を参照。Python は uv が自動で用意するので、個別インストールは不要です。

## git

- **macOS**: `xcode-select --install`(または `brew install git`)
- **Linux (Debian/Ubuntu)**: `sudo apt install git`
- **Windows**: [Git for Windows](https://git-scm.com/download/win) をインストール

## 環境構築と依存管理

```bash
uv sync
```

`pyproject.toml` の宣言と `uv.lock` の固定バージョンに従って `.venv` が作られ、依存がインストールされます。実行は有効化不要で `uv run python main.py ...`。

依存の宣言は `pyproject.toml` の `[project.dependencies]` が唯一の場所で、`uv.lock` が正確なバージョンを固定します。依存を足すときは `uv add <パッケージ名>`(ロックも自動更新)、手で変えたら `uv lock` でロックを更新してください。
