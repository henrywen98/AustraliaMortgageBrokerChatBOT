from utils.unified_client import UnifiedAIClient
from utils.knowledge_base import KnowledgeBase
from utils.web_search import WebSearchClient, SearchAugmentor
from pathlib import Path
from typing import List, Dict, Any
import textwrap
import datetime as _dt
from config import RAG_ENABLED, RAG_TOP_K, MODEL_NAME


def _load_prompt(reasoning: bool = False) -> str:
    """Load English system prompt, instruct output in Simplified Chinese.
    If input is Chinese, model should internally translate to English for reasoning
    (do not display translation) and then respond in Simplified Chinese.
    """
    base = Path(__file__).resolve().parents[1] / "prompts"
    path = base / "broker_system.en.md"

    def _strip_structure(txt: str) -> str:
        lines = txt.splitlines()
        out = []
        skip = 0
        for i, ln in enumerate(lines):
            if skip:
                skip -= 1
                continue
            if "请严格按以下结构输出" in ln:
                # 跳过提示与后续两行编号说明
                skip = 3
                continue
            if ln.strip().lower().startswith("output strictly in two"):
                skip = 3
                continue
            out.append(ln)
        return "\n".join(out)

    if path.exists():
        txt = path.read_text(encoding="utf-8").strip()
        # Always append unified language/output rules
        rules = [
            "Always produce the final answer in Simplified Chinese.",
            "If the user input is in Chinese, first internally translate it to English for reasoning; do not display the translation; only output the final answer in Simplified Chinese.",
        ]
        if not reasoning:
            txt = _strip_structure(txt)
        txt = f"{txt}\n\n" + "\n".join(rules)
        return txt

    # Fallback minimal prompt (Chinese)
    base = (
        "You are an Australian mortgage broker AI assistant."
        " Always output in Simplified Chinese."
        " If the user input is in Chinese, first internally translate it to English for reasoning; do not display the translation."
    )
    if reasoning:
        base += " Output two sections: ‘推理过程（简要要点）’ and ‘结论’."
    return base


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


def _detect_language(text: str) -> str:
    """极简语言检测：含中文字符则判为中文，否则英文。"""
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return "中文"
    return "English"


class AustralianMortgageBroker:
    """澳大利亚抵押贷款经纪人AI助手（OpenAI + 可选网络搜索）"""

    def __init__(self):
        self.api_client = UnifiedAIClient(model=MODEL_NAME)
        self.conversation_history = []
        self.rag = SimpleRAG(enabled=RAG_ENABLED, top_k=RAG_TOP_K)
        
        # 初始化网络搜索功能
        self.web_search_client = WebSearchClient()
        self.search_augmentor = SearchAugmentor(self.api_client, self.web_search_client)

    # 提供商固定为 OpenAI，此处无需名称映射

    def test_provider_connection(self):
        return self.api_client.test_connection()

    def generate_response(self, user_input: str, reasoning: bool = False, **kwargs) -> str:
        """生成AI回复。仅推理模式展示“推理过程”，普通模式仅“结论”。"""

        # 构建系统提示（英文提示 + 简体中文输出规则）
        system_prompt = _load_prompt(reasoning=reasoning)

        # 统一英文推理输入：若为中文，先翻译为英文，再送模型；输出仍为简体中文
        clean_input = self._translate_for_reasoning_if_needed(user_input)

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
        
        # 添加当前用户输入（英文推理文本；附加时间戳在内部记录，避免污染提示）
        messages.append({"role": "user", "content": clean_input})
        
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
            
            content = response.strip()
            # 仅在推理模式下兜底输出“推理过程”；普通模式不展示推理过程
            if reasoning:
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
            return f"生成回复时出现错误: {str(e)}"

    def generate_response_with_search(self, user_input: str, search_enabled: bool = True, num_results: int = 3, reasoning: bool = False, **kwargs) -> str:
        """生成回复（带网络搜索功能）"""
        try:
            # 为搜索与推理统一英文输入（提高搜索质量，尤其是中文提问）
            english_query = self._translate_for_reasoning_if_needed(user_input)
            # 使用网络搜索增强的回复生成
            response_data = self.search_augmentor.search_and_answer(
                user_query=user_input,
                search_query=english_query,  # 使用英文搜索查询
                search_enabled=search_enabled,
                num_results=num_results,
                reasoning=reasoning,
            )
            
            # 更新对话历史（带时间戳）
            ts = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.conversation_history.append({"role": "user", "content": user_input, "ts": ts})
            self.conversation_history.append({"role": "assistant", "content": response_data['answer'], "ts": ts})
            
            # 保持历史长度在合理范围内
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # 格式化带来源的回复
            content = response_data['answer'].strip()
            
            # 添加搜索来源
            if response_data.get('sources'):
                sources_text = "\n\n🌐 网络搜索来源：\n"
                for i, source in enumerate(response_data['sources'], 1):
                    sources_text += f"{i}. {source.get('title', '未知标题')}\n"
                    sources_text += f"   📍 {source.get('url', '未知链接')}\n"
                    # 从search_results中获取snippet，因为sources中可能没有snippet
                    search_results = response_data.get('search_results', [])
                    if i <= len(search_results) and search_results[i-1].get('snippet'):
                        sources_text += f"   📝 {search_results[i-1]['snippet'][:100]}...\n"
                    sources_text += "\n"
                content = f"{content}\n{sources_text}"
            
            return content
            
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

    # ----------------------------
    # 内部工具：翻译与清理
    # ----------------------------
    def _translate_for_reasoning_if_needed(self, text: str) -> str:
        """若输入含中文字符，则调用轻量翻译生成英文查询/推理文本；否则原样返回。
        使用相同OpenAI客户端，限制较小的max_tokens以减少时延。
        包含金融领域术语映射以提高准确性（如：现金利率→official cash rate）。
        """
        if _detect_language(text) == "中文":
            try:
                messages = [
                    {"role": "system", "content": (
                        "You are a precise translator for Australian finance. "
                        "Translate the user's query to concise English suitable for web search and reasoning. "
                        "Use established terms: 现金利率 -> official cash rate (RBA); 房贷 -> home loan or mortgage; "
                        "浮动利率 -> variable rate; 固定利率 -> fixed rate; 首次购房者/首置 -> first home buyer / FHOG. "
                        "Output English only, no notes or explanations."
                    )},
                    {"role": "user", "content": text},
                ]
                translated = self.api_client.generate_response(messages=messages, max_tokens=80)
                return self._strip_latency_suffix(translated).strip()
            except Exception:
                # 兜底：原文返回（仍可由模型内部翻译）
                return text
        return text

    @staticmethod
    def _strip_latency_suffix(text: str) -> str:
        """移除UnifiedAIClient附加的(延迟 xxms | OpenAI model)后缀"""
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith("(延迟 ")]
        return "\n".join(lines).strip()
