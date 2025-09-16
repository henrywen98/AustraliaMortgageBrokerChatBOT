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

# Azure OpenAI 配置
AZURE_OPENAI_API_KEY_VAR = "AZURE_OPENAI_API_KEY"
AZURE_OPENAI_ENDPOINT_VAR = "AZURE_OPENAI_ENDPOINT"
AZURE_OPENAI_DEPLOYMENT_VAR = "AZURE_OPENAI_DEPLOYMENT"

# 默认模型配置
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5-mini")
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")

# =============================================================================
# 可选功能配置
# =============================================================================

# 外部网络搜索与 RAG 配置已移除：gpt-5-mini 使用模型内置 Web Search 工具

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
    provider = (MODEL_PROVIDER or "openai").strip().lower()
    if provider == "azure":
        required = [
            AZURE_OPENAI_API_KEY_VAR,
            AZURE_OPENAI_ENDPOINT_VAR,
        ]
        return required
    return [
        OPENAI_API_KEY_VAR
    ]

def validate_environment():
    """验证环境配置"""
    missing_vars = []
    for var in get_required_env_vars():
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

# 无知识库设置（已移除）
