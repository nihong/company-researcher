#!/usr/bin/env python3
import sys
import os
import json
import argparse
import time

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("Error: akshare or pandas is not installed.")
    sys.exit(1)

# Argument Parsing
parser = argparse.ArgumentParser(description="扫描十倍股星辰大海白名单概念回调坑位")
parser.add_argument("--support_ma", type=int, default=20, help="支撑均线参数 (默认20日线)")
parser.add_argument("output_dir", nargs="?", default=".", help="输出目录")
args = parser.parse_args()

output_dir = args.output_dir
ma_window = args.support_ma
os.makedirs(output_dir, exist_ok=True)

# Load Whitelist
config_path = os.path.join(os.path.dirname(__file__), "..", "config", "hyper_growth_concepts.json")
if not os.path.exists(config_path):
    print(f"Error: 找不到白名单配置文件 {config_path}")
    sys.exit(1)

with open(config_path, "r", encoding="utf-8") as f:
    whitelist = json.load(f)

print(f"[*] 已加载 {len(whitelist)} 个星辰大海超级白名单: {', '.join(whitelist)}")
print(f"[*] 设定的支撑均线: {ma_window} 日线")

golden_pits = []
oscillating = []
broken = []

# Fetch Data for Whitelist Concepts Only
for concept in whitelist:
    print(f"  -> 正在侦测: {concept}...")
    df = pd.DataFrame()
    
    def fetch_concept_with_fallback(c):
        try:
            print(f"    -> [Tier 1] 尝试抓取东方财富接口...")
            res = ak.stock_board_concept_hist_em(symbol=c, adjust="qfq")
            if not res.empty:
                return res
        except Exception as e:
            print(f"       [!] 东财历史K线请求失败 ({e})")
            
        print(f"    -> [Tier 2] 尝试无缝切换至同花顺概念接口...")
        try:
            # 同花顺的列名和东财类似，直接取用。注意同花顺年份传参要求
            res = ak.stock_board_concept_hist_ths(symbol=c, start_year="2020")
            if not res.empty:
                # 同花顺列名统一规范为: 日期, 开盘, 最高, 最低, 收盘, 成交量, 成交额
                res = res.rename(columns={'日期': '日期', '收盘价': '收盘', '成交额': '成交额'})
                return res
        except Exception as e:
            print(f"       [!] 同花顺概念接口降级失败 ({e})")
            
        return pd.DataFrame()

    max_retries = 3
    for i in range(max_retries):
        if i > 0:
            print(f"  => 所有概念数据源均熔断，触发防爬虫降速休眠 {2*i}s (第 {i} 次重试)...")
            time.sleep(2 * i)
            
        print(f"  -> 第 {i+1} 次全源轮询侦测: {concept}")
        df = fetch_concept_with_fallback(concept)
        if not df.empty:
            break
            
    if df.empty or len(df) < ma_window:
        print(f"     [!] 无法获取 {concept} 的足够K线数据, 跳过。")
        continue
        
    df = df.tail(60).copy() # 取最近60个交易日
    df['收盘'] = pd.to_numeric(df['收盘'], errors='coerce')
    df['成交额'] = pd.to_numeric(df['成交额'], errors='coerce')
    
    # 计算均线
    ma_col = f'MA{ma_window}'
    df[ma_col] = df['收盘'].rolling(window=ma_window).mean()
    
    latest = df.iloc[-1]
    latest_close = latest['收盘']
    latest_ma = latest[ma_col]
    latest_vol = latest['成交额']
    
    # 找前高成交额 (过去10天内的高点)
    recent_10 = df.tail(10)
    peak_vol = recent_10['成交额'].max()
    
    # 判定逻辑：
    # 1. 破位危险区：收盘价跌破 MA60 且跌破 MA20 超过 3%
    if latest_close < latest_ma * 0.97:
        broken.append({
            "concept": concept,
            "status": f"跌破 {ma_window} 日线",
            "close": latest_close,
            "ma": latest_ma
        })
    # 2. 黄金坑触发区：缩量回踩 (距离 MA 偏差在 1.5% 以内，且成交量萎缩至前高的 60% 以下)
    elif abs(latest_close - latest_ma) / latest_ma < 0.015 and latest_vol < peak_vol * 0.6:
        golden_pits.append({
            "concept": concept,
            "status": f"精准回踩 {ma_window} 日线",
            "vol_shrinkage": f"{int((latest_vol/peak_vol)*100)}%",
            "close": latest_close,
            "ma": latest_ma
        })
    # 3. 趋势震荡区
    else:
        oscillating.append({
            "concept": concept,
            "status": "趋势内震荡",
            "close": latest_close,
            "ma": latest_ma
        })
            

# Save Results
results = {
    "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
    "support_ma": ma_window,
    "golden_pits": golden_pits,
    "oscillating": oscillating,
    "broken": broken
}

out_file = os.path.join(output_dir, "hyper_growth_scan.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"[+] 定点爆破完成！发现 {len(golden_pits)} 个黄金坑概念。")
print(f"[+] 数据已保存至: {out_file}")
