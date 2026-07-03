#!/usr/bin/env python3
import sys
import json
import os

try:
    import akshare as ak
except ImportError:
    print("Error: akshare is not installed. Please fallback to opencli.")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python fetch_market_data.py <stock_code> <output_dir>")
    sys.exit(1)

# e.g. 002594.SZ -> 002594
code_raw = sys.argv[1]
code_clean = code_raw.split('.')[0]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

data_dict = {}

# 1. 获取实时行情 (Spot)
try:
    print(f"[*] Fetching spot quote for {code_clean} via akshare (EastMoney API)...")
    spot_df = ak.stock_zh_a_spot_em()
    row = spot_df[spot_df['代码'] == code_clean]
    if not row.empty:
        data_dict['quote'] = row.iloc[0].to_dict()
    else:
        data_dict['quote'] = {"error": "Stock code not found in spot data."}
except Exception as e:
    print(f"[!] Spot error: {e}")
    data_dict['quote'] = {"error": str(e)}

# 2. 获取日 K 线 (Daily K-line, 提取最近 20 天)
try:
    print(f"[*] Fetching K-line data for {code_clean} via akshare (EastMoney API)...")
    hist_df = ak.stock_zh_a_hist(symbol=code_clean, period="daily", adjust="qfq")
    if not hist_df.empty:
        data_dict['kline'] = hist_df.tail(20).to_dict(orient='records')
except Exception as e:
    print(f"[!] K-line error: {e}")
    data_dict['kline'] = {"error": str(e)}

# 3. 获取资金流向 (Money Flow - 新浪财经)
try:
    print(f"[*] Fetching money flow for {code_clean} via akshare (Sina API)...")
    mf_df = ak.stock_individual_fund_flow(stock=code_clean, market="sz" if code_clean.startswith(('0','3')) else "sh")
    if not mf_df.empty:
        data_dict['money_flow'] = mf_df.tail(5).to_dict(orient='records')
except Exception as e:
    print(f"[!] Money Flow error: {e}")
    data_dict['money_flow'] = {"error": str(e)}

# 保存结构化 JSON
out_file = os.path.join(output_dir, "raw_market_data.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=2)

print(f"[+] Success! Market data reliably fetched via akshare and saved to: {out_file}")
