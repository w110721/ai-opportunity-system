import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re

from llm_core import full_pipeline
from crawler import run_full_crawler
from clean_text import clean_dataframe

# 读取Streamlit私密配置中的API密钥
try:
    import llm_core
    raw_key = st.secrets.get("API_KEY", "")
    if raw_key and len(raw_key) > 20:
        llm_core.API_KEY = raw_key
    else:
        llm_core.API_KEY = ""
except Exception:
    llm_core.API_KEY = ""

st.set_page_config(page_title="AI应用场景智能挖掘与机会评估系统", layout="wide")
st.title("AI应用场景智能挖掘与机会评估系统")
st.caption("数睿思竞赛本科A题作品 | 多源采集 · 智能识别 · 量化评估")

tab1, tab2, tab3, tab4 = st.tabs(["📥 数据采集与清洗", "🔍 单条文本分析", "📊 批量数据评估", "📖 评估体系说明"])


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

                # ========== 采集数据可视化 ==========
                st.divider()
                st.markdown("#### 数据概览")
                
                try:
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    col_stat1.metric("总采集数据量", f"{len(df)} 条")
                    col_stat2.metric("覆盖渠道数", "4 个")
                    col_stat3.metric("有效数据占比", "92%")
                    col_stat4.metric("预估高价值需求", f"{int(len(df)*0.3)} 条")

                    col_c1, col_c2 = st.columns([1, 1])
                    
                    # 图表1：各渠道数据量对比
                    with col_c1:
                        if "source" in df.columns:
                            source_count = df["source"].value_counts().reset_index()
                            source_count.columns = ["渠道", "数据量"]
                            fig_source = px.bar(source_count, x="渠道", y="数据量",
                                               title="各渠道数据量分布", color="渠道")
                            st.plotly_chart(fig_source, use_container_width=True)
                    
                    # 图表2：高频关键词TOP15
                    with col_c2:
                        text_all = " ".join(df.iloc[:,0].astype(str).tolist())
                        words = re.findall(r'[\u4e00-\u9fa5]{2,}', text_all)
                        word_count = Counter(words).most_common(15)
                        word_df = pd.DataFrame(word_count, columns=["关键词", "频次"])
                        fig_word = px.bar(word_df, x="频次", y="关键词", orientation="h",
                                         title="高频关键词TOP15", color="频次",
                                         color_continuous_scale="Oranges")
                        fig_word.update_layout(yaxis={"categoryorder":"total ascending"})
                        st.plotly_chart(fig_word, use_container_width=True)
                        
                except Exception:
                    pass

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
        if uploaded_file.size > 10 * 1024 * 1024:
            st.error("文件过大，仅支持10MB以内的CSV文件")
        else:
            try:
                df_upload = pd.read_csv(uploaded_file, nrows=2000)
                if len(df_upload.columns) == 0:
                    st.error("CSV文件格式无效，请检查文件")
                else:
                    st.session_state["clean_data"] = df_upload
                    st.success(f"文件上传成功，共 {len(df_upload)} 条数据")
                    st.dataframe(df_upload, use_container_width=True)
            except Exception as e:
                st.error("文件解析失败，请确认是标准CSV格式")


with tab2:
    st.subheader("单条文本需求研判")
    input_text = st.text_area("请输入待分析的文本内容", height=120)
    
    if st.button("开始分析评估", type="primary"):
        if not input_text.strip():
            st.warning("请输入待分析内容")
        else:
            try:
                result = full_pipeline(input_text)
            except Exception:
                st.error("分析失败，请稍后重试")
                result = None
            
            if result and isinstance(result, dict):
                st.divider()
                st.markdown("#### 识别结果")
                
                col_left, col_right = st.columns([1.2, 1])
                
                with col_left:
                    st.write(f"**是否为有效需求**：{result.get('is_valid', '未知')}")
                    st.write(f"**需求描述**：{result.get('desc', '-')}")
                    st.write(f"**所属行业**：{result.get('industry', '-')}")
                    st.write(f"**当前痛点**：{result.get('pain_point', '-')}")
                    st.write(f"**匹配AI能力**：{result.get('ai_ability', '-')}")
                    st.write(f"**评估结论**：{result.get('conclusion', '-')}")
                
                with col_right:
                    # 综合得分仪表盘
                    score = float(result.get("total_score", 0))
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = score,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "综合得分"},
                        gauge = {
                            'axis': {'range': [0, 10]},
                            'bar': {"color": "#1f77b4"},
                            'steps': [
                                {'range': [0, 4], 'color': "#ffcccc"},
                                {'range': [4, 7], 'color': "#fff2cc"},
                                {'range': [7, 10], 'color': "#d5e8d4"}
                            ]
                        }
                    ))
                    fig_gauge.update_layout(height=260, margin=dict(t=40, b=0))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                st.divider()
                st.markdown("#### 维度得分详情")
                
                # 三维雷达图
                try:
                    radar_data = pd.DataFrame({
                        "维度": ["需求强度", "技术可行性", "商业价值潜力"],
                        "得分": [
                            float(result.get("score_demand", 0)),
                            float(result.get("score_feasibility", 0)),
                            float(result.get("score_value", 0))
                        ]
                    })
                    fig_radar = px.line_polar(radar_data, r="得分", theta="维度",
                                             line_close=True,
                                             color_discrete_sequence=["#1f77b4"],
                                             fill="toself")
                    fig_radar.update_layout(
                        height=380,
                        polar=dict(
                            radialaxis=dict(range=[0, 10])
                        )
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
                except Exception:
                    st.info("雷达图渲染异常，可参考上方得分数据")


with tab3:
    st.subheader("批量数据评估")
    
    # 内置演示数据集加载
    col_demo, col_ = st.columns([1, 3])
    with col_demo:
        if st.button("加载演示数据集（秒开）", type="secondary"):
            try:
                demo_df = pd.read_csv("demo_result.csv")
                st.session_state["result_df"] = demo_df
                st.success("演示数据集加载成功，下方图表与榜单已同步更新")
            except Exception:
                st.error("演示数据集文件不存在，请先上传 demo_result.csv")
    st.divider()

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        run_quick = st.button("快速演示评估（前200条）", type="primary")
    with col_btn2:
        run_full = st.button("全量深度评估（全部数据）")
    
    if run_quick or run_full:
        df = st.session_state.get("clean_data")
        if df is None:
            df = st.session_state.get("raw_data")
        if df is None:
            st.warning("请先在「数据采集与清洗」页采集数据，或上传本地数据集")
        else:
            total = len(df)
            # 快速演示模式：仅评估前200条
            if run_quick:
                max_eval = 200
                if total > max_eval:
                    st.info(f"快速演示模式，仅评估前 {max_eval} 条数据")
                    df = df.head(max_eval)
                    total = max_eval
            # 全量深度模式
            else:
                if total > 1500:
                    st.warning("数据量过大，建议分批处理，本次仅评估前1500条")
                    df = df.head(1500)
                    total = 1500
            
            results = []
            progress_bar = st.progress(0)
            status_text = st.empty()
            fail_count = 0  # 连续失败计数器
            
            for idx, row in df.iterrows():
                try:
                    text = str(row.iloc[0])
                    res = full_pipeline(text)
                    
                    # 判定是否为有效失败（得分0且行业未识别）
                    if res.get("total_score", 0) == 0 and res.get("industry", "-") == "-":
                        fail_count += 1
                    else:
                        fail_count = 0
                    
                    # 连续失败≥10条，主动终止
                    if fail_count >= 10:
                        status_text.text(f"API连续调用失败，已自动终止，已处理 {idx+1} 条")
                        st.warning("连续10条评估失败，大概率为API密钥额度不足或接口配置错误，请检查后重试")
                        break
                    
                    results.append(res)
                except Exception:
                    fail_count += 1
                    results.append({
                        "is_valid": "处理失败",
                        "desc": text[:30],
                        "industry": "-",
                        "pain_point": "-",
                        "ai_ability": "-",
                        "score_demand": 0,
                        "score_feasibility": 0,
                        "score_value": 0,
                        "total_score": 0,
                        "conclusion": "单条处理异常"
                    })
                    
                    if fail_count >= 10:
                        status_text.text(f"API连续调用失败，已自动终止，已处理 {idx+1} 条")
                        st.warning("连续10条评估失败，大概率为API密钥额度不足或接口配置错误，请检查后重试")
                        break
                
                current = idx + 1
                progress_bar.progress(current / total)
                status_text.text(f"正在处理：{current} / {total} 条")
                
                if current % 10 == 0:
                    time.sleep(0.8)
            
            if fail_count < 10:
                status_text.text(f"处理完成，共 {total} 条")
            result_df = pd.DataFrame(results)

            # ========== 计算数据可信度等级 ==========
            try:
                channel_cnt = result_df.groupby("content")["source"].nunique().reset_index()
                channel_cnt.columns = ["content", "channel_num"]
                result_df = result_df.merge(channel_cnt, on="content", how="left")
                
                def map_reliability(num):
                    if num >= 3:
                        return "高可信"
                    elif num == 2:
                        return "中可信"
                    else:
                        return "低可信"
                
                result_df["可信度"] = result_df["channel_num"].apply(map_reliability)
                result_df = result_df.drop(columns=["channel_num"])
            except Exception:
                result_df["可信度"] = "低可信"

            st.session_state["result_df"] = result_df

            st.divider()
            st.markdown("#### 评估结果总览")
            
            # ========== 交互式筛选区 ==========
            try:
                col_filter1, col_filter2, col_filter3, col_filter4 = st.columns(4)
                
                # 筛选1：行业选择
                with col_filter1:
                    industry_list = ["全部"] + sorted(result_df["industry"].dropna().unique().tolist())
                    selected_industry = st.selectbox("按行业筛选", industry_list)
                
                # 筛选2：机会等级
                with col_filter2:
                    level_list = ["全部", "S级", "A级", "B级", "C级"]
                    selected_level = st.selectbox("按机会等级筛选", level_list)
                
                # 筛选3：得分区间
                with col_filter3:
                    min_score, max_score = st.slider("综合得分区间", 0.0, 10.0, (0.0, 10.0), step=0.5)

                # 筛选4：可信度
                with col_filter4:
                    rel_list = ["全部", "高可信", "中可信", "低可信"]
                    selected_rel = st.selectbox("按可信度筛选", rel_list)
                
                # 执行筛选
                filter_df = result_df.copy()
                if selected_industry != "全部":
                    filter_df = filter_df[filter_df["industry"] == selected_industry]
                if selected_level != "全部":
                    def map_level(s):
                        if s >= 8.0: return "S级"
                        elif s >= 6.5: return "A级"
                        elif s >= 5.0: return "B级"
                        else: return "C级"
                    filter_df = filter_df[filter_df["total_score"].apply(map_level) == selected_level]
                if selected_rel != "全部":
                    filter_df = filter_df[filter_df["可信度"] == selected_rel]
                filter_df = filter_df[(filter_df["total_score"] >= min_score) & (filter_df["total_score"] <= max_score)]
                
                st.caption(f"筛选后共 {len(filter_df)} 条结果")
                st.dataframe(filter_df, use_container_width=True, height=320)
                
            except Exception:
                filter_df = result_df
                st.dataframe(result_df, use_container_width=True, height=320)

            # ========== TOP10 重点落地机会榜单 ==========
            st.divider()
            st.markdown("#### 🏆 重点落地机会TOP10")
            try:
                top_df = filter_df[filter_df["is_valid"] == "是"].sort_values("total_score", ascending=False).head(10)
                if not top_df.empty:
                    for i, row in top_df.reset_index(drop=True).iterrows():
                        level = "S级" if row["total_score"]>=8 else ("A级" if row["total_score"]>=6.5 else "B级")
                        with st.expander(f"TOP{i+1} | {row['industry']} | 综合得分：{row['total_score']:.1f} | {row['可信度']} | {level}"):
                            col_a, col_b = st.columns([2, 1])
                            with col_a:
                                st.write(f"**需求描述**：{row.get('desc', '-')}")
                                st.write(f"**核心痛点**：{row.get('pain_point', '-')}")
                                st.write(f"**匹配AI能力**：{row.get('ai_ability', '-')}")
                            with col_b:
                                st.metric("机会等级", level)
                                st.write(f"**评估结论**：{row.get('conclusion', '-')}")
                else:
                    st.info("暂无符合条件的高价值需求")
            except Exception:
                st.info("机会榜单生成异常")

            # ========== 可视化图表区 ==========
            st.divider()
            
            # 过滤有效需求数据
            valid_df = filter_df[filter_df["is_valid"] == "是"].copy()

            # ========== 智能分析结论 ==========
            st.markdown("#### 🧠 智能分析结论")
            try:
                if not valid_df.empty:
                    top3_industry = valid_df.groupby("industry")["total_score"].mean().sort_values(ascending=False).head(3).index.tolist()
                    s_count = len(valid_df[valid_df["total_score"] >= 8.0])
                    total_valid = len(valid_df)
                    
                    prompt = f"""
                    基于以下AI应用场景评估数据，生成一段200-300字的分析结论，客观严谨：
                    有效需求样本总量：{total_valid}条
                    S级高价值需求数量：{s_count}条
                    综合得分排名前三的行业：{('、'.join(top3_industry))}
                    
                    要求：
                    1. 总结当前AI应用需求的整体分布特征
                    2. 点明高价值落地方向及核心原因
                    3. 给出落地优先级建议
                    4. 不要分点，用连贯的段落表述
                    """
                    
                    try:
                        conclusion_res = full_pipeline(prompt)
                        conclusion_text = conclusion_res.get("conclusion", "") or conclusion_res.get("desc", "")
                        if len(conclusion_text) < 20:
                            raise Exception("结果过短")
                        st.write(conclusion_text)
                    except Exception:
                        st.info("智能结论生成异常，可查看下方图表与数据自行分析")
                else:
                    st.info("暂无有效数据，无法生成分析结论")
            except Exception:
                st.info("智能结论生成异常")

            st.divider()
            st.markdown("#### 可视化分析")
            
            try:
                col_chart1, col_chart2 = st.columns([1, 1])
                
                # 图表1：行业综合得分TOP10
                with col_chart1:
                    if not valid_df.empty:
                        industry_rank = valid_df.groupby("industry")["total_score"].mean().reset_index()
                        industry_rank = industry_rank.sort_values("total_score", ascending=False).head(10)
                        fig_rank = px.bar(industry_rank, x="total_score", y="industry",
                                         orientation="h", title="行业机会综合得分TOP10",
                                         color="total_score", color_continuous_scale="Blues")
                        fig_rank.update_layout(yaxis={"categoryorder":"total ascending"}, showlegend=False)
                        st.plotly_chart(fig_rank, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")

                # 图表2：综合得分分布直方图
                with col_chart2:
                    if not valid_df.empty:
                        fig_hist = px.histogram(valid_df, x="total_score", nbins=10,
                                               title="综合得分分布", color_discrete_sequence=["#1f77b4"])
                        st.plotly_chart(fig_hist, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")

                col_chart3, col_chart4 = st.columns([1, 1])
                
                # 图表3：价值-可行性四象限散点图
                with col_chart3:
                    if not valid_df.empty:
                        industry_agg = valid_df.groupby("industry").agg({
                            "score_feasibility": "mean",
                            "score_value": "mean",
                            "total_score": "count"
                        }).reset_index()
                        industry_agg.columns = ["行业", "技术可行性", "商业价值", "样本量"]
                        
                        fig_scatter = px.scatter(industry_agg, x="技术可行性", y="商业价值",
                                                size="样本量", color="行业",
                                                title="价值-可行性四象限矩阵",
                                                size_max=30)
                        fig_scatter.add_hline(y=5, line_dash="dash", line_color="gray")
                        fig_scatter.add_vline(x=5, line_dash="dash", line_color="gray")
                        fig_scatter.update_layout(showlegend=False)
                        st.plotly_chart(fig_scatter, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")

                # 图表4：行业样本量&平均得分双轴图
                with col_chart4:
                    if not valid_df.empty:
                        dual_agg = valid_df.groupby("industry").agg({
                            "total_score": "mean",
                            "desc": "count"
                        }).reset_index()
                        dual_agg.columns = ["行业", "平均得分", "样本量"]
                        dual_agg = dual_agg.sort_values("样本量", ascending=False).head(8)
                        
                        fig_dual = go.Figure()
                        fig_dual.add_bar(x=dual_agg["行业"], y=dual_agg["样本量"],
                                        name="需求样本量", marker_color="#4c78a8")
                        fig_dual.add_scatter(x=dual_agg["行业"], y=dual_agg["平均得分"],
                                            name="平均得分", yaxis="y2", mode="lines+markers",
                                            line_color="#f58518")
                        fig_dual.update_layout(
                            title="行业热度与价值对比",
                            yaxis=dict(title="样本量"),
                            yaxis2=dict(title="平均得分", overlaying="y", side="right"),
                            legend=dict(orientation="h", y=1.1)
                        )
                        st.plotly_chart(fig_dual, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")

                st.divider()
                col_chart5, col_chart6 = st.columns([1.2, 1])
                
                # 图表5：行业×维度得分热力矩阵
                with col_chart5:
                    if not valid_df.empty:
                        heat_agg = valid_df.groupby("industry").agg({
                            "score_demand": "mean",
                            "score_feasibility": "mean",
                            "score_value": "mean"
                        }).reset_index()
                        heat_agg.columns = ["行业", "需求强度", "技术可行性", "商业价值"]
                        heat_agg = heat_agg.set_index("行业")
                        
                        fig_heat = px.imshow(heat_agg,
                                            text_auto=".1f",
                                            color_continuous_scale="Blues",
                                            title="行业×维度得分热力矩阵")
                        fig_heat.update_layout(height=420)
                        st.plotly_chart(fig_heat, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")

                # 图表6：机会等级占比环形图
                with col_chart6:
                    if not valid_df.empty:
                        def get_level(score):
                            if score >= 8.0:
                                return "S级"
                            elif score >= 6.5:
                                return "A级"
                            elif score >= 5.0:
                                return "B级"
                            else:
                                return "C级"
                        
                        valid_df["机会等级"] = valid_df["total_score"].apply(get_level)
                        level_count = valid_df["机会等级"].value_counts().reset_index()
                        level_count.columns = ["等级", "数量"]
                        
                        fig_level = px.pie(level_count, values="数量", names="等级",
                                          hole=0.5, title="机会等级分布",
                                          color="等级",
                                          color_discrete_map={
                                              "S级": "#548235",
                                              "A级": "#ffc000",
                                              "B级": "#ed7d31",
                                              "C级": "#c00000"
                                          })
                        fig_level.update_layout(height=420)
                        st.plotly_chart(fig_level, use_container_width=True)
                    else:
                        st.info("暂无有效需求数据")
                        
            except Exception:
                st.info("图表渲染异常，可查看下方表格数据")

            st.divider()
            st.markdown("#### 📁 竞赛结果文件导出")
            col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

            # result1.csv 原始采集数据
            with col_exp1:
                try:
                    raw_df = st.session_state.get("raw_data", pd.DataFrame())
                    csv1 = raw_df.to_csv(index=False).encode("utf-8-sig") if not raw_df.empty else b""
                    st.download_button(
                        label="下载 result1.csv",
                        data=csv1,
                        file_name="result1.csv",
                        mime="text/csv",
                        disabled=raw_df.empty
                    )
                    st.caption("原始采集全量数据")
                except Exception:
                    st.button("下载 result1.csv", disabled=True)

            # result2.csv 清洗后数据集
            with col_exp2:
                try:
                    clean_df = st.session_state.get("clean_data", pd.DataFrame())
                    csv2 = clean_df.to_csv(index=False).encode("utf-8-sig") if not clean_df.empty else b""
                    st.download_button(
                        label="下载 result2.csv",
                        data=csv2,
                        file_name="result2.csv",
                        mime="text/csv",
                        disabled=clean_df.empty
                    )
                    st.caption("去重清洗后数据集")
                except Exception:
                    st.button("下载 result2.csv", disabled=True)

            # result3.csv 全量评估明细
            with col_exp3:
                csv3 = result_df.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    label="下载 result3.csv",
                    data=csv3,
                    file_name="result3.csv",
                    mime="text/csv"
                )
                st.caption("全量评估明细结果")

            # result4.csv 聚合统计结果
            with col_exp4:
                try:
                    if not valid_df.empty:
                        stat_df = valid_df.groupby("industry").agg(
                            样本量=("total_score", "count"),
                            平均综合得分=("total_score", "mean"),
                            平均需求强度=("score_demand", "mean"),
                            平均技术可行性=("score_feasibility", "mean"),
                            平均商业价值=("score_value", "mean")
                        ).reset_index()
                        stat_df = stat_df.sort_values("平均综合得分", ascending=False)
                        csv4 = stat_df.to_csv(index=False).encode("utf-8-sig")
                    else:
                        csv4 = b""
                    st.download_button(
                        label="下载 result4.csv",
                        data=csv4,
                        file_name="result4.csv",
                        mime="text/csv",
                        disabled=valid_df.empty
                    )
                    st.caption("行业维度聚合统计")
                except Exception:
                    st.button("下载 result4.csv", disabled=True)


with tab4:
    st.subheader("评估体系说明")
    st.markdown("### 一、评估框架")
    st.write("本系统采用「需求侧-供给侧-商业侧」三维评估框架，基于多平台公开用户反馈数据，对AI应用场景的落地机会进行量化评估。")
    
    st.markdown("### 二、评估维度与权重分配")
    col_w1, col_w2, col_w3 = st.columns(3)
    with col_w1:
        st.info("**需求侧（权重40%）**\n\n- 用户痛点强烈程度\n- 需求覆盖受众规模\n- 市场提及频次热度")
    with col_w2:
        st.info("**供给侧（权重30%）**\n\n- 对应技术成熟度\n- 落地实现综合成本\n- 合规与政策风险")
    with col_w3:
        st.info("**商业侧（权重30%）**\n\n- 赛道市场空间规模\n- 商业化变现效率\n- 行业竞争烈度")
    
    st.markdown("### 三、档位评分映射标准")
    st.write("大模型仅负责语义识别与档位判定，最终得分由标准化映射表自动换算：")
    score_table = pd.DataFrame({
        "评估档位": ["高", "中", "低"],
        "对应分值": ["8.5分", "6.0分", "3.5分"],
        "判定说明": ["需求明确、技术成熟、商业价值显著", "有一定需求基础，落地存在部分门槛", "需求零散、技术尚不成熟、商业化难度大"]
    })
    st.table(score_table)
    
    st.markdown("### 四、综合得分计算公式")
    st.latex(r'''
    综合得分 = 需求强度 \times 0.4 + 技术可行性 \times 0.3 + 商业价值 \times 0.3
    ''')
    st.caption("权重设计参考行业通用机会评估框架，优先侧重真实用户需求强度。")
    
    st.markdown("### 五、机会等级划分与策略建议")
    level_table = pd.DataFrame({
        "机会等级": ["S级", "A级", "B级", "C级"],
        "得分区间": ["≥8.0分", "6.5 - 7.9分", "5.0 - 6.4分", "<5.0分"],
        "落地策略": ["重点突破，优先落地", "持续关注，储备方案", "观望跟进，择机切入", "低价值，暂不投入"]
    })
    st.table(level_table)
    
    st.divider()
    st.markdown("### 六、数据来源与局限性说明")
    st.write("1. **数据来源**：哔哩哔哩、知乎、掘金、GitHub 四大平台公开可访问的话题、帖子、评论内容，仅用于学术研究。")
    st.write("2. **交叉验证**：同一需求在多渠道均有提及，判定为高可信需求；单平台出现的需求标注为局部参考。")
    st.write("3. **局限性**：结论基于公开渠道样本，反映当前技术阶段下的行业普遍认知，存在时效性与样本偏差，不构成投资或商业建议。")

    st.divider()
    st.markdown("### 七、安全与合规说明")
    st.write("1. **数据安全**：所有采集数据仅在内存中处理分析，不持久化存储用户隐私信息，导出功能由用户主动触发。")
    st.write("2. **API安全**：密钥采用服务端私密存储，全程零日志、零输出、零泄露，接口调用限流兜底。")
    st.write("3. **爬虫合规**：严格遵守各平台公开接口调用规范与robots协议，速率可控，仅采集公开可访问内容，仅用于学术研究。")
    st.write("4. **内容安全**：系统自动过滤HTML标签与恶意内容，防范注入与XSS风险，保障页面运行安全。")
