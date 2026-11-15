import json
import requests

API_KEY = "你的DeepSeek_API_Key"
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"

def call_llm(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=data, timeout=30)
        resp_json = resp.json()
        return resp_json["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"调用失败: {e}")
        return ""

def full_pipeline(text):
    prompt = f"""
    你是AI应用场景评估专家，请分析下面这段文本，判断是否包含可落地的AI应用需求，并完成结构化标签抽取。
    待分析文本：{text}
    
    请严格按照JSON格式输出，不要输出额外解释，字段如下：
    1. is_valid：是否为有效真实需求，值为"是"或"否"
    2. desc：一句话概括需求内容
    3. industry：所属行业/场景
    4. pain_point：当前存在的核心痛点
    5. ai_ability：匹配的AI技术能力
    6. demand_level：需求强度档位，值为"高""中""低"三选一，依据：用户痛点强烈程度、受众规模、提及频次
    7. feasibility_level：技术可行性档位，值为"高""中""低"三选一，依据：技术成熟度、实现成本、合规风险
    8. value_level：商业价值档位，值为"高""中""低"三选一，依据：市场规模、变现效率、竞争烈度
    9. conclusion：20字以内的评估结论
    """
    
    raw = call_llm(prompt)
    
    # 默认兜底结果
    default_result = {
        "is_valid": "否",
        "desc": text[:50],
        "industry": "未识别",
        "pain_point": "-",
        "ai_ability": "-",
        "score_demand": 0,
        "score_feasibility": 0,
        "score_value": 0,
        "total_score": 0,
        "conclusion": "解析异常"
    }
    
    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)
        
        # 档位对应分数表
        score_map = {"高": 8.5, "中": 6.0, "低": 3.5}
        s_demand = score_map.get(data.get("demand_level", "低"), 3.5)
        s_feasibility = score_map.get(data.get("feasibility_level", "低"), 3.5)
        s_value = score_map.get(data.get("value_level", "低"), 3.5)
        
        # 加权计算综合得分：需求40% + 可行性30% + 价值30%
        total = round(s_demand * 0.4 + s_feasibility * 0.3 + s_value * 0.3, 1)
        
        result = {
            "is_valid": data.get("is_valid", "否"),
            "desc": data.get("desc", "-"),
            "industry": data.get("industry", "未识别"),
            "pain_point": data.get("pain_point", "-"),
            "ai_ability": data.get("ai_ability", "-"),
            "score_demand": s_demand,
            "score_feasibility": s_feasibility,
            "score_value": s_value,
            "total_score": total,
            "conclusion": data.get("conclusion", "-")
        }
        return result
        
    except Exception:
        return default_result
