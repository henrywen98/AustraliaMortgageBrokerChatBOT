import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from utils.broker_logic import AustralianMortgageBroker
from config import MODEL_NAME, validate_environment, is_streamlit_cloud

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


def main():
    # 首先检查环境配置
    check_environment()
    
    # 初始化会话状态
    initialize_session_state()
    
    # 添加自定义CSS样式
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
    
    # 优化标题显示 - 智能响应式设计
    st.markdown("""
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
            专业的房贷咨询AI助手 | 支持中英文 | 可选网页搜索
        </p>
    </div>
    
    <style>
    @media (max-width: 768px) {
        .desktop-title { display: none !important; }
        .mobile-title { display: inline !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.title("⚙️ 设置")

        # 显示当前模型信息（只读）
        current_model = getattr(st.session_state.broker.api_client, 'model', MODEL_NAME)
        st.info(f"当前模型：{current_model}")

        # 对话选项（统一放置在侧边栏）
        st.subheader("对话选项")
        st.session_state.use_web_search = st.toggle(
            "🌐 启用网络搜索",
            value=st.session_state.use_web_search,
            help="默认关闭。开启后将搜索最新信息并附带引用链接。",
        )
        st.session_state.reasoning_mode = st.toggle(
            "🧠 推理模式",
            value=st.session_state.reasoning_mode,
            help="开启后，回答将包含‘推理过程’与‘结论’两部分。",
        )

        # （RAG UI 已移除；功能接口保留以便未来启用）

        # 健康检查按钮
        if st.button("🔍 测试连接 / Test Connection"):
            ok = st.session_state.broker.test_provider_connection()
            if ok:
                st.success("模型调用成功✔️")
            else:
                st.error("连接或调用失败，请检查网络 / API Key")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 清除对话历史"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("↩️ 撤销上一轮"):
                if len(st.session_state.messages) >= 2:
                    st.session_state.messages = st.session_state.messages[:-2]
                    st.rerun()

        # 导出对话
        if st.session_state.messages:
            st.subheader("📥 导出对话")
            export_json = json.dumps(st.session_state.messages, ensure_ascii=False, indent=2)
            st.download_button(
                label="下载 JSON",
                data=export_json.encode("utf-8"),
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

        st.markdown("---")
        st.markdown("""
        **关于本应用 / About**

        澳大利亚房贷专业AI助手
        - 🏦 专业房贷知识
        - 💬 多轮对话
        - 🌏 双语输出 (ZH / EN)
        - 🤖 AI驱动分析
        """)
    
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
            st.markdown(message["content"])
            if ts:
                st.markdown(f"<div class='chat-ts'>{ts}</div>", unsafe_allow_html=True)
    
    # 对话框下方设置（已迁移至侧边栏，这里移除）

    # 用户输入
    if prompt := st.chat_input("请输入您的房贷相关问题（支持中文/English）…"):
        # 添加用户消息
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append({"role": "user", "content": prompt, "ts": now_ts})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            st.markdown(f"<div class='chat-ts'>{now_ts}</div>", unsafe_allow_html=True)
        
        # 生成AI回复
        with st.chat_message("assistant", avatar="🏦"):
            search_indicator = "🌐 " if st.session_state.get("use_web_search", False) else ""
            with st.spinner(f"{search_indicator}正在思考 / Thinking ..."):
                try:
                    # 根据是否启用网络搜索选择不同的回复方法
                    if st.session_state.get("use_web_search", False):
                        response = st.session_state.broker.generate_response_with_search(
                            prompt,
                            search_enabled=True,
                            num_results=3,
                            reasoning=st.session_state.reasoning_mode,
                        )
                    else:
                        response = st.session_state.broker.generate_response(
                            prompt,
                            reasoning=st.session_state.reasoning_mode,
                        )
                    now_ts2 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.markdown(response)
                    st.markdown(f"<div class='chat-ts'>{now_ts2}</div>", unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": response, "ts": now_ts2})
                except Exception as e:
                    error_msg = f"抱歉，生成回复时出现错误 / Error: {str(e)}"
                    st.session_state.last_error = str(e)
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ts": datetime.now().strftime('%Y-%m-%d %H:%M:%S')})


if __name__ == "__main__":
    main()
