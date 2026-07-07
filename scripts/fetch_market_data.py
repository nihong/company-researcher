import json
import os
import datetime
import urllib.request
# 【终极防线】Monkey Patch：彻底阻断 macOS 底层 SystemConfiguration 代理读取
# 在 Mac 环境下，requests 底层会绕过 os.environ 强制去读系统的全局网络代理配置。
# 直接重写 getproxies，强行返回空字典，实现真正的无死角直连！
urllib.request.getproxies = lambda: {}
os.environ["no_proxy"] = "*"
os.environ["NO_PROXY"] = "*"

try:
    import akshare as ak
except ImportError:
    print("Error: akshare is not installed. Please fallback to opencli.")
    sys.exit(1)

import sys

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super(DateEncoder, self).default(obj)

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
# 轮询顺序：东方财富 -> 新浪 -> 腾讯(通过日线拼凑)
try:
    print(f"[*] Fetching spot quote for {code_clean} via akshare (EastMoney API)...")
    spot_df = ak.stock_zh_a_spot_em()
    if '代码' in spot_df.columns:
        row = spot_df[spot_df['代码'] == code_clean]
    elif 'symbol' in spot_df.columns:
        row = spot_df[spot_df['symbol'] == code_clean]
    else:
        row = spot_df.head(1)
        
    if not row.empty:
        data_dict['quote'] = row.iloc[0].to_dict()
        print("[+] Success with EastMoney")
    else:
        raise ValueError("EastMoney returned empty row.")
except Exception as e:
    print(f"[-] EastMoney Spot failed: {e}. Trying Sina...")
    try:
        spot_df = ak.stock_zh_a_spot()
        row = spot_df[spot_df['代码'] == code_clean] if '代码' in spot_df.columns else spot_df[spot_df['symbol'] == code_clean]
        if not row.empty:
            data_dict['quote'] = row.iloc[0].to_dict()
            print("[+] Success with Sina")
        else:
            raise ValueError("Sina Spot returned empty (Note: Sina Spot does not cover 688 STAR market).")
    except Exception as e2:
        print(f"[-] Sina Spot failed: {e2}. Trying Baostock (Quantitative Fallback)...")
        try:
            import baostock as bs
            import pandas as pd
            import datetime
            bs.login()
            if str(code_clean).endswith('.HK') or str(code_clean).startswith('00') and len(str(code_clean)) == 5:
                prefix = "hk."
            else:
                prefix = "sh." if str(code_clean).startswith(('6')) else "sz."
            bs_symbol = f"{prefix}{str(code_clean).replace('.HK', '')}"
            
            # Fetch latest daily data
            rs = bs.query_history_k_data_plus(bs_symbol,
                "date,code,open,high,low,close,volume,amount,turn,peTTM,pbMRQ",
                start_date=(datetime.datetime.now() - datetime.timedelta(days=10)).strftime('%Y-%m-%d'),
                frequency="d", adjustflag="3")
            data_list = []
            while (rs.error_code == '0') & rs.next():
                data_list.append(rs.get_row_data())
            bs.logout()
            
            if data_list:
                bs_df = pd.DataFrame(data_list, columns=rs.fields)
                last_row = bs_df.iloc[-1]
                data_dict['quote'] = {
                    "代码": code_clean,
                    "名称": "N/A (Baostock Fallback)",
                    "最新价": float(last_row['close']),
                    "今开": float(last_row['open']),
                    "最高": float(last_row['high']),
                    "最低": float(last_row['low']),
                    "成交量": float(last_row['volume']),
                    "成交额": float(last_row['amount']),
                    "换手率": float(last_row['turn']),
                    "市盈率-动态": float(last_row['peTTM']),
                    "市净率": float(last_row['pbMRQ']),
                    "_fallback_source": "Baostock"
                }
                print("[+] Success with Baostock (Fallback)")
            else:
                raise ValueError("Baostock returned empty.")
        except Exception as e3:
            print(f"[-] Baostock failed: {e3}. Trying Tencent (Basic Fallback via Hist)...")
            try:
                # 腾讯接口需要加 sh/sz/hk 前缀
                if str(code_clean).endswith('.HK') or str(code_clean).startswith('00') and len(str(code_clean)) == 5:
                    prefix = "hk"
                else:
                    prefix = "sh" if str(code_clean).startswith(('6')) else "sz"
                tx_symbol = f"{prefix}{str(code_clean).replace('.HK', '')}"
                tx_df = ak.stock_zh_a_hist_tx(symbol=tx_symbol)
                if not tx_df.empty:
                    last_row = tx_df.iloc[-1]
                    data_dict['quote'] = {
                        "代码": code_clean,
                        "名称": "N/A (Tencent Fallback)",
                        "最新价": last_row['close'],
                        "今开": last_row['open'],
                        "最高": last_row['high'],
                        "最低": last_row['low'],
                        "成交量": last_row['amount'],
                        "_fallback_source": "Tencent_Hist"
                    }
                    print("[+] Success with Tencent (Fallback)")
                else:
                    raise ValueError("Tencent Hist returned empty.")
            except Exception as e4:
                print(f"[!] All spot fallbacks failed. Last error: {e4}")
                data_dict['quote'] = {"error": "All spot sources failed."}

# 2. 获取日 K 线 (Daily K-line, 提取最近 20 天)
try:
    print(f"[*] Fetching K-line data for {code_clean} via akshare (EastMoney API)...")
    hist_df = ak.stock_zh_a_hist(symbol=code_clean, period="daily", adjust="qfq")
    if not hist_df.empty:
        data_dict['kline'] = hist_df.tail(20).to_dict(orient='records')
        print("[+] Success with EastMoney K-line")
    else:
        raise ValueError("EastMoney K-line returned empty.")
except Exception as e:
    print(f"[-] EastMoney K-line failed: {e}. Trying Tencent...")
    try:
        if str(code_clean).endswith('.HK') or str(code_clean).startswith('00') and len(str(code_clean)) == 5:
            prefix = "hk"
        else:
            prefix = "sh" if str(code_clean).startswith(('6')) else "sz"
        tx_symbol = f"{prefix}{str(code_clean).replace('.HK', '')}"
        hist_df = ak.stock_zh_a_hist_tx(symbol=tx_symbol)
        if not hist_df.empty:
            data_dict['kline'] = hist_df.tail(20).to_dict(orient='records')
            print("[+] Success with Tencent K-line")
        else:
            raise ValueError("Tencent K-line returned empty.")
    except Exception as e2:
        print(f"[!] K-line error: {e2}")
        data_dict['kline'] = {"error": str(e2)}

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
    json.dump(data_dict, f, ensure_ascii=False, indent=2, cls=DateEncoder)

print(f"[+] Success! Market data reliably fetched via akshare and saved to: {out_file}")
