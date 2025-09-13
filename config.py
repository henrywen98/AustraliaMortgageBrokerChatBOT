"""单模型配置（OpenAI Chat Completions）
支持通过 .env 覆盖 MODEL_NAME，并提供 RAG 预留开关。
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY_VAR = "OPENAI_API_KEY"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# 模型名允许 .env 覆盖；默认保持 gpt-5-mini
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-mini")

# RAG 预留开关（默认关闭）
def _as_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}

RAG_ENABLED = _as_bool(os.getenv("RAG_ENABLED"), False)
try:
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
except ValueError:
    RAG_TOP_K = 3
