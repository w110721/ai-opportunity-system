            # ========== 可视化图表区 ==========
            st.divider()
            st.markdown("#### 可视化分析")
            
            # 过滤有效需求数据
            valid_df = filter_df[filter_df["is_valid"] == "是"].copy()
            
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
                        # 添加四象限分割虚线
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
