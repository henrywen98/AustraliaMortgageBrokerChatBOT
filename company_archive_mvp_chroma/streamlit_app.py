import os
# Ensure Chroma telemetry disabled before any chroma/chromadb import
os.environ.setdefault("CHROMA_DISABLE_TELEMETRY", "1")
import streamlit as st
from dotenv import load_dotenv

from backend.retrieve import search_chunks
from backend.llm import answer
from backend import db
# from backend import sync
# from backend.sync import scan_library

load_dotenv()
st.set_page_config(page_title="公司档案馆（Chroma 版 MVP）", layout="wide")
st.title("🏛️ 公司档案馆 + AI 问答（Chroma 版）")

# Initialize DB
db.init_db()

# Run a startup sync only once per Streamlit session to avoid repeated scans on every rerun
# if 'library_synced' not in st.session_state:
#     st.session_state['library_synced'] = False
#
# if not st.session_state['library_synced']:
#     try:
#         sync.sync_library_once()
#     except Exception:
#         pass
#     st.session_state['library_synced'] = True

# Load documents for display
docs = db.get_documents(limit=200)

with st.sidebar:
    st.markdown('### 已导入的文档')
    if not docs:
        st.markdown('_（未导入文档）_')
    else:
        for d in docs[:200]:
            title = d.get('title') or os.path.basename(d.get('path',''))
            pages = d.get('pages') or 0
            uploader = d.get('uploader') or 'local'
            with st.expander(f"{title} ({pages} 页) — {uploader}"):
                st.write(f"路径: {d.get('path')}")
                st.write(f"上传时间: {d.get('created_at')}")
                st.write(f"状态: {d.get('status','ok')}")
st.subheader("自然语言提问（带引用）")
q = st.text_input("请输入你的问题：", placeholder="例如：Suncorp HPP 投资房的最高LVR是多少？")

def render_answer(text: str):
    """Render answer text in Streamlit, attempting to render LaTeX blocks if present.

    We split on $...$ or $$...$$ blocks. For safety we avoid executing any code;
    Render math-like blocks as code/markdown to avoid Streamlit's LaTeX styling which
    produced odd centered/large fragments in the UI. This keeps layout consistent.
    """
    import re
    parts = re.split(r"(\$\$.*?\$\$|\$.*?\$)", text, flags=re.S)
    for part in parts:
        if not part:
            continue
        # Math-like block ($$...$$)
        if part.startswith("$$") and part.endswith("$$"):
            expr = part[2:-2].strip()
            # If the block is tiny (looks like a stray fragment), render inline; else render as code block
            if len(expr) < 40 and re.match(r"^[\d\s\-:.,]+$", expr):
                st.markdown(expr)
            else:
                st.code(expr, language='latex')
        # Inline math ($...$)
        elif part.startswith("$") and part.endswith("$"):
            expr = part[1:-1].strip()
            if len(expr) < 40 and re.match(r"^[\d\s\-:.,]+$", expr):
                st.markdown(expr)
            else:
                # Show inline math as inline code to avoid LaTeX rendering
                st.markdown(f"`{expr}`")
        else:
            # Render normal text/markdown; preserve newlines
            st.markdown(part)

if st.button("检索并回答", type="primary") and q.strip():
    progress = st.progress(0)
    try:
        # Retrieval step
        with st.spinner("正在检索相关片段..."):
            chunks = search_chunks(q, top_k=6)
            progress.progress(40)

        # Answer generation step
        with st.spinner("正在生成回答（调用模型）..."):
            ans = answer(q, chunks)
            progress.progress(100)

        st.markdown("### 💡 回答")
        render_answer(ans)

        with st.expander("查看命中片段（用于核对）"):
            for ch in chunks:
                st.markdown(f"**{ch['title']} | p.{ch['page_from']}-{ch['page_to']}**")
                st.caption((ch['text'] or '')[:1000] + ("..." if ch.get('text') and len(ch['text']) > 1000 else ""))
    except Exception as e:
        progress.progress(0)
        st.error(f"检索或生成过程中出错: {e}")
