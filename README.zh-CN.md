<div align="center">

# AI Ecommerce Agent

**商品资料进来，审核过的营销文案出去。**

[![Backend Tests](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/backend-tests.yml/badge.svg)](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/backend-tests.yml)
[![Backend Quality](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/backend-quality.yml/badge.svg)](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/backend-quality.yml)
[![Web](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/web.yml/badge.svg)](https://github.com/JettxonHo/ai-ecommerce-agent/actions/workflows/web.yml)
![FastAPI](https://img.shields.io/badge/FastAPI-PostgreSQL-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=black)

语言：简体中文 | [English 治理文档](README.md#product)（README.md 下方英文区）

[快速开始](#快速开始) · [Issues](https://github.com/JettxonHo/ai-ecommerce-agent/issues) · [决策记录](docs/decisions/decision-log.md)

</div>

> 这个项目回答的问题：**LLM 的输出能不能直接拿去做生意决策？**——答案是不能直接，但可以治理：五阶段流水线 + 人工审核门禁 + 失败终止处置，让每一步都可追责。

## 目录

- [它是什么](#它是什么)
- [功能特性](#功能特性)
- [真实运行界面](#真实运行界面)
- [验证状态](#验证状态)
- [它和其他"AI 营销文案工具"的区别](#它和其他ai-营销文案工具的区别)
- [快速开始](#快速开始)
- [常见问题](#常见问题)

## 它是什么

一个**本地优先**的电商上新策略工作台，面向中小电商运营。上新时，商品调研、评论分析、竞品差异化和平台文案是四项割裂的重复劳动；这个工作台把它们收敛为一条五阶段流水线：

1. **事实**——商品资料结构化，是后续所有结论的锚点
2. **洞察**——用户在什么场景下需要什么
3. **定位**——差异化表达
4. **Marketing Brief**——平台中性的营销简报
5. **小红书 Brief**——平台适配文案

模型只在受控边界内做语义分析，**每一层结果都必须经人工审核才算数**。核心与平台无关，小红书是第一个演示适配器。

<img src="docs/assets/readme/aia-flow.png" alt="商品资料 → 五阶段分析 → 双平台文案 → 人工审核后导出" width="100%">

## 功能特性

- **五阶段 Agent 流水线**：事实 → 洞察 → 定位 → 双 Brief，阶段状态机全程可见
- **Human Review 门禁**：每层结果必须人工确认或驳回，AI 不能替人做决定
- **Markdown 导出**：审核通过的 Brief 一键导出，附不可变快照
- **中断恢复**：任务持久化在本地 PostgreSQL，刷新、重启后可从原状态继续
- **输入校验**：资料不足的输入在入口处被正确阻断，不产生垃圾输出
- **试点治理**：真实商品验证按 P0–P6 分阶段合同推进，入组、分母、停止条件先冻结再执行

## 真实运行界面

| 任务列表 | 双 Brief 人工审核 | Markdown 导出 |
|---|---|---|
| <img src="docs/assets/readme/tasks-01.png" alt="任务列表" width="100%"> | <img src="docs/assets/readme/review-02.png" alt="双 Brief 人工审核界面" width="100%"> | <img src="docs/assets/readme/export-03.png" alt="Markdown 预览与导出" width="100%"> |

## 验证状态

> 截至 2026-09-02，与仓库治理区 current truth 口径一致。

| 验证 | 状态 |
|---|---|
| 端到端功能验收 | 3 组仿真业务场景全部通过：浏览器 → FastAPI → PostgreSQL 跑通创建、重载、审核与双 Brief 导出；非法输入正确阻断 |
| 真实商品试点 | 8 件真实商品已完成入组评审与试点合同冻结，按 P0–P6 分阶段门禁串行推进 |
| 首次授权真实运行 | 在导出阶段失败，按合同**终止处置**：零静默重试、零输入替换，以决策记录重建基线 |
| 真实 P01 运行 | 尚未执行，待新一轮授权 |

## 它和其他"AI 营销文案工具"的区别

- **失败要诚实**：授权运行失败后按合同终止处置，不静默重试、不换输入重跑——失败记录本身就是资产
- **试点有合同**：真实验证的入组标准、分母、停止条件全部先冻结再执行，不接受"先跑了再说"
- **本地优先**：数据不出本机，PostgreSQL 本地持久化，无云端依赖

## 快速开始

前置条件：Docker 与 Docker Compose。

```bash
docker compose --profile local-web up
```

启动后在浏览器打开本地工作台地址即可创建任务。详见 `apps/backend/README.md` 与 `apps/web/README.md`。

## 常见问题

**我的商品数据会被上传吗？**
不会。应用本地优先运行，数据存储在本机 PostgreSQL；模型调用只在受控边界内发生，且需要显式授权。

**支持哪些电商平台？**
核心流程与平台无关；当前内置小红书 Brief 作为首个平台适配器，Marketing Brief 为平台中性产物。

**为什么没有"一键全自动生成并发布"？**
这是刻意的产品决策：上新生意决策的错误成本高于效率收益，所以人工审核被设计成流水线的一部分，而不是可跳过的选项。

## 深入阅读（协作者入口）

本仓库以 Issue / PR + CI 门禁推进，一 Issue 一可观测结果，独立评审后合并。治理规则、决策记录与当前状态见 [English 治理文档](README.md#product) 及 `docs/` 目录（决策日志、试点合同、验收记录）。
