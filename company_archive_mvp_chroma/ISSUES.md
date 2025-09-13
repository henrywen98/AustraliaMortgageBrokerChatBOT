可追踪 Issue 列表（建议用于 GitHub Issues / 内部任务追踪）

1. 安全与认证
- Title: 升级管理员登录到 SSO/LDAP
- Description: 将目前的 ADMIN_PWD_HASH 登录替换为公司 SSO/LDAP 集成，支持单点登录与企业审计。
- Priority: High
- Assignee: Dev/Ops

2. 备份与恢复自动化
- Title: 实现自动恢复脚本与验证
- Description: 实现 `backup/restore.sh restore` 的完整逻辑：验证备份完整性、下线服务、恢复文件、重建索引（如需）、并提供回滚能力。
- Priority: High

3. 数据一致性监控
- Title: 添加索引一致性监控任务
- Description: 定期检查 `data/storage/` 与 `documents` 表的差异，并报警（如发现孤立的向量或遗失的文档元数据）。
- Priority: Medium

4. 配置与部署
- Title: 容器化部署（Dockerfile + docker-compose）
- Description: 为项目添加 Dockerfile，方便在内部服务器/容器平台部署。包含健康检查与 environment 文件示例。
- Priority: Medium

5. 费用控制
- Title: Embedding 调用配额与缓存
- Description: 实施 embeddings 调用配额，缓存常见问题的 embeddings 以减少重复调用并控制成本。
- Priority: Medium

6. UX 改进
- Title: 用户反馈按钮（有用/无用）
- Description: 在检索结果/回答下增加“有用/无用”反馈按钮，结果写入统计表用于后续优化。
- Priority: Low

7. 日志与审计
- Title: 导出操作日志与审计报表
- Description: 实现导出 `operations_log` 到 CSV 的接口，便于审计或合规检查。
- Priority: Low

8. 性能
- Title: 批量重建索引的并发控制
- Description: 在 sync 时添加并发/速率限制，避免短时间内大量 OpenAI 请求导致配额耗尽或超时。
- Priority: Medium

---

如果你希望，我可以把这些 issue 按照仓库格式生成 GitHub Issue 的 markdown 模板或直接创建 PR。
