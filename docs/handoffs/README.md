# Handoffs（交接）

本目录用于存放阶段交接与开发就绪状态。

---

## 文件

- [implementation-readiness.md](implementation-readiness.md) — 进入开发阶段的就绪状态与前置条件。

---

## 定位

- 本目录是 **Execution Gate（执行门）**。
- 进入开发前，`implementation-readiness.md` 必须由 `NOT READY` 转为就绪，且必须通过 [../reviews/](../reviews/) 中的 Implementation Readiness Review，并由用户再次明确批准。
- 在就绪条件全部满足前，仓库中只允许存在文档与模板，不得出现业务实现代码。
