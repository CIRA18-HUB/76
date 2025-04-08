import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="口力营销物料与销售分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f3867;
        text-align: center;
        margin-bottom: 1rem;
    }
    .card-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #444444;
    }
    .card-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f3867;
    }
    .metric-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .card-text {
        font-size: 0.9rem;
        color: #6c757d;
    }
    .alert-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .alert-success {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
    }
    .alert-warning {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
    }
    .alert-danger {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
    }
</style>
""", unsafe_allow_html=True)


# 加载数据函数修改
@st.cache_data(ttl=3600)
def load_data():
    """加载Excel数据文件"""
    try:
        # 尝试加载真实数据
        material_file = "2025物料源数据.xlsx"
        sales_file = "25物料源销售数据.xlsx"
        price_file = "物料单价.xlsx"

        df_material = pd.read_excel(material_file)
        df_sales = pd.read_excel(sales_file)
        df_material_price = pd.read_excel(price_file)

        # 处理物料单价表 - 检测到重复的"物料类别"列
        if '物料代码' in df_material_price.columns and '单价（元）' in df_material_price.columns:
            df_material_price = df_material_price[['物料代码', '单价（元）']]
        else:
            # 根据您提供的数据结构，实际上是第二列和第四列
            try:
                df_material_price.columns = ['物料类别1', '物料代码', '物料类别2', '单价（元）']
                df_material_price = df_material_price[['物料代码', '单价（元）']]
            except:
                st.error("物料单价表结构与预期不符，请检查数据")
                return None, None, None

        st.success("成功加载数据文件")

    except Exception as e:
        st.error(f"无法加载Excel文件: {e}。请确保所有必需的数据文件都已正确放置。")
        return None, None, None

    # 数据预处理
    # 1. 确保日期格式一致 - 处理YYYY-MM格式
    if '发运月份' in df_material.columns:
        try:
            # 检查是否为YYYY-MM格式
            if isinstance(df_material['发运月份'].iloc[0], str) and len(df_material['发运月份'].iloc[0]) == 7:
                # 转换为日期时间格式，添加日
                df_material['发运月份'] = df_material['发运月份'].apply(
                    lambda x: pd.to_datetime(f"{x}-01" if isinstance(x, str) else x)
                )
            else:
                df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
        except:
            st.warning("物料数据日期格式转换出错，尝试备选方法")
            try:
                df_material['发运月份'] = pd.to_datetime(df_material['发运月份'], errors='coerce')
            except:
                st.error("物料数据日期格式无法解析")
                return None, None, None

    if '发运月份' in df_sales.columns:
        try:
            # 检查是否为YYYY-MM格式
            if isinstance(df_sales['发运月份'].iloc[0], str) and len(df_sales['发运月份'].iloc[0]) == 7:
                # 转换为日期时间格式，添加日
                df_sales['发运月份'] = df_sales['发运月份'].apply(
                    lambda x: pd.to_datetime(f"{x}-01" if isinstance(x, str) else x)
                )
            else:
                df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])
        except:
            st.warning("销售数据日期格式转换出错，尝试备选方法")
            try:
                df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'], errors='coerce')
            except:
                st.error("销售数据日期格式无法解析")
                return None, None, None

    # 2. 将物料单价添加到物料数据中
    material_price_dict = dict(zip(df_material_price['物料代码'], df_material_price['单价（元）']))
    df_material['物料单价'] = df_material['物料代码'].map(material_price_dict)
    df_material['物料单价'].fillna(0, inplace=True)

    # 3. 计算物料总成本
    df_material['物料总成本'] = df_material['物料数量'] * df_material['物料单价']

    # 4. 计算销售总额 - 重新计算确保准确性
    # 确保销售总额正确计算且不存在重复
    df_sales['销售总额'] = df_sales['求和项:数量（箱）'] * df_sales['求和项:单价（箱）']

    # 检查是否存在重复记录
    duplicates = df_sales.duplicated(subset=['发运月份', '客户代码', '产品代码'], keep=False)
    if duplicates.any():
        st.warning(f"检测到{duplicates.sum()}条可能的重复销售记录，将保留唯一值")
        # 保留唯一值，避免重复计算
        df_sales = df_sales.drop_duplicates(subset=['发运月份', '客户代码', '产品代码'])

    return df_material, df_sales, df_material_price


def filter_data(df, regions=None, provinces=None, start_date=None, end_date=None):
    """按区域、省份和日期筛选数据"""
    filtered_df = df.copy()

    # 区域筛选
    if regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df['所属区域'].isin(regions)]

    # 省份筛选
    if provinces and len(provinces) > 0:
        filtered_df = filtered_df[filtered_df['省份'].isin(provinces)]

    # 日期筛选
    if start_date and end_date:
        # 确保发运月份列是日期时间类型
        if '发运月份' in filtered_df.columns:
            if not pd.api.types.is_datetime64_any_dtype(filtered_df['发运月份']):
                try:
                    filtered_df['发运月份'] = pd.to_datetime(filtered_df['发运月份'])
                except:
                    st.warning("发运月份列无法转换为日期时间格式，日期筛选可能不准确")

            # 修正日期筛选逻辑
            # 使用月份的第一天进行比较，确保包含整月数据
            start_year_month = start_date.strftime('%Y-%m')
            end_year_month = end_date.strftime('%Y-%m')

            # 使用字符串比较确保只筛选整月
            filtered_df['年月'] = filtered_df['发运月份'].dt.strftime('%Y-%m')
            filtered_df = filtered_df[
                (filtered_df['年月'] >= start_year_month) &
                (filtered_df['年月'] <= end_year_month)
                ]
            filtered_df.drop(columns=['年月'], inplace=True)

    return filtered_df


# 计算费比
def calculate_fee_ratio(cost, sales):
    """计算费比 = (物料成本 / 销售额) * 100%"""
    if sales > 0:
        return (cost / sales) * 100
    return np.nan  # 返回NaN而不是0，更符合数学逻辑


# 创建KPI卡片
def display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness):
    """显示KPI卡片"""
    cols = st.columns(4)

    # 总物料成本 - 修改为保留两位小数
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总物料成本</p>
            <p class="card-value">￥{total_material_cost:,.2f}</p>
            <p class="card-text">总投入物料资金</p>
        </div>
        """, unsafe_allow_html=True)

    # 总销售额 - 修改为保留两位小数
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总销售额</p>
            <p class="card-value">￥{total_sales:,.2f}</p>
            <p class="card-text">总体销售收入</p>
        </div>
        """, unsafe_allow_html=True)

    # 总体费比
    with cols[2]:
        fee_color = "#4CAF50" if overall_cost_sales_ratio < 3 else "#FF9800" if overall_cost_sales_ratio < 5 else "#F44336"
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总体费比</p>
            <p class="card-value" style="color: {fee_color};">{overall_cost_sales_ratio:.2f}%</p>
            <p class="card-text">物料成本占销售额比例</p>
        </div>
        """, unsafe_allow_html=True)

    # 平均物料效益 - 修改为保留两位小数
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均物料效益</p>
            <p class="card-value">￥{avg_material_effectiveness:,.2f}</p>
            <p class="card-text">每单位物料平均产生销售额</p>
        </div>
        """, unsafe_allow_html=True)


# 区域销售分析
def region_analysis(filtered_material, filtered_sales):
    """区域销售与费比分析"""
    st.markdown("## 区域分析")

    cols = st.columns(2)

    with cols[0]:
        # 区域销售图表
        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index().sort_values('销售总额', ascending=False)

        if not region_sales.empty:
            fig = px.bar(
                region_sales,
                x='所属区域',
                y='销售总额',
                title="各区域销售总额",
                color='所属区域',
                text='销售总额'
            )
            fig.update_traces(
                texttemplate='￥%{text:,.2f}',  # 修改为保留两位小数
                textposition='outside'
            )
            fig.update_layout(
                xaxis_title="区域",
                yaxis_title="销售总额 (元)",
                yaxis=dict(tickprefix="￥", tickformat=",.2f")
            )
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 此图表展示了各个销售区域的总销售额排名。
            - 柱形越高表示该区域销售业绩越好。
            - 可以清晰识别出表现最突出的区域和需要加强的区域。
            - 业务团队可根据此图调整区域资源分配，重点支持高潜力区域。
            """)
        else:
            st.warning("没有足够的数据来生成区域销售图表")

    with cols[1]:
        # 区域物料费比分析
        region_material = filtered_material.groupby('所属区域').agg({
            '物料总成本': 'sum'
        }).reset_index()

        region_sales_data = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index()

        region_metrics = pd.merge(region_material, region_sales_data, on='所属区域', how='outer')
        region_metrics['费比'] = region_metrics.apply(
            lambda row: calculate_fee_ratio(row['物料总成本'], row['销售总额']), axis=1
        )

        if not region_metrics.empty:
            fig = px.bar(
                region_metrics.sort_values('费比'),
                x='所属区域',
                y='费比',
                title="各区域费比分析",
                color='费比',
                color_continuous_scale='RdYlGn_r',
                text='费比'
            )
            fig.update_traces(
                texttemplate='%{text:.2f}%',  # 已经是保留两位小数
                textposition='outside'
            )
            fig.update_layout(
                xaxis_title="区域",
                yaxis_title="费比 (%)",
                yaxis=dict(ticksuffix="%", tickformat=".2f")
            )
            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 费比指物料成本占销售额的百分比，是衡量投入产出效率的重要指标。
            - 费比越低（柱形越短）表示该区域物料使用效率越高，每花费1元物料产生的销售额越多。
            - 费比超过5%的区域需要关注物料使用情况，考虑优化策略。
            - 建议分析费比偏高区域的物料投放结构，提高物料使用效率。
            """)
        else:
            st.warning("没有足够的数据来生成区域费比图表")


# 申请人使用物料效率分析
def applicant_material_efficiency_analysis(filtered_material, filtered_sales):
    """申请人使用物料效率分析"""
    st.markdown("## 申请人使用物料效率分析")

    # 确保数据中有申请人字段
    if '申请人' not in filtered_material.columns:
        st.warning("数据中缺少'申请人'字段，无法进行申请人物料效率分析")
        return

    # 按申请人聚合数据
    applicant_material = filtered_material.groupby('申请人').agg({
        '物料总成本': 'sum',
        '物料数量': 'sum'
    }).reset_index()

    # 关联销售数据
    # 假设申请人与特定客户相关联，通过客户代码进行映射
    if '申请人' in filtered_sales.columns:
        # 如果销售数据中直接有申请人字段
        applicant_sales = filtered_sales.groupby('申请人').agg({
            '销售总额': 'sum'
        }).reset_index()
    else:
        # 通过物料数据中的申请人和客户代码关系，映射到销售数据
        applicant_customer_map = filtered_material[['申请人', '客户代码']].drop_duplicates()
        merged_sales = pd.merge(filtered_sales, applicant_customer_map, on='客户代码', how='inner')
        applicant_sales = merged_sales.groupby('申请人').agg({
            '销售总额': 'sum'
        }).reset_index()

    # 合并物料和销售数据
    applicant_data = pd.merge(applicant_material, applicant_sales, on='申请人', how='outer')
    applicant_data.fillna(0, inplace=True)

    # 计算物料效率指标 - 每单位物料产生的销售额
    applicant_data['物料效率'] = 0  # 默认值
    mask = applicant_data['物料数量'] > 0
    if mask.any():
        applicant_data.loc[mask, '物料效率'] = applicant_data.loc[mask, '销售总额'] / applicant_data.loc[
            mask, '物料数量']

    # 计算费比
    applicant_data['费比'] = applicant_data.apply(
        lambda row: calculate_fee_ratio(row['物料总成本'], row['销售总额']), axis=1
    )

    # 创建物料效率图表
    cols = st.columns(2)

    with cols[0]:
        if not applicant_data.empty and len(applicant_data) > 0:
            # 按物料效率排序，选取前10名
            top_applicants = applicant_data.nlargest(10, '物料效率')

            fig = px.bar(
                top_applicants,
                x='申请人',
                y='物料效率',
                title="申请人物料效率TOP10",
                color='费比',
                color_continuous_scale='RdYlGn_r',
                text='物料效率'
            )

            fig.update_traces(
                texttemplate='￥%{text:,.2f}',  # 保留两位小数
                textposition='outside'
            )

            fig.update_layout(
                xaxis_title="申请人",
                yaxis_title="物料效率 (元/件)",
                xaxis=dict(tickangle=-45),
                yaxis=dict(tickprefix="￥", tickformat=",.2f"),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 物料效率表示每单位物料产生的销售额，数值越高表示物料使用效率越高。
            - 颜色深浅表示费比水平，颜色越浅表示费比越低，物料利用效率越高。
            - TOP10申请人在物料利用方面表现最佳，值得学习其物料使用经验。
            - 对于高效率但费比较高的申请人，可以探索如何优化其物料组合。
            - 建议组织高效率申请人分享经验，提升团队整体物料使用水平。
            """)
        else:
            st.warning("没有足够的数据来生成申请人物料效率图表")

    with cols[1]:
        if not applicant_data.empty and len(applicant_data) > 0:
            # 创建物料数量与销售额散点图
            fig = px.scatter(
                applicant_data,
                x='物料数量',
                y='销售总额',
                size='物料效率',
                color='费比',
                hover_name='申请人',
                title="申请人物料使用效益矩阵",
                labels={
                    '物料数量': '物料数量 (件)',
                    '销售总额': '销售总额 (元)',
                    '物料效率': '物料效率 (元/件)',
                    '费比': '费比 (%)'
                },
                color_continuous_scale='RdYlGn_r',
                size_max=50
            )

            fig.update_layout(
                height=500,
                xaxis=dict(tickformat=",.0f"),  # 不保留小数
                yaxis=dict(tickprefix="￥", tickformat=",.2f")  # 保留两位小数
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 此矩阵展示了申请人的物料使用量与销售额的关系。
            - 点的大小表示物料效率，越大表示单位物料产生的销售额越高。
            - 点的颜色表示费比，颜色越浅表示物料使用效率越高。
            - 右上方的申请人代表高物料投入高销售产出。
            - 左上方的申请人代表低物料投入高销售产出，物料使用效率高。
            - 建议分析位于左上方且点较大的申请人的工作方法，总结推广其成功经验。
            """)
        else:
            st.warning("没有足够的数据来生成申请人物料效益矩阵")

    # 申请人物料组合分析
    if not applicant_data.empty and len(applicant_data) >= 5:
        st.markdown("### 申请人物料使用习惯分析")

        # 获取每个申请人使用的物料类型
        applicant_material_types = filtered_material.groupby('申请人')['物料名称'].apply(
            lambda x: len(set(x))
        ).reset_index()
        applicant_material_types.columns = ['申请人', '物料种类数']

        # 获取每个申请人的客户数量
        applicant_customer_count = filtered_material.groupby('申请人')['客户代码'].nunique().reset_index()
        applicant_customer_count.columns = ['申请人', '客户数量']

        # 合并数据
        applicant_habits = pd.merge(
            pd.merge(applicant_data, applicant_material_types, on='申请人', how='left'),
            applicant_customer_count, on='申请人', how='left'
        )

        # 计算每个客户平均使用的物料种类
        applicant_habits['客均物料种类'] = 0  # 默认值
        mask = applicant_habits['客户数量'] > 0
        if mask.any():
            applicant_habits.loc[mask, '客均物料种类'] = applicant_habits.loc[mask, '物料种类数'] / \
                                                         applicant_habits.loc[mask, '客户数量']

        # 创建气泡图
        fig = px.scatter(
            applicant_habits,
            x='客户数量',
            y='物料种类数',
            size='销售总额',
            color='物料效率',
            hover_name='申请人',
            title="申请人物料使用习惯分析",
            labels={
                '客户数量': '服务客户数量',
                '物料种类数': '使用物料种类数',
                '销售总额': '销售总额 (元)',
                '物料效率': '物料效率 (元/件)'
            },
            color_continuous_scale='Blues',
            size_max=50
        )

        fig.update_layout(
            height=600,
            xaxis=dict(tickformat=",.0f"),  # 不保留小数
            yaxis=dict(tickformat=",.0f")  # 不保留小数
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解读
        st.markdown("""
        **图表解读：**
        - 此图展示了申请人的物料使用习惯与客户服务特点。
        - 横轴表示服务的客户数量，纵轴表示使用的物料种类数。
        - 点的大小表示销售总额，越大表示销售业绩越好。
        - 点的颜色表示物料效率，颜色越深表示物料使用效率越高。
        - 位于右上方的申请人客户覆盖广且物料多样化，显示出全面发展特点。
        - 位于左上方的申请人客户较少但物料种类多，可能针对少数客户提供深度服务。
        - 位于右下方的申请人客户多但物料种类少，可能采用标准化服务模式。
        - 建议根据申请人的不同特点，提供有针对性的支持和培训。
        """)

        # 分析申请人的物料偏好
        st.markdown("### 申请人物料偏好分析")

        # 修改这部分，提供更灵活的申请人选择选项
        sort_options = {
            "销售总额": "销售总额",
            "物料效率": "物料效率",
            "费比": "费比",
            "物料种类数": "物料种类数"
        }

        # 添加排序选项
        sort_by = st.radio(
            "按照以下指标排序申请人:",
            options=list(sort_options.keys()),
            horizontal=True
        )

        # 决定显示多少申请人
        display_count = st.slider("显示申请人数量:", min_value=5, max_value=min(50, len(applicant_data)), value=10,
                                  step=5)

        # 根据选择的指标排序申请人
        if sort_by == "费比":
            # 费比是越低越好，所以用升序
            top_applicants_list = applicant_data.nsmallest(display_count, sort_options[sort_by])['申请人'].tolist()
        else:
            # 其他指标都是越高越好，用降序
            top_applicants_list = applicant_data.nlargest(display_count, sort_options[sort_by])['申请人'].tolist()

        # 添加"显示全部"选项
        show_all = st.checkbox("显示全部申请人", value=False)

        if show_all:
            # 如果选择显示全部，则使用所有申请人
            applicants_list = applicant_data['申请人'].tolist()
        else:
            # 否则使用筛选后的申请人列表
            applicants_list = top_applicants_list

        # 根据提供的列表允许用户选择申请人
        selected_applicant = st.selectbox("选择要分析的申请人:", applicants_list)

        if selected_applicant:
            # 获取该申请人使用的物料情况
            applicant_materials = filtered_material[filtered_material['申请人'] == selected_applicant]

            if not applicant_materials.empty:
                # 按物料名称分组
                material_usage = applicant_materials.groupby('物料名称').agg({
                    '物料数量': 'sum',
                    '物料总成本': 'sum'
                }).reset_index().sort_values('物料总成本', ascending=False)

                # 创建物料使用情况饼图
                fig1 = px.pie(
                    material_usage,
                    values='物料总成本',
                    names='物料名称',
                    title=f"{selected_applicant} 物料成本分布",
                    hole=0.4
                )

                fig1.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hoverinfo='label+percent+value',
                    textfont_size=12
                )

                fig1.update_layout(height=450)

                st.plotly_chart(fig1, use_container_width=True)

                # 创建物料数量柱状图 - 修改显示方式避免遮挡
                top_materials = material_usage.nlargest(10, '物料数量')

                fig2 = px.bar(
                    top_materials,
                    x='物料名称',
                    y='物料数量',
                    title=f"{selected_applicant} 最常用物料TOP10",
                    color='物料总成本',
                    color_continuous_scale='Blues',
                    text='物料数量'
                )

                fig2.update_traces(
                    texttemplate='%{text:,.0f}',  # 不保留小数
                    textposition='outside'
                )

                # 调整布局解决文本遮挡问题
                fig2.update_layout(
                    xaxis_title="物料名称",
                    yaxis_title="物料使用数量",
                    xaxis=dict(
                        tickangle=-45,  # 倾斜角度更大
                        tickfont=dict(size=10),  # 减小字体
                    ),
                    height=550,  # 增加高度
                    margin=dict(b=180, l=60, r=40, t=80),  # 增加底部边距
                    autosize=True
                )

                st.plotly_chart(fig2, use_container_width=True)

                # 添加申请人分析结论
                # 计算一些指标
                total_cost = material_usage['物料总成本'].sum()
                total_quantity = material_usage['物料数量'].sum()
                material_count = len(material_usage)

                # 查找该申请人的销售额和物料效率
                applicant_metrics = applicant_data[applicant_data['申请人'] == selected_applicant]
                sales_amount = applicant_metrics['销售总额'].iloc[0] if not applicant_metrics.empty else 0
                material_efficiency = applicant_metrics['物料效率'].iloc[0] if not applicant_metrics.empty else 0
                fee_ratio = applicant_metrics['费比'].iloc[0] if not applicant_metrics.empty else 0

                # 确保能正确获取最常用的物料名称
                most_used_material = "无数据"
                most_cost_material = "无数据"

                if not material_usage.empty:
                    most_used_idx = material_usage['物料数量'].idxmax()
                    most_cost_idx = material_usage['物料总成本'].idxmax()

                    if most_used_idx is not None:
                        most_used_material = material_usage.loc[most_used_idx, '物料名称']

                    if most_cost_idx is not None:
                        most_cost_material = material_usage.loc[most_cost_idx, '物料名称']

                st.markdown(f"""
                **{selected_applicant} 物料使用分析结论:**

                **基本指标:**
                - 总物料成本: ￥{total_cost:,.2f}
                - 物料种类数: {material_count}
                - 总物料数量: {total_quantity:,.0f}
                - 销售总额: ￥{sales_amount:,.2f}
                - 物料效率: ￥{material_efficiency:,.2f} /件
                - 费比: {fee_ratio:.2f}%

                **特点总结:**
                - 该申请人最常使用的物料是: {most_used_material}
                - 物料成本占比最高的是: {most_cost_material}
                - 物料使用多样性: {'较高' if material_count > 5 else '一般' if material_count > 3 else '较低'}
                - 物料使用效率: {'较高' if material_efficiency > applicant_data['物料效率'].median() else '一般' if material_efficiency > applicant_data['物料效率'].quantile(0.25) else '较低'}

                **改进建议:**
                """)

                # 根据物料效率和费比提供针对性建议
                if material_efficiency > applicant_data['物料效率'].median() and fee_ratio < applicant_data[
                    '费比'].median():
                    st.markdown("""
                    - 该申请人物料使用效率高且费比低，是优秀的物料管理者
                    - 建议组织其分享经验，推广成功做法
                    - 可以适当增加其物料预算，扩大业务规模
                    - 考虑让其尝试新型物料，进一步提升效率
                    """)
                elif material_efficiency > applicant_data['物料效率'].median() and fee_ratio >= applicant_data[
                    '费比'].median():
                    st.markdown("""
                    - 该申请人物料效率高但费比较高，需优化物料组合
                    - 建议减少低效物料的使用，更多使用高ROI物料
                    - 指导其优化物料与客户的匹配，避免资源浪费
                    - 分析其高效物料的使用模式，保持优势同时降低成本
                    """)
                elif material_efficiency <= applicant_data['物料效率'].median() and fee_ratio < applicant_data[
                    '费比'].median():
                    st.markdown("""
                    - 该申请人控制成本能力强但物料效率有提升空间
                    - 建议增加物料种类多样性，尝试更多高效物料
                    - 提供物料使用培训，提高物料投放效果
                    - 学习高效率申请人的经验，优化客户物料推荐
                    """)
                else:
                    st.markdown("""
                    - 该申请人物料使用效率和费比均需改进
                    - 建议全面分析其物料使用策略，制定改进计划
                    - 提供系统的物料管理培训，包括物料选择和使用方法
                    - 安排与高效率申请人同行学习，掌握先进经验
                    - 设定物料效率提升目标，定期跟踪进展
                    """)
            else:
                st.warning(f"未找到 {selected_applicant} 的物料使用数据")
# 时间趋势分析
def time_analysis(filtered_material, filtered_sales):
    """时间趋势分析"""
    st.markdown("## 时间趋势分析")

    # 按月份聚合数据
    monthly_material = filtered_material.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
        '物料总成本': 'sum',
        '物料数量': 'sum'
    }).reset_index()

    monthly_sales = filtered_sales.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
        '销售总额': 'sum'
    }).reset_index()

    monthly_data = pd.merge(monthly_material, monthly_sales, on='发运月份', how='outer')
    monthly_data.sort_values('发运月份', inplace=True)

    # 计算费比
    monthly_data['费比'] = monthly_data.apply(
        lambda row: calculate_fee_ratio(row['物料总成本'], row['销售总额']), axis=1
    )

    # 添加格式化月份字段
    monthly_data['月份'] = monthly_data['发运月份'].dt.strftime('%Y-%m')

    if len(monthly_data) >= 3:
        # 创建销售额和物料成本趋势图
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加销售额线
        fig.add_trace(
            go.Scatter(
                x=monthly_data['月份'],
                y=monthly_data['销售总额'],
                name='销售总额',
                line=dict(color='#1f77b4', width=3),
                mode='lines+markers'
            ),
            secondary_y=False
        )

        # 添加物料成本线
        fig.add_trace(
            go.Scatter(
                x=monthly_data['月份'],
                y=monthly_data['物料总成本'],
                name='物料成本',
                line=dict(color='#ff7f0e', width=3),
                mode='lines+markers'
            ),
            secondary_y=True
        )

        # 更新布局
        fig.update_layout(
            title_text="销售额与物料成本月度趋势",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=500
        )

        # 更新y轴 - 修改为保留两位小数
        fig.update_yaxes(title_text="销售总额 (元)", secondary_y=False, tickprefix="￥", tickformat=",.2f")
        fig.update_yaxes(title_text="物料成本 (元)", secondary_y=True, tickprefix="￥", tickformat=",.2f")

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解读
        st.markdown("""
        **图表解读：**
        - 蓝线显示销售总额随时间的变化趋势，橙线显示物料成本的变化。
        - 理想情况下，销售额应该增长快于物料成本的增长。
        - 两条线之间的距离越大，表示物料投入产生的销售效益越高。
        - 若某月物料成本上升但销售额未相应增长，需调查物料使用效率问题。
        - 关注季节性波动模式，有助于更好地规划物料投放时机。
        """)

        # 创建费比趋势图
        fig_fee = px.line(
            monthly_data,
            x='月份',
            y='费比',
            title="月度费比变化趋势",
            markers=True,
            line_shape='linear'
        )

        # 添加平均费比参考线
        avg_fee_ratio = monthly_data['费比'].mean()
        fig_fee.add_hline(
            y=avg_fee_ratio,
            line_dash="dash",
            line_color="red",
            annotation_text=f"平均费比: {avg_fee_ratio:.2f}%",
            annotation_position="bottom right"
        )

        fig_fee.update_layout(
            xaxis_title="月份",
            yaxis_title="费比 (%)",
            yaxis=dict(ticksuffix="%", tickformat=".2f"),  # 修改为保留两位小数
            height=400
        )

        st.plotly_chart(fig_fee, use_container_width=True)

        # 添加图表解读
        st.markdown("""
        **图表解读：**
        - 此图展示了各月份物料费比的波动情况。
        - 红色虚线表示平均费比水平，是判断各月表现的基准线。
        - 费比低于平均线的月份表示物料使用效率高于平均水平。
        - 连续多月费比上升需引起警惕，可能表明物料使用效率下降。
        - 费比持续下降的趋势表明物料管理策略有效，应总结经验并继续执行。
        """)
    else:
        st.warning("没有足够的数据来生成时间趋势图表")


# 客户价值分析
def customer_analysis(filtered_material, filtered_sales):
    """客户价值分析"""
    st.markdown("## 客户价值分析")

    # 按客户聚合数据
    customer_material = filtered_material.groupby(['客户代码', '经销商名称']).agg({
        '物料总成本': 'sum',
        '物料数量': 'sum'
    }).reset_index()

    customer_sales = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
        '销售总额': 'sum'
    }).reset_index()

    customer_value = pd.merge(customer_material, customer_sales, on=['客户代码', '经销商名称'], how='outer')

    # 处理NaN值，确保计算正确
    customer_value['物料总成本'] = customer_value['物料总成本'].fillna(0)
    customer_value['物料数量'] = customer_value['物料数量'].fillna(0)
    customer_value['销售总额'] = customer_value['销售总额'].fillna(0)

    # 计算客户价值指标
    customer_value['费比'] = customer_value.apply(
        lambda row: calculate_fee_ratio(row['物料总成本'], row['销售总额']), axis=1
    )

    # 安全地计算物料效率，避免除以零
    customer_value['物料效率'] = 0  # 默认值
    mask = customer_value['物料数量'] > 0
    if mask.any():
        customer_value.loc[mask, '物料效率'] = customer_value.loc[mask, '销售总额'] / customer_value.loc[
            mask, '物料数量']

    customer_value['客户价值'] = customer_value['销售总额'] - customer_value['物料总成本']

    # 修正ROI计算，使用(收益-成本)/成本公式
    customer_value['ROI'] = np.nan  # 默认值为NaN
    mask = customer_value['物料总成本'] > 0
    if mask.any():
        customer_value.loc[mask, 'ROI'] = (customer_value.loc[mask, '销售总额'] - customer_value.loc[
            mask, '物料总成本']) / customer_value.loc[mask, '物料总成本']

    # 删除任何无效行
    customer_value = customer_value.replace([np.inf, -np.inf], np.nan).dropna(
        subset=['ROI', '费比', '物料效率', '客户价值'])

    # 创建客户价值分布图
    cols = st.columns(2)

    with cols[0]:
        if not customer_value.empty and len(customer_value) > 0:
            top_customers = customer_value.nlargest(10, '客户价值')

            fig = px.bar(
                top_customers,
                x='经销商名称',
                y='客户价值',
                title="客户价值TOP10",
                color='费比',
                color_continuous_scale='RdYlGn_r',
                text='客户价值'
            )

            fig.update_traces(
                texttemplate='￥%{text:,.2f}',  # 修改为保留两位小数
                textposition='outside'
            )

            fig.update_layout(
                xaxis_title="经销商",
                yaxis_title="客户价值 (元)",
                xaxis=dict(tickangle=-45),
                yaxis=dict(tickprefix="￥", tickformat=",.2f"),  # 修改为保留两位小数
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 客户价值 = 销售总额 - 物料总成本，表示客户为公司贡献的净利润。
            - 颜色深浅代表费比水平，颜色越浅表示费比越低，物料利用效率越高。
            - TOP10客户是公司最重要的资源，应优先维护合作关系。
            - 对于高价值但费比较高的客户，可探索降低物料成本的方案。
            - 建议针对高价值客户制定专属服务计划，提升客户忠诚度。
            """)
        else:
            st.warning("没有足够的数据来生成客户价值分布图表")

    with cols[1]:
        if not customer_value.empty and len(customer_value) > 0:
            # 客户ROI散点图 - 修复此部分
            try:
                # 确保数据有效
                scatter_data = customer_value.copy()

                # 如果ROI异常大，进行限制
                max_roi = scatter_data['ROI'].quantile(0.95) if len(scatter_data) > 10 else scatter_data['ROI'].max()
                scatter_data['ROI_display'] = scatter_data['ROI'].clip(upper=max_roi)

                # 如果费比异常大，进行限制
                max_fee = scatter_data['费比'].quantile(0.95) if len(scatter_data) > 10 else scatter_data['费比'].max()
                scatter_data['费比_display'] = scatter_data['费比'].clip(upper=max_fee)

                fig = px.scatter(
                    scatter_data,
                    x='物料总成本',
                    y='销售总额',
                    size='ROI_display',
                    color='费比_display',
                    hover_name='经销商名称',
                    title="客户ROI矩阵",
                    labels={
                        '物料总成本': '物料总成本 (元)',
                        '销售总额': '销售总额 (元)',
                        'ROI_display': 'ROI',
                        '费比_display': '费比 (%)'
                    },
                    color_continuous_scale='RdYlGn_r',
                    size_max=50
                )

                # 添加ROI=1参考线
                max_cost = scatter_data['物料总成本'].max() * 1.1 if not scatter_data.empty else 1000
                min_cost = scatter_data['物料总成本'].min() * 0.9 if not scatter_data.empty else 0

                if max_cost > 0 and min_cost >= 0:
                    fig.add_shape(
                        type="line",
                        x0=min_cost,
                        y0=min_cost,
                        x1=max_cost,
                        y1=max_cost,
                        line=dict(color="red", width=2, dash="dash")
                    )

                fig.update_layout(
                    height=500,
                    xaxis=dict(tickprefix="￥", type="log", tickformat=",.2f"),  # 修改为保留两位小数
                    yaxis=dict(tickprefix="￥", type="log", tickformat=",.2f")  # 修改为保留两位小数
                )

                st.plotly_chart(fig, use_container_width=True)

                # 客户ROI矩阵解读更新
                st.markdown("""
                **图表解读：**
                - 散点图展示了客户的投入(物料成本)与产出(销售额)关系。
                - 点的大小表示ROI(投资回报率)，计算公式为(销售额-物料成本)/物料成本，越大表示回报率越高。
                - 点的颜色表示费比，颜色越浅表示物料使用效率越高。
                - 红色虚线是销售额=物料成本的参考线，点位于此线上方表示有正向回报，位于线下方表示投入大于产出。
                - 右上方的客户代表高投入高产出，左上方的客户代表低投入高产出(高效客户)。
                - 建议重点维护位于图表右上角且颜色较浅的大点客户。
                """)
            except Exception as e:
                st.warning(f"创建客户ROI矩阵时出错: {str(e)}")
                st.info("尝试使用简化版散点图...")

                # 回退到简化版散点图
                fig = px.scatter(
                    customer_value,
                    x='物料总成本',
                    y='销售总额',
                    hover_name='经销商名称',
                    title="客户投入产出矩阵",
                    labels={
                        '物料总成本': '物料总成本 (元)',
                        '销售总额': '销售总额 (元)'
                    }
                )
                fig.update_layout(
                    height=500,
                    xaxis=dict(tickprefix="￥", tickformat=",.2f"),  # 修改为保留两位小数
                    yaxis=dict(tickprefix="￥", tickformat=",.2f")  # 修改为保留两位小数
                )
                st.plotly_chart(fig, use_container_width=True)

                # 添加简化版的图表解读
                st.markdown("""
                **图表解读：**
                - 此简化图展示了客户的物料投入与销售产出关系。
                - 位于图表右上方的点表示高投入高产出的客户。
                - 位于左上方的点表示低投入高产出的客户，这些客户物料使用效率高。
                - 对比客户间的相对位置，可帮助识别高效和低效客户。
                """)
        else:
            st.warning("没有足够的数据来生成客户ROI矩阵")

    # 客户分群分析
    if not customer_value.empty and len(customer_value) >= 4:
        st.markdown("### 客户分群分析")

        try:
            # 使用统计阈值而不是排名
            # 计算价值和效率的中位数作为分隔线
            value_median = customer_value['客户价值'].median()
            efficiency_median = customer_value['物料效率'].median()

            # 定义分群函数，使用中位数作为分隔点
            def get_customer_group(row):
                if row['客户价值'] >= value_median and row['物料效率'] >= efficiency_median:
                    return '核心客户'
                elif row['客户价值'] >= value_median and row['物料效率'] < efficiency_median:
                    return '高潜力客户'
                elif row['客户价值'] < value_median and row['物料效率'] >= efficiency_median:
                    return '高效率客户'
                else:
                    return '一般客户'

            customer_value['客户分群'] = customer_value.apply(get_customer_group, axis=1)

            # 创建分群散点图
            fig = px.scatter(
                customer_value,
                x='客户价值',
                y='物料效率',
                color='客户分群',
                size='销售总额',
                hover_name='经销商名称',
                title="客户分群矩阵",
                labels={
                    '客户价值': '客户价值 (元)',
                    '物料效率': '物料效率 (元/件)',
                    '销售总额': '销售总额 (元)',
                    '客户分群': '客户分群'
                },
                color_discrete_map={
                    '核心客户': '#4CAF50',
                    '高潜力客户': '#FFC107',
                    '高效率客户': '#2196F3',
                    '一般客户': '#9E9E9E'
                },
                size_max=50
            )

            # 添加中位数参考线
            fig.add_vline(x=value_median, line_dash="dash", line_color="gray")
            fig.add_hline(y=efficiency_median, line_dash="dash", line_color="gray")

            fig.update_layout(
                height=600,
                xaxis=dict(tickprefix="￥", tickformat=",.2f"),
                yaxis=dict(tickprefix="￥", tickformat=",.2f")
            )

            st.plotly_chart(fig, use_container_width=True)

            # 更新图表解读，说明使用中位数分隔
            st.markdown("""
            **图表解读：**
            - 此矩阵根据客户价值和物料效率将客户分为四类：
              * 核心客户(绿色)：高价值且高效率，是最优质的客户群体
              * 高潜力客户(黄色)：高价值但效率较低，有提升空间
              * 高效率客户(蓝色)：价值较低但效率高，有成长潜力
              * 一般客户(灰色)：价值和效率均低，需评估合作价值
            - 点的大小表示销售总额，越大表示销售规模越大。
            - 灰色虚线表示客户价值和物料效率的中位数水平，用于客观划分客户群体。
            - 建议针对不同分群制定差异化策略：
              * 核心客户：维护关系，提供优先服务
              * 高潜力客户：优化物料使用，提高效率
              * 高效率客户：扩大合作规模，提升价值
              * 一般客户：筛选有潜力的重点培养，其余考虑调整合作模式
            """)

            # 分群统计 - 删除表格，改为展示关键指标的图表
            st.markdown("### 客户分群关键指标")

            # 计算分群统计
            group_stats = customer_value.groupby('客户分群').agg({
                '客户代码': 'count',
                '销售总额': 'sum',
                '物料总成本': 'sum',
                '客户价值': 'sum',
                '费比': 'mean',
                '物料效率': 'mean'
            }).reset_index()

            group_stats.columns = ['客户分群', '客户数量', '销售总额', '物料总成本', '客户价值总和', '平均费比',
                                   '平均物料效率']

            # 计算百分比
            total_customers = group_stats['客户数量'].sum()
            total_value = group_stats['客户价值总和'].sum()

            if total_customers > 0:
                group_stats['客户占比'] = group_stats['客户数量'] / total_customers * 100
            else:
                group_stats['客户占比'] = 0

            if total_value != 0:
                group_stats['价值占比'] = group_stats['客户价值总和'] / total_value * 100
            else:
                group_stats['价值占比'] = 0

            # 创建客户数量饼图
            fig1 = px.pie(
                group_stats,
                values='客户数量',
                names='客户分群',
                title="客户分群数量分布",
                color='客户分群',
                color_discrete_map={
                    '核心客户': '#4CAF50',
                    '高潜力客户': '#FFC107',
                    '高效率客户': '#2196F3',
                    '一般客户': '#9E9E9E'
                }
            )
            fig1.update_traces(textinfo='percent+label')

            # 创建客户价值条形图
            fig2 = px.bar(
                group_stats,
                x='客户分群',
                y='客户价值总和',
                title="各分群客户价值总和",
                color='客户分群',
                text='价值占比',
                color_discrete_map={
                    '核心客户': '#4CAF50',
                    '高潜力客户': '#FFC107',
                    '高效率客户': '#2196F3',
                    '一般客户': '#9E9E9E'
                }
            )
            fig2.update_traces(
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
            fig2.update_layout(
                xaxis_title="客户分群",
                yaxis_title="客户价值总和 (元)",
                yaxis=dict(tickprefix="￥", tickformat=",.2f")  # 修改为保留两位小数
            )

            # 创建平均费比对比图
            fig3 = px.bar(
                group_stats,
                x='客户分群',
                y='平均费比',
                title="各分群平均费比",
                color='客户分群',
                text='平均费比',
                color_discrete_map={
                    '核心客户': '#4CAF50',
                    '高潜力客户': '#FFC107',
                    '高效率客户': '#2196F3',
                    '一般客户': '#9E9E9E'
                }
            )
            fig3.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside'
            )
            fig3.update_layout(
                xaxis_title="客户分群",
                yaxis_title="平均费比 (%)",
                yaxis=dict(ticksuffix="%", tickformat=".2f")  # 修改为保留两位小数
            )

            # 显示图表
            subcols = st.columns(2)
            with subcols[0]:
                st.plotly_chart(fig1, use_container_width=True)
            with subcols[1]:
                st.plotly_chart(fig2, use_container_width=True)

            st.plotly_chart(fig3, use_container_width=True)

            # 添加分群指标解读
            st.markdown("""
            **分群指标解读：**
            - 客户数量分布图展示了各类客户的占比情况，帮助了解客户结构。
            - 客户价值总和图反映了各分群对公司总价值的贡献，百分比表示占总价值的比例。
            - 平均费比图对比了不同分群的物料使用效率，费比越低表示效率越高。
            - 通常，核心客户和高效率客户的费比较低，而高潜力客户的费比较高。
            - 建议关注高潜力客户群体的费比优化，通过提升物料使用效率将其转化为核心客户。
            """)

        except Exception as e:
            st.warning(f"创建客户分群时出错: {str(e)}")
            st.info("客户分群需要更多有效数据。")


# 物料效益分析
def material_analysis(filtered_material, filtered_sales):
    """物料效益分析"""
    st.markdown("## 物料效益分析")

    # 按物料分组，计算ROI
    material_metrics = filtered_material.groupby(['物料代码', '物料名称']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    # 物料销售关联
    material_sales_map = pd.merge(
        filtered_material[['发运月份', '客户代码', '物料代码', '物料名称', '物料总成本']],
        filtered_sales[['发运月份', '客户代码', '销售总额']],
        on=['发运月份', '客户代码'],
        how='inner'
    )

    material_sales = material_sales_map.groupby(['物料代码', '物料名称']).agg({
        '销售总额': 'sum'
    }).reset_index()

    # 合并数据
    material_roi = pd.merge(material_metrics, material_sales, on=['物料代码', '物料名称'], how='left')
    material_roi['销售总额'].fillna(0, inplace=True)

    # 修正ROI计算公式
    material_roi['ROI'] = np.nan
    mask = material_roi['物料总成本'] > 0
    if mask.any():
        material_roi.loc[mask, 'ROI'] = (material_roi.loc[mask, '销售总额'] - material_roi.loc[mask, '物料总成本']) / \
                                        material_roi.loc[mask, '物料总成本']

    cols = st.columns(2)

    with cols[0]:
        if not material_roi.empty:
            # 物料ROI排名
            top_materials = material_roi.dropna(subset=['ROI']).nlargest(10, 'ROI')

            fig = px.bar(
                top_materials,
                x='物料名称',
                y='ROI',
                title="物料ROI TOP10",
                color='ROI',
                color_continuous_scale='Blues',
                text='ROI'
            )

            fig.update_traces(
                texttemplate='%{text:.2f}',  # 已经是保留两位小数
                textposition='outside'
            )

            fig.update_layout(
                xaxis_title="物料",
                yaxis_title="ROI",
                xaxis=dict(tickangle=-45),
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)

            # 物料ROI解读更新
            st.markdown("""
            **图表解读：**
            - ROI表示投入物料成本所产生的回报率，计算公式为(销售额-物料成本)/物料成本。
            - ROI越高表示物料的销售转化效果越好，投资回报越高。
            - TOP10中的物料是最具投资价值的物料类型，应优先考虑增加投放。
            - ROI低于0的物料意味着投入大于产出，需要审视其投放策略或调整目标客户。
            - 建议将高ROI物料作为重点推广品类，提高整体营销效率。
            """)
        else:
            st.warning("没有足够的数据来生成物料ROI图表")

    with cols[1]:
        if not material_roi.empty and not material_roi['物料总成本'].isna().all():
            # 物料销售贡献度
            fig = px.pie(
                material_roi,
                values='物料总成本',
                names='物料名称',
                title="物料成本分布",
                hole=0.4
            )

            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hoverinfo='label+percent+value',
                textfont_size=12
            )

            fig.update_layout(height=450)

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 此图展示了不同物料在总物料成本中的占比分布。
            - 占比较大的物料是主要投资方向，对整体费比影响较大。
            - 应结合ROI图表分析：
              * 高占比且高ROI的物料是核心物料，应继续投入
              * 高占比但低ROI的物料是重点优化对象，需调整使用策略
              * 低占比但高ROI的物料是潜力物料，可考虑增加投放
            - 物料投放应避免过度集中，建议保持多元化的物料组合以分散风险。
            """)
        else:
            st.warning("没有足够的数据来生成物料成本分布图表")

    # 物料投资优化建议
    if not material_roi.empty and not material_roi['ROI'].isna().all():
        st.markdown("### 物料投资优化建议")

        # 高ROI和低ROI物料
        high_roi_materials = material_roi.dropna(subset=['ROI']).nlargest(5, 'ROI')
        low_roi_materials = material_roi.dropna(subset=['ROI']).nsmallest(5, 'ROI')

        opt_cols = st.columns(2)

        with opt_cols[0]:
            st.markdown("""
            <div class="alert-box alert-success">
                <h4 style="margin-top: 0;">高ROI物料 (建议增加投放)</h4>
                <ul style="margin-bottom: 0;">
            """, unsafe_allow_html=True)

            for _, row in high_roi_materials.iterrows():
                st.markdown(f"""
                <li><strong>{row['物料名称']}</strong> - ROI: {row['ROI']:.2f}，
                成本: ￥{row['物料总成本']:,.2f}，
                销售额: ￥{row['销售总额']:,.2f}</li>
                """, unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)

            # 添加建议解读
            st.markdown("""
            **优化建议：**
            - 增加高ROI物料的投放预算，提高整体营销效率
            - 将高ROI物料投放到更多经销商，扩大覆盖范围
            - 分析高ROI物料的使用场景，总结成功经验并推广
            - 考虑针对高ROI物料开展专项促销活动
            """)

        with opt_cols[1]:
            st.markdown("""
            <div class="alert-box alert-danger">
                <h4 style="margin-top: 0;">低ROI物料 (建议优化投放)</h4>
                <ul style="margin-bottom: 0;">
            """, unsafe_allow_html=True)

            for _, row in low_roi_materials.iterrows():
                st.markdown(f"""
                <li><strong>{row['物料名称']}</strong> - ROI: {row['ROI']:.2f}，
                成本: ￥{row['物料总成本']:,.2f}，
                销售额: ￥{row['销售总额']:,.2f}</li>
                """, unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)

            # 添加建议解读
            st.markdown("""
            **优化建议：**
            - 减少低ROI物料的投放量，控制成本支出
            - 分析低ROI物料失效原因，可能是目标客户不匹配或使用方式不当
            - 尝试调整低ROI物料的使用策略，如搭配其他产品销售
            - 评估是否需要更新或替换低效物料设计
            - 对部分长期低ROI物料考虑逐步淘汰
            """)


# 物料-产品关联分析
def material_product_analysis(filtered_material, filtered_sales):
    """物料-产品关联分析"""
    st.markdown("## 物料-产品关联分析")

    # 增加物料搜索功能
    search_term = st.text_input("搜索特定物料名称 (例如: 挂网挂条)", "")

    # 增加考虑滞后效应的选项
    lag_effect = st.checkbox("考虑物料投放的滞后效应", value=False,
                             help="启用后，将分析物料投放后下一个月的销售效果，以考虑物料效果的滞后性")

    # 合并物料和销售数据，使用更灵活的匹配逻辑
    if lag_effect:
        # 如果考虑滞后效应，需要将物料数据的月份加一个月
        filtered_material_lag = filtered_material.copy()
        filtered_material_lag['发运月份'] = filtered_material_lag['发运月份'] + pd.DateOffset(months=1)

        # 使用滞后调整后的物料数据进行关联
        material_product = pd.merge(
            filtered_material_lag[
                ['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
            on=['发运月份', '客户代码', '经销商名称'],
            how='inner'
        )

        if material_product.empty:
            st.warning("考虑滞后效应后未找到匹配数据，尝试更宽松的匹配...")
            # 只按客户代码和经销商名称匹配，不考虑发运月份
            material_product = pd.merge(
                filtered_material_lag[['客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
                filtered_sales[['客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
                on=['客户代码', '经销商名称'],
                how='inner'
            )
    else:
        # 原始匹配逻辑
        material_product = pd.merge(
            filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
            on=['发运月份', '客户代码', '经销商名称'],
            how='inner'
        )

        if material_product.empty:
            st.warning("使用精确匹配未找到物料-产品关联数据，尝试更宽松的匹配...")
            # 只按客户代码和经销商名称匹配，不考虑发运月份
            material_product = pd.merge(
                filtered_material[['客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
                filtered_sales[['客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
                on=['客户代码', '经销商名称'],
                how='inner'
            )

    if material_product.empty:
        st.warning("没有匹配的物料-产品数据来进行关联分析")
        return

    # 添加相关性和因果关系说明
    st.info("""
    **分析说明：**
    - 此分析仅显示物料投放与产品销售之间的相关性，并不一定代表因果关系。
    - 销售表现可能受到物料以外的多种因素影响，如产品促销、节假日、季节性等。
    - 建议结合市场营销活动和其他因素进行综合判断。
    """)

    # 显示找到的物料种类
    all_materials = filtered_material['物料名称'].unique()
    st.markdown(f"**数据中共包含 {len(all_materials)} 种物料**")

    # 如果有搜索词，进行过滤并展示
    if search_term:
        matched_materials = [mat for mat in all_materials if search_term.lower() in mat.lower()]
        if matched_materials:
            st.success(f"找到包含 '{search_term}' 的物料: {', '.join(matched_materials)}")

            # 提取这些物料的数据统计
            for material in matched_materials:
                material_data = filtered_material[filtered_material['物料名称'] == material]
                st.markdown(f"""
                **{material} 数据统计:**
                - 总发放数量: {material_data['物料数量'].sum():,.0f}
                - 总物料成本: ￥{material_data['物料总成本'].sum():,.2f}
                - 使用客户数: {material_data['客户代码'].nunique()}
                """)
        else:
            st.warning(f"未找到包含 '{search_term}' 的物料")

    # 合并物料和销售数据，使用更灵活的匹配逻辑
    material_product = pd.merge(
        filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
        filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
        on=['发运月份', '客户代码', '经销商名称'],
        how='inner'
    )

    # 如果没有匹配数据，尝试使用更宽松的连接
    if material_product.empty:
        st.warning("使用精确匹配未找到物料-产品关联数据，尝试更宽松的匹配...")
        # 只按客户代码和经销商名称匹配，不考虑发运月份
        material_product = pd.merge(
            filtered_material[['客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
            on=['客户代码', '经销商名称'],
            how='inner'
        )

    if material_product.empty:
        st.warning("没有匹配的物料-产品数据来进行关联分析")
        return

    # 如果有搜索词并找到了匹配物料，尝试找到该物料的产品关联
    if search_term and matched_materials:
        for material in matched_materials:
            material_product_specific = material_product[material_product['物料名称'] == material]
            if not material_product_specific.empty:
                st.markdown(f"**{material} 与产品的关联:**")

                # 按产品分组计算销售数据
                product_relation = material_product_specific.groupby('产品名称').agg({
                    '销售总额': 'sum'
                }).reset_index().sort_values('销售总额', ascending=False)

                if not product_relation.empty:
                    # 显示前5个关联产品
                    top_products = product_relation.head(5)

                    fig = px.bar(
                        top_products,
                        x='销售总额',
                        y='产品名称',
                        title=f"{material} 关联最强的产品 (TOP5)",
                        orientation='h'
                    )

                    fig.update_layout(
                        xaxis_title="关联销售额 (元)",
                        yaxis_title="产品名称",
                        xaxis=dict(tickprefix="￥", tickformat=",.2f"),
                        height=350
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"未找到 {material} 与任何产品的直接关联")
            else:
                st.info(f"未找到 {material} 与任何产品的直接关联")

    # 按物料和产品分组
    material_product_agg = material_product.groupby(['物料名称', '产品名称']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    # 计算投入产出比
    material_product_agg['投入产出比'] = material_product_agg['销售总额'] / material_product_agg['物料总成本'].where(
        material_product_agg['物料总成本'] > 0, np.nan
    )

    cols = st.columns(2)

    with cols[0]:
        if not material_product_agg.empty:
            # 修改TOP物料选择逻辑，考虑多个维度
            st.subheader("热力图显示选项")
            top_by = st.radio(
                "选择TOP5物料的排序依据:",
                ["销售总额", "物料数量", "投入产出比", "物料总成本"],
                horizontal=True
            )

            # 获取前5个物料和前5个产品
            if top_by == "销售总额":
                top_materials = material_product_agg.groupby('物料名称')['销售总额'].sum().nlargest(5).index
                top_products = material_product_agg.groupby('产品名称')['销售总额'].sum().nlargest(5).index
            elif top_by == "物料数量":
                top_materials = material_product_agg.groupby('物料名称')['物料数量'].sum().nlargest(5).index
                top_products = material_product_agg.groupby('产品名称')['销售总额'].sum().nlargest(5).index
            elif top_by == "投入产出比":
                # 先按物料计算平均投入产出比
                material_avg_roi = material_product_agg.groupby('物料名称')['投入产出比'].mean().dropna()
                top_materials = material_avg_roi.nlargest(5).index
                top_products = material_product_agg.groupby('产品名称')['销售总额'].sum().nlargest(5).index
            else:  # 物料总成本
                top_materials = material_product_agg.groupby('物料名称')['物料总成本'].sum().nlargest(5).index
                top_products = material_product_agg.groupby('产品名称')['销售总额'].sum().nlargest(5).index

            # 筛选数据
            heatmap_data = material_product_agg[
                material_product_agg['物料名称'].isin(top_materials) &
                material_product_agg['产品名称'].isin(top_products)
                ]

            # 创建透视表
            if not heatmap_data.empty:
                pivot = heatmap_data.pivot_table(
                    index='物料名称',
                    columns='产品名称',
                    values='销售总额',
                    aggfunc='sum',
                    fill_value=0
                )

                # 创建热力图
                fig = px.imshow(
                    pivot,
                    labels=dict(x="产品名称", y="物料名称", color="销售额 (元)"),
                    x=pivot.columns,
                    y=pivot.index,
                    color_continuous_scale="Blues",
                    title=f"物料-产品销售关联热力图 (TOP5, 按{top_by}排序)",
                    text_auto='.2f'  # 修改为保留两位小数
                )

                fig.update_layout(
                    xaxis=dict(tickangle=-45),
                    height=450
                )

                st.plotly_chart(fig, use_container_width=True)

                # 添加图表解读
                st.markdown("""
                **图表解读：**
                - 热力图展示了TOP5物料与TOP5产品之间的销售关联强度。
                - 颜色越深表示该物料与产品的销售关联越强，即该物料对该产品销售的贡献越大。
                - 水平方向比较可发现哪些产品对特定物料反应最强烈。
                - 垂直方向比较可发现哪些物料对特定产品促销效果最好。
                - 强关联组合应作为核心营销搭配，弱关联组合需评估投放必要性。
                - 建议重点关注深色区域的物料-产品组合，这些是最有效的组合。
                """)
            else:
                st.warning("没有足够的数据来生成热力图")
        else:
            st.warning("没有足够的数据来生成热力图")

    with cols[1]:
        if not material_product_agg.empty:
            # 最佳物料-产品组合
            st.subheader("物料-产品组合排名选项")
            rank_by = st.radio(
                "选择排序依据:",
                ["投入产出比", "销售总额", "物料数量"],
                horizontal=True
            )

            # 根据选择进行排序
            if rank_by == "投入产出比":
                top_pairs = material_product_agg.dropna(subset=['投入产出比']).nlargest(10, '投入产出比')
                value_col = '投入产出比'
                title = "投入产出比最高的物料-产品组合 (TOP10)"
            elif rank_by == "销售总额":
                top_pairs = material_product_agg.nlargest(10, '销售总额')
                value_col = '销售总额'
                title = "销售额最高的物料-产品组合 (TOP10)"
            else:  # 物料数量
                top_pairs = material_product_agg.nlargest(10, '物料数量')
                value_col = '物料数量'
                title = "使用数量最多的物料-产品组合 (TOP10)"

            fig = px.bar(
                top_pairs,
                x=value_col,
                y='物料名称',
                color='产品名称',
                title=title,
                orientation='h',
                height=450
            )

            if rank_by == "投入产出比":
                fig.update_layout(
                    xaxis_title="投入产出比",
                    yaxis_title="物料名称",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(tickformat=".2f")  # 修改为保留两位小数
                )
            elif rank_by == "销售总额":
                fig.update_layout(
                    xaxis_title="销售总额 (元)",
                    yaxis_title="物料名称",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(tickprefix="￥", tickformat=",.2f")  # 修改为保留两位小数
                )
            else:  # 物料数量
                fig.update_layout(
                    xaxis_title="物料数量",
                    yaxis_title="物料名称",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(tickformat=",.0f")  # 不保留小数
                )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            if rank_by == "投入产出比":
                st.markdown("""
                **图表解读：**
                - 此图展示了投入产出比最高的物料-产品组合。
                - 投入产出比 = 销售总额/物料总成本，表示每单位物料成本带来的销售额。
                - 同一物料可能与不同产品组合时效果不同，不同颜色代表不同产品。
                - 图表越长表示投入产出比越高，此组合的物料投资回报越高。
                - 在促销活动设计中，建议优先选择这些高效组合进行推广。
                - 业务人员应学习这些高效组合的成功经验，复制到其他客户。
                """)
            elif rank_by == "销售总额":
                st.markdown("""
                **图表解读：**
                - 此图展示了销售额最高的物料-产品组合。
                - 销售额高表示该组合在绝对规模上贡献较大。
                - 不同颜色代表不同产品，可以看出哪些产品与特定物料组合效果最佳。
                - 这些组合代表了最主流的市场选择，是核心业务组合。
                - 业务团队应确保这些组合的物料供应稳定，保障主要销售渠道。
                """)
            else:  # 物料数量
                st.markdown("""
                **图表解读：**
                - 此图展示了使用数量最多的物料-产品组合。
                - 使用数量高表明该物料的投放量大，是客户频繁需求的物料。
                - 不同颜色代表不同产品，展示了物料的不同使用场景。
                - 数量多的物料需要确保库存充足，并关注其使用效率。
                - 建议评估高使用量物料的投入产出效果，优化资源配置。
                """)
        else:
            st.warning("没有足够的数据来生成物料-产品组合图表")

    # 物料组合分析 - 修改分组方式，更好支持单个物料分析
    if not material_product.empty:
        st.markdown("### 物料组合分析")
        st.info("此部分分析经销商使用的物料组合（多种物料一起使用）的效果。单个物料效果请参考上方图表。")

        # 计算每个客户-月份组合使用的物料组合
        material_combinations = material_product.groupby(['客户代码', '经销商名称', '发运月份']).agg({
            '物料名称': lambda x: ', '.join(sorted(set(x))),
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        # 计算物料组合的效益指标
        material_combinations['投入产出比'] = material_combinations['销售总额'] / material_combinations[
            '物料总成本'].where(
            material_combinations['物料总成本'] > 0, np.nan
        )

        # 分析物料组合效果 - 修改为仅计算包含2个及以上物料的组合
        # 添加物料数量统计
        material_combinations['物料数量'] = material_combinations['物料名称'].apply(lambda x: len(x.split(', ')))

        # 单物料与组合分开分析
        single_materials = material_combinations[material_combinations['物料数量'] == 1].copy()
        multi_materials = material_combinations[material_combinations['物料数量'] > 1].copy()

        # 先分析单物料效果
        if not single_materials.empty:
            st.subheader("单个物料效果分析")

            # 对单物料进行分组分析
            single_analysis = single_materials.groupby('物料名称').agg({
                '客户代码': 'count',
                '物料总成本': 'sum',
                '销售总额': 'sum',
                '投入产出比': 'mean'
            }).reset_index()

            single_analysis.columns = ['物料名称', '使用次数', '物料总成本', '销售总额', '平均投入产出比']

            # 筛选使用次数>=2的物料
            frequent_singles = single_analysis[single_analysis['使用次数'] >= 2]

            if not frequent_singles.empty:
                # 创建单物料效率条形图
                top_singles = frequent_singles.nlargest(10, '平均投入产出比')

                fig = px.bar(
                    top_singles,
                    x='平均投入产出比',
                    y='物料名称',
                    color='使用次数',
                    color_continuous_scale='Viridis',
                    title="高效单物料TOP10",
                    orientation='h',
                    hover_data=['物料总成本', '销售总额']
                )

                fig.update_layout(
                    xaxis_title="平均投入产出比",
                    yaxis_title="物料名称",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(tickformat=".2f"),
                    height=400
                )

                st.plotly_chart(fig, use_container_width=True)

                # 添加图表解读
                st.markdown("""
                **单物料效果解读：**
                - 此图展示了当单独使用时效果最好的物料TOP10。
                - 平均投入产出比越高，表示该物料单独使用时产生的销售效益越高。
                - 点的颜色表示使用次数，颜色越深表示样本越多，结果越可靠。
                - 这些高效单物料适合向对成本敏感或首次合作的客户推荐。
                - 单物料使用简单直接，可以快速验证效果，是初步合作的良好选择。
                """)
            else:
                st.info("数据中没有足够的单物料使用记录进行分析")

        # 再分析物料组合
        if not multi_materials.empty:
            st.subheader("物料组合效果分析")

            # 对物料组合进行分组分析
            combo_analysis = multi_materials.groupby('物料名称').agg({
                '客户代码': 'count',
                '物料总成本': 'sum',
                '销售总额': 'sum',
                '投入产出比': 'mean'
            }).reset_index()

            combo_analysis.columns = ['物料组合', '使用次数', '物料总成本', '销售总额', '平均投入产出比']

            # 筛选出现次数>=2的组合
            frequent_combos = combo_analysis[combo_analysis['使用次数'] >= 2]

            if not frequent_combos.empty:
                # 创建组合效率条形图
                top_combos = frequent_combos.nlargest(10, '平均投入产出比')

                fig = px.bar(
                    top_combos,
                    x='平均投入产出比',
                    y='物料组合',
                    color='使用次数',
                    color_continuous_scale='Viridis',
                    title="高效物料组合TOP10",
                    orientation='h',
                    hover_data=['物料总成本', '销售总额']
                )

                fig.update_layout(
                    xaxis_title="平均投入产出比",
                    yaxis_title="物料组合",
                    yaxis=dict(autorange="reversed"),
                    xaxis=dict(tickformat=".2f"),
                    height=500
                )

                # 为悬停数据添加格式化
                fig.update_traces(
                    hovertemplate='<b>%{y}</b><br>平均投入产出比: %{x:.2f}<br>使用次数: %{marker.color}<br>物料总成本: ￥%{customdata[0]:.2f}<br>销售总额: ￥%{customdata[1]:.2f}'
                )

                st.plotly_chart(fig, use_container_width=True)

                # 添加图表解读
                st.markdown("""
                **物料组合效果解读：**
                - 此图展示了效率最高的物料组合TOP10，颜色深浅表示组合的使用频次。
                - 物料组合是指经销商同时使用的多种物料，组合使用往往比单一物料效果更好。
                - 平均投入产出比越高，表示该组合产生的销售效益越高。
                - 使用次数较多且投入产出比高的组合（图右侧深色部分）是最值得推广的组合。
                - 业务团队可以：
                  * 向其他经销商推广这些高效组合
                  * 分析这些组合为何高效，找出物料协同效应
                  * 设计包含这些组合的促销方案
                  * 培训销售人员如何向客户推荐最佳物料组合
                """)

                # 添加物料组合分析工具
                st.subheader("物料组合分析工具")
                st.info("输入想要分析的物料名称，查看其在哪些组合中效果最佳")

                material_to_analyze = st.text_input("输入物料名称 (例如: 挂网挂条)", "", key="combo_analysis")

                if material_to_analyze:
                    # 找出包含该物料的所有组合
                    containing_combos = combo_analysis[
                        combo_analysis['物料组合'].str.contains(material_to_analyze, case=False)]

                    if not containing_combos.empty:
                        st.success(f"找到 {len(containing_combos)} 个包含 '{material_to_analyze}' 的物料组合")

                        # 展示效果最好的组合
                        best_combos = containing_combos.nlargest(5, '平均投入产出比')

                        fig = px.bar(
                            best_combos,
                            x='平均投入产出比',
                            y='物料组合',
                            color='使用次数',
                            color_continuous_scale='Viridis',
                            title=f"包含 '{material_to_analyze}' 的最佳组合TOP5",
                            orientation='h',
                            hover_data=['物料总成本', '销售总额']
                        )

                        fig.update_layout(
                            xaxis_title="平均投入产出比",
                            yaxis_title="物料组合",
                            yaxis=dict(autorange="reversed"),
                            xaxis=dict(tickformat=".2f"),
                            height=350
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        # 提供组合建议
                        st.markdown(f"""
                        **物料 '{material_to_analyze}' 组合建议:**
                        - 此物料在与其他物料组合使用时效果最好，特别是上图所示的TOP5组合。
                        - 平均投入产出比最高的组合为: {best_combos.iloc[0]['物料组合']}
                        - 使用次数最多的组合为: {containing_combos.nlargest(1, '使用次数').iloc[0]['物料组合']}
                        - 建议销售人员向客户推荐这些经过验证的高效组合。
                        """)
                    else:
                        st.warning(f"未找到包含 '{material_to_analyze}' 的物料组合数据")
            else:
                st.warning("没有足够的物料组合数据来进行分析")
        else:
            st.warning("数据中没有多物料组合使用记录")
    else:
        st.warning("没有足够的数据来进行物料组合分析")


def create_sidebar_filters(df_material):
    """创建侧边栏过滤器"""
    st.sidebar.header("数据筛选")

    # 获取所有区域和省份
    regions = sorted(df_material['所属区域'].dropna().unique())
    provinces = sorted(df_material['省份'].dropna().unique())

    # 区域筛选器
    selected_regions = st.sidebar.multiselect(
        "选择区域:",
        options=regions,
        default=[]
    )

    # 省份筛选器
    selected_provinces = st.sidebar.multiselect(
        "选择省份:",
        options=provinces,
        default=[]
    )

    # 获取可用的发运月份列表（唯一值）
    if '发运月份' in df_material.columns:
        try:
            # 确保发运月份是datetime类型
            if not pd.api.types.is_datetime64_any_dtype(df_material['发运月份']):
                df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])

            # 提取年月格式
            available_months = sorted(df_material['发运月份'].dt.strftime('%Y-%m').unique())

            # 设置默认选择范围
            if len(available_months) > 0:
                default_start = available_months[0]
                default_end = available_months[-1]
            else:
                current_date = datetime.now()
                default_start = (current_date - timedelta(days=365)).strftime('%Y-%m')
                default_end = current_date.strftime('%Y-%m')
        except Exception as e:
            st.warning(f"处理发运月份数据时出错: {e}")
            current_date = datetime.now()
            available_months = [
                (current_date - timedelta(days=i * 30)).strftime('%Y-%m')
                for i in range(12, -1, -1)
            ]
            default_start = available_months[0]
            default_end = available_months[-1]
    else:
        current_date = datetime.now()
        available_months = [
            (current_date - timedelta(days=i * 30)).strftime('%Y-%m')
            for i in range(12, -1, -1)
        ]
        default_start = available_months[0]
        default_end = available_months[-1]

    # 使用选择框选择开始月份和结束月份
    col1, col2 = st.sidebar.columns(2)

    with col1:
        start_month = st.selectbox(
            "开始月份:",
            options=available_months,
            index=available_months.index(default_start) if default_start in available_months else 0
        )

    with col2:
        # 确保结束月份不早于开始月份
        end_month_options = [m for m in available_months if m >= start_month]
        end_month = st.selectbox(
            "结束月份:",
            options=end_month_options,
            index=end_month_options.index(default_end) if default_end in end_month_options else len(
                end_month_options) - 1
        )

    # 将月份字符串转换为datetime对象，设置为月份的第一天
    start_date = pd.to_datetime(f"{start_month}-01")
    # 为结束月份设置为下个月的第一天减去一天（即当月最后一天）
    end_month_dt = pd.to_datetime(f"{end_month}-01")
    next_month = end_month_dt + pd.DateOffset(months=1)
    end_date = next_month - pd.DateOffset(days=1)

    return selected_regions, selected_provinces, start_date, end_date


# 主函数中也需要添加调试代码
def main():
    # 页面标题
    st.markdown("<h1 class='main-header'>物料与销售分析仪表盘</h1>", unsafe_allow_html=True)

    # 添加密码保护
    password = st.text_input("请输入访问密码:", type="password")

    # 验证密码
    if password != "SAL":
        st.warning("请输入正确的密码以访问仪表盘")
        st.stop()  # 如果密码不正确，停止执行后续代码

    # 密码正确，继续执行原有代码
    # 加载数据
    with st.spinner("正在加载数据，请稍候..."):
        df_material, df_sales, df_material_price = load_data()

    # 创建侧边栏过滤器
    selected_regions, selected_provinces, start_date, end_date = create_sidebar_filters(df_material)

    # 添加调试信息
    st.sidebar.write(f"筛选月份范围: {start_date.strftime('%Y-%m')} 至 {end_date.strftime('%Y-%m')}")
    if '销售总额' in df_sales.columns:
        raw_sales_total = df_sales['销售总额'].sum()
        st.sidebar.write(f"原始销售总额: ¥{raw_sales_total:,.2f}")

    # 应用过滤器
    filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
    filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

    # 打印筛选后数据行数
    st.sidebar.write(f"筛选后物料数据行数: {len(filtered_material)}")
    st.sidebar.write(f"筛选后销售数据行数: {len(filtered_sales)}")

    # 检查过滤后的数据是否为空
    if filtered_material.empty or filtered_sales.empty:
        st.warning("当前筛选条件下没有数据。请尝试更改筛选条件。")
        return

    # 计算关键绩效指标
    total_material_cost = filtered_material['物料总成本'].sum()
    total_sales = filtered_sales['销售总额'].sum()

    # 添加调试信息
    st.sidebar.write(f"筛选后销售总额: ¥{total_sales:,.2f}")

    # 如果总额仍然不对，可以尝试手动重新计算
    recalculated_sales = (filtered_sales['求和项:数量（箱）'] * filtered_sales['求和项:单价（箱）']).sum()
    st.sidebar.write(f"重新计算的销售总额: ¥{recalculated_sales:,.2f}")

    # 如果有明显差异，使用重新计算的值
    if abs(total_sales - recalculated_sales) > 1:
        st.sidebar.warning("销售总额存在计算差异，使用重新计算的值")
        total_sales = recalculated_sales

    overall_cost_sales_ratio = calculate_fee_ratio(total_material_cost, total_sales)
    avg_material_effectiveness = total_sales / filtered_material['物料数量'].sum() if filtered_material[
                                                                                          '物料数量'].sum() > 0 else 0

    # 显示KPI卡片
    display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness)

    # 创建分析选项卡
    tabs = st.tabs([
        "区域分析",
        "时间趋势",
        "客户价值",
        "物料效益",
        "物料-产品关联"
    ])

    # 渲染各个选项卡
    with tabs[0]:
        # 先执行原有的区域分析
        region_analysis(filtered_material, filtered_sales)

        # 添加一个分隔符
        st.markdown("---")

        # 再执行申请人使用物料效率分析
        applicant_material_efficiency_analysis(filtered_material, filtered_sales)

    with tabs[1]:
        time_analysis(filtered_material, filtered_sales)

    with tabs[2]:
        customer_analysis(filtered_material, filtered_sales)

    with tabs[3]:
        material_analysis(filtered_material, filtered_sales)

    with tabs[4]:
        material_product_analysis(filtered_material, filtered_sales)

    # 添加页脚信息
    st.markdown("""
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
        <p>口力营销物料与销售分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年4月</p>
        <p>使用Streamlit和Plotly构建 | 数据更新频率: 每季度</p>
    </div>
    """, unsafe_allow_html=True)


# 运行应用
if __name__ == "__main__":
    main()