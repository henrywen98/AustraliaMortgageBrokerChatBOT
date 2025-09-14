from utils.unified_client import UnifiedAIClient
from pathlib import Path
from typing import List, Dict, Any
import datetime as _dt
from config import MODEL_NAME


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
            "If the user input is in Chinese, first internally translate it to English for reasoning and web search; do not display the translation; only output the final answer in Simplified Chinese.",
            "When presenting numbers: include units (e.g., AUD $), use thousands separators, and keep precision consistent.",
            "For mortgage calculations, define terms clearly: deposit (首付), loan amount (贷款额), interest rate (利率), term (年限).",
            "If deposit is given as a percentage, loan amount = property price − (property price × deposit rate). If deposit is given as an amount, loan amount = property price − deposit. If applicable, deduct eligible government grants from loan amount and explain assumptions.",
            "Validate consistency: if you compute monthly repayment, cross-check with the standard amortization formula and ensure text and numbers match.",
            "Prefer clear text formulas and concise steps; if using math notation, keep it simple (e.g., $$...$$) and avoid raw LaTeX code blocks.",
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
        # 内置网络搜索由模型侧（Responses API tools）处理；无需本地搜索客户端

    # 提供商固定为 OpenAI，此处无需名称映射

    def test_provider_connection(self):
        return self.api_client.test_connection()

    def generate_response(self, user_input: str, reasoning: bool = False, use_web_search: bool = False, **kwargs) -> str:
        """生成AI回复。仅推理模式展示“推理过程”，普通模式仅“结论”。"""

        # 构建系统提示（英文提示 + 简体中文输出规则）
        system_prompt = _load_prompt(reasoning=reasoning)

        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话（最近5轮）
        for msg in self.conversation_history[-10:]:
            messages.append(msg)
        
        # 添加当前用户输入（直接传递给模型；模型侧处理翻译/搜索）
        messages.append({"role": "user", "content": user_input})
        
        try:
            # 生成回复
            response = self.api_client.generate_response(
                messages=messages,
                max_tokens=1500,
                use_web_search=use_web_search,
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
            # 参考来源由模型在开启搜索时自行在正文中引用（例如“参考资料/References”）
            return content
            
        except Exception as e:
            return f"生成回复时出现错误: {str(e)}"

    # 内置搜索由模型处理；此处不再提供翻译或外部搜索辅助
