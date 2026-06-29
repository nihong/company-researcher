<div align="center">

# 🔎 机构级 A 股买方投研智能体（Company Researcher）

### 防幻觉铁律 · 资金面博弈 · 政策周期解析 · 产业链图谱

*「不再像卖方一样写空话研报，而是像买方一样做交易决策」*

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![类型](https://img.shields.io/badge/类型-Agent%20Skill-black)
![版本](https://img.shields.io/badge/版本-v3.0.0-success)
![平台](https://img.shields.io/badge/平台-Antigravity%20·%20Claude%20·%20ChatGPT%20·%20Gemini-7c3aed)

</div>

---

## 🎯 这是什么

一个面向 **Antigravity / Claude / ChatGPT / Gemini** 等 AI Agent 的投研技能（Skill）。

**v3.0 版本是一次彻底的重构**。基于最新大模型的特性，我们为其增加了 **China Equity Adaptation Layer（中国股票市场适配层）**。它抛弃了传统的“估值+基本面”的美股分析套路，真正融入了 A 股的核心驱动力：**基本面 + 政策周期 + 产业趋势 + 资金博弈 + 主题情绪**。

| 痛点 | 本 Skill (v3.0) 的解法 |
|------|----------------|
| **只有基本面，忽略资金面** | 新增 **Capital Flow 模块**：分析龙虎榜、公募抱团、大股东减持。 |
| **忽略中国政策导向** | 新增 **Policy Cycle 模块**：定调政策是支持、中性还是压制。 |
| **缺乏散户可执行的交易纪律** | 新增 **A_Share_Quant_Scorer 微型智能体**：基于 DeepSeek 铁血法则的量化打分裁判员，一票否决垃圾股，只做右侧交易。 |
| **长文本注意力遗忘** | 引入 `<evidence_ledger>` (证据账本) XML标签强制锁定思考核心。 |
| **报告全是干瘪文字** | 强制使用 **Mermaid** 语法绘制产业链全景图与利润流向图。 |
| **幻觉（编造数据）** | 研究宪法八条铁律 + 输出前强制打印 Firewall Check 结果。 |

## 🚀 快速开始

### 安装

将本仓库克隆到 Antigravity 的全局技能目录：

```bash
cd ~/.gemini/config/skills/
git clone https://github.com/nihong/company-researcher.git
```

### 使用

安装后，在 Antigravity 中直接对话即可触发：

```
帮我调研一下宁德时代
以买方视角分析海光信息的投资机会
对比茅台和五粮液的资金筹码结构
```

AI 会自动加载本 Skill，执行 12 步 SOP，并输出带可视化图表的实战研报。

## 📂 目录结构 (v3.0)

```
company-researcher/
├── SKILL.md            # 核心指令文件（包含12步SOP与宪法铁律）
├── skill.yml           # 技能清单
├── README.md           # 本文件
├── china_market/       # 【新增】A股特色适配层模块
│   ├── capital_flow.md # 资金博弈与筹码结构
│   └── policy_cycle.md # 政策周期分析
├── industry/           # 【新增】产业链分析模块
│   └── chain_mapping.md# 景气度传导映射
├── agents/             # 【新增】专属子智能体 (Subagents)
│   └── A_Share_Quant_Scorer.md # 散户量化打分裁判员 (基于 DeepSeek 实战法则)
└── references/         # 知识库
```

## 📜 License

MIT
