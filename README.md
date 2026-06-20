<div align="center">
  <br />
  <img src="./assets/niurou-cow.svg" alt="牛肉项目雷达 mascot" width="360" />
  <br />
  <h1>牛肉项目雷达</h1>
  <p><strong>Backend Agent Resume Scout</strong></p>
  <p>从 GitHub 里筛出真正能写进简历、能经得起面试追问的后端 / AI Agent 项目。</p>

  <p>
    <a href="#problem">中文</a>
    ·
    <a href="#english-summary">English</a>
  </p>

  <p>
    <a href="#usage">快速开始</a>
    ·
    <a href="#modes">推荐模式</a>
    ·
    <a href="#workflow">工作流程</a>
    ·
    <a href="#structure">项目结构</a>
  </p>

  <p>
    <img alt="version" src="https://img.shields.io/badge/version-v1.0.0-2EA043?style=for-the-badge" />
    <img alt="license" src="https://img.shields.io/badge/license-Apache--2.0-0969DA?style=for-the-badge" />
    <img alt="audience" src="https://img.shields.io/badge/audience-Backend%20%2F%20AI%20Agent-F97316?style=for-the-badge" />
    <img alt="workflow" src="https://img.shields.io/badge/workflow-Source%20Verified-7C3AED?style=for-the-badge" />
    <img alt="codex skill" src="https://img.shields.io/badge/Codex-Skill-111827?style=for-the-badge" />
  </p>
</div>

> 程序员牛肉出品：一个面向后端、AI Agent 和求职项目表达的 Codex Skill。它不是项目链接合集，而是“项目筛选 + 源码验证 + 简历表达”的完整工作流。

---

<a id="problem"></a>

## 它解决什么问题？

很多求职者不是找不到开源项目，而是不知道什么项目真的值得写进简历。

常见问题包括：

- 只会按 star 数找项目，最后选到过热、同质化或不适合自己的项目
- 容易把 demo、教程复刻、浅层 CRUD、插件壳子当成简历项目
- 不知道项目里哪些模块有技术难点，哪些只是普通功能实现
- 简历写法容易虚，面试官一追问源码、链路、状态、异常处理就露怯
- AI Agent 项目很多，但真正有业务数据、状态流转和用户价值的很少

牛肉项目雷达把“找项目”变成一个可验证的决策流程：先搜索候选池，再做业务价值筛选，再让用户确认短名单，最后拉取源码做证据验证，并输出简历表达。

---

## 核心能力

- **项目搜索**：从 GitHub / Web 搜索当前可用的后端项目和业务型 AI Agent 项目
- **候选池分桶**：覆盖电商交易、CRM / ERP、协作办公、工单客服、知识库、Agent 工作流等不同方向
- **反热门陷阱**：不迷信 star 数，主动覆盖中等热度和细分领域项目
- **浅层项目淘汰**：默认排除 demo、薄封装、纯框架、浏览器插件、简单聊天机器人和浅层 CRUD
- **源码证据验证**：最终入选项目前必须拉取本地源码，不能只靠 README、网页描述或模型记忆判断
- **简历写法生成**：输出项目简介、代码验证摘要、负责功能 / 技术难点、建议改造方向和面试可追问点
- **双格式交付**：默认生成 Markdown 和 PDF 两个版本的项目简历包

---

## 适合谁用？

- 想找后端实习 / 校招项目的学生
- 想从普通 CRUD 项目升级到业务闭环项目的后端候选人
- 想把 AI Agent 项目写进简历，但不知道怎么选题的人
- 想准备 Java / Python / Go / Node.js 等后端项目亮点的人
- 想让简历项目经得起“你看过源码吗？”“异常怎么处理？”“状态怎么流转？”这类追问的人

---

<a id="modes"></a>

## 推荐模式

使用时必须明确选择一种推荐模式。

| 模式 | 说明 |
| --- | --- |
| `agent-only` | 只推荐完整业务型 AI Agent 项目 |
| `backend-only` | 只推荐传统软件后端项目，默认排除 IoT / 硬件接入类项目 |
| `mixed` | 推荐一个 Agent 项目 + 一个传统软件后端项目 |
| `safe-mode` | 推荐容易落地、依赖少、部署成本低的项目 |
| `challenge-mode` | 推荐更难、更有差异化、更适合深度改造的项目 |

如果用户没有指定推荐模式，Skill 会先反问，不会直接开始搜索或推荐。

---

<a id="workflow"></a>

## 工作流程

```text
用户画像与推荐模式
        ↓
联网搜索 GitHub / Web
        ↓
构建多样化候选池
        ↓
README probe 与项目类型初筛
        ↓
输出 3-4 个短名单项目
        ↓
用户确认方向
        ↓
拉取 GitHub 仓库到本地
        ↓
基于源码提取证据点
        ↓
生成 Markdown / PDF 简历项目包
```

关键原则：README 和网页搜索只能用于前置筛选，最终“负责功能 / 技术难点”必须来自本地源码验证。

---

<a id="usage"></a>

## 使用示例

当前 Skill 名称为：`backend-agent-project-selector`。

### 快速使用

```text
Use $backend-agent-project-selector 推荐模式：mixed 帮我找 1 个业务型 Agent 项目和 1 个传统软件后端项目，并生成简历写法。
```

### 完整输入

```text
Use $backend-agent-project-selector
推荐模式：mixed
技术栈：Java / Python
目标岗位：后端实习
时间预算：2 周
背景水平：普通本科，无实习
项目偏好：一个新奇 Agent 项目，一个有业务闭环的扎实后端项目
避开方向：浏览器插件、简单聊天机器人、IoT、硬件接入、太难部署
输出需求：推荐 + 简历写法 + 面试题 + 改造计划
```

### 如果只想找 Java 后端项目

```text
Use $backend-agent-project-selector 推荐模式：backend-only 我投 Java 后端实习，想找一个比普通商城更有技术深度的业务项目。
```

### 如果只想找 Agent 项目

```text
Use $backend-agent-project-selector 推荐模式：agent-only 我想找一个能写进简历的业务型 AI Agent 项目，不要浏览器插件和简单聊天机器人。
```

---

## 输出内容

默认会在当前工作区生成：

- `backend-agent-project-shortlist.md`：短名单确认稿，包含候选项目、选择理由和主要风险
- `backend-agent-project-resume-pack.md`：最终简历项目包，包含源码证据、负责功能、技术难点和改造建议
- `backend-agent-project-resume-pack.pdf`：适合阅读和分享的 PDF 版本
- `repo-source-manifest.json`：本地源码拉取结果和仓库状态记录

最终简历项目包通常包含：

- 结论先行的项目推荐
- 候选池和淘汰理由
- 推荐模式和多样性说明
- 每个项目的定位、已有能力和风险
- 本地源码验证摘要
- 80-120 字项目简介
- 5-6 条负责功能 / 技术难点
- 建议简历功能点
- 二次改造计划和面试追问方向

---

<a id="structure"></a>

## 项目结构

```text
backend-agent-project-selector/
├── SKILL.md                         # Skill 主入口与核心规则
├── agents/
│   └── openai.yaml                  # Codex Skill UI 元数据
└── references/
    ├── 用户输入模板.md              # 推荐模式和用户画像输入模板
    ├── 执行流程.md                  # 搜索、筛选、确认、验证、输出流程
    ├── 筛选评分.md                  # 项目筛选和评分标准
    ├── 简历写法.md                  # 简历 bullet、技术难点和面试表达规则
    ├── 输出模板.md                  # 最终 Markdown 简历包结构
    ├── 规则索引.md                  # 规则文档索引
    ├── search_github_candidates.py  # GitHub 候选池搜索脚本
    ├── pull_github_repos.py         # 本地源码拉取与 manifest 生成脚本
    └── markdown_to_pdf.py           # Markdown 转 PDF 脚本
```

---

## 安装方式

把 `backend-agent-project-selector` 目录复制到 Codex 的 Skills 目录即可。

### macOS / Linux

```bash
mkdir -p ~/.codex/skills
cp -R backend-agent-project-selector ~/.codex/skills/
```

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force .\backend-agent-project-selector "$env:USERPROFILE\.codex\skills\"
```

安装后，在 Codex 中使用：

```text
Use $backend-agent-project-selector 推荐模式：mixed 帮我找项目。
```

---

## 设计原则

### 1. 先选方向，再找项目

Skill 不会默认替用户选择推荐模式。找项目之前必须先明确是 `agent-only`、`backend-only`、`mixed`、`safe-mode` 还是 `challenge-mode`。

### 2. 优先业务闭环，不迷信技术名词

真正适合简历的项目，不只是“用了 Redis / MQ / ES / LLM”，而是能讲清楚业务数据、状态流转、异常处理、权限边界和用户价值。

### 3. 源码证据优先

最终负责功能必须能在本地源码、配置、测试、迁移脚本或运行入口中找到证据。README、GitHub 页面和网页搜索只能作为前置筛选依据。

### 4. 建议改造不能冒充已完成

Skill 会区分“已有能力”“建议改造”“可写入简历”。没有实现的内容，只能作为完成改造后可写的建议，不会包装成已完成成果。

---

## 和普通项目推荐列表有什么不同？

| 普通项目列表 | 牛肉项目雷达 |
| --- | --- |
| 按 star 数排序 | 按简历价值、业务闭环、源码证据和可改造空间筛选 |
| 给一堆链接 | 先给短名单，再让用户确认方向 |
| 看 README 就推荐 | 最终必须拉取本地源码验证 |
| 容易推荐 demo / 框架 / 插件 | 默认淘汰薄封装、浅层 CRUD 和工具壳 |
| 只告诉你项目名 | 生成项目简介、技术难点、简历 bullet 和改造计划 |
| 容易写虚 | 区分已有能力和建议改造，避免把没做过的内容写成成果 |

---


## 适用边界

这个 Skill 适合帮助用户选择和表达项目，但不会替用户伪造经历。

它会告诉你：

- 哪些能力是原项目已有的
- 哪些功能适合你二次改造
- 哪些内容完成改造后可以写进简历
- 哪些点面试官可能会追问

真正写进简历前，仍然需要你完成对应阅读、部署、改造或实现。

---

## 作者

程序员牛肉

专注于后端、AI Agent、简历项目设计和求职项目表达。

---

## English Summary

Backend Agent Resume Scout is a Codex Skill for students and early-career engineers who need resume-worthy backend or business-grade AI Agent projects. It searches GitHub / Web, filters out shallow demos and thin wrappers, verifies final candidates against local source code, and generates Markdown / PDF resume project packages with evidence-backed talking points.
