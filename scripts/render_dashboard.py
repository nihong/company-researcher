#!/usr/bin/env python3
import csv
import os
import sys

if len(sys.argv) < 2:
    print("Usage: python render_dashboard.py <workspace_dir>")
    sys.exit(1)

workspace = sys.argv[1]
path = os.path.join(workspace, 'tracking/ledger.csv')
readme_path = os.path.join(workspace, 'README.md')

if not os.path.exists(path):
    print(f"Error: ledger.csv not found at {path}")
    sys.exit(1)

rows = []
with open(path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['日期'].strip():
            rows.append(row)

# Sort by Date descending
rows.sort(key=lambda x: x['日期'], reverse=True)
top_20 = rows[:20]

md_content = '''<div align="center">
  <h1>🛰️ 量化投研决策指挥舱 (Terminal V4.2)</h1>
  <img src="https://img.shields.io/badge/AI_Agent-company--researcher-blueviolet?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Strategy-A_Share_Quant-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/System_Status-Online-brightgreen?style=for-the-badge" />
</div>

> **极客决策舱**：以下数据由底层追踪台账 `ledger.csv` 实时渲染。为追求极简决策，**已自动过滤噪音，仅提纯展示最新调研的 Top 20 份作战简报**。

## ⚔️ 实时作战台 (Latest 20 Decisions)

| 🗓 调研日期 | 🎯 标的 (行业) | 💡 评级 (得分) | 🚦 资金状态 | ⚡️ 买方核心决策 | 🔗 研报归档 |
| :--- | :--- | :--- | :--- | :--- | :--- |
'''

for r in top_20:
    date = r.get('日期', '').strip()
    code = r.get('股票代码', '').strip()
    name = r.get('股票名称', '').strip()
    industry = r.get('所属行业', '').strip()
    rating = r.get('评级', '').strip()
    score = r.get('量化评分', '').strip()
    light = r.get('资金灯', '').strip()
    decision = r.get('买方决策', '').strip()
    link = r.get('研报路径', '').strip()
    
    # 评级高亮渲染
    if rating == 'S': rating_fmt = '**[S] 满仓强推**'
    elif rating == 'A': rating_fmt = '**[A] 逢低增持**'
    elif rating == 'B': rating_fmt = '[B] 观望等待'
    elif rating == 'C': rating_fmt = '~~[C] 压降仓位~~'
    elif rating == 'D': rating_fmt = '❌ **[D] 坚决清仓**'
    else: rating_fmt = rating
    
    # 标的格式化
    target_fmt = f"**{name}** <code>{code}</code><br>*{industry}*"
    
    # 评分格式化
    score_fmt = f"{rating_fmt}<br>{score}分" if score and score != '0' else rating_fmt
    
    # 决策高亮
    if '买' in decision or '建仓' in decision or '增持' in decision:
        decision = f"**{decision}**"
    elif '规避' in decision or '清仓' in decision or '减持' in decision:
        decision = f"**{decision}**"
        
    link_fmt = f"[📂 查看]( {link} )" if link and link != 'N/A' else "-"
    
    md_content += f"| {date} | {target_fmt} | {score_fmt} | {light} | {decision} | {link_fmt} |\n"

md_content += '''
---
*Powered by `company-researcher` AI Agent | 数据引擎：EastMoney & Xueqiu | 渲染引擎：Python Auto-Render*
'''

with open(readme_path, 'w', encoding='utf-8') as f:
    f.write(md_content)

print(f"README.md successfully rendered at {readme_path}")
