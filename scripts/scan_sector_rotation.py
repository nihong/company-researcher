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
def fetch_with_fallback():
    try:
        print("    -> [Tier 1] 尝试抓取东方财富接口...")
        df = ak.stock_board_industry_spot_em()
        if not df.empty and '板块名称' in df.columns:
            return df, "EastMoney"
        else:
            print("       [!] 东财接口返回数据格式异常 (可能触发了软拦截)")
    except Exception as e:
        print(f"       [!] 东财接口请求失败 ({e})")
        
    print("    -> [Tier 2] 尝试无缝切换至新浪财经接口...")
    try:
        df = ak.stock_sector_spot(indicator="新浪行业")
        if not df.empty and '板块' in df.columns:
            df = df.rename(columns={'板块': '板块名称', '涨跌幅': '涨跌幅', '领涨股票名称': '领涨股票'})
            if '领涨股票' not in df.columns:
                df['领涨股票'] = "-"
            # 严禁造假：如果新浪接口没有换手率，强行置为 None，不得捏造数据！
            df['换手率'] = None
            return df, "Sina"
        else:
            print("       [!] 新浪接口返回数据格式异常")
    except Exception as e:
        print(f"       [!] 新浪接口降级失败: {e}")
        
    return None, None

def fetch_with_retry_and_fallback():
    max_retries = 3
    for i in range(max_retries):
        if i > 0:
            print(f"  => 所有数据源均熔断，触发防爬虫降速休眠 {2*i}s (第 {i} 次重试)...")
            time.sleep(2 * i)
            
        print(f"  -> 第 {i+1} 次全源轮询:")
        df, source = fetch_with_fallback()
        if df is not None:
            return df, source
            
    return None, None

spot_df, source = fetch_with_retry_and_fallback()
if spot_df is None:
    print("Error: 所有数据源(Tier 1 & Tier 2)均被封锁，请稍后再试或更换代理。")
    sys.exit(1)

print(f"[*] 成功从 {source} 获取 {len(spot_df)} 个板块数据。")

# 清洗数据
spot_df = spot_df.dropna(subset=['板块名称', '涨跌幅'])

# 简单拥挤度计算方案：利用涨跌幅、换手率
# 由于 spot 接口不直接提供具体成交金额数值（如果有的话可以用），我们可以用换手率作为短期情绪/拥挤度的核心代理指标。
# 换手率极高 (例如 > 5%) 往往代表情绪过热。

spot_df['涨跌幅'] = pd.to_numeric(spot_df['涨跌幅'], errors='coerce')
spot_df['换手率'] = pd.to_numeric(spot_df['换手率'], errors='coerce')
spot_df['换手率'] = spot_df['换手率'].fillna(0)

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
