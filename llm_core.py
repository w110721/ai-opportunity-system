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
    你是AI应用场景评估专家，请分析下面这段文本，判断是否包含可落地的AI应用需求，并完成结构化评估。
    待分析文本：{text}
    
    请严格按照JSON格式输出，不要输出额外解释，字段如下：
    1. is_valid：是否为有效真实需求，值为"是"或"否"
    2. desc：一句话概括需求内容
    3. industry：所属行业/场景
    4. pain_point：当前存在的核心痛点
    5. ai_ability：匹配的AI技术能力
    6. score_demand：需求强度得分，0-10分整数
    7. score_feasibility：AI技术可行性得分，0-10分整数
    8. score_value：商业价值潜力得分，0-10分整数
    9. total_score：综合得分，按需求强度35%、可行性35%、价值30%加权计算，保留1位小数
    10. conclusion：20字以内的评估结论
    """
    raw = call_llm(prompt)
    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)
        return result
    except:
        return {
            "is_valid": "识别失败",
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
