公司档案馆 运维手册（简明版）

目的

提供管理员和运维人员在部署、备份、恢复、监控和常见故障处理时的具体步骤和命令。

目录

1. 启动与停止
2. 环境变量与配置
3. 备份与恢复
4. 管理员操作（同步/重建/删除）
5. 日志与监控
6. 常见问题与恢复步骤

1. 启动与停止

- 在服务器上，用非交互 shell 启动：

```bash
export OPENAI_API_KEY=sk-...
export ADMIN_PWD_HASH="<sha256 hex>"
export CHROMA_DISABLE_TELEMETRY=1
cd /path/to/company_archive_mvp_chroma
# 推荐使用 tmux/systemd/docker 等持久化方法运行
streamlit run streamlit_app.py --server.port 8501
```

- 停止：通过 tmux/pm2/systemd 停止对应进程；若直接以 shell 启动可发 Ctrl-C。

2. 环境变量与配置

- 必需：
  - `OPENAI_API_KEY`：用于 embeddings 与 LLM。
  - `ADMIN_PWD_HASH`：管理员密码的 sha256 hex 值，用于后台登录验证。
  - `CHROMA_DISABLE_TELEMETRY=1`：建议设置以避免 chromadb 的 telemetry 错误输出。
- 可选：
  - `LIBRARY_DIR`：资料库文件夹（默认 `data/storage/`）。
  - `EMBEDDING_MODEL` / `CHAT_MODEL`：可在 `backend/config.py` 覆盖默认模型。

3. 备份与恢复

- 备份：
  - 手动备份（推荐操作前执行）

```bash
./backup/restore.sh backup
# 这会在 backup/<timestamp>/ 下保存 archive.db 与 data/chroma 的副本
```

- 恢复（占位说明）：
  - 恢复请在运维维护窗口进行：停止服务 -> 复制备份文件 -> 启动服务。
  - 示例（手动）：

```bash
# 停止服务
# 复制备份
cp backup/<timestamp>/archive.db data/archive.db
rm -rf data/chroma
cp -r backup/<timestamp>/chroma data/chroma
# 启动服务
streamlit run streamlit_app.py
```

注意：恢复前请务必确认备份来源可信并做好当前状态快照。

4. 管理员操作

- 上传：管理员登录后可通过 UI 上传文件或直接把文件放到 `data/storage/`，然后在 UI 点击“手动同步”。
- 手动同步 / 重建索引：
  - 手动同步会扫描 `LIBRARY_DIR`，对新增/修改文件进行 upsert，并触发 ingest（会调用 OpenAI）。
  - 重建索引会逐文件触发同步（与手动同步类似），请在低峰期运行并先备份。
- 删除文档：管理员可在 UI 删除单个文档，会同时删除 DB rows 与 Chroma 向量。

5. 日志与监控

- 审计：所有管理员动作会写入 `operations_log` 表。
- 错误日志：Streamlit 的 stdout/stderr 中会打印运行时错误；建议将服务通过 systemd 或 supervisor 启动并收集日志。
- 建议监控项：OpenAI 错误率、Chroma 计数（docs/chunks）、同步失败率。

6. 常见问题

- CHROMA telemetry 错误：确保环境变量 `CHROMA_DISABLE_TELEMETRY=1` 被设置在服务启动前。
- OpenAI 调用配额/失败：检查 `OPENAI_API_KEY` 是否可用，并在 README 中限制批次大小。

---

如需，我可以把这些步骤整理为运维 runbook（可直接贴入 Confluence 或运维手册）。
