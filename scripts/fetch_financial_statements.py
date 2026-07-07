import os
import sys
import json
import urllib.request
import traceback
import datetime

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super(DateEncoder, self).default(obj)

# Monkey Patch for macOS
urllib.request.getproxies = lambda: {}
os.environ["no_proxy"] = "*"
os.environ["NO_PROXY"] = "*"

try:
    import akshare as ak
except ImportError:
    print("Error: akshare is not installed.")
    sys.exit(1)

if len(sys.argv) < 3:
    print("Usage: python fetch_financial_statements.py <stock_code> <output_dir>")
    sys.exit(1)

code_raw = sys.argv[1]
code_clean = code_raw.split('.')[0]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)

data_dict = {}

print(f"[*] Fetching financial abstract for {code_clean} via akshare...")
try:
    # 尝试使用新浪财经核心财务指标 (Sina financial indicators)
    # stock_financial_analysis_indicator 需要 sz/sh 前缀
    prefix = "sh" if code_clean.startswith(('6')) else ("hk" if code_clean.endswith('.HK') else "sz")
    symbol = f"{prefix}{code_clean.replace('.HK', '')}"
    
    try:
        # 1. 尝试新浪财务分析指标
        df_sina = ak.stock_financial_analysis_indicator(symbol=symbol)
        if not df_sina.empty:
            data_dict["financial_abstract"] = df_sina.head(4).to_dict(orient='records')
            print("[+] Success fetched Sina financial abstract.")
        else:
            raise ValueError("Empty data from Sina")
    except Exception as e:
        print(f"[-] Sina API failed: {e}")
        # 2. 回退到东方财富业绩报表 (获取最新日期的)
        current_year = datetime.datetime.now().year
        # 尝试当年一季报或去年年报
        fallback_date = f"{current_year}0331"
        try:
            df_em = ak.stock_yjbb_em(date=fallback_date)
        except Exception:
            fallback_date = f"{current_year - 1}1231"
            df_em = ak.stock_yjbb_em(date=fallback_date)
            
        row = df_em[df_em['股票代码'] == code_clean]
        if not row.empty:
            record = row.to_dict(orient='records')[0]
            record['report_date'] = fallback_date
            
            # --- 深度财务排雷指标抓取 (Cash Flow & Balance Sheet) ---
            print(f"[*] Fetching deep financial metrics (Cash flow & Balance sheet) for {fallback_date}...")
            try:
                # 抓取现金流量表
                df_xj = ak.stock_xjll_em(date=fallback_date)
                xj_row = df_xj[df_xj['股票代码'] == code_clean]
                if not xj_row.empty:
                    xj_record = xj_row.to_dict(orient='records')[0]
                    record['OCF'] = xj_record.get('经营性现金流-现金流量净额', 'N/A')
                    record['CAPEX'] = xj_record.get('投资性现金流-现金流量净额', 'N/A')
                    print("[+] Success fetched Cash Flow")
                
                # 抓取资产负债表
                df_zc = ak.stock_zcfz_em(date=fallback_date)
                zc_row = df_zc[df_zc['股票代码'] == code_clean]
                if not zc_row.empty:
                    zc_record = zc_row.to_dict(orient='records')[0]
                    record['Total_Assets'] = zc_record.get('资产-总资产', 'N/A')
                    record['Total_Liabilities'] = zc_record.get('负债-总负债', 'N/A')
                    record['Cash_Equivalents'] = zc_record.get('资产-货币资金', 'N/A')
                    print("[+] Success fetched Balance Sheet")
            except Exception as inner_e:
                print(f"[-] Deep finance fetch failed: {inner_e}")
                record['cash_flow_warning'] = "⚠️ 深度财务报表抓取超时或无数据，请大模型填写 N/A，严禁自行编造。"
            
            data_dict["financial_abstract"] = [record]
            print("[+] Success fetched EastMoney YJBB.")
        else:
            raise ValueError("Empty data from EM")
            
except Exception as e:
    print(f"[!] Financial API error: {e}")
    # 注入兜底数据结构防止大模型幻觉
    data_dict["financial_abstract"] = {
        "error": f"Failed to fetch financial data: {str(e)}",
        "warning": "⚠️ 系统未获取到财务数据，严禁大模型自行捏造营收、净利润等具体数值！请在研报中标注 '数据缺失'。"
    }

out_file = os.path.join(output_dir, "financial_statements.json")
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(data_dict, f, ensure_ascii=False, indent=2, cls=DateEncoder)

print(f"[+] Success! Financial data saved to: {out_file}")
