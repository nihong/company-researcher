# A股买方外科手术级个股尽调 SOP (微服务流水线架构)

> **核心纪律**：严禁在一个长上下文中试图“一步到位”写完研报。你必须按照以下四大流水线环节逐步推进。
> **防偷懒模板约束**：最终生成的研报必须 **100% 映射** `report_template.md` 的骨架，绝不允许删除其中的表格或标题！

## 第一阶段：Data Agent (底层事实源收集)
1. **获取宏观天气预报**：调用 `python scripts/fetch_advanced_context.py <股票代码> <当前工作区>` 或读取大盘雷达 json，获取大盘情绪。
2. **三级容灾数据采集**：
   - 优先使用 `python scripts/fetch_market_data.py` 获取数据。
   - 失败则降级使用 `opencli eastmoney quote/kline/holders <股票代码> -f json`。
   - 极度失败时才使用 `search_web`。
3. **竞对抓取**：搜索同行业 Top 3 竞对的估值（PE/PB）数据，为后续表格做准备。
4. **生成唯一事实源 (`ledger.json`)**：
   清洗所有脏数据，在个股根目录下强制生成 `ledger.json`。**自此开始，后续所有推理只能 READ，严禁篡改数字。**

## 第二阶段：Logic Agent (多空建构与估值分析)
1. **绘制产业链 Mermaid 图谱**：标注利润流向与议价权。*(注：已删除冗余的波特五力纯文字分析)*
2. **财务排雷穿透**：检查营收占比、现金流、存货等核心指标，找出可能存在的“纸面富贵”。
3. **建构预期差与多空池**：
   - 列出市场一致预期与你的独立判断差异。
   - 分别穷尽列出 ≥5 条看多硬证据与 ≥5 条致命看空证据。

## 第三阶段：Red Team Agent (独立风控审查)
1. **调用风控子智能体**：调用 `invoke_subagent` 唤醒 `agents/Red_Team_Review_Agent.md`，把草稿给它审阅。
2. **提炼致命一击**：吸收红队的反馈，提炼出最能证伪当前看多逻辑的核心数据指标与时间节点。
3. **资金风控定级**：结合 T+1 交易规则，判定红黄绿微观资金灯，并明确 14:30 尾盘应对策略。

## 第四阶段：Writer & DevOps Agent (渲染与归档)
1. **套用强制模板 (Writer)**：
   - 必须严格遵循 `agents/report_template.md` 格式生成正文。
   - 在正文顶部植入 `ledger.json` 代码块。
   - 使用 `<metric id="json里的key">31.8</metric>` 包裹所有核心数据。
2. **外部程序强校验 (Firewall)**：
   - 在终端执行 `python scripts/validate_report.py <报告文件> <ledger.json>`。
   - 必须看到 `[Firewall Pass]`，否则打回重写。
3. **环境深度清理 (Hygiene)**：
   - **执行强删令**：`rm -f quote.json kline.json holders.json` 等所有中间废料，当前目录**只允许**存活 `ledger.json` 和最终的 `.md` 研报。
4. **量化台账登记与极客看板渲染**：
   - 调用 A_Share_Quant_Scorer 算分。
   - 遵守格式追加写入 `<当前工作区路径>/tracking/ledger.csv`。
   - 执行 `python scripts/render_dashboard.py <当前工作区路径>` 刷新大盘。
