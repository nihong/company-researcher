import akshare as ak
try:
    df = ak.stock_yjbb_em(date="20231231")
    print(df.head(1).columns.tolist())
except Exception as e:
    print("Error:", e)
