import time
import requests
import pandas as pd
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def crawl_bilibili(keyword, max_count=10):
    url = f"https://search.bilibili.com/all?keyword={keyword}"
    data_list = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".video-item")[:max_count]
        for item in items:
            title = item.select_one(".title").get("title", "").strip()
            desc = item.select_one(".des")
            desc_text = desc.get_text(strip=True) if desc else ""
            link = "https:" + item.select_one("a").get("href", "")
            data_list.append({
                "content": title + " " + desc_text,
                "source": "哔哩哔哩",
                "url": link,
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"B站采集异常: {e}")
    return data_list

def crawl_github(keyword, max_count=10):
    url = f"https://github.com/search?q={keyword}&type=issues"
    data_list = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".search-title")[:max_count]
        for item in items:
            title = item.get_text(strip=True)
            link = "https://github.com" + item.select_one("a").get("href", "")
            data_list.append({
                "content": title,
                "source": "GitHub Issues",
                "url": link,
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"GitHub采集异常: {e}")
    return data_list

def crawl_juejin(keyword, max_count=10):
    url = f"https://juejin.cn/search?query={keyword}"
    data_list = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".title")[:max_count]
        for item in items:
            title = item.get_text(strip=True)
            data_list.append({
                "content": title,
                "source": "掘金",
                "url": "",
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"掘金采集异常: {e}")
    return data_list

def crawl_zhihu(keyword, max_count=10):
    url = f"https://www.zhihu.com/search?type=content&q={keyword}"
    data_list = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select(".ContentItem-title")[:max_count]
        for item in items:
            title = item.get_text(strip=True)
            data_list.append({
                "content": title,
                "source": "知乎",
                "url": "",
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"知乎采集异常: {e}")
    return data_list

def run_full_crawler():
    keywords = ["AI 痛点", "AI 效率工具", "AI 应用需求", "AI 创业机会"]
    all_data = []
    
    for kw in keywords:
        all_data.extend(crawl_bilibili(kw, 8))
        all_data.extend(crawl_github(kw, 3))
        all_data.extend(crawl_juejin(kw, 3))
        all_data.extend(crawl_zhihu(kw, 3))
    
    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df
