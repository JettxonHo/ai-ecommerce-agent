# DEC-074：采用 MVP-0 HTTP Adapter、本地栈与 Worker 基线

## Type

Architecture / Application Runtime / Local Development

## Status

Accepted

## Decision

用户接受 Development Plan 的推荐组合 `P-71A + P-72A + P-73A`：

- HTTP Adapter 使用 FastAPI + Uvicorn，但 authored OpenAPI 3.1 文件仍是唯一公共契约权威；框架生成 Schema 只能作为一致性检查输入，不能成为第二权威。
- 本地栈由 Compose 管理 PostgreSQL Service，并在同一 Service 中隔离 Business 与 Checkpoint Database；仓库脚本管理 API、Worker 与 Web host process 的 preflight、启动和停止。
- Worker 使用项目自有的同步 Python poll loop，实现 RFC-003 的 PostgreSQL Work Intent、poll-and-claim、Lease / Heartbeat / Fencing 与协作式取消；MVP-0 不引入 Celery、Redis 或 API 进程内 background task。

## Reason

该组合直接匹配已接受的同步 Python、PostgreSQL、LangGraph 与本地演示边界，依赖面最小，且不会让框架默认行为覆盖公共契约或 Durable Dispatch 语义。

## Impact

- 相关依赖只能在各自有界实现 Issue 中加入并锁定。
- 本地启动必须有版本 preflight、明确进程生命周期和可复现说明。
- Worker 不得在实现 Issue 中临场改用外部队列或进程内任务。
- 公共 HTTP 契约变更仍属于人工 Gate；框架选择不授权修改 RFC-004。

## Related

- [MVP-0 Development Plan](../development/mvp0-development-plan.md)
- [RFC-003](../rfcs/rfc-003-langgraph-runtime-and-checkpoint-architecture.md)
- [RFC-004](../rfcs/rfc-004-api-and-human-review-architecture.md)
- [Session-003](../sessions/session-003-pre-development-planning-and-goal-governance.md)

## Source

用户于 2026-08-08 明确回复：“接受 P-71A、P-72A、P-73A”。
