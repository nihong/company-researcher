import sys
import json
import asyncio
import re
from datetime import datetime, timedelta

try:
    from playwright.async_api import async_playwright
except ImportError:
    print(json.dumps({"error": "Playwright 未安装。请执行: pip install playwright && playwright install chromium"}, ensure_ascii=False))
    sys.exit(1)

def filter_noise(text, weight):
    """过滤水军噪音"""
    text = text.strip()
    if len(text) < 5 and weight < 5: return False
    if "直播" in text or "点击查看" in text or "裙" in text or "加微" in text: return False
    # 纯数字或重复字符
    if re.match(r'^\d+$', text): return False
    return True

async def extract_metric(element, selector):
    try:
        val = await element.query_selector(selector)
        if val:
            txt = await val.inner_text()
            nums = re.findall(r'\d+', txt)
            if nums: return int(nums[0])
    except:
        pass
    return 0

async def scrape_forums(stock_code):
    results = {"Xueqiu": [], "Tonghuashun": [], "EastMoney": [], "Taoguba": [], "Status": "Success"}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # 拦截不必要的资源加载以加速
        await page.route("**/*.{png,jpg,jpeg,gif,css,woff2}", lambda route: route.abort())

        # 1. 打通雪球 (Xueqiu) - 包含权重提取
        try:
            prefix = "SH" if str(stock_code).startswith('6') else "SZ"
            xq_url = f"https://xueqiu.com/S/{prefix}{stock_code}"
            await page.goto(xq_url, timeout=15000)
            await page.wait_for_selector(".timeline__item", timeout=5000)
            
            items = await page.query_selector_all(".timeline__item")
            for item in items[:15]:
                try:
                    content_el = await item.query_selector(".timeline__item__content")
                    text = await content_el.inner_text() if content_el else ""
                    
                    time_el = await item.query_selector(".timeline__item__time")
                    time_str = await time_el.inner_text() if time_el else "刚刚"
                    
                    # 雪球的转评赞通常在 bottom
                    likes = await extract_metric(item, ".like") or await extract_metric(item, "[title='赞']")
                    comments = await extract_metric(item, ".comment") or await extract_metric(item, "[title='评论']")
                    
                    weight = likes * 2 + comments
                    
                    # 水军过滤与时间过滤（简化版时间判定：只要不是包含'2022'或远古年份即算近48小时内，实战中需更精确）
                    if filter_noise(text, weight) and "202" not in time_str:
                        results["Xueqiu"].append({
                            "text": text.strip().replace('\n', ' '),
                            "time": time_str,
                            "likes": likes,
                            "comments": comments,
                            "weight": weight
                        })
                except Exception:
                    pass
        except Exception as e:
            results["Xueqiu"].append({"error": f"抓取失败: {str(e)}"})

        # 2. 打通东方财富股吧 (EastMoney)
        try:
            prefix = "sh" if str(stock_code).startswith('6') else "sz"
            em_url = f"http://guba.eastmoney.com/list,{stock_code}.html"
            await page.goto(em_url, timeout=15000)
            
            await page.wait_for_selector(".articleh", timeout=5000)
            items = await page.query_selector_all(".articleh")
            for item in items[:20]:
                try:
                    title_el = await item.query_selector(".title")
                    text = await title_el.inner_text() if title_el else ""
                    
                    # 东财股吧结构: .l1(阅读), .l2(评论), .l6(时间)
                    comments = await extract_metric(item, ".l2")
                    reads = await extract_metric(item, ".l1")
                    likes = int(reads / 100) # 估算
                    weight = likes * 2 + comments
                    
                    time_el = await item.query_selector(".l6")
                    time_str = await time_el.inner_text() if time_el else ""
                    
                    if filter_noise(text, weight):
                        results["EastMoney"].append({
                            "text": text.strip().replace('\n', ' '),
                            "time": time_str,
                            "likes": likes,
                            "comments": comments,
                            "weight": weight
                        })
                except Exception:
                    pass
        except Exception as e:
            results["EastMoney"].append({"error": f"东财抓取失败: {str(e)}"})

        await browser.close()
        
    # 对提取到的帖子按权重降序排列
    for k in ["Xueqiu", "EastMoney"]:
        if results[k] and isinstance(results[k][0], dict) and "weight" in results[k][0]:
            results[k] = sorted(results[k], key=lambda x: x.get("weight", 0), reverse=True)[:10]

    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少股票代码参数"}))
        sys.exit(1)
        
    code = sys.argv[1].replace('.SH', '').replace('.SZ', '')
    
    out = asyncio.run(scrape_forums(code))
    print(json.dumps(out, ensure_ascii=False, indent=2))
