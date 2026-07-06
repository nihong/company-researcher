#!/usr/bin/env python3
import sys
import json
import os
import time

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("Error: akshare or pandas is not installed. Skipping advanced context.")
    sys.exit(0)

if len(sys.argv) < 3:
    print("Usage: python fetch_advanced_context.py <stock_code> <output_dir>")
    sys.exit(1)

code_raw = sys.argv[1]
code_clean = code_raw.split('.')[0]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

context_dict = {}

# 1. Macro Weather (宏观天气)
macro = {}
try:
    print("[*] Fetching Macro PMI...")
    pmi = ak.macro_china_pmi()
    macro['pmi_latest'] = pmi.iloc[0].to_dict()
except Exception as e:
    macro['pmi_error'] = str(e)

try:
    print("[*] Fetching M1/M2 Money Supply...")
    m2 = ak.macro_china_money_supply()
    macro['m1_m2_latest'] = m2.iloc[0].to_dict()
except Exception as e:
    macro['m1_m2_error'] = str(e)

try:
    print("[*] Fetching 10Y Bond Yield...")
    bond = ak.bond_china_yield()
    # 最新中债10年期国债收益率
    latest_bond = bond[bond['曲线名称'] == '中债国债收益率曲线']
    if not latest_bond.empty:
        macro['10y_bond_yield'] = latest_bond.iloc[0].to_dict()
except Exception as e:
    macro['10y_bond_error'] = str(e)

context_dict['macro_weather'] = macro


# 2. Company News & Events (财联社/机构快讯监听)
news = []
try:
    print(f"[*] Fetching real-time news for {code_clean}...")
    news_df = ak.stock_news_em(symbol=code_clean)
    if not news_df.empty:
        news = news_df.head(5)[['新闻标题', '新闻内容', '发布时间']].to_dict(orient='records')
except Exception as e:
    news = [{"error": str(e)}]

context_dict['latest_news'] = news


# 3. Industry & Valuation Profile (行业与估值基础)
profile = {}
try:
    print(f"[*] Fetching company profile for {code_clean}...")
    info = ak.stock_profile_cninfo(symbol=code_clean)
    if not info.empty:
        profile['industry'] = info.iloc[0]['所属行业']
        profile['main_business'] = info.iloc[0]['主营业务']
except Exception as e:
    profile['error'] = str(e)

# 附加：个股估值指标 (PE, PB)
try:
    print(f"[*] Fetching valuation indicators for {code_clean}...")
    val_df = ak.stock_a_indicator_lg(symbol=code_clean)
    if not val_df.empty:
        profile['valuation'] = val_df.tail(1).to_dict(orient='records')[0]
except Exception as e:
    profile['valuation_error'] = str(e)

context_dict['company_profile'] = profile

# Save to JSON
out_file = os.path.join(output_dir, "advanced_context.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(context_dict, f, ensure_ascii=False, indent=2, default=str)

print(f"[+] Success! Advanced context (Macro, News, Profile) saved to: {out_file}")
