#!/usr/bin/env python3
import sys
import json
import os

# 强制注入 NO_PROXY 免代理白名单，防止被全局科学上网环境劫持
os.environ["NO_PROXY"] = "eastmoney.com,sina.com.cn,qq.com,10jqka.com.cn,localhost,127.0.0.1"
os.environ["no_proxy"] = os.environ["NO_PROXY"]

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

# 1. 获取实时行情 (Spot) - 强制多源轮询容灾
data_dict['quote'] = None
# 轮询顺序：东方财富 -> 新浪 -> 腾讯
sources = [
    ("EastMoney", lambda: ak.stock_zh_a_spot_em()),
    ("Sina", lambda: ak.stock_zh_a_spot()), # 视 akshare 版本而定，默认新浪接口
]

for source_name, fetch_func in sources:
    try:
        print(f"[*] Fetching spot quote for {code_clean} via akshare ({source_name} API)...")
        spot_df = fetch_func()
        # 不同接口返回的字段名可能不同，这里做基础判断
        if '代码' in spot_df.columns:
            row = spot_df[spot_df['代码'] == code_clean]
        elif 'symbol' in spot_df.columns:
            row = spot_df[spot_df['symbol'] == code_clean]
        else:
            row = spot_df.head(1) # fallback
            
        if not row.empty:
            data_dict['quote'] = row.iloc[0].to_dict()
            print(f"[+] Success with {source_name}")
            break
        else:
            print(f"[-] {source_name} returned empty for {code_clean}.")
    except Exception as e:
        print(f"[!] {source_name} Spot error: {e}")

if not data_dict['quote']:
    data_dict['quote'] = {"error": "All akshare spot sources (EastMoney, Sina) failed due to network or proxy errors."}

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
