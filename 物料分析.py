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


# 加载数据
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

        # 简化处理物料单价数据
        if '物料代码' in df_material_price.columns and '单价（元）' in df_material_price.columns:
            pass
        elif '物料代码' in df_material_price.columns:
            # 尝试找到价格列
            price_col = [col for col in df_material_price.columns if '单价' in col or '价格' in col][0]
            df_material_price = df_material_price[['物料代码', price_col]]
            df_material_price.columns = ['物料代码', '单价（元）']
        else:
            # 使用前两列作为物料代码和单价
            df_material_price.columns = ['物料代码' if i == 0 else '单价（元）' if i == 1 else f'列{i + 1}'
                                         for i in range(len(df_material_price.columns))]
            df_material_price = df_material_price[['物料代码', '单价（元）']]

        st.success("成功加载数据文件")

    except Exception as e:
        st.warning(f"无法加载Excel文件: {e}，创建模拟数据用于演示...")

        # 创建模拟数据
        # 生成日期范围
        date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS')

        # 区域、省份、城市和经销商数据
        regions = ['华北区', '华东区', '华南区', '西南区', '东北区']
        provinces = ['北京', '上海', '广东', '四川', '浙江', '江苏', '湖北', '辽宁', '黑龙江', '河南']
        cities = ['北京', '上海', '广州', '成都', '杭州', '南京', '武汉', '沈阳', '哈尔滨', '郑州']
        distributors = [f'经销商{i}' for i in range(1, 21)]
        customer_codes = [f'C{i:04d}' for i in range(1, 21)]
        sales_persons = [f'销售{i}' for i in range(1, 11)]

        # 物料数据
        material_codes = [f'M{i:04d}' for i in range(1, 11)]
        material_names = ['促销海报', '展示架', '货架陈列', '柜台展示', '地贴', '吊旗', '宣传册', '样品', '门店招牌',
                          '促销礼品']
        material_prices = [100, 500, 300, 200, 50, 80, 20, 5, 1000, 10]

        # 产品数据
        product_codes = [f'P{i:04d}' for i in range(1, 11)]
        product_names = ['口力薄荷糖', '口力泡泡糖', '口力果味糖', '口力清新糖', '口力夹心糖', '口力棒棒糖', '口力软糖',
                         '口力硬糖', '口力奶糖', '口力巧克力']
        product_prices = [20, 25, 18, 22, 30, 15, 28, 26, 35, 40]

        # 创建物料单价数据
        df_material_price = pd.DataFrame({
            '物料代码': material_codes,
            '单价（元）': material_prices
        })

        # 创建物料数据
        material_data = []
        for _ in range(500):  # 生成500条记录
            date = np.random.choice(date_range)
            region = np.random.choice(regions)
            province = np.random.choice(provinces)
            city = np.random.choice(cities)
            distributor_idx = np.random.randint(0, len(distributors))
            distributor = distributors[distributor_idx]
            customer_code = customer_codes[distributor_idx]
            material_idx = np.random.randint(0, len(material_codes))
            material_code = material_codes[material_idx]
            material_name = material_names[material_idx]
            material_quantity = np.random.randint(1, 100)
            sales_person = np.random.choice(sales_persons)

            material_data.append({
                '发运月份': date,
                '所属区域': region,
                '省份': province,
                '城市': city,
                '经销商名称': distributor,
                '客户代码': customer_code,
                '物料代码': material_code,
                '物料名称': material_name,
                '物料数量': material_quantity,
                '申请人': sales_person
            })

        df_material = pd.DataFrame(material_data)

        # 创建销售数据
        sales_data = []
        for _ in range(600):  # 生成600条记录
            date = np.random.choice(date_range)
            region = np.random.choice(regions)
            province = np.random.choice(provinces)
            city = np.random.choice(cities)
            distributor_idx = np.random.randint(0, len(distributors))
            distributor = distributors[distributor_idx]
            customer_code = customer_codes[distributor_idx]
            product_idx = np.random.randint(0, len(product_codes))
            product_code = product_codes[product_idx]
            product_name = product_names[product_idx]
            product_price = product_prices[product_idx]
            product_quantity = np.random.randint(10, 1000)
            sales_person = np.random.choice(sales_persons)

            sales_data.append({
                '发运月份': date,
                '所属区域': region,
                '省份': province,
                '城市': city,
                '经销商名称': distributor,
                '客户代码': customer_code,
                '产品代码': product_code,
                '产品名称': product_name,
                '求和项:数量（箱）': product_quantity,
                '求和项:单价（箱）': product_price,
                '申请人': sales_person
            })

        df_sales = pd.DataFrame(sales_data)

    # 数据预处理
    # 1. 确保日期格式一致
    df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
    df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])

    # 2. 将物料单价添加到物料数据中
    material_price_dict = dict(zip(df_material_price['物料代码'], df_material_price['单价（元）']))
    df_material['物料单价'] = df_material['物料代码'].map(material_price_dict)
    df_material['物料单价'].fillna(0, inplace=True)

    # 3. 计算物料总成本
    df_material['物料总成本'] = df_material['物料数量'] * df_material['物料单价']

    # 4. 计算销售总额
    df_sales['销售总额'] = df_sales['求和项:数量（箱）'] * df_sales['求和项:单价（箱）']

    return df_material, df_sales, df_material_price


# 筛选数据函数
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
        filtered_df = filtered_df[(filtered_df['发运月份'] >= pd.Timestamp(start_date)) &
                                  (filtered_df['发运月份'] <= pd.Timestamp(end_date))]

    return filtered_df


# 计算费比
def calculate_fee_ratio(cost, sales):
    """计算费比 = (物料成本 / 销售额) * 100%"""
    if sales > 0:
        return (cost / sales) * 100
    return 0


# 创建KPI卡片
def display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness):
    """显示KPI卡片"""
    cols = st.columns(4)

    # 总物料成本
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总物料成本</p>
            <p class="card-value">￥{total_material_cost:,.0f}</p>
            <p class="card-text">总投入物料资金</p>
        </div>
        """, unsafe_allow_html=True)

    # 总销售额
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总销售额</p>
            <p class="card-value">￥{total_sales:,.0f}</p>
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

    # 平均物料效益
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
                texttemplate='￥%{text:,.0f}',
                textposition='outside'
            )
            fig.update_layout(
                xaxis_title="区域",
                yaxis_title="销售总额 (元)",
                yaxis=dict(tickprefix="￥")
            )
            st.plotly_chart(fig, use_container_width=True)
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
                texttemplate='%{text:.2f}%',
                textposition='outside'
            )
            fig.update_layout(
                xaxis_title="区域",
                yaxis_title="费比 (%)",
                yaxis=dict(ticksuffix="%")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("没有足够的数据来生成区域费比图表")


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

        # 更新y轴
        fig.update_yaxes(title_text="销售总额 (元)", secondary_y=False, tickprefix="￥")
        fig.update_yaxes(title_text="物料成本 (元)", secondary_y=True, tickprefix="￥")

        st.plotly_chart(fig, use_container_width=True)

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
            yaxis=dict(ticksuffix="%"),
            height=400
        )

        st.plotly_chart(fig_fee, use_container_width=True)
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

    # 计算客户价值指标
    customer_value['费比'] = customer_value.apply(
        lambda row: calculate_fee_ratio(row['物料总成本'], row['销售总额']), axis=1
    )
    customer_value['物料效率'] = customer_value['销售总额'] / customer_value['物料数量'].where(
        customer_value['物料数量'] > 0, np.nan
    )
    customer_value['客户价值'] = customer_value['销售总额'] - customer_value['物料总成本']
    customer_value['ROI'] = customer_value['销售总额'] / customer_value['物料总成本'].where(
        customer_value['物料总成本'] > 0, np.nan
    )

    # 创建客户价值分布图
    cols = st.columns(2)

    with cols[0]:
        if not customer_value.empty:
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
                texttemplate='￥%{text:,.0f}',
                textposition='outside'
            )

            fig.update_layout(
                xaxis_title="经销商",
                yaxis_title="客户价值 (元)",
                xaxis=dict(tickangle=-45),
                yaxis=dict(tickprefix="￥"),
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("没有足够的数据来生成客户价值分布图表")

    with cols[1]:
        if not customer_value.empty:
            # 客户ROI散点图
            fig = px.scatter(
                customer_value,
                x='物料总成本',
                y='销售总额',
                size='ROI',
                color='费比',
                hover_name='经销商名称',
                title="客户ROI矩阵",
                labels={
                    '物料总成本': '物料总成本 (元)',
                    '销售总额': '销售总额 (元)',
                    'ROI': 'ROI',
                    '费比': '费比 (%)'
                },
                color_continuous_scale='RdYlGn_r',
                size_max=50
            )

            # 添加ROI=1参考线
            max_cost = customer_value['物料总成本'].max() * 1.1
            min_cost = customer_value['物料总成本'].min() * 0.9

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
                xaxis=dict(tickprefix="￥", type="log"),
                yaxis=dict(tickprefix="￥", type="log")
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("没有足够的数据来生成客户ROI矩阵")

    # 客户分群分析
    if not customer_value.empty and len(customer_value) >= 4:
        st.markdown("### 客户分群分析")

        # 简化的客户分群
        customer_value['价值得分'] = pd.qcut(
            customer_value['客户价值'].rank(method='first'),
            4,
            labels=[1, 2, 3, 4]
        ).astype(int)

        customer_value['效率得分'] = pd.qcut(
            customer_value['物料效率'].rank(method='first'),
            4,
            labels=[1, 2, 3, 4]
        ).astype(int)

        # 定义客户分群
        def get_customer_group(row):
            if row['价值得分'] >= 3 and row['效率得分'] >= 3:
                return '核心客户'
            elif row['价值得分'] >= 3 and row['效率得分'] < 3:
                return '高潜力客户'
            elif row['价值得分'] < 3 and row['效率得分'] >= 3:
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

        # 添加平均线
        avg_value = customer_value['客户价值'].median()
        avg_efficiency = customer_value['物料效率'].median()

        fig.add_vline(x=avg_value, line_dash="dash", line_color="gray")
        fig.add_hline(y=avg_efficiency, line_dash="dash", line_color="gray")

        fig.update_layout(
            height=600,
            xaxis=dict(tickprefix="￥"),
            yaxis=dict(tickprefix="￥")
        )

        st.plotly_chart(fig, use_container_width=True)

        # 分群统计
        st.markdown("### 客户分群统计")
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
        group_stats['客户占比'] = group_stats['客户数量'] / group_stats['客户数量'].sum() * 100
        group_stats['价值占比'] = group_stats['客户价值总和'] / group_stats['客户价值总和'].sum() * 100

        # 格式化显示
        display_cols = ['客户分群', '客户数量', '客户占比', '销售总额', '客户价值总和', '价值占比', '平均费比',
                        '平均物料效率']
        fmt_group_stats = group_stats[display_cols].copy()

        # 格式化数值列
        fmt_group_stats['客户占比'] = fmt_group_stats['客户占比'].map('{:.1f}%'.format)
        fmt_group_stats['销售总额'] = fmt_group_stats['销售总额'].map('￥{:,.0f}'.format)
        fmt_group_stats['客户价值总和'] = fmt_group_stats['客户价值总和'].map('￥{:,.0f}'.format)
        fmt_group_stats['价值占比'] = fmt_group_stats['价值占比'].map('{:.1f}%'.format)
        fmt_group_stats['平均费比'] = fmt_group_stats['平均费比'].map('{:.2f}%'.format)
        fmt_group_stats['平均物料效率'] = fmt_group_stats['平均物料效率'].map('￥{:,.2f}'.format)

        st.dataframe(fmt_group_stats, use_container_width=True)


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

    # 计算ROI
    material_roi['ROI'] = material_roi['销售总额'] / material_roi['物料总成本'].where(
        material_roi['物料总成本'] > 0, np.nan
    )

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
                texttemplate='%{text:.2f}',
                textposition='outside'
            )

            fig.update_layout(
                xaxis_title="物料",
                yaxis_title="ROI",
                xaxis=dict(tickangle=-45),
                height=450
            )

            st.plotly_chart(fig, use_container_width=True)
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
                成本: ￥{row['物料总成本']:,.0f}，
                销售额: ￥{row['销售总额']:,.0f}</li>
                """, unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)

        with opt_cols[1]:
            st.markdown("""
            <div class="alert-box alert-danger">
                <h4 style="margin-top: 0;">低ROI物料 (建议优化投放)</h4>
                <ul style="margin-bottom: 0;">
            """, unsafe_allow_html=True)

            for _, row in low_roi_materials.iterrows():
                st.markdown(f"""
                <li><strong>{row['物料名称']}</strong> - ROI: {row['ROI']:.2f}，
                成本: ￥{row['物料总成本']:,.0f}，
                销售额: ￥{row['销售总额']:,.0f}</li>
                """, unsafe_allow_html=True)

            st.markdown("</ul></div>", unsafe_allow_html=True)


# 物料-产品关联分析
def material_product_analysis(filtered_material, filtered_sales):
    """物料-产品关联分析"""
    st.markdown("## 物料-产品关联分析")

    # 合并物料和销售数据
    material_product = pd.merge(
        filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
        filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
        on=['发运月份', '客户代码', '经销商名称'],
        how='inner'
    )

    if material_product.empty:
        st.warning("没有匹配的物料-产品数据来进行关联分析")
        return

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
            # 获取前5个物料和前5个产品
            top_materials = material_product_agg.groupby('物料名称')['销售总额'].sum().nlargest(5).index
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
                    title="物料-产品销售关联热力图 (TOP5)",
                    text_auto='.2s'
                )

                fig.update_layout(
                    xaxis=dict(tickangle=-45),
                    height=450
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("没有足够的数据来生成热力图")
        else:
            st.warning("没有足够的数据来生成热力图")

    with cols[1]:
        if not material_product_agg.empty:
            # 最佳物料-产品组合
            top_pairs = material_product_agg.dropna(subset=['投入产出比']).nlargest(10, '投入产出比')

            fig = px.bar(
                top_pairs,
                x='投入产出比',
                y='物料名称',
                color='产品名称',
                title="最佳物料-产品组合 (TOP10)",
                orientation='h',
                height=450
            )

            fig.update_layout(
                xaxis_title="投入产出比",
                yaxis_title="物料名称",
                yaxis=dict(autorange="reversed")
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("没有足够的数据来生成物料-产品组合图表")

    # 物料组合分析
    if not material_product.empty:
        st.markdown("### 物料组合分析")

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

        # 分析物料组合效果
        combo_analysis = material_combinations.groupby('物料名称').agg({
            '客户代码': 'count',
            '物料总成本': 'sum',
            '销售总额': 'sum',
            '投入产出比': 'mean'
        }).reset_index()

        combo_analysis.columns = ['物料组合', '使用次数', '物料总成本', '销售总额', '平均投入产出比']

        # 筛选出现次数>=3的组合
        frequent_combos = combo_analysis[combo_analysis['使用次数'] >= 3]

        if not frequent_combos.empty:
            # 显示前10个高效组合
            top_combos = frequent_combos.nlargest(10, '平均投入产出比')

            # 格式化显示
            formatted_combos = top_combos.copy()
            formatted_combos['物料总成本'] = formatted_combos['物料总成本'].map('￥{:,.0f}'.format)
            formatted_combos['销售总额'] = formatted_combos['销售总额'].map('￥{:,.0f}'.format)
            formatted_combos['平均投入产出比'] = formatted_combos['平均投入产出比'].map('{:.2f}'.format)

            st.dataframe(formatted_combos, use_container_width=True)
        else:
            st.warning("没有足够的物料组合数据来进行分析")


# 创建侧边栏过滤器
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

    # 日期范围筛选器
    try:
        # 确保日期列为datetime类型
        if '发运月份' in df_material.columns:
            min_date = df_material['发运月份'].min().date()
            max_date = df_material['发运月份'].max().date()
        else:
            min_date = datetime.now().date() - timedelta(days=365)
            max_date = datetime.now().date()
    except:
        min_date = datetime.now().date() - timedelta(days=365)
        max_date = datetime.now().date()

    date_range = st.sidebar.date_input(
        "选择日期范围:",
        value=(min_date, max_date)
    )

    # 处理日期选择结果
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = min_date
        end_date = max_date

    # 添加帮助信息
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px;'>
        <h4 style='color: #1f3867; margin-top: 0;'>使用说明</h4>
        <p style='font-size: 0.9rem;'>
            通过上方筛选器可以过滤数据范围。选择区域、省份和时间范围后，仪表盘内所有图表将自动更新。
        </p>
        <p style='font-size: 0.9rem;'>
            点击图表可放大查看详情，鼠标悬停可查看具体数据点信息。
        </p>
    </div>
    """, unsafe_allow_html=True)

    return selected_regions, selected_provinces, start_date, end_date


# 主函数
def main():
    # 页面标题
    st.markdown("<h1 class='main-header'>口力营销物料与销售分析仪表盘</h1>", unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载数据，请稍候..."):
        df_material, df_sales, df_material_price = load_data()

    # 创建侧边栏过滤器
    selected_regions, selected_provinces, start_date, end_date = create_sidebar_filters(df_material)

    # 应用过滤器
    filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
    filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

    # 检查过滤后的数据是否为空
    if filtered_material.empty or filtered_sales.empty:
        st.warning("当前筛选条件下没有数据。请尝试更改筛选条件。")
        return

    # 计算关键绩效指标
    total_material_cost = filtered_material['物料总成本'].sum()
    total_sales = filtered_sales['销售总额'].sum()
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
        region_analysis(filtered_material, filtered_sales)

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
        <p>使用Streamlit和Plotly构建 | 数据更新频率: 每月</p>
    </div>
    """, unsafe_allow_html=True)


# 运行应用
if __name__ == "__main__":
    main()