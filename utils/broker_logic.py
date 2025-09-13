from utils.api_client import OpenAIClient
from utils.knowledge_base import KnowledgeBase
from pathlib import Path
from typing import List, Dict, Any
import textwrap
import datetime as _dt
from config import RAG_ENABLED, RAG_TOP_K


def _load_prompt(language: str) -> str:
    """Load system prompt text from prompts/ directory by language.
    Defaults to Chinese prompt if specific language file is missing.
    """
    base = Path(__file__).resolve().parents[1] / "prompts"
    if language == "English":
        path = base / "broker_system.en.md"
    else:
        path = base / "broker_system.zh.md"

    if path.exists():
        return path.read_text(encoding="utf-8").strip()

    # Fallback minimal prompt (Chinese)
    return (
        "你是澳大利亚房贷中介AI助手，只能用中文回答。"
        "请严格按以下结构输出：先‘推理过程（简要要点）’，后‘结论’。"
    )


class SimpleRAG:
    """ChromaDB-backed retrieval used as optional RAG component."""

    def __init__(self, enabled: bool = False, top_k: int = 3):
        self.enabled = enabled
        self.top_k = max(1, top_k)
        self.kb: KnowledgeBase | None = None
        if self.enabled:
            try:
                self.kb = KnowledgeBase()
            except Exception:
                self.kb = None

    def retrieve(self, query: str, k: int | None = None) -> List[Dict[str, Any]]:
        if not self.enabled or not self.kb:
            return []
        return self.kb.search(query, top_k=k or self.top_k)

    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            return ""
        lines = ["检索到的可能相关资料（仅供参考）："]
        for i, ch in enumerate(chunks, 1):
            src = ch.get("source") or "unknown"
            content = (ch.get("content") or "").strip()
            content = textwrap.shorten(content, width=600, placeholder=" …")
            lines.append(f"[{i}] 来源: {src}\n{content}")
        lines.append(
            "请优先参考上述资料回答，引用时请用 [序号] 标注来源；在不确定时提示核验，不得编造未证实的利率或政策。"
        )
        return "\n\n".join(lines)

    def format_sources(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieval results as numbered source list."""
        if not chunks:
            return ""
        lines = []
        for i, ch in enumerate(chunks, 1):
            src = ch.get("source") or "unknown"
            lines.append(f"[{i}] {src}")
        return "\n".join(lines)


class AustralianMortgageBroker:
    """澳大利亚抵押贷款经纪人AI助手（系统提示外置，结构化输出）"""

    def __init__(self):
        self.api_client = OpenAIClient()
        self.conversation_history = []
        self.rag = SimpleRAG(enabled=RAG_ENABLED, top_k=RAG_TOP_K)
    
    # 单模型实现，这些方法不再需要，保留兼容占位
    def get_available_providers(self):
        return ["openai"]

    def set_provider(self, provider: str):
        return True

    def get_provider_name(self, provider: str):
        return "OpenAI"

    def test_provider_connection(self):
        return self.api_client.test_connection()
    
    def generate_response(self, user_input: str, language: str = "中文", mode: str = "simple", **kwargs) -> str:
        """生成AI回复（结构化：先“推理过程（简要要点）”，后“结论”）。
        System Prompt 外置，默认中文；若传入 English 则加载英文提示词文件。
        """

        # 构建系统提示（从文件加载，便于维护）
        system_prompt = _load_prompt(language)

        # 可选：RAG 检索上下文（不影响原始逻辑，默认关闭）
        rag_context = ""
        rag_chunks: List[Dict[str, Any]] = []
        if self.rag.enabled:
            try:
                rag_chunks = self.rag.retrieve(user_input, k=self.rag.top_k)
                rag_context = self.rag.format_context(rag_chunks)
            except Exception:
                rag_context = ""
                rag_chunks = []

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        if rag_context:
            messages.append({"role": "system", "content": rag_context})
        
        # 添加历史对话（最近5轮）
        for msg in self.conversation_history[-10:]:
            messages.append(msg)
        
        # 添加当前用户输入（附加时间戳在内部记录，避免污染提示）
        messages.append({"role": "user", "content": user_input})
        
        try:
            # 生成回复
            response = self.api_client.generate_response(
                messages=messages,
                max_tokens=1500
            )
            
            # 更新对话历史（带时间戳）
            ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.conversation_history.append({"role": "user", "content": user_input, "ts": ts})
            self.conversation_history.append({"role": "assistant", "content": response, "ts": ts})
            
            # 保持历史长度在合理范围内
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # 保障中文与结构：若模型未按结构返回，做轻量兜底格式化
            content = response.strip()
            if "推理过程" not in content or "结论" not in content:
                content = (
                    "推理过程（简要要点）：\n"
                    "- 根据提问内容进行政策与流程匹配\n"
                    "- 结合贷款目的、身份、收入与负债等\n"
                    "- 参考各贷方公开政策并提示差异\n"
                    "- 如信息不足，建议补充关键细节\n"
                    f"\n结论：\n{content}"
                )
            if rag_chunks:
                sources_text = self.rag.format_sources(rag_chunks)
                if sources_text:
                    content = f"{content}\n\n参考来源：\n{sources_text}"
            return content
            
        except Exception as e:
            error_msg = f"生成回复时出现错误: {str(e)}"
            if language == "English":
                error_msg = f"Error generating response: {str(e)}"
            return error_msg
