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
    keywords = ["AI文案生成", "AI智能客服", "AI数据分析", "AI办公自动化",
        "AI教育辅导", "AI工业质检", "AI医疗辅助", "AI电商运营",
        "AI代码助手", "AI设计作图", "AI语音转写", "AI内容审核",
        "AI智能推荐", "AI运维监控", "AI供应链优化", "AI客户管理"]
    all_data = []
    
    for kw in keywords:
        all_data.extend(crawl_bilibili(kw, 12))
        all_data.extend(crawl_github(kw, 12))
        all_data.extend(crawl_juejin(kw, 12))
        all_data.extend(crawl_zhihu(kw, 12))
        time.sleep(0.8)

    df = pd.DataFrame(all_data)
    df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df
