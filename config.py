"""配置文件 - 澳大利亚房贷AI助手
针对GitHub开源和Streamlit Cloud部署优化
默认使用OpenAI，可选启用其他提供商
"""

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# 核心API配置
# =============================================================================

# OpenAI配置（主要提供商）
OPENAI_API_KEY_VAR = "OPENAI_API_KEY"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

# 默认模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")

# =============================================================================
# 可选功能配置
# =============================================================================

# 网络搜索配置
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # Google Serper API密钥（可选）

# RAG功能配置（归档状态，保留接口）
def _as_bool(val: str | None, default: bool = False) -> bool:
    """环境变量布尔值转换"""
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}

RAG_ENABLED = _as_bool(os.getenv("RAG_ENABLED"), False)
try:
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))
except ValueError:
    RAG_TOP_K = 3

# 知识库配置（归档状态）
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


def validate_environment() -> str:
    """Quick environment validation for deployment checks."""
    missing = []
    if not os.getenv(OPENAI_API_KEY_VAR):
        missing.append(OPENAI_API_KEY_VAR)
    msg = []
    if missing:
        msg.append("Missing: " + ", ".join(missing))
    else:
        msg.append("OPENAI_API_KEY: OK")
    msg.append(f"MODEL_NAME: {MODEL_NAME}")
    return " | ".join(msg)

# =============================================================================
# 部署环境检测
# =============================================================================

def is_streamlit_cloud():
    """检测是否运行在Streamlit Cloud环境"""
    return any([
        os.getenv("STREAMLIT_SHARING"),
        os.getenv("STREAMLIT_CLOUD"),
        "streamlit.app" in os.getenv("HOSTNAME", "")
    ])

def get_required_env_vars():
    """获取必需的环境变量列表"""
    return [
        "OPENAI_API_KEY"
    ]

def validate_environment():
    """验证环境配置"""
    missing_vars = []
    for var in get_required_env_vars():
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

# Knowledge base settings
CHROMA_DIR = os.getenv("CHROMA_DIR", "data/chroma")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
