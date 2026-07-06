#!/usr/bin/env python3
import sys
import os
import json
import time

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("Error: akshare or pandas is not installed.")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python scan_sector_rotation.py <output_dir>")
    sys.exit(1)

output_dir = sys.argv[1]
os.makedirs(output_dir, exist_ok=True)

print("[*] 正在拉取全市场板块实时概况...")
try:
    spot_df = ak.stock_board_industry_spot_em()
    # 列名大致为: ['排名', '板块名称', '板块代码', '最新价', '涨跌额', '涨跌幅', '总市值', '换手率', '上涨家数', '下跌家数', '领涨股票', '领涨股票-涨跌幅']
except Exception as e:
    print(f"Error fetching industry spot: {e}")
    sys.exit(1)

# 清洗数据
spot_df = spot_df.dropna(subset=['板块名称', '涨跌幅'])

# 简单拥挤度计算方案：利用涨跌幅、换手率
# 由于 spot 接口不直接提供具体成交金额数值（如果有的话可以用），我们可以用换手率作为短期情绪/拥挤度的核心代理指标。
# 换手率极高 (例如 > 5%) 往往代表情绪过热。

spot_df['涨跌幅'] = pd.to_numeric(spot_df['涨跌幅'], errors='coerce')
spot_df['换手率'] = pd.to_numeric(spot_df['换手率'], errors='coerce')

# 排序并提取三种状态
# 1. 刚启动 (左侧/温和右侧): 涨幅处于 1% ~ 3%，换手率适中 (1% ~ 3%)，说明温和放量上涨。
starting = spot_df[(spot_df['涨跌幅'] > 0.5) & (spot_df['换手率'] > 1.0) & (spot_df['换手率'] < 3.0)]
starting = starting.sort_values(by='涨跌幅', ascending=False).head(5)

# 2. 高潮预警 (拥挤度爆表): 换手率极高 (全市场排名前列)，通常 > 4% 甚至更高。
crowded = spot_df.sort_values(by='换手率', ascending=False).head(5)

# 3. 冰点区 (无人问津): 跌幅大，换手率极低
freezing = spot_df.sort_values(by='涨跌幅', ascending=True).head(5)

results = {
    "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "total_sectors_scanned": len(spot_df),
    "starting_sectors": starting[['板块名称', '涨跌幅', '换手率', '领涨股票']].to_dict(orient='records'),
    "crowded_warning_sectors": crowded[['板块名称', '涨跌幅', '换手率', '领涨股票']].to_dict(orient='records'),
    "freezing_sectors": freezing[['板块名称', '涨跌幅', '换手率', '领涨股票']].to_dict(orient='records')
}

out_file = os.path.join(output_dir, "sector_radar_scan.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[+] 板块扫描完成！发现 {len(starting)} 个启动板块, {len(crowded)} 个过热预警板块。")
print(f"[+] 数据已保存至: {out_file}")
