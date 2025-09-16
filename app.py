import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.broker_logic import AustralianMortgageBroker
from config import MODEL_NAME, validate_environment, is_streamlit_cloud
import re

# 加载环境变量
load_dotenv()

# 早期环境验证
def check_environment():
    """检查环境配置并显示必要的错误信息"""
    missing_vars = validate_environment()
    
    if missing_vars:
        st.error("🔑 **配置错误**: 缺少必需的环境变量")
        
        if is_streamlit_cloud():
            st.markdown("""
            **Streamlit Cloud 部署检查清单**:
            1. 确保在应用设置的 "Secrets" 中配置了以下变量：
            """)
            for var in missing_vars:
                st.code(f'{var} = "your_{var.lower()}_here"')
            
            st.markdown("""
            2. 保存 Secrets 配置后重新部署应用
            3. 如需帮助，请查看 [部署文档](https://github.com/henrywen98/AustraliaMortgageBrokerChatBOT#streamlit-cloud-部署推荐)
            """)
        else:
            st.markdown("""
            **本地开发检查清单**:
            1. 确保项目根目录存在 `.env` 文件
            2. 在 `.env` 文件中配置以下变量：
            """)
            for var in missing_vars:
                st.code(f'{var}=your_{var.lower()}_here')
            
            st.markdown("""
            3. 如果没有 `.env` 文件，请复制 `.env.example` 并重命名
            ```bash
            cp .env.example .env
            ```
            """)
        
        st.stop()  # 停止应用继续执行

# 页面配置
st.set_page_config(
    page_title="澳洲房贷AI助手",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
def initialize_session_state():
    """快速初始化会话状态（不初始化重量级组件）"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "broker" not in st.session_state:
        # 快速创建broker实例，数据库组件将在首次使用时懒加载
        with st.spinner("🚀 正在初始化AI助手..."):
            st.session_state.broker = AustralianMortgageBroker()
    if "current_model" not in st.session_state:
        st.session_state.current_model = MODEL_NAME
    if "use_web_search" not in st.session_state:
        st.session_state.use_web_search = False
    if "reasoning_mode" not in st.session_state:
        st.session_state.reasoning_mode = False
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "ui_lang" not in st.session_state:
        st.session_state.ui_lang = "zh"  # zh or en


def _t(key: str) -> str:
    """Simple i18n for UI labels."""
    zh = {
        "settings": "⚙️ 设置",
        "current_model": "当前模型",
        "conversation_options": "对话选项",
        "toggle_search": "🌐 启用网络搜索",
        "toggle_search_help": "默认关闭。开启后将搜索最新信息并附带引用链接。",
        "toggle_reasoning": "🧠 推理模式",
        "toggle_reasoning_help": "开启后，回答将包含‘推理过程’与‘结论’两部分。",
        "test_conn": "🔍 测试连接 / Test Connection",
        "clear_history": "🗑️ 清除对话历史",
        "undo": "↩️ 撤销上一轮",
        "export": "📥 导出对话",
        "download_json": "下载 JSON",
        "about_title": "关于本应用 / About",
        "about_lines": "澳大利亚房贷专业AI助手\n- 🏦 专业房贷知识\n- 💬 多轮对话\n- 🌏 双语输出 (ZH / EN)\n- 🤖 AI驱动分析",
        "mode_search_on": "模式：模型 + 网络搜索",
        "mode_search_off": "模式：仅模型",
        "reasoning_on": "推理模式：已开启",
        "reasoning_off": "推理模式：关闭",
        "ui_lang": "界面语言 / UI Language",
        "lang_zh": "中文",
        "lang_en": "English",
        "help": "🆘 使用帮助 / Help",
        "help_text": "- 侧边栏可开启网络搜索与推理模式\n- 搜索开启时将引用权威来源（RBA/政府/银行）\n- 公式自动渲染，避免出现原始 LaTeX 代码\n- 如需英文界面，请切换 UI Language",
        "chat_placeholder": "请输入您的房贷相关问题（支持中文/English）…",
        "search_sources": "🌐 网络搜索来源：",
        "unknown_title": "未知标题",
        "unknown_link": "未知链接",
    }
    en = {
        "settings": "⚙️ Settings",
        "current_model": "Current model",
        "conversation_options": "Conversation Options",
        "toggle_search": "🌐 Enable Web Search",
        "toggle_search_help": "Off by default. When on, fetch recent info with citations.",
        "toggle_reasoning": "🧠 Reasoning Mode",
        "toggle_reasoning_help": "When on, show 'Reasoning' and 'Conclusion'.",
        "test_conn": "🔍 Test Connection",
        "clear_history": "🗑️ Clear History",
        "undo": "↩️ Undo Last",
        "export": "📥 Export Chat",
        "download_json": "Download JSON",
        "about_title": "About",
        "about_lines": "Australian Mortgage Broker AI\n- 🏦 Mortgage expertise\n- 💬 Multi-turn chat\n- 🌏 Bilingual UI (ZH / EN)\n- 🤖 AI-powered analysis",
        "mode_search_on": "Mode: Model + Web Search",
        "mode_search_off": "Mode: Model only",
        "reasoning_on": "Reasoning: ON",
        "reasoning_off": "Reasoning: OFF",
        "ui_lang": "UI Language",
        "lang_zh": "中文",
        "lang_en": "English",
        "help": "🆘 Help",
        "help_text": "- Use sidebar to toggle search and reasoning\n- With search on, cites authoritative AU sources (RBA/gov/banks)\n- Formulas are auto-rendered (no raw LaTeX)\n- Switch UI Language for English labels",
        "chat_placeholder": "Ask your mortgage question (中文/English)…",
        "search_sources": "🌐 Sources:",
        "unknown_title": "Untitled",
        "unknown_link": "Unknown link",
    }
    lang = st.session_state.get("ui_lang", "zh")
    return (en if lang == "en" else zh).get(key, key)


def render_rich_text(text: str):
    """Render Markdown with basic LaTeX support: ```latex``` blocks and $$...$$ blocks.
    Falls back to markdown for other content.
    """
    if not text:
        return

    content = str(text)

    # Handle fenced latex blocks: ```latex ... ```
    parts = []
    idx = 0
    fence_pat = re.compile(r"```latex\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    for m in fence_pat.finditer(content):
        if m.start() > idx:
            parts.append(("md", content[idx:m.start()]))
        parts.append(("latex", m.group(1).strip()))
        idx = m.end()
    if idx < len(content):
        parts.append(("md", content[idx:]))

    # Now split md parts further by $$...$$ blocks
    final_parts = []
    for kind, chunk in parts:
        if kind == "latex":
            final_parts.append(("latex", chunk))
            continue
        # split by $$...$$
        s = chunk
        pos = 0
        while True:
            start = s.find("$$", pos)
            if start == -1:
                final_parts.append(("md", s[pos:]))
                break
            end = s.find("$$", start + 2)
            if end == -1:
                # unmatched, treat as md
                final_parts.append(("md", s[pos:]))
                break
            if start > pos:
                final_parts.append(("md", s[pos:start]))
            expr = s[start + 2 : end].strip()
            final_parts.append(("latex", expr))
            pos = end + 2

    # Render
    for kind, chunk in final_parts:
        if not chunk:
            continue
        if kind == "latex":
            try:
                st.latex(chunk)
            except Exception:
                st.markdown(f"``{chunk}``")
        else:
            # Replace '$' with 'AUD' to avoid inline-math rendering issues
            safe_chunk = chunk.replace("$", "AUD")
            st.markdown(safe_chunk)


def main():
    # 首先检查环境配置
    check_environment()
    
    # 初始化会话状态
    initialize_session_state()

    provider = getattr(getattr(st.session_state, "broker", None), "api_client", None)
    provider_name = getattr(provider, "provider", "openai") if provider else "openai"
    if provider_name == "azure":
        # 强制关闭 Azure 当前不支持的功能
        st.session_state.use_web_search = False
        st.session_state.reasoning_mode = False
    
    # 添加自定义CSS样式
    subtitle = "专业的房贷咨询AI助手 | 支持中英文 | 可选网页搜索" if provider_name != "azure" else "专业的房贷咨询AI助手 | 支持中英文"

    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* 优化移动端显示 */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    
    /* 隐藏Streamlit默认的菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    if provider_name == "azure":
        st.markdown(
            """
            <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
            </style>
            """,
            unsafe_allow_html=True,
        )
    
    # 优化标题显示 - 智能响应式设计
    st.markdown(
        f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 class="main-title" style="
            color: #1f77b4; 
            margin-bottom: 0.5rem; 
            font-weight: 600;
            font-size: clamp(1.2rem, 3.5vw, 2.5rem); 
            line-height: 1.2;
            word-break: keep-all;
            overflow-wrap: break-word;
        ">
            <span class="desktop-title">🏦 澳大利亚抵押贷款经纪人AI助手</span>
            <span class="mobile-title" style="display: none;">🏦 澳洲房贷AI助手</span>
        </h1>
        <p style="
            color: #666; 
            font-size: clamp(0.8rem, 2.2vw, 1.1rem); 
            margin-top: 0; 
            line-height: 1.4;
            word-break: keep-all;
        ">
            {subtitle}
        </p>
    </div>
    
    <style>
    @media (max-width: 768px) {{
        .desktop-title {{ display: none !important; }}
        .mobile-title {{ display: inline !important; }}
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )
    
    # 侧边栏配置（OpenAI 模式可用）
    if provider_name != "azure":
        with st.sidebar:
            st.title(_t("settings"))

            # UI language selector
            st.selectbox(
                _t("ui_lang"),
                options=["zh", "en"],
                format_func=lambda v: _t("lang_zh") if v == "zh" else _t("lang_en"),
                key="ui_lang",
            )

            # 显示当前模型信息（只读）
            current_model = getattr(st.session_state.broker.api_client, 'model', MODEL_NAME)
            st.info(f"{_t('current_model')}：{current_model}")

            # 对话选项（统一放置在侧边栏）
            st.subheader(_t("conversation_options"))
            st.session_state.use_web_search = st.toggle(
                _t("toggle_search"),
                value=st.session_state.use_web_search,
                help=_t("toggle_search_help"),
            )
            st.session_state.reasoning_mode = st.toggle(
                _t("toggle_reasoning"),
                value=st.session_state.reasoning_mode,
                help=_t("toggle_reasoning_help"),
            )

            # Status indicators
            if st.session_state.use_web_search:
                st.success(_t("mode_search_on"))
            else:
                st.info(_t("mode_search_off"))
            st.caption(_t("reasoning_on") if st.session_state.reasoning_mode else _t("reasoning_off"))

            # 健康检查按钮
            if st.button(_t("test_conn")):
                ok = st.session_state.broker.test_provider_connection()
                if ok:
                    st.success("模型调用成功✔️" if st.session_state.ui_lang=="zh" else "API connection OK ✔️")
                else:
                    st.error("连接或调用失败，请检查网络 / API Key" if st.session_state.ui_lang=="zh" else "Connection or call failed. Check network/API key.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(_t("clear_history")):
                    st.session_state.messages = []
                    st.rerun()
            with col2:
                if st.button(_t("undo")):
                    if len(st.session_state.messages) >= 2:
                        st.session_state.messages = st.session_state.messages[:-2]
                        st.rerun()

            # 导出对话
            if st.session_state.messages:
                st.subheader(_t("export"))
                export_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
                st.download_button(
                    label=_t("download_json"),
                    data=export_json.encode("utf-8"),
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            st.markdown("---")
            st.markdown(f"**{_t('about_title')}**")
            st.markdown(_t("about_lines"))

            with st.expander(_t("help")):
                st.markdown(_t("help_text"))
    else:
        st.session_state.ui_lang = st.session_state.get("ui_lang", "zh")
        st.info("当前使用 Azure OpenAI 部署，已为你启用精简界面。" if st.session_state.ui_lang == "zh" else "Running with Azure OpenAI deployment; sidebar controls are hidden.")
    
    # 轻量样式优化：更紧凑的聊天区域
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 1.5rem;}
        .stChatMessage {max-width: 900px; margin-left: auto; margin-right: auto;}
        .stChatMessage .stMarkdown p {margin-bottom: 0.4rem;}
        .chat-ts {font-size: 0.75rem; color: #888; margin-top: 0.25rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 聊天区域下方的快捷设置（紧邻输入框）

    # 显示对话历史
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        ts = message.get("ts")
        avatar = "👤" if role == "user" else "🏦"
        with st.chat_message(role, avatar=avatar):
            if role == "assistant":
                render_rich_text(message["content"])
            else:
                st.markdown(message["content"])
            if ts:
                st.markdown(f"<div class='chat-ts'>{ts}</div>", unsafe_allow_html=True)
    
    # 对话框下方设置（已迁移至侧边栏，这里移除）

    # 用户输入
    if prompt := st.chat_input(_t("chat_placeholder")):
        # 添加用户消息
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": prompt, "ts": now_ts})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.markdown(f"<div class='chat-ts'>{now_ts}</div>", unsafe_allow_html=True)
        
        # 生成AI回复
        with st.chat_message("assistant", avatar="🏦"):
            search_indicator = "🌐 " if st.session_state.get("use_web_search", False) else ""
            thinking_text = (
                f"{search_indicator}正在思考 ..." if st.session_state.ui_lang=="zh" else f"{search_indicator}Thinking ..."
            )
            with st.spinner(thinking_text):
                try:
                    # 统一由模型侧处理（Responses API 工具启用/禁用）
                    response = st.session_state.broker.generate_response(
                        prompt,
                        reasoning=st.session_state.reasoning_mode,
                        use_web_search=st.session_state.get("use_web_search", False),
                    )
                    now_ts2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    render_rich_text(response)
                    st.markdown(f"<div class='chat-ts'>{now_ts2}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response, "ts": now_ts2})
                except Exception as e:
                    error_msg = (
                        f"抱歉，生成回复时出现错误 / Error: {str(e)}" if st.session_state.ui_lang=="zh" else f"Error generating reply: {str(e)}"
                    )
                    st.session_state.last_error = str(e)
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ts": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


if __name__ == "__main__":
    main()
