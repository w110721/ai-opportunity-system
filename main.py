import streamlit as st
import pandas as pd
from llm_core import full_pipeline
from crawler import run_full_crawler
from clean_text import clean_dataframe

st.set_page_config(page_title="AI应用场景智能挖掘与机会评估系统", layout="wide")
st.title("AI应用场景智能挖掘与机会评估系统")
st.caption("数睿思竞赛本科A题作品 | 多源采集 · 智能识别 · 量化评估")

tab1, tab2, tab3 = st.tabs(["📥 数据采集与清洗", "🔍 单条文本分析", "📊 批量数据评估"])

with tab1:
    st.subheader("多源数据采集")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("一键启动全渠道采集", type="primary"):
            with st.spinner("正在采集数据，请稍候..."):
                df = run_full_crawler()
                st.session_state["raw_data"] = df
                st.success(f"采集完成，共获取 {len(df)} 条数据")
                st.dataframe(df, use_container_width=True)
    
    with col2:
        if st.button("一键清洗数据集"):
            if "raw_data" in st.session_state:
                df_clean = clean_dataframe(st.session_state["raw_data"])
                st.session_state["clean_data"] = df_clean
                st.success(f"清洗完成，剩余有效数据 {len(df_clean)} 条")
                st.dataframe(df_clean, use_container_width=True)
            else:
                st.warning("请先采集数据或上传数据集")

    st.divider()
    st.subheader("上传本地数据集")
    uploaded_file = st.file_uploader("上传CSV格式的数据集", type="csv")
    if uploaded_file is not None:
        df_upload = pd.read_csv(uploaded_file)
        st.session_state["clean_data"] = df_upload
        st.success("文件上传成功")
        st.dataframe(df_upload, use_container_width=True)

with tab2:
    st.subheader("单条文本需求研判")
    input_text = st.text_area("请输入待分析的文本内容", height=120, placeholder="例如：做短视频每天要写几十条文案，太费时间了，有没有AI工具能帮忙")
    if st.button("开始分析评估", type="primary"):
        if not input_text.strip():
            st.warning("请输入文本内容")
        else:
            with st.spinner("正在分析中..."):
                result = full_pipeline(input_text)
                col_a, col_b = st.columns([2, 1])
                with col_a:
                    st.markdown("#### 识别结果")
                    st.write(f"**是否为有效需求**：{result.get('is_valid', '未知')}")
                    st.write(f"**需求描述**：{result.get('desc', '-')}")
                    st.write(f"**所属行业**：{result.get('industry', '-')}")
                    st.write(f"**当前痛点**：{result.get('pain_point', '-')}")
                    st.write(f"**匹配AI能力**：{result.get('ai_ability', '-')}")
                    st.write(f"**评估结论**：{result.get('conclusion', '-')}")
                with col_b:
                    st.markdown("#### 价值评分")
                    score1 = result.get('score_demand', 0)
                    score2 = result.get('score_feasibility', 0)
                    score3 = result.get('score_value', 0)
                    total = result.get('total_score', 0)
                    st.metric("综合得分", f"{total} 分")
                    st.write(f"需求强度：{score1} 分")
                    st.write(f"AI可行性：{score2} 分")
                    st.write(f"价值潜力：{score3} 分")
                    
                    scores = pd.DataFrame({
                        '维度': ['需求强度', 'AI可行性', '价值潜力'],
                        '得分': [score1, score2, score3]
                    })
                    import plotly.express as px
                    fig = px.bar(scores, x='维度', y='得分', range_y=[0, 10], color='维度')
                    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("批量数据评估")
    if st.button("开始批量评估", type="primary"):
        if "clean_data" not in st.session_state:
            st.warning("请先上传或采集数据集")
        else:
            df = st.session_state["clean_data"]
            results = []
            progress_bar = st.progress(0)
            for i, row in df.iterrows():
                text = str(row.get("content", row.iloc[0]))
                res = full_pipeline(text)
                res["原始文本"] = text
                results.append(res)
                progress_bar.progress((i+1)/len(df))
            
            result_df = pd.DataFrame(results)
            st.session_state["final_result"] = result_df
            st.success("批量评估完成")
            st.dataframe(result_df.sort_values("total_score", ascending=False), use_container_width=True)
            
            csv = result_df.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label="下载评估结果CSV",
                data=csv,
                file_name="ai_opportunity_result.csv",
                mime="text/csv"
            )
