---
name: backend-agent-project-selector
description: "Find suitable traditional software backend or business-grade AI agent projects from GitHub for students or early-career engineers, evaluate resume value, and generate a Markdown resume-writing package. Use when a user asks to choose backend projects, Java/Spring projects, distributed-system projects, complete AI agent business projects, multi-agent systems, LLM apps, GitHub projects for resumes, or turn selected projects into resume bullets/interview talking points. Supports modes: agent-only, backend-only, mixed, safe-mode, and challenge-mode. If no mode is specified, ask the user to choose before searching or recommending. Backend recommendations exclude IoT, embedded, hardware-integration, device-management, and industrial-control platforms unless requested. Avoid simple browser extensions, thin LLM wrappers, shallow AI plugins, and browser-automation libraries unless requested."
---

# 后端 / Agent 项目选择器

## 能力范围

从 GitHub / Web 搜索适合写进简历的后端项目或完整业务型 Agent 项目，筛选后生成 `backend-agent-project-resume-pack.md`。

推荐模式是必填项。用户必须指定 `agent-only`、`backend-only`、`mixed`、`safe-mode`、`challenge-mode` 中的一种；如果用户初始化找项目、选择项目、推荐项目或生成简历项目但没有指定模式，先完整列出所有可选模式并让用户选择，不要开始搜索或生成推荐。

## 必须遵守

- 用户每次初始化找项目、选择项目、推荐项目或生成简历项目时，如果推荐模式缺失，必须先完整列出所有可选模式并反问，不能自行默认、推断或继续执行。
- 除非用户明确要求不要联网，否则要搜索当前 GitHub / Web 项目后再推荐。
- 优先完整业务系统，避免 demo、插件、薄封装、纯框架和只会调用一次大模型的项目。
- `backend-only` 不要默认只推荐 API 网关、IAM、调度、监控等底层技术项目；除非用户明确要求基础设施 / 中间件，否则应优先覆盖电商交易、内容社区、协作办公、工单客服、CRM/ERP、知识库、网盘、在线教育等完整业务项目。
- 不要避开有业务闭环的业务项目；只避开浅层 CRUD、教程复刻、没有状态流转 / 异步链路 / 失败恢复 / 权限边界的业务项目。
- 默认不要把 IoT、嵌入式、硬件接入、设备管理、工业控制类平台作为后端项目推荐；除非用户明确要求硬件 / IoT / 物联网方向，否则这些项目应降权或淘汰。
- 先构建多样化候选池，再做最终选择；不要直接推荐全局高星项目，也不要把 star 数作为主要排序依据。
- star 数只作为“项目已有一定社区验证”的弱信号：达到 1k star 即可纳入正式候选池并认真评估；超过 1k 后不应因为 star 更高而显著加分。
- 搜索候选时必须主动覆盖中等 star 区间和细分领域项目，避免只用 `sort=stars` 或只看几万 star 项目；后端和 Agent 项目都适用该规则。
- 候选池阶段要读取 README 前若干行做项目类型 probe，用于判断是否为业务系统、框架 / SDK / 桌面壳 / 工具链；README probe 只能用于筛选和项目定位，不能支撑最终“负责功能 / 技术难点”。
- 构建候选池时优先使用 `references/search_github_candidates.py` 自动搜索、README probe、去重、分桶和初筛；如果手动搜索，最终也要输出同等字段的候选池和短名单确认内容。
- 拉取最终候选源码前，必须先向用户展示 3-4 个短名单项目、每个项目的选择理由和主要淘汰理由，并等待用户确认方向；用户确认后才能执行 `pull_github_repos.py`。
- 最终入选项目前必须运行 `references/pull_github_repos.py` 真实拉取对应 GitHub 仓库到本地；未经过该脚本成功拉取并写入 manifest 的项目不得进入最终推荐。
- 源码验证只能基于 `pull_github_repos.py` 拉取到本地的仓库目录进行；不能用 GitHub raw/API、README、网页搜索、模型记忆或经验判断替代本地源码验证。
- 如果脚本执行失败、仓库无法拉取、manifest 中该仓库状态不是 `cloned`、本地源码不可读，或无法从源码提取至少 5 个证据点，该项目必须淘汰。
- 必须区分 `已有能力`、`建议改造`、`可写入简历`。
- 简历功能点默认输出为“建议简历功能点（完成对应改造后可写）”；除非用户明确已经实现或本轮完成代码改造，否则不能把建议改造写成已完成成果。
- 项目亮点必须挖掘技术难度，不能只写“实现功能 / 接入组件 / 提供接口”；优先挖数据同步与一致性、MQ 异步链路、缓存与高并发、并发控制与幂等、任务调度、线程池与异步编排、流量治理、数据库优化、检索索引、权限安全、可观测性、接口治理、规则引擎、状态机、文件处理、实时通信、交易链路、Agent 工程等机制。
- 默认使用中文输出，除非用户要求其他语言。

## 参考资料加载

按任务需要加载，不要一次性加载所有资料：

- `references/执行流程.md`：项目选择任务必载。
- `references/用户输入模板.md`：用户需要模板、示例，或推荐模式缺失需要反问时加载。
- `references/筛选评分.md`：筛选、分桶、推荐模式打分时加载。
- `references/简历写法.md`：写简历条目和面试问题前加载。
- `references/输出模板.md`：生成最终 Markdown 文件前加载。
- `references/search_github_candidates.py`：候选池搜索和短名单确认前优先执行；用于自动搜索 GitHub、读取 README probe、去重、分桶、排除前端 / 库 / IoT / 框架 / SDK / 桌面壳 / coding-agent 工具链等不合适项目，并生成候选池 JSON 与短名单预览 Markdown。
- `references/pull_github_repos.py`：最终候选源码验证前必须执行；用于真实拉取 GitHub 仓库并生成本地源码 manifest。
- `references/markdown_to_pdf.py`：最终交付必执行；将最终 Markdown 转成浅色、中文友好的 PDF。
- `references/规则索引.md`：只在需要查看文档映射关系时加载。

## 高层流程

1. 先检查用户是否明确给出推荐模式。
2. 如果没有给出推荐模式，停止执行，并使用“缺少推荐模式时的反问话术”完整展示所有可选模式后让用户选择。
3. 如果已给出推荐模式，再提取用户画像。
4. 优先运行 `references/search_github_candidates.py` 搜索多个项目分桶，建立候选池；候选池必须包含 1k+ star 的中等热度项目，不能只来自全局高星榜。
5. 按 `筛选评分.md` 过滤浅层项目，并给剩余候选打分。
6. 按推荐模式选择 3-4 个短名单项目，输出短名单、选择理由、淘汰理由和待拉取 URL，先让用户确认技术栈和方向。
7. 用户确认短名单后，将最终候选仓库 URL 写入临时列表或作为 `--repo` 参数，强制执行 `python references/pull_github_repos.py` 拉取源码并生成 manifest。
8. 只读取 manifest 中状态为 `cloned` 的本地仓库目录；阅读 README / 文档只是前置步骤，不能代替本地源码验证。
9. 只保留能够从本地源码证据提取功能点的项目；无法完成脚本拉取或源码验证的候选直接淘汰。
10. 按 `输出模板.md` 和 `简历写法.md` 生成 `backend-agent-project-resume-pack.md`。
11. 默认最终必须同时生成 Markdown 和 PDF 两个版本；执行 `python backend-agent-project-selector/references/markdown_to_pdf.py backend-agent-project-resume-pack.md --output backend-agent-project-resume-pack.pdf --title "业务型 Agent 项目推荐报告"`。

## 推荐模式

- `agent-only`：只推荐完整业务型 Agent 项目。
- `backend-only`：只推荐传统软件后端项目，默认排除 IoT / 硬件接入类项目。
- `mixed`：推荐一个 Agent 项目 + 一个传统软件后端项目；其中后端项目默认排除 IoT / 硬件接入类项目。
- `safe-mode`：只推荐容易落地、依赖少、部署成本低的项目。
- `challenge-mode`：推荐更难、更有差异化、更适合深度改造的项目。

## 缺少推荐模式时的反问话术

如果用户没有明确写出推荐模式，直接回复：

```text
你想按哪种推荐模式执行？

- agent-only：只找完整业务型 Agent 项目
- backend-only：只找传统软件后端项目，默认排除 IoT / 硬件接入类
- mixed：一个 Agent 项目 + 一个传统软件后端项目
- safe-mode：只推荐容易落地、部署成本低的项目
- challenge-mode：推荐更难、更有差异化的项目

你回复其中一个模式后，我再开始搜索 GitHub 并生成简历写法。
```

## Agent 项目标准

Agent 项目必须是完整业务系统，而不是 LLM UI、浏览器插件或浏览器自动化库。它应该解决具体领域问题，例如 AI 投研、多智能体协作、客服自动化、数据分析、代码修复、DevOps 运维、报告生成、企业知识流转。

Agent 候选短名单必须优先满足业务型强门槛：业务数据、状态流转、持久化、工具调用、评测、用户价值至少命中 2-3 项；纯 framework / SDK / library / toolkit / desktop companion / coding-agent 工具链不得和业务型 Agent 混在同一短名单中，除非用户明确要求工具链方向。

除非用户明确要求，否则淘汰简单浏览器插件、网页侧边栏、总结器、提示词管理器、单次 LLM 调用包装，以及没有业务数据、状态、持久化、评测或可见用户价值的项目。

## 输出约定

始终在当前工作区创建或更新 Markdown 与 PDF 两个交付物；Markdown 内容包括：

- 结论先行的推荐
- 候选池
- 推荐模式和多样性说明
- 可替换项目
- 每个推荐项目的详细分析
- 简历写法：先给 80-120 字项目简介，再给代码验证摘要，然后给 5-6 条“负责功能 / 技术难点”，最后给“建议简历功能点（完成对应改造后可写）”；其中“负责功能 / 技术难点”必须来自源码验证。
- 下一步落地或改造计划
- PDF 必须生成：使用 `references/markdown_to_pdf.py` 输出 `backend-agent-project-resume-pack.pdf`，保持浅色背景块、清晰标题层级，不添加“阅读导航”，内联代码按普通正文渲染以避免中文段落异常换行。

