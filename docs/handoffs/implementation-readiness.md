# Implementation Readiness（开发就绪状态）

> **Status: NOT READY**
>
> 当前**不得**进入开发。

进入开发至少需要以下条件**全部**满足，并须先通过 Implementation Readiness Review（见 [../reviews/](../reviews/)），再由用户明确批准。

---

## 前置条件 Checklist

- [ ] 项目定位已确认
- [ ] 目标用户已确认
- [ ] 核心问题已确认
- [ ] MVP 范围已确认
- [ ] 关键 Agent 边界已确认
- [ ] RAG 与 Skill 的职责已确认
- [ ] 开源项目使用方式已确认
- [ ] 必要 RFC 已完成（且相关 RFC 状态为 Accepted）
- [ ] 关键 Decision Records 已完成（状态为 Accepted）
- [ ] PRD 和架构文档已同步
- [ ] 数据契约与集成边界已明确
- [ ] 验收标准已存在
- [ ] 文档不存在未同步或冲突部分
- [ ] 已通过 Implementation Readiness Review
- [ ] 用户明确发出「进入开发阶段」指令

---

## 当前状态

- **Status:** NOT READY
- **就绪审查:** 未进行
- **用户开发指令:** 未下达
- **可创建的业务代码目录:** 无（`backend/`、`frontend/`、`src/`、`api/`、Agent 实现、RAG 实现、Docker 配置、数据库迁移、部署配置等当前一律不得创建）

---

## 状态变更规则

- 只有当前置条件全部满足、审查通过、且用户明确批准后，Claude 才可将本文件 Status 改为就绪。
- 任何一项条件未满足，Status 保持 NOT READY。
- 状态变更须在 [../decisions/decision-log.md](../decisions/decision-log.md) 记录或在审查文件中留痕。
