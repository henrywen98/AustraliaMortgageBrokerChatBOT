# 公司档案馆（Chroma 版 MVP）

简短说明：本项目把公司内部文档（PDF/TXT）索引到 Chroma，支持自然语言检索并返回带引用的回答。

快速开始

1) 安装依赖

```bash
python -m pip install -r requirements.txt
```

2) 配置环境变量

```bash
export OPENAI_API_KEY=sk-...
export CHROMA_DISABLE_TELEMETRY=1
```

3) 启动 Web UI

```bash
streamlit run streamlit_app.py
```

常用运维命令

- 手动同步（扫描 `data/storage/` 并 ingest 新文件）：

```bash
python -c "from backend import sync; print(sync.sync_library_once())"
```

## 备份与恢复

- 请在执行删除或重建索引前备份 `data/archive.db` 与 `data/chroma/`。

## 变更摘要

- 简化并实现了后端核心模块：`backend/db.py`, `backend/ingest.py`, `backend/sync.py`，使得本仓库可以在本地运行并同步 `storage/` 下的文件到 Chroma。
