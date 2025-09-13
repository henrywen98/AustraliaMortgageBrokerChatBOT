import streamlit as st
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.broker_logic import AustralianMortgageBroker
from config import MODEL_NAME, RAG_ENABLED, RAG_TOP_K

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="澳大利亚抵押贷款经纪人助手",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
def initialize_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "broker" not in st.session_state:
        st.session_state.broker = AustralianMortgageBroker()
    if "language" not in st.session_state:
        st.session_state.language = "中文"
    if "current_model" not in st.session_state:
        st.session_state.current_model = MODEL_NAME
    if "last_error" not in st.session_state:
        st.session_state.last_error = None


def main():
    initialize_session_state()
    
    # 标题
    st.title("🏦 澳大利亚抵押贷款经纪人助手")
    st.markdown("专业的房贷咨询AI助手（支持中英文，默认中文）")
    
    # 侧边栏配置
    with st.sidebar:
        st.title("⚙️ 设置")
        st.subheader("🔑 当前模型")
        st.info(f"使用模型：{MODEL_NAME}")

        # 语言切换
        st.subheader("🌏 语言设置")
        st.session_state.language = st.selectbox("回答语言 / Answer Language", ["中文", "English"], index=0)

        # RAG 信息
        st.subheader("📚 检索增强（RAG）")
        st.caption("当前为预留插槽：默认关闭，可在 .env 配置")
        st.write(f"启用：{'是' if RAG_ENABLED else '否'}，Top-K：{RAG_TOP_K}")

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

    # 显示对话历史
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        ts = message.get("ts")
        avatar = "👤" if role == "user" else "🏦"
        with st.chat_message(role, avatar=avatar):
            st.markdown(message["content"])
            if ts:
                st.markdown(f"<div class='chat-ts'>{ts}</div>", unsafe_allow_html=True)
    
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
            with st.spinner("正在思考 / Thinking ..."):
                try:
                    response = st.session_state.broker.generate_response(
                        prompt,
                        language=st.session_state.language,
                        mode="simple",
                        model=st.session_state.current_model
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
