# 一句话提 GitHub issue

[**English**](./README.md) · 中文

> **一句话进去，一条 GitHub issue 出来。**
> One-Sentence Issue · File an issue in one sentence.

跟你的 AI 助手说一句哪儿坏了，它就去：**冻住现场**（期间别刷新、别重启、别更新、别关窗口）、
抓你机器上够得着的证据、扫一遍草稿里有没有你不想公开的东西、按目标仓库的语言写出报告、
用 `gh` 提交，**最后把正文拉回来核对一遍**，确认真的发出去了，再把链接交给你。

**任何软件、游戏、网页都能用**——不限于 AI 工具。但有两个前提：**项目开源、托管在 GitHub 上**
（`gh` 只能往 GitHub 提 issue），以及你的环境够、权限你也给。

---

## 30 秒上手

安装：

```bash
gh skill install qjzzsky/one-sentence-issue --agent claude-code
```

（不在这 48 种 agent 里的，比如 Hermes，走 `git clone` 到技能目录。）

然后一句话：

> 这个页面点提交一直转圈，控制台报了个 undefined，帮我提上去。

接下来：

```
正在搜集相关信息 —— 期间别刷新、别重启、别更新、别关窗口。
      ↓  只读取证        ↓  隐私扫描
      ↓  查重 + 用仓库模板  ↓  写正文
      ↓  你过目（整块）    ↓  提交 + 传截图 + 读回核对
https://github.com/<owner>/<repo>/issues/123
```

**在你看到完整正文并点头之前，什么都不会发出去。**

---

## 安装

| 路径 | 命令 |
|---|---|
| **A. `gh skill`**（Claude Code、Cursor、Codex、Copilot、Gemini CLI 等 48 种） | `gh skill install qjzzsky/one-sentence-issue --agent claude-code` |
| **B. Hermes** | `hermes skills install qjzzsky/one-sentence-issue` |
| **C. 手动 clone** | `git clone https://github.com/qjzzsky/one-sentence-issue.git <你的技能目录>/one-sentence-issue` |

> 技能目录**因平台而异**（Windows 与 Unix 不是一个路径），用 `hermes skills list` 看你的在哪。
> `gh skill install` 不带技能名时只会**列出**仓库里的技能，脚本化调用要写全：
> `gh skill install qjzzsky/one-sentence-issue one-sentence-issue --agent claude-code`

**依赖**：`gh` 命令行（[cli.github.com](https://cli.github.com)）+ `gh auth login`。
没有它也能用——会降级成把写好的正文整块交给你，你自己贴网页。

---

## 十二步

| # | 步骤 | 说明 |
|---|---|---|
| 1 | 听懂你那句话 | 什么坏了、哪个仓库、你手上有什么 |
| 2 | 定目标仓库 | **只有两个来源**：本地 `git remote`，或你给的链接/仓库名 |
| 3 | 能力探测 | 决定能抓到第几层——只有聊天窗口就停在 L0 |
| 4 | 冻现场 | "期间别刷新、别重启、别更新、别关窗口" |
| 5 | 分层取证 L0→L3 | **只读**；抓不到的标 `not captured` |
| 6 | 查重 | 已有同类 → 建议补评论而不是新开 |
| 7 | 用仓库自己的模板 | 有模板就照它写；**模板要日志就先问你** |
| 8 | 隐私扫描 | 一级提醒一次 · **二级（密钥/token）要你二次确认** |
| 9 | 写正文 | 六段，按目标仓库的语言 |
| 10 | **你过目** | 完整标题 + 正文，点头才发 |
| 11 | 提交、传图、读回 | `gh issue create --attach …` 再 `gh issue view …` 复扫 |
| 12 | （可选）盯回复 | `gh issue view <n> --comments` |

---

## 各处用什么语言

| 层 | 语言 |
|---|---|
| AI 回复你 | 你用什么语言，它就用什么语言 |
| issue 正文 | 跟目标仓库走，默认英文 |
| `SKILL.md` + `references/` | 英文——那是给 AI 读的，不是给你读的 |
| 本 README | 中文在此 · English in [README.md](./README.md) |

---

## 隐私：提醒制，默认不主动抓、不主动传

| 级别 | 例子 | 做法 |
|---|---|---|
| 1 — 身份/位置/历史 | 用户名、本机路径、聊天记录 | **提醒一次**，你决定 |
| 2 — 密钥 | 密码、API key、token、私钥 | **二次确认**：先讲后果，你再决定 |

你自己粘贴的内容同样提醒。你被提醒后仍坚持要发，就按你说的发。

它**永远不会替你跑日志上传命令**。遇到模板强制要日志时，它会问你——包括"不传也行，
issue 照发"这个选项。

---

## 边界

- **只支持 GitHub。** 目标不在 GitHub（Discord、论坛、客服）→ 给你整块正文自己贴，那是成功不是失败。
- **只读取证。** 不写、不重启、不改配置——那些会破坏正在记录的现场。
- **不点头不发。** 第 10 步是硬闸门。
- **标签会是空的。** 外部贡献者没权限打标签，有的模板还引用了不存在的标签——仓库机器人几分钟内会补，属正常。

---

## 真实案例

### 1. AI 助手本身出问题 —— 在对话里一句话报

**场景：使用 GitHub 上的开源 AI 助手出了问题。** 装上这个技能，用一句话告诉 AI 哪里出了问题 —— 它会自动抓证据、扫描、总结，替你向开发者提交 issue。

- **[#137132](https://github.com/NousResearch/hermes-agent/issues/137132)** — 桌面端批量提问卡片的推荐项自带浅色高亮，看着像已选中，用户跳过点击后提交，模型反馈有一题没选。（建议类）
- **[#136914](https://github.com/NousResearch/hermes-agent/issues/136914)** — 聊天读到一半，视口自己跳到上半段；查出 3 行缺排序索引，读取改走了另一条路径。
- **[#134290](https://github.com/NousResearch/hermes-agent/issues/134290)** — 切换会话再切回来，已完成的对话在界面上消失，但数据库里一行没少。
- **[#127316](https://github.com/NousResearch/hermes-agent/issues/127316)** — 某个渠道投递失败后重启标记一直不清，其他正常渠道就再也收不到「网关在线」提示。

### 2. 装来的技能出问题 —— 直接去那个技能的仓库提

**场景：从 GitHub 装的技能不好使。** 复现步骤你手上就有，那个技能自己的仓库正是维护者看的地方。

- **[#21](https://github.com/isjiamu/gzh-design-skill/issues/21)** — 装来的公众号排版技能粘贴到编辑器时触发「内容结构检测」弹窗：深色模式不认渐变背景，建议默认纯色。（已关闭，作者已处理）

五条全部由本工作流产出：只读取证 → 隐私扫描 → `gh` 提交 → 读回核对。

---

## 和已有的比，多了什么

| 已有的 | 它做什么 | 我们多的 |
|---|---|---|
| 绑定单一项目的 issue 技能 | 只给那个项目提 | **任意仓库**，`git remote` 或你给的链接定位 |
| "深挖完存本地" | 写个文件，不提交 | **真的提交**，然后读回核对 |
| 单项目的 bug report 技能 | 脱敏草稿、一个项目 | **L0→L3 分层取证**、可执行的隐私扫描器、模板适配 |

---

## 目录

```
one-sentence-issue/
├── README.md / README.zh-CN.md
├── LICENSE · .gitignore
├── AGENTS.md, CLAUDE.md          短指引，指向 SKILL.md
└── skills/
    └── one-sentence-issue/
        ├── SKILL.md              工作流本体（AI 读）
        ├── references/           证据分层 · 隐私规则 · 正文结构 · 坑
        ├── templates/            bug / feature 正文骨架
        └── scripts/
            ├── privacy_scan.py   两级扫描器（只含通用规则，不含真实姓名）
            └── file_issue.sh     查重 → 扫描 → 提交 → 读回 → 复扫
```

AI 需要的东西**全在 `skills/one-sentence-issue/` 里面** —— `gh skill install` 复制的正是这个
目录，放外面的话装完就缺扫描器和模板。

---

## 关于作者

**qjzzsky · 曲靖中中**

- GitHub：[qjzzsky](https://github.com/qjzzsky)
- 个人网页：[qjzzsky.com](https://qjzzsky.com)
- 哔哩哔哩：[space.bilibili.com/1546459](https://space.bilibili.com/1546459)
- 微博：[weibo.com/u/1074366780](https://weibo.com/u/1074366780)

---

## 协议

[MIT](./LICENSE) © 2026 qjzzsky。
引用其他开源项目的片段，出处与协议已在 `skills/one-sentence-issue/references/pitfalls.md` 标注。
