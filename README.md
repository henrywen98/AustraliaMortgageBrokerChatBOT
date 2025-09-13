# 澳大利亚抵押贷款经纪人AI助手 | Australian Mortgage Broker AI Assistant

一个聚焦澳大利亚房贷咨询场景的简洁 Streamlit 聊天助手，支持中英文，对话上下文记忆，基于单一 OpenAI Chat 模型运行（当前模型：`gpt-5-mini`）。

已完成精简与模块化：
- 移除多提供商 / 多模型 / 示例冗余代码，仅保留稳定的单模型问答；
- 系统 Prompt 外置到 `prompts/`，便于维护与版本化；
- 集成 Chroma+OpenAI Embeddings 的知识库检索（可选开启）；
- 清理无用文件与编译产物，新增 `.gitignore`；
- 修复“测试连接”按钮调用；
- 保持 GPT-5-mini 调用逻辑不变（HTTP Chat Completions，无 temperature，使用 `max_completion_tokens`）。
- UI 微调：头像、气泡间距、时间戳、撤销上一轮、导出对话。

## 📥 新增功能
- 侧边栏上传 PDF 文件自动加入知识库
- 生成回复时引用知识库内容并标注来源

## ✨ 功能概览
- 多轮上下文：保留最近对话（自动截断防膨胀）
- 双语支持：侧边栏切换中文 / English
- 专业领域提示词：内置澳洲房贷经纪人角色设定
- 稳定调用：内置网络重试、模型存在性探测、错误信息优化
- 简单部署：只需设置 `OPENAI_API_KEY` 即可运行

## 🚀 快速开始
### 1. 克隆项目
```
git clone <your-repo-url>
cd AustraliaMortgageBrokerChatBOT
```
### 2. 安装依赖
```
pip install -r requirements.txt
```
### 3. 配置环境变量
创建 `.env`（若不存在）：
```
OPENAI_API_KEY=你的真实key
```
可选：如果想覆盖默认模型（不推荐随意修改）：
```
MODEL_NAME=gpt-5-mini
```
> 代码默认使用 `config.py` 中的 `MODEL_NAME`，`.env` 中的 `MODEL_NAME` 仅作可读性参考。

### 4. 启动
```
streamlit run app.py
```
浏览器访问：http://localhost:8501

## 🧩 代码结构（精简版）
```
├── app.py                         # Streamlit UI & 会话状态（头像/时间戳/导出/撤销）
├── config.py                      # 常量：API 地址 / 模型名
├── prompts/
│   ├── broker_system.zh.md        # 中文系统提示（默认）
│   └── broker_system.en.md        # 英文系统提示（可选）
├── utils/
│   ├── api_client.py              # OpenAI HTTP 调用（重试/探测，无 temperature）
│   └── broker_logic.py            # 对话历史与消息组织（从 prompts 读取，含 RAG 预留）
├── requirements.txt
├── README.md
└── .env (本地自建，不进版控)
```

## 🛠 配置说明
| 项 | 说明 |
|----|------|
| OPENAI_API_KEY | 必填，用于访问 OpenAI 接口 |
| MODEL_NAME | 可选，默认 `gpt-5-mini` |
| 历史长度 | 代码中限制保留最近 20 条消息 |
| 超时 & 重试 | 每次请求最长 60s，最多 3 次指数退避重试 |
| temperature | 不使用（保持与当前接口兼容） |
| max_tokens | 对 gpt-5-mini 实际映射为 `max_completion_tokens` |
| RAG_ENABLED | 可选，默认 `false`（启用知识库检索） |
| RAG_TOP_K | 可选，默认 `3` |
| CHROMA_DIR | 可选，知识库存储目录，默认 `data/chroma` |
| EMBEDDING_MODEL | 可选，默认 `text-embedding-3-small` |

如果你看到 SSL / EOF / 502 等错误，客户端会自动重试；仍失败会在界面显示错误信息。

## 🧠 领域角色（System Prompt）
- 位置：`prompts/broker_system.zh.md`（默认）与 `prompts/broker_system.en.md`（可选）
- 语气：专业、清晰、合规，不夸大收益
- 结构：先“推理过程（简要要点）”，后“结论”

## 🔄 常见操作
| 需求 | 方法 |
|------|------|
| 清空上下文 | 侧边栏按钮 “清除对话” |
| 切换语言 | 侧边栏下拉框 |
| 查看模型 | 侧边栏展示（只读） |

## 🧪 健康检查与知识库构建
当前 `api_client` 在初始化时会调用 `/v1/models` 列表探测所配置模型是否存在：
- 若未列出：打印警告，但仍尝试直接调用（有些网关会代理映射）
- 若多次请求失败：界面显示错误栈前缀（截断保护）

如需使用知识库检索，可执行：
```
python ingest.py your_file.pdf
```
脚本会将 PDF 分页拆分、生成向量并写入本地 `Chroma` 数据库。索引建立后在 `.env` 中设置 `RAG_ENABLED=true` 即可启用检索。

## ☁️ 部署（Streamlit Cloud 示例）
1. 推送代码到 GitHub
2. 在 Streamlit Cloud 创建新应用：
   - Main file path: `app.py`
3. 在 Secrets 设置：
```
OPENAI_API_KEY="你的真实key"
MODEL_NAME="gpt-5-mini"  # 可选
```
4. 保存后自动构建

## ❓ 常见问题
### 1. 模型名称报错 / 404
确认 `config.py` 中 `MODEL_NAME` 是否为账号可用模型；当前已设为 `gpt-5-mini`。
### 2. SSL 或 UNEXPECTED_EOF_WHILE_READING
可能为临时网络中断；客户端已内置重试。持续失败可：
- 重试运行
- 检查本地代理 / 防火墙
- 升级 `requests`：`pip install -U requests`
### 3. 想扩展 RAG / 多模型？
当前版本已模块化，便于扩展：
- 在 `prompts/` 维护领域提示词；
- 在 `utils/broker_logic.py` 的 `SimpleRAG` 中接入检索，或替换为你的实现；
- 若需多模型/多提供商，可在 `config.py` 与 `utils/api_client.py` 中按需扩展。

## 🧭 后续可选增强
- 消息持久化（文件 / sqlite）
- Token 消耗估算
- 响应流式输出（当前为整块返回）
- 模型健康缓存 & 自适应降级

## 📄 许可证
当前未指定许可证（默认保留所有权）。如需开源，请添加 `LICENSE` 文件（MIT / Apache-2.0 建议）。

---
如需再加功能（RAG、费用估算、审计日志等）随时提出。
