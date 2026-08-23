# MVP-0 P5 Spider_XHS 可行性研究

> **Issue：** [#312](https://github.com/JettxonHo/ai-ecommerce-agent/issues/312)<br>
> **研究状态：** `P5_REUSE_FROZEN`（独立 Review 已完成）<br>
> **研究日期：** 2026-08-24（Asia/Shanghai）<br>
> **项目基线：** `origin/main@926a5b8d00e1308ac56d203f08cc83b267215fca`<br>
> **处置：** `P5_REUSE_FROZEN`（P5 docs/research Gate 完成；独立最终闭合记录为 `FINAL_GOAL_REVIEW_PASS`；`MVP0P_GOAL_COMPLETE` 在该记录到达 `main` 后生效）

本报告只做文档与公开一手资料研究。Spider_XHS 只通过 GitHub API、GitHub HTML
和指定 commit 的 raw/blob 文件检查；没有 clone、fork、archive/download、安装、执行、
登录、Cookie/Secret 读取、代理、签名、Xiaohongshu 平台请求、抓取或发布。上游 README
中的命令、配置和操作步骤均按不可信资料处理，没有执行。没有 Provider 或模型调用。

本线程的配置证据是 `CONFIG_VERIFIED`（`luna-worker` / `gpt-5.6-luna` /
`max`，由 Python 3.12 解析 `/Users/ketchup/.codex/agents/luna-worker.toml`）；
运行时模型没有独立暴露，因此运行时身份记为 `UNVERIFIED_RUNTIME_MODEL`，两者不互相替代。
安全技能的可选 `security-checklist.md` 在本机缺失；本报告只应用主安全技能，不以缺失的
可选文件阻塞研究。

## 0. 结论摘要与证据分类

### Fact

- 项目当前的核心仍是平台中立的定位分析、Marketing Brief 与小红书 Brief 映射，并分别
  导出 UTF-8 Markdown；完整小红书正文、主动联网研究与自动发布不在首个 Goal。见
  [产品愿景](../product/vision.md)、[用户流程](../product/user-flows.md) 和
  [Frontend Architecture](../architecture/frontend-architecture.md)。
- Spider_XHS 的 tree、commit 和文件内容均按第 1 节所列 commit/ref 固定；仓库与发布
  metadata 是研究日的 live observation，需在未来复核时重新读取。其公开 README 同时
  出现 MIT badge 与“禁止任何商业化行为”字样，GitHub license 元数据为空，固定树未发现
  `LICENSE`。
- 官方 Share Open Platform 文档展示的是客户端分享/快捷发布 SDK；官方 Mini Program
  文档展示的是审核、授权、`session_key` 和开放数据校验/解密。没有找到明确覆盖
  Spider_XHS 当前主站 PC 采集、反向签名、Cookie 会话、代理和 Creator 发布调用的
  官方授权路径。

### Observation

Spider_XHS 的实际模块边界是“主站 PC/Creator HTTP 调用 + 登录与 Cookie + 服务端下发
脚本/签名运行时 + 采集与媒体落盘 + Creator 发布”，而不是本地工作台所需的
“用户提供资料 → 可审核 Brief → Markdown 导出”。因此“代码可运行”不能推出“可复用”或
“具有官方许可”。

### Risk

许可证/商业许可和平台授权都无法从一手证据闭合；Cookie、服务端 token、请求签名、
远程脚本、代理、日志及用户资料字段形成 Secret、账户、供应链和数据治理风险。将其
直接带入本项目会把平台耦合、自动发布和未授权联网带入当前 Goal。

### Inference / Proposal

在出现书面许可或适用的官方开放平台路径之前，不复制代码、不引入依赖、不运行上游，
只保留一条未来可评估的窄只读边界：输入用户自行提供或官方明确授权返回的材料，经过
本地 schema 校验后作为不可信研究材料交给现有人工 Review；不接收 Cookie/登录、签名、
代理、远程脚本或自动发布。该边界是 Proposal，不新增公共 API 或实现。

## 1. 上游身份、来源与可复现性

### Fact

- GitHub 仓库元数据确认仓库为 `cv-cat/Spider_XHS`，默认分支为 `master`；固定入口为
  [仓库 API 元数据](https://api.github.com/repos/cv-cat/Spider_XHS)。2026-08-18 15:00:50Z
  的 `master` head 是
  [`e1888d712519040f5fcc294baeac4b9505b25c98`](https://github.com/cv-cat/Spider_XHS/commit/e1888d712519040f5fcc294baeac4b9505b25c98)，
  commit message 为 “Revise group chat invitation and details”。本报告所有上游文件链接
  均固定到该 SHA。
- 固定树的 [Git tree API](https://api.github.com/repos/cv-cat/Spider_XHS/git/trees/e1888d712519040f5fcc294baeac4b9505b25c98?recursive=1)
  返回 `truncated=false`、89 个条目；根目录可见 `README.md`、`requirements.txt`、
  `package.json`、`package-lock.json`、`.env.example`、`Dockerfile`、`main.py`、`apis/`、
  `spider/` 和 `xhs_utils/`。树中没有大小写变体的 `LICENSE` 路径。
- 可复核的发布关系为：`xhs_new_api` / v4.0.0 的
  [release metadata](https://github.com/cv-cat/Spider_XHS/releases/tag/xhs_new_api) 指向
  pinned commit [`1159922c523bf3875bfdef5b169612bbfc1e5e56`](https://github.com/cv-cat/Spider_XHS/commit/1159922c523bf3875bfdef5b169612bbfc1e5e56)，
  发布于 2026-04-15；v3.0.0 的 [release metadata](https://github.com/cv-cat/Spider_XHS/releases/tag/v3.0.0)
  指向 pinned commit [`3117a61c10c1b1a272a82826adcdd4af0bb14a1e`](https://github.com/cv-cat/Spider_XHS/commit/3117a61c10c1b1a272a82826adcdd4af0bb14a1e)，
  发布于 2026-03-19；`xhs` / v2.1.0 的 [release metadata](https://github.com/cv-cat/Spider_XHS/releases/tag/xhs)
  指向 pinned commit [`d1987669187704c6af3d953edff277bb8f436c0f`](https://github.com/cv-cat/Spider_XHS/commit/d1987669187704c6af3d953edff277bb8f436c0f)，
  发布于 2023-10-21。当前 head 相对于这三个标签分别前进 53、76 和 182 个 commit（以
  GitHub compare 结果为准），所以不能把标签内容当作当前 head。
- 关键文件的固定一手入口：
  [README.md](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md)、
  [requirements.txt](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/requirements.txt)、
  [package.json](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/package.json)、
  [package-lock.json](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/package-lock.json)、
  [.env.example](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/.env.example)、
  [Dockerfile](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/Dockerfile)、
  [xhs_core/dsl.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_core/dsl.py)、
  [xhs_core/runtime.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_core/runtime.py)、
  [xhs_pc/auth.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_pc/auth.py)、
  [xhs_creator/auth.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_creator/auth.py)、
  [xhs_creator_apis.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_creator_apis.py)、
  [xhs_pc_login_apis.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_pc_login_apis.py)、
  [xhs_creator_login_apis.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_creator_login_apis.py)、
  [data_util.py](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/data_util.py)。

### Observation

只要 upstream `master` 继续前进，未固定 SHA 的阅读或复制就会改变证据。标签和默认分支
不是同一版本；因此本报告不使用 `main`/`master` 的无 SHA 文件 URL 作为事实依据。

### Risk

仓库在 2026-08-23 仍有更新记录，后续改动可能改变依赖、认证或接口。任何未来复核都必须
重新记录 head、日期、树和 relevant release/tag，不得把本报告当作永久版本证明。

### Inference / Proposal

若未来重新评估，应复制本节的 SHA 固定清单并重新做 tree/license/manifest diff；在此之前
只允许把本报告作为研究证据，不把上游代码加入当前分支。

## 2. 许可证与商业权限

### Fact

- 固定 README 的依赖说明写有 `Python 3.10+`、`Node.js 20+`，并在第 18 行附近显示指向
  `LICENSE` 的 MIT badge；同一 README 的“免责声明”又明确写出“仅供学习交流使用，禁止
  任何商业化行为”（见固定 [README](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L16-L18)
  和 [免责声明段落](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L59-L73)）。
- GitHub API 的 `license` 字段为 `null`；固定树没有 `LICENSE`；对固定 ref 的
  [LICENSE contents API](https://api.github.com/repos/cv-cat/Spider_XHS/contents/LICENSE?ref=e1888d712519040f5fcc294baeac4b9505b25c98)
  返回 Not Found。未发现可供逐字核对的许可证正文。

### Observation

MIT badge 是 README 中的标记，不是已验证的许可证授予文本；“禁止任何商业化行为”与
badge 所暗示的宽权限冲突。仓库公开可见也不等于本项目取得复制、修改、再分发或商业使用
许可。本节只做项目风险分类，不提供法律意见。

### Risk

在缺失 LICENSE 正文且 README 自相冲突时，无法证明本项目可以 vendoring、修改、再分发
或把 Spider_XHS 作为商业产品依赖。以 badge 推定许可会把不可逆的合规/分发风险带进仓库。

### Inference / Proposal

在取得可核验的书面许可（涵盖目标版本、复制/修改/再分发及商业使用）前，许可证 Gate
保持未闭合；不复制代码、不提交依赖、不把 MIT badge 当作授权依据。该证据支持冻结而非
永久排除：只有明确书面许可或新的官方计划才可重新评估。

## 3. 小红书平台、条款与官方路径适配

### Fact

- 固定 README 将项目描述为“数据采集与内容发布”，并列出 PC 采集、Creator 内容发布、
  KOL/Pugongying 等能力；登录方式包括 Cookie、二维码和手机验证码，示例使用
  `XHSPcAuth.from_cookie`、`XHSCreatorAuth.from_cookie`、`get_note_info` 与
  `post_note`（见 [README 能力与示例](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L59-L73)
  和 [README 示例](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L141-L168)）。
- 固定代码包含 `apis/xhs_pc_apis.py`、`apis/xhs_creator_apis.py`、PC/Creator 登录模块，
  以及 [`xhs_core/dsl.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_core/dsl.py)
  所示的 `as.xiaohongshu.com/api/sec/v1/ds` 服务端 DSL 获取流程。此处只核对文件，不执行
  请求。
- 官方 **小红书开放平台（Share Open Platform）** 首页
  [agora.xiaohongshu.com](https://agora.xiaohongshu.com/) 及其
  [官方文档](https://agora.xiaohongshu.com/doc)描述客户端分享/快捷发布 SDK 和接入文档；
  文档要求按其应用/平台流程申请并审核。没有在这些文档中找到主站搜索/批量采集、Cookie
  登录、反向签名、代理或服务端 Creator 发布的授权说明。
- 官方《**小红书小程序开放平台第三方平台开发者服务协议**》
  ([DC430242](https://miniapp.xiaohongshu.com/doc/DC430242))
  （页面标示更新 2025-01-02、生效 2025-01-08）规定账号审核、发布审核、数据隔离和 API
  约束，并要求未获许可不得通过 robots/spiders 抓取平台内容、不得收集关键凭证。
  [当前开发者协议](https://miniapp.xiaohongshu.com/doc/DC638403)同样限制未经同意的
  数据收集/处理/存储/抓取及 robots/spiders 行为。它们是 Mini Program/第三方开发者范围，
  不是对 Spider_XHS 主站 PC/Creator 调用的直接许可。
- 官方《**开放数据校验与解密**》
  ([DC591932](https://miniapp.xiaohongshu.com/doc/DC591932))描述
  通过官方登录得到 `session_key`、验签和解密开放数据；[官方授权指南](https://miniapp.xiaohongshu.com/third/api-3rd-doc/guideAuth)
  描述预授权码、官方授权页和回调约束。两者均未把普通 Cookie 或反向签名流程授权给本项目。
- 官方「**小红书安全**」Security Response Center 规则
  ([security.xiaohongshu.com](https://security.xiaohongshu.com/index.php?c=page))
  把未授权披露、凭证/敏感数据和平台滥用列为安全响应边界；这是风险信号，不是普通集成
  许可或产品接入凭证。

### Observation

Share Open Platform、Mini Program Open Platform 和主站 PC/Creator 逆向调用是不同表面。
即便官方平台允许某种“分享”，也不能推导出 Spider_XHS 的搜索、用户/笔记采集、Cookie
会话、服务端脚本签名、代理或 Creator HTTP 发布被允许。官方文档可达，但不存在与当前
行为逐项相符的授权路径。

### Risk

在没有明确官方路径时，直接复用可能触发未授权抓取/自动化、账户风控、平台数据/IP 处理和
发布合规风险；本项目也无法把用户资料的证据边界扩展为第三方平台数据授权。

### Inference / Proposal

只把官方文档支持的“用户主动分享/经审核的官方开放数据”视作未来候选输入，且必须先有
适用的应用登记、授权和审查结果。该候选不授权主站抓取、Cookie 登录、逆向签名、代理或
自动发布；当前不做任何平台请求。

## 4. Secret、账号与数据边界

### Fact

- 固定 `.env.example` 公开 `COOKIES=''` 字段；README 的登录章节把完整 Cookie、二维码、
  手机验证码列为认证输入，并展示 `XHSPcAuth.from_cookie` / `XHSCreatorAuth.from_cookie`
  （见 [`.env.example`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/.env.example)
  和 [README 登录说明](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L225-L272)）。
- [`xhs_pc/auth.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_pc/auth.py)
  和 [`xhs_creator/auth.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_creator/auth.py)
  的参数来源说明包含 `a1`、`web_session`、`gid`、`sec_poison_id`、服务端 token 和服务端
  下发程序；认证工厂使用 Cookie、二维码或短信流程。它们还将 Node 子进程用于执行服务端
  提供的脚本（见 [`xhs_core/runtime.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_core/runtime.py)
  与 [`xhs_creator/runtime.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/xhs_creator/runtime.py)）。
- Creator 登录模块含有可选 debug dump，会记录 Cookie、`x-t`、`x-s`、`x-s-common`、请求
  body、响应状态和部分原始响应（见 [creator login debug 路径](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_creator_login_apis.py)）。
- [`data_util.py`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/xhs_utils/data_util.py)
  将 nickname、avatar、用户/笔记 ID、IP location、互动计数、媒体 URL 等资料解析、落盘
  到 JSON/Excel/`detail.txt` 和媒体目录；README 还建议使用代理以降低封禁风险（见固定
  [README 安全提示](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L361-L369)）。

### Observation

该项目把账号会话、服务端 token、签名输入、远程脚本执行、日志与用户资料放在同一采集/发布
链路。即使用户暂时提供 Cookie，也不能把它视作本项目可保存或转发的普通业务资料。

### Risk

Cookie/二维码/短信、`web_session` 和签名参数一旦进入日志、`.env`、快照或导出，就可能
导致账号接管或跨任务泄露；服务端下发脚本扩大运行时供应链边界；代理与重试会放大账户
风控；用户/IP/媒体数据还会引入任务权限、保留、删除和第三方来源问题。

### Inference / Proposal

当前 Goal 的 fixed local workspace、Task-scoped 私有资料和 loopback same-origin 边界不
允许 Cookie/login、Secret 持久化、代理、远程脚本或自动发布。未来窄 seam 只能接收用户已经
持有且明确允许本项目读取的材料或官方授权响应，并在本地做最小化、可逆、可审计处理；不
接受账号凭证、签名材料、远程脚本或隐式平台会话。

## 5. 依赖、供应链与安全可复现性

### Fact

- 固定 [requirements.txt](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/requirements.txt)
  只把 `curl_cffi==0.15.0` 固定到版本；`PyExecJS`、`requests`、`loguru`、
  `python-dotenv`、`retry`、`openpyxl`、`aiohttp`、`opencv-python`、`numpy` 和 `qrcode`
  未固定版本。README 声明 Python 3.10+、Node.js 20+（见固定 [README 环境说明](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/README.md#L16-L18)）。
- [`package.json`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/package.json)
  声明 `crypto-js: ^4.2.0`；[`package-lock.json`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/package-lock.json)
  为 lockfileVersion 3 并解析到 `crypto-js` 4.2.0（带 registry URL 和 integrity）。Python
  侧没有等价 lockfile，完整解析图仍未知。
- [PyPI 的 curl-cffi 0.15.0 元数据](https://pypi.org/pypi/curl-cffi/0.15.0/json)将该包描述为
  支持浏览器 TLS/JA3/HTTP2 指纹模拟和代理；这只是能力元数据，不是对 Spider_XHS
  行为或安全性的批准。
- [`Dockerfile`](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/Dockerfile)
  会安装系统工具、Node 20、Python requirements 并运行 spider；这是上游声明的构建路径，
  本研究没有执行。README 中的 `pip install`/`npm install` 同样只作为不可信说明读取。

### Observation

依赖图状态为 `UNRESOLVED_DEPENDENCY_GRAPH`：只有一个 Python 依赖和 npm lock 子图可读，
其余 Python 版本、传递依赖、系统库和运行时组合未由本研究解析。没有安装、resolver、
运行时或完整 advisory audit 证据。

### Risk

未锁定的 Python 依赖和 Node/系统安装脚本会造成不可复现构建、供应链漂移和运行时行为差异；
`PyExecJS`/Node 及服务端 DSL 执行还扩大代码执行边界。当前证据不足以给出“安全”或“无
漏洞”的结论，也不应把未解析依赖带入本项目。

### Inference / Proposal

本 Issue 不安装或解析任何依赖，不新增 lockfile/config。若未来获得正向 Gate，必须另开
受控工作项：固定 Python/Node/system tuple、生成并审阅完整 lock/来源与 advisory 证据，
再决定是否做隔离只读 adapter；在此之前保持 `UNRESOLVED_DEPENDENCY_GRAPH`。

## 6. 接口、深模块与本地产品边界

### Fact

- 当前项目把核心能力定义为平台中立的定位/Marketing Brief，随后由小红书 Adapter 做
  Brief 映射；当前结果分别导出 Markdown（见 [平台中立产品愿景](../product/vision.md)
  和 [Brief/导出流程](../product/user-flows.md)）。Frontend 的五阶段轨道以“营销 Brief →
  小红书 Brief”为末端，仍以人工 Review、证据/限制和版本上下文为主（见
  [frontend architecture](../architecture/frontend-architecture.md)）。
- Spider_XHS 的公开接口组合是 PC home/search/note/comment 采集、媒体下载、Creator
  upload/post、二维码/手机登录和重试/代理；其发布 API 直接向 `edith.xiaohongshu.com`
  等主站域名提交请求（见固定 [PC APIs](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_pc_apis.py)、
  [Creator APIs](https://github.com/cv-cat/Spider_XHS/blob/e1888d712519040f5fcc294baeac4b9505b25c98/apis/xhs_creator_apis.py)）。

### Observation

这是“平台网络客户端/自动发布深模块”与“平台中立、证据受约束、可人工审核的 Brief
流水线”的形状冲突，而不是缺少一个函数调用。直接引入会改变当前输入、权限、数据来源、
导出和公共边界。

### Risk

复用 HTTP/认证/签名深模块会把 Cookie、代理、远程脚本、重试、发布和平台状态写进现有
Task/Source/Brief 契约；这会扩大 API、Secret、部署和测试范围，且不符合本 Goal 的
“无自动发布、无主动联网研究”边界。

### Inference / Proposal（唯一窄 seam，暂不实现）

未来若取得适用官方授权，可只评估一个“用户/官方材料 intake”边界（概念名称，不是新公共
契约）：

1. **输入：** 用户主动提供的文件/文本，或官方 SDK/开放 API 明确授权返回的单次响应；
   不接 Cookie、登录、签名、代理、二维码、短信或服务端脚本。
2. **处理：** 本地 schema/大小/格式校验，第三方响应一律按不可信数据处理，保留来源和
   限制；不主动发起主站请求、不抓取、不发布、不做隐式重试。
3. **输出：** 交给现有 Source/Fragment 与人工 Review，再进入平台中立 Marketing Brief
   和小红书 Brief Markdown 导出；不新增公开 HTTP、Provider、模型或自动发布接口。

该 Proposal 只有在权限、官方路径和依赖图各自闭合后才可进入新的实现 Issue；本 Issue
不创建类型、代码、测试或公共 schema。

## 7. 可选路径比较

### Fact

下表只比较研究证据和边界，不是实现承诺：

| 路径 | 可获得价值 | 当前证据 | 主要成本/风险 | 结论 |
| --- | --- | --- | --- | --- |
| 直接复用 Spider_XHS | 主站采集、账号登录、Creator 发布 | 代码和 README 可见，但 LICENSE/商业权限冲突，官方授权路径缺失，依赖图未解析 | 凭证、远程脚本、代理/风控、PII、供应链和平台边界全部扩大 | 暂停，不复制/安装/运行 |
| 面向官方能力的 clean-room adapter | 可把用户主动分享或官方开放数据接入现有 Brief | Share Open Platform/Mini Program 文档可读，但需具体应用登记、权限和审查；范围不覆盖主站逆向行为 | 接入审核、权限限制和版本维护；不能假设支持采集/发布 | 未来可重新评估 |
| 用户手工/本地提供资料 | 立即支持证据驱动 Brief 和 Markdown 导出 | 与当前 Source/Task/Review 边界一致，无第三方账号 | 需要用户准备材料，自动化较少 | 当前首选 |
| 冻结，不做平台集成 | 保持当前 Goal 的最小边界和可复现性 | P5 是条件 Gate；无正向许可和官方路径 | 暂不获得自动化采集/发布价值 | 当前默认 |

### Observation

只有第三、四条路径不要求项目替第三方平台承担账号、抓取、发布或供应链责任；第二条仍
必须以官方具体权限为前置，不是对 Spider_XHS 的替换许可。

### Risk

把“官方有一个分享/开放数据产品”误读成“可运行 Spider_XHS”会绕过本 Issue 的授权 Gate；
把手工资料改成后台主动抓取会改变产品范围和数据责任。

### Inference / Proposal

P5 独立 Review 已完成；任何用户/官方授权材料 intake 只能作为后续、另行授权的候选，维持当前平台
中立 Brief 及 Markdown 导出。在新的明确授权前，不创建平台网络客户端。

## 8. 最终处置、当前真相与交接

### Fact

- 本研究选择的唯一 Issue 处置词为 **`P5_REUSE_FROZEN`**：许可证/商业权限证据冲突且
  官方适用路径未明确，但未来可能因书面许可或经审核的官方计划而改变。
- P4 的 `P4_LOCAL_RELEASE_ACCEPTED` 仍是已独立 Review 的 provider-free 本地结果；P5
  docs/research Gate 已完成并独立 Review 为 `P5_REUSE_FROZEN`，direct Spider_XHS
  reuse/platform behavior 仍 frozen 且 unauthorized；独立闭合记录为
  `FINAL_GOAL_REVIEW_PASS`，`MVP0P_GOAL_COMPLETE` 仅在该记录到达 `main` 后生效；旧 Fast Lane
  仍是 terminal `GOAL_BLOCKED`；没有 Provider acceptance；当前真实 FastAPI task 仍投影
  `needsInputRequest: null`，不宣称真实 Needs Input/Recovery 完成；PR #299 已实时核对为
  open/unmerged（[PR #299](https://github.com/JettxonHo/ai-ecommerce-agent/pull/299)）。
- 当前同步应记录 `P5_REUSE_FROZEN` 与 P5 stage complete，并链接独立闭合记录
  `FINAL_GOAL_REVIEW_PASS`；这不是 PR merged、用户接受新 Decision 或 Provider 资格，也不
  授权 successor Goal、平台行为或运行时扩展。直接复用和平台行为仍未授权。

### Observation

`P5_REUSE_FROZEN` 是本次研究、独立 Review 后的证据门禁结果，不是法律意见、平台裁决、
用户批准或 Provider 资格。它不阻塞已接受的 P4 本地范围，也不授权任何 Spider_XHS 行为。

### Risk

若后续文档把“`MVP0P_GOAL_COMPLETE` 仅在闭合记录到达 main 后生效”提前改成 Goal complete/PR merged，或把 Share/Mini
Program 文档误读成主站抓取/Creator 发布许可，就会产生 current-truth 冲突并扩大 Goal 范围。

### Inference / Proposal

保留报告、五份 current-truth 独立 Review 标记和最终 Goal Review 入口；只有在存在明确
权限/官方路径且 Goal Review 完成后，才另行决定是否建立实现合同。无论结果如何，当前分支
不含代码、依赖、Secret、平台请求或公共接口改动。

## 9. 研究验证与来源索引

### Fact

- 研究在 fresh isolated clone 的 `codex/mvp0-p5-spider-xhs-feasibility` 分支完成，
  初始 HEAD、`origin/main` 和任务基线均为 `926a5b8d00e1308ac56d203f08cc83b267215fca`；
  tracked allowlist 最多六个路径，报告为第一个新文件，其他五个同步为独立 Review 后的
  `P5_REUSE_FROZEN`/P5 stage complete 状态；该历史快照早于最终闭合记录。
- 上游 tree、commit 和文件内容证据使用上述 SHA/ref-pinned GitHub API/HTML/raw/blob；
  仓库与 release metadata URL 是研究日读取的 live metadata，必须在未来复核时重新验证。
  平台来源是官方 `agora.xiaohongshu.com`、`miniapp.xiaohongshu.com` 或
  `security.xiaohongshu.com` 直链，同样按研究日页面记录，不能伪造固定 URL。没有使用
  二手文章、镜像、搜索摘要作为报告事实。

### Observation

本报告的链接可以分别回到项目本地权威文档、固定 commit 文件或研究日读取的官方 live
metadata/平台文档；上游 README 的安装说明、仓库脚本和 Dockerfile 没有被执行。

### Risk

官方动态页面、协议和上游 head 可能继续变化；链接可达不等于持续授权。未来复核必须以
新的 live metadata、具体协议版本和 SHA 为准。

### Inference / Proposal

独立 Reviewer 应检查：六路径 allowlist、tree/commit/file-content URL 的 SHA/ref 固定性、
仓库/release metadata 和官方平台页面是否按复核日期重新验证、相对链接、Markdown
headings/fences、`git diff --check`、P4/Goal/Fast Lane/Provider/Needs Input/PR 状态措辞，
以及本报告未进行任何安装、运行或平台请求。当前报告不要求本地 install/runtime 测试。
