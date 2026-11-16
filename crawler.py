import time
import requests
import pandas as pd

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def crawl_bilibili(keyword, max_count=20):
    data_list = []
    try:
        headers = BASE_HEADERS.copy()
        headers["Referer"] = "https://search.bilibili.com/all"
        # 采集第1、2页，单关键词合计40条
        for page in [1, 2]:
            url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={keyword}&page={page}"
            resp = requests.get(url, headers=headers, timeout=10)
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
            time.sleep(1.2)
    except Exception as e:
        print(f"B站采集异常: {e}")
    return data_list

def crawl_github(keyword, max_count=30):
    data_list = []
    try:
        headers = BASE_HEADERS.copy()
        headers["Accept"] = "application/vnd.github.v3+json"
        # 单页拉满30条，减少请求次数，降低限流风险
        url = f"https://api.github.com/search/issues?q={keyword}&per_page={max_count}&sort=updated"
        resp = requests.get(url, headers=headers, timeout=15)
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
        time.sleep(2.5)
    except Exception as e:
        print(f"GitHub采集异常: {e}")
    return data_list

def crawl_juejin(keyword, max_count=15):
    data_list = []
    try:
        url = "https://api.juejin.cn/search_api/v1/search"
        params = {
            "query": keyword,
            "limit": max_count,
            "sort_type": 0
        }
        resp = requests.get(url, params=params, headers=BASE_HEADERS, timeout=10)
        data = resp.json()
        items = data.get("data", [])[:max_count]
        for item in items:
            article_info = item.get("article_info", {})
            title = article_info.get("title", "")
            desc = article_info.get("brief_content", "")
            article_id = item.get("article_id", "")
            data_list.append({
                "content": title + " " + desc,
                "source": "掘金",
                "url": f"https://juejin.cn/post/{article_id}" if article_id else "",
                "time": ""
            })
        time.sleep(1)
    except Exception as e:
        print(f"掘金采集异常: {e}")
    return data_list

def crawl_zhihu(keyword, max_count=10):
    data_list = []
    try:
        headers = BASE_HEADERS.copy()
        headers["Referer"] = "https://www.zhihu.com/search"
        url = f"https://www.zhihu.com/api/v4/search_v3?t=general&q={keyword}&limit={max_count}"
        resp = requests.get(url, headers=headers, timeout=10)
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
        time.sleep(2)
    except Exception as e:
        print(f"知乎采集异常: {e}")
    return data_list

def run_full_crawler():
    # 30个核心关键词，覆盖8大赛道，兼顾覆盖面与重复率
    keywords = [
        # 通用生产力
        "AI文案生成", "AI办公自动化", "AI语音转写", "AI内容审核",
        # 研发技术
        "AI代码助手", "AI运维监控", "AI数据分析", "AI测试自动化",
        # 电商运营
        "AI智能客服", "AI电商运营", "AI用户画像", "AI选品分析",
        # 教育学习
        "AI教育辅导", "AI作业批改", "AI口语陪练", "AI个性化学习",
        # 设计内容
        "AI设计作图", "AI视频剪辑", "AIPPT生成", "AI海报制作",
        # 工业制造
        "AI工业质检", "AI供应链优化", "AI预测性维护", "AI缺陷检测",
        # 医疗健康
        "AI医疗辅助", "AI医学影像", "AI病历分析", "AI健康管理",
        # 商业管理
        "AI客户管理", "AI智能推荐", "AI风控检测"
    ]
    all_data = []
    
    for kw in keywords:
        all_data.extend(crawl_bilibili(kw, 20))
        all_data.extend(crawl_github(kw, 30))
        all_data.extend(crawl_juejin(kw, 15))
        all_data.extend(crawl_zhihu(kw, 10))
        time.sleep(1)

    df = pd.DataFrame(all_data)
    if not df.empty:
        df = df.drop_duplicates(subset=["content"]).reset_index(drop=True)
    return df
