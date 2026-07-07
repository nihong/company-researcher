import requests
import sys
import json
import os

def fetch_xueqiu(stock_code):
    # 雪球需要带有特定 User-Agent，有时候还需要 cookies。
    # 这里我们使用简易的 API 伪装进行请求。
    # 雪球搜索 API 示例 (此处为降级演示，真实抓取需要维持 Session)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://xueqiu.com",
        "Referer": f"https://xueqiu.com/S/{stock_code}"
    }
    
    # 获取初始 Cookie
    try:
        session = requests.Session()
        session.get("https://xueqiu.com/", headers=headers, timeout=5)
        
        # 尝试通过雪球搜索接口获取帖子 (简易版)
        search_url = f"https://xueqiu.com/query/v1/search/status.json?q={stock_code}&count=10&page=1"
        res = session.get(search_url, headers=headers, timeout=5)
        
        if res.status_code == 200:
            data = res.json()
            comments = []
            for item in data.get('list', []):
                text = item.get('text', '')
                if text:
                    # 简易去除 HTML 标签
                    import re
                    clean_text = re.sub(r'<[^>]+>', '', text)
                    comments.append(clean_text)
            return {"source": "Xueqiu", "status": "success", "comments": comments}
        else:
            return {"source": "Xueqiu", "status": "failed", "error": f"HTTP {res.status_code}"}
    except Exception as e:
        return {"source": "Xueqiu", "status": "error", "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fetch_xueqiu_sentiment.py <stock_code>")
        sys.exit(1)
    
    code = sys.argv[1]
    # 格式化代码，如 600143 -> SH600143
    if code.startswith('6'):
        code = f"SH{code}"
    elif code.startswith('0') or code.startswith('3'):
        code = f"SZ{code}"
        
    result = fetch_xueqiu(code)
    print(json.dumps(result, ensure_ascii=False, indent=2))
