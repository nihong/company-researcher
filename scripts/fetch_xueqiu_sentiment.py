import sys
import json
import asyncio
try:
    from playwright.async_api import async_playwright
except ImportError:
    print(json.dumps({"error": "Playwright 未安装。请执行: pip install playwright && playwright install chromium"}, ensure_ascii=False))
    sys.exit(1)

async def scrape_forums(stock_code):
    results = {"Xueqiu": [], "Tonghuashun": [], "EastMoney": [], "Taoguba": [], "Status": "Success"}
    
    async with async_playwright() as p:
        # 使用真实的 Chrome 浏览器内核启动，规避 WAF 防火墙
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # 1. 打通雪球 (Xueqiu)
        try:
            prefix = "SH" if str(stock_code).startswith('6') else "SZ"
            xq_url = f"https://xueqiu.com/S/{prefix}{stock_code}"
            await page.goto(xq_url, timeout=15000)
            # 等待评论区加载
            await page.wait_for_selector(".timeline__item__content", timeout=5000)
            
            # 抓取前 10 条文字内容
            comments = await page.query_selector_all(".timeline__item__content")
            for i, comment in enumerate(comments[:10]):
                text = await comment.inner_text()
                if text.strip():
                    results["Xueqiu"].append(text.strip().replace('\n', ' '))
        except Exception as e:
            results["Xueqiu"].append(f"抓取失败: {str(e)}")

        # 2. 打通同花顺股吧 (10jqka)
        try:
            ths_url = f"http://guba.10jqka.com.cn/{stock_code}/"
            await page.goto(ths_url, timeout=15000)
            
            await page.wait_for_selector(".list_title", timeout=5000)
            titles = await page.query_selector_all(".list_title")
            for i, title in enumerate(titles[:10]):
                text = await title.inner_text()
                if text.strip():
                    results["Tonghuashun"].append(text.strip().replace('\n', ' '))
        except Exception as e:
            results["Tonghuashun"].append(f"同花顺抓取失败: {str(e)}")

        # 3. 打通东方财富股吧 (EastMoney - A股散户最大阵地)
        try:
            # 东财代码有特定后缀前缀，例如 sh600143 或 sz000001
            prefix = "sh" if str(stock_code).startswith('6') else "sz"
            em_url = f"http://guba.eastmoney.com/list,{stock_code}.html"
            await page.goto(em_url, timeout=15000)
            
            # 东方财富帖子标题通常在 .title 或者 .l3 里面
            await page.wait_for_selector(".title", timeout=5000)
            em_titles = await page.query_selector_all(".title")
            for i, title in enumerate(em_titles[:15]):
                text = await title.inner_text()
                # 过滤掉置顶广告
                if text.strip() and len(text.strip()) > 3 and "直播" not in text:
                    results["EastMoney"].append(text.strip().replace('\n', ' '))
        except Exception as e:
            results["EastMoney"].append(f"东财抓取失败: {str(e)}")

        # 4. 打通淘股吧 (Taoguba - 游资与打板族阵地)
        try:
            tgb_url = f"https://www.taoguba.com.cn/quotes/{stock_code}/"
            await page.goto(tgb_url, timeout=15000)
            
            await page.wait_for_selector(".t_title", timeout=5000)
            tgb_titles = await page.query_selector_all(".t_title")
            for i, title in enumerate(tgb_titles[:10]):
                text = await title.inner_text()
                if text.strip():
                    results["Taoguba"].append(text.strip().replace('\n', ' '))
        except Exception as e:
            results["Taoguba"].append(f"淘股吧抓取失败: {str(e)}")

        await browser.close()
        
    return results

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "缺少股票代码参数"}))
        sys.exit(1)
        
    code = sys.argv[1].replace('.SH', '').replace('.SZ', '')
    
    # 运行异步爬虫
    out = asyncio.run(scrape_forums(code))
    print(json.dumps(out, ensure_ascii=False, indent=2))
