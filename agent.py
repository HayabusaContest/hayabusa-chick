"""
hayabusa-chick: 早押しクイズエージェント

改造するのはこのファイルだけです。

predict_answer() は、問題文が少しずつ読み上げられるたびに呼び出されます。
まだ問題文が最後まで読まれていなくても、確信が持てなくても構わないので、
その時点で最も可能性が高いと思う解答を常に1つ返してください。

使用するLLMプロバイダと モデルは config/config.yml で切り替えられます:
  - API系: openai / google / anthropic(内部は LangChain の init_chat_model で一元化)
  - ローカル: ollama(OpenAI互換)/ huggingface(transformers を GPU/CPU で直接実行)
プロンプトも config/config.yml の prompt.system で管理します。
APIキーは config/.env に設定します。
呼び出しは毎回独立で、会話履歴は持ちません(前の回答が次を汚染しないように)。
回答が正解かどうかの自動判定は行いません。
"""

from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable

from config_loader import load_config

# API系・ollama は LangChain のチャットモデルで扱う。
# config.yml の llm.type と LangChain の model_provider の対応。
_CHAT_PROVIDER_MAP = {
    "openai": "openai",
    "google": "google_genai",
    "anthropic": "anthropic",
    "ollama": "ollama",
}

_chain = None


def _build_chat_chain(llm_type: str, params: Dict[str, Any]) -> Runnable:
    """API系 / ollama 用。messages を受け取り文字列を返す Runnable。"""
    from langchain.chat_models import init_chat_model

    model = params.pop("model", None)
    chat = init_chat_model(model, model_provider=_CHAT_PROVIDER_MAP[llm_type], **params)
    return chat | StrOutputParser()


def _build_huggingface_chain(params: Dict[str, Any]) -> Runnable:
    """HuggingFace ローカル用。transformers のモデルを GPU/CPU で直接実行する。

    Colab 等で GPU を使いたい場合は config.yml で device: 0(GPUのcuda:0)を指定します。
    CPU の場合は device: -1。langchain-huggingface / transformers / torch が必要です。
    """
    from langchain_core.runnables import RunnableLambda
    from langchain_huggingface import HuggingFacePipeline

    pipeline_kwargs: Dict[str, Any] = {
        "max_new_tokens": params.get("max_new_tokens", 64),
        "return_full_text": False,  # 入力プロンプトを出力に含めない
    }
    if params.get("temperature") is not None:
        pipeline_kwargs["temperature"] = params["temperature"]
        pipeline_kwargs["do_sample"] = True

    llm = HuggingFacePipeline.from_model_id(
        model_id=params.get("model", "gpt2"),
        task="text-generation",
        device=params.get("device", -1),  # -1: CPU / 0: GPU(cuda:0)
        pipeline_kwargs=pipeline_kwargs,
    )

    # HuggingFacePipeline は文字列を受け取るので、messages を1つのプロンプトに連結する。
    def _messages_to_prompt(messages) -> str:
        return "\n\n".join(m.content for m in messages)

    return RunnableLambda(_messages_to_prompt) | llm | StrOutputParser()


def _build_chain() -> Runnable:
    config = load_config()
    llm_type = (config.get("llm", {}).get("type") or "openai").lower()

    # プロバイダブロックの設定を LangChain 側の引数として渡す。空値は除外する。
    params = {k: v for k, v in (config.get(llm_type) or {}).items() if v not in (None, "")}

    if llm_type == "huggingface":
        return _build_huggingface_chain(params)
    if llm_type in _CHAT_PROVIDER_MAP:
        return _build_chat_chain(llm_type, params)

    supported = list(_CHAT_PROVIDER_MAP) + ["huggingface"]
    raise ValueError(
        f"未対応のプロバイダです: '{llm_type}'。"
        f"config.yml の llm.type には次のいずれかを指定してください: {', '.join(supported)}"
    )


def _get_chain() -> Runnable:
    global _chain
    if _chain is None:
        _chain = _build_chain()
    return _chain


def predict_answer(partial_question: str) -> Optional[str]:
    """
    Args:
        partial_question: これまでに読み上げられた問題文の断片。

    Returns:
        その時点で最も可能性が高いと思う解答(常に何か返します)。
    """
    # 毎回 system + user だけを渡す単発呼び出し(履歴なし)。
    system_prompt = load_config()["prompt"]["system"]
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=partial_question),
    ]
    return _get_chain().invoke(messages).strip()
