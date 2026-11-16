import time
import requests
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def crawl_bilibili(keyword, max_count=12):
    data_list = []
    try:
        url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("data", {}).get("result", [])[:max_count]
        for item in items:
            title = item.get("title", "").replace('<em class="keyword">', '').replace('</em>', '')
            desc = item.get("description", "")
            link = f"https://www.bilibili.com/video/{item.get('bvid', '')}"
            data_list.append({
                "content": title + " " + desc,
                "source": "哔哩哔哩",
                "url": link,
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"B站采集异常: {e}")
    return data_list

def crawl_github(keyword, max_count=12):
    data_list = []
    try:
        url = f"https://api.github.com/search/issues?q={keyword}&per_page={max_count}&sort=updated"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("items", [])[:max_count]
        for item in items:
            title = item.get("title", "")
            link = item.get("html_url", "")
            data_list.append({
                "content": title,
                "source": "GitHub Issues",
                "url": link,
                "time": item.get("updated_at", "")
            })
        time.sleep(1.5)
    except Exception as e:
        print(f"GitHub采集异常: {e}")
    return data_list

def crawl_juejin(keyword, max_count=12):
    data_list = []
    try:
        url = "https://api.juejin.cn/search_api/v1/search"
        params = {
            "keyword": keyword,
            "limit": max_count,
            "sort_type": 0
        }
        resp = requests.post(url, json=params, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("data", [])[:max_count]
        for item in items:
            title = item.get("article_info", {}).get("title", "")
            desc = item.get("article_info", {}).get("brief_content", "")
            data_list.append({
                "content": title + " " + desc,
                "source": "掘金",
                "url": f"https://juejin.cn/post/{item.get('article_id', '')}",
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"掘金采集异常: {e}")
    return data_list

def crawl_zhihu(keyword, max_count=12):
    data_list = []
    try:
        url = f"https://www.zhihu.com/api/v4/search_v3?t=general&q={keyword}&limit={max_count}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        items = data.get("data", [])[:max_count]
        for item in items:
            obj = item.get("object", {})
            title = obj.get("title", "")
            desc = obj.get("excerpt", "")
            data_list.append({
                "content": title + " " + desc,
                "source": "知乎",
                "url": "",
                "time": ""
            })
        time.sleep(1.5)
    except Exception as e:
        print(f"知乎采集异常: {e}")
    return data_list

def run_full_crawler():
    keywords = [
        "AI文案生成", "AI智能客服", "AI数据分析", "AI办公自动化",
        "AI教育辅导", "AI工业质检", "AI医疗辅助", "AI电商运营",
        "AI代码助手", "AI设计作图", "AI语音转写", "AI内容审核",
        "AI智能推荐", "运维监控", "供应链优化", "客户管理"
    ]
    all_data = []
    
    for kw in keywords:
        all_data.extend(crawl_bilibili(kw, 12))
        all_data.extend(crawl_github(kw, 12))
        all_data.extend(crawl_juejin(kw, 12))
        all_data.extend(crawl_zhihu(kw, 12))
        time.sleep(0.8)

    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df
