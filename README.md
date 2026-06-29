<div align="center">

# 🔎 机构级 A 股买方投研智能体 (Company Researcher v3.0)

### 防幻觉铁律 · 资金面博弈 · 政策周期解析 · 产业链图谱 · 量化排雷裁判

*「不再像卖方一样写干瘪的空话研报，而是像顶级买方一样做杀伐果断的交易决策」*

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![类型](https://img.shields.io/badge/Type-Agent_Skill-black)
![版本](https://img.shields.io/badge/Version-v3.0.0-success)
![生态](https://img.shields.io/badge/Ecosystem-Antigravity%20%7C%20Claude%20%7C%20DeepSeek-7c3aed)
![状态](https://img.shields.io/badge/Status-Production_Ready-brightgreen)

</div>

---

## 🔥 核心痛点与降维打击

绝大多数开源的“AI 炒股助手”或“财报分析插件”在 A 股实战中都是**无效的**。它们只会生硬地背诵美国股市的“价值投资”教条，却对 A 股独有的**政策博弈、游资接力、大股东抽血**一无所知。

本项目（Company Researcher v3.0）是一次**彻底的重构**，专为高度博弈的中国 A 股市场特化定制！

| 传统 AI 炒股助手的通病 | 🎯 本 Agent (v3.0) 的降维打击解法 |
|:---|:---|
| **只看财报，不懂博弈** | 引入 **China Equity Adaptation** 层：重点扫描龙虎榜、公募抱团、机构大宗交易与游资情绪。 |
| **生搬硬套美股教条** | 引入 **Policy Cycle** 模块：精准定调行业当前处于政策的“吹风期”、“落地期”还是“退潮期”。 |
| **模棱两可的“建议关注”** | 独创 **A_Share_Quant_Scorer** 微型智能体：以 **DeepSeek 实战法则**为核心的量化裁判员，坚决执行一票否决与排雷，只做右侧交易。 |
| **长文本注意力遗忘** | 强制引入 `<evidence_ledger>`（证据账本）XML 标签，输出报告前在后台死锁关键财务数字。 |
| **文字堆砌，缺乏直观感** | 强制调用 **Mermaid** 引擎，全自动渲染清晰的“上下游产业链流转”与“核心利润流向”图谱。 |
| **AI 常见的“幻觉编造”** | 设定“研究宪法八条铁律” + 强制执行红蓝军多空互搏 + 文末强制打印 **Firewall Check (防火墙清单)**。 |

---

## 🛠 核心能力矩阵

### 1. 🔍 深度定性引擎 (The Qualitative Engine)
基于 12 步严苛 SOP，从接到任务到输出报告绝不跳步。从“大基金三期落地”等宏观政策，到“黄磷/硫磺涨价对毛利率挤压”的微观颗粒度，精准刻画。

### 2. 🧮 铁血量化裁判 (A_Share_Quant_Scorer)
在定性报告生成后，触发末端量化裁判员。
- **动态权重**：自动识别大盘处于“进攻市”还是“防守市”，动态调整基本面与动量的权重。
- **六维雷达**：输出酷炫的 ASCII 进度条（涵盖基本面、景气度、估值、资金、政策、动量）。
- **一票否决排雷**：遇到流动性陷阱、巨额解禁或立案调查，总分直接清零！

### 3. 🛡️ 红队攻击与自我证伪 (Red Team Attack)
每一份研报必须在末尾进行自我证伪：“我这份报告最大的事实错误可能在哪里？最可能打脸我的事件是什么？”——确保在极其复杂的 A 股环境中保持极端清醒。

---

## 🚀 快速开始

### 安装指南
针对使用 Antigravity 或类似 AI 终端框架的用户，直接将本仓库克隆至全局定制化目录即可自动生效：

```bash
mkdir -p ~/.gemini/config/skills
cd ~/.gemini/config/skills/
git clone https://github.com/nihong/company-researcher.git
```

### 触发方式
安装完成后，在终端直接向您的 AI 助手输入自然语言即可极速唤醒：

```text
"帮我深度调研一下兴福电子，并给出量化打分。"
"以买方视角分析海光信息的投资机会。"
"对比茅台和五粮液当前的资金筹码结构与政策周期。"
```

> **💡 高阶玩法 (Teamwork Preview)**: 
> 结合多模型（如同时调度 Claude 3.5 Sonnet, DeepSeek, Gemini），您可以让该 Agent 自动化抓取各大模型的独立观点，提炼出没有偏见的“终极共识”，并排版为精美的 PDF 发送到您的邮箱！

---

## 📂 项目结构

```text
company-researcher/
├── SKILL.md            # 🧠 核心指令与心智模型（包含 12 步 SOP 与宪法铁律）
├── skill.yml           # 📝 Agent 系统注册清单
├── README.md           # 📖 本文档
├── china_market/       # 🇨🇳 A股特色适配层模块
│   ├── capital_flow.md # 资金博弈与筹码结构逻辑
│   └── policy_cycle.md # 政策周期分析体系
├── industry/           # 🏭 产业链分析模块
│   └── chain_mapping.md# 景气度传导映射规则
├── agents/             # 🤖 专属子智能体 (Subagents)
│   └── A_Share_Quant_Scorer.md # 散户量化打分裁判员 (基于 DeepSeek 实战降维法则)
└── references/         # 📚 外部研报、术语与知识库缓存
```

---

## 🌟 推广与致谢
如果您觉得这个项目让您的 AI 在处理 A 股投研时变得更加“聪明且有实战价值”，请毫不吝啬地为本仓库点亮一颗 **Star ⭐️**！

欢迎在 Issues 中提出您对 A 股独有因子提取的宝贵建议。

## 📜 License
MIT License © nihong
