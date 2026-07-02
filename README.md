<div align="center">

# 🔎 机构级 A/H 股买方投研与决策智能体 (Company Researcher V5)
### —— 从“写研报”全面进化为“买方投资操作系统 (CIO)”

**“Research Agent 永远不能决定买不买，只有 Portfolio Manager 才能。”**

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![版本](https://img.shields.io/badge/Version-v5.0-success)
![架构](https://img.shields.io/badge/Architecture-Decision_First-ff69b4)
![引擎](https://img.shields.io/badge/Reasoning_Core-DeepSeek_Expert-red)
</div>

---

## 🚀 V5.0 史诗级重构：Decision First（决策优先）

在 V4 时代，本智能体是一个极其优秀的“研究员”（排雷、打分、红队攻击）。但我们意识到，个人投资者最缺的不是一份 3000 字的研报，而是**“现在应该持有什么、卖什么、或者空仓等待？”**

因此，V5.0 架构引入了**独立的首席投资官智能体 (Portfolio Manager)**，彻底颠覆了传统 AI 投研的玩法：
- **新增候选池 (Watchlist Engine)**：AI 不再是一次性问答，而是主动管理你的持仓与观察池。
- **候选竞争 (Candidate Competition)**：买小米？AI 会自动将小米与你当前持仓的腾讯进行 1V1 PK，告诉你是否值得替换。
- **资金来源铁律 (Position Source)**：严禁凭空建议“买入”。如果要买，AI 必须告诉你资金从哪里来（卖谁？用多少现金？）。
- **拒绝交易优先 (No Trade)**：大多数时候最好的操作是等待，AI 现已具备强大的空仓定力。

最终，系统不再长篇大论，而是输出一张极简、致命的 **💼 Portfolio Decision Card**。

---

## 🌟 V5.0 全景决策流图 (Workflow)

```mermaid
graph TD
    A([输入标的/唤醒 AI]) --> B[Step 0-11: Data & Research Agent]
    B --> C[Step 12: Quant Scorer 评级]
    
    C -->|携带报告与分数| D{👑 唤醒 Portfolio Manager}
    
    subgraph 资产组合引擎 (Portfolio Engine)
        P1[(当前持仓 portfolio.yaml)] -.-> D
        P2[(候选池 watchlist.yaml)] -.-> D
        P3[风险预算 Risk Budget] -.-> D
    end
    
    D --> E1{组合暴露审查}
    E1 -->|行业/风格/波动率| E2
    
    D --> F1{候选竞争}
    F1 -->|小米 VS 腾讯| F2
    
    D --> G1{资金来源判定}
    
    E2 & F2 & G1 --> H[输出最终 Decision Card]
    H -->|BUY / WAIT / REJECT| I([结束流程])
    
    classDef red fill:#f9d0c4,stroke:#333,stroke-width:2px;
    class D red;
    classDef blue fill:#d4edda,stroke:#333,stroke-width:2px;
    class P1,P2,P3 blue;
```

---

## 💼 核心功能一：Portfolio Manager 的 5 个灵魂拷问
研究员只负责找证据，而 Portfolio Manager (CIO) 必须强制回答：
1. **是否值得占用稀缺的风险预算？**（超预算一律拒绝建仓）
2. **是否值得替换已有持仓？**（Candidate Competition）
3. **买完以后，整个组合是变得更好还是更糟？**（测算行业集中度 HHI）
4. **当前市场环境，是否应该保持现金？**
5. **在当前的 Watchlist 里，它排第一吗？**

## 📊 核心功能二：组合暴露度智能计算 (Exposure Analysis)
告别凭感觉买股，系统会自动帮你监控：
- **行业集中度 (HHI)**：比如，科技权重暴增到 45% 时，系统会强制拦截买单，提示“暂停增加科技股”。
- **风格暴露**：自动计算你的“成长/价值/红利”比例，指出“成长风格过重”。
- **市场/Beta 暴露**：计算当前 A股/港股 的比例，提示你潜在的美元利率风险或高波动风险。

## 🎯 核心功能三：极致输出 —— Decision Card
V5 摒弃了研究报告的繁文缛节，直接把最值钱的结论拍在你的脸上：

```text
=========================
💼 Portfolio Decision Card
=========================
【当前风险预算】: 100 | 已用: 82 | 本次预估: +15 
【决策结论】: WAIT

【组合暴露度变动评估】:
- 行业集中度: 科技 (40% → 55%) ⚠️ 严重超标
- 综合组合评分: 86 → 84 (下降)

【候选竞争 (Candidate Competition)】:
- 小米 VS 腾讯：成长性占优，但现金流质量不及腾讯。
- 结论: 暂不值得替换当前核心持仓。

【CIO 最终寄语】:
本周无需交易。耐心等待小米跌至 20 日均线，或等腾讯释放出部分仓位。
=========================
```

---

## 📂 V5.0 最佳实践目录结构
为了实现“个人投资操作系统”的目标，项目结构已进行彻底重构：

```text
company-researcher/
├── SKILL.md                   # 🌟 主入口：定义了从数据到 CIO 决策的完整 SOP
├── README.md                  # 📖 说明书
│
├── agents/                    # 🤖 智能体矩阵
│   ├── Research_Agent.md      # 基本面研究员
│   ├── Quant_Scorer.md        # 量化裁判员
│   ├── Red_Team.md            # 红队风控刺客 (DeepSeek 内核)
│   └── Portfolio_Manager.md   # ⭐⭐⭐⭐⭐ (V5新增) 首席投资官 (CIO)
│
├── portfolio/                 # 💼 组合配置引擎 (V5核心)
│   ├── portfolio.yaml         # 你真实的当前持仓、权重、现金比例
│   └── watchlist.yaml         # 候选池与自动触发器
│
├── china_market/              # 🇨🇳 A股底层限制逻辑
└── hk_market/                 # 🇭🇰 港股底层限制逻辑
```

---

## 🚀 快速开始与配置指南

### 第一步：安装依赖
你需要安装 `opencli` 才能激活底层数据抓取与 DeepSeek 红队外脑：
```bash
npm i -g opencli
opencli auth login
```

### 第二步：配置你的真实持仓 (极度重要)
在使用 V5 之前，请务必打开 `portfolio/portfolio.yaml`，填入你当前的真实仓位和现金比例。
然后再打开 `portfolio/watchlist.yaml`，把你想买的股票和心理价位（Trigger）填进去。

### 第三步：向 AI 下达决策指令
```text
“CIO，帮我看看现在能买寒武纪吗？”
“用最新的季报复盘一下茅台，决定一下是否需要从组合里把它踢出去。”
```

---
## 📜 License
MIT License © nihong
