import baostock as bs
import pandas as pd
bs.login()
codes = ["sh.600276", "sh.688235", "sh.688506"]
for c in codes:
    rs = bs.query_history_k_data_plus(c, "code,peTTM,pbMRQ", start_date='2026-07-06', end_date='2026-07-06', frequency="d", adjustflag="3")
    while (rs.error_code == '0') & rs.next():
        print(rs.get_row_data())
bs.logout()
