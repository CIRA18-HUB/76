import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings

# 设置页面配置
st.set_page_config(
    page_title="口力营销物料与销售分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
warnings.filterwarnings('ignore')

# 自定义CSS样式
st.markdown("""
<style>
    * {font-family: "Microsoft YaHei", "SimHei", sans-serif;}
    .main-header {font-size: 2rem; color: #1f3867; text-align: center; margin-bottom: 1rem;}
    .section-header {font-size: 1.5rem; color: #1f3867; margin-top: 1.5rem; margin-bottom: 1rem;}
    .card {background-color: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); 
           padding: 1rem; margin-bottom: 1rem;}
    .metric-card {text-align: center; padding: 1rem; background-color: white; border-radius: 5px;
                 box-shadow: 0 2px 5px rgba(0,0,0,0.1); height: 100%;}
    .card-header {font-size: 1rem; color: #666; margin-bottom: 0.5rem;}
    .card-value {font-size: 1.8rem; font-weight: bold; color: #1f3867;}
    .progress-bar {height: 6px; background-color: #f0f0f0; border-radius: 3px; margin: 0.5rem 0;}
    .progress-value {height: 100%; border-radius: 3px;}
</style>
""", unsafe_allow_html=True)


# 加载数据
@st.cache_data(ttl=3600)
def load_data():
    """加载物料和销售数据"""
    try:
        # 加载真实数据
        material_file = "2025物料源数据.xlsx"
        sales_file = "25物料源销售数据.xlsx"
        price_file = "物料单价.xlsx"

        df_material = pd.read_excel(material_file)
        df_sales = pd.read_excel(sales_file)
        df_material_price = pd.read_excel(price_file)

        st.success("成功加载数据文件")

    except Exception as e:
        st.warning(f"无法加载Excel文件: {e}，创建模拟数据用于演示...")

        # 创建模拟数据
        # 日期范围
        date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS')

        # 模拟数据参数
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
        product_names = ['口力薄荷糖', '口力泡泡糖', '口力果味糖', '口力清新糖', '口力夹心糖', '口力棒棒糖',
                         '口力软糖', '口力硬糖', '口力奶糖', '口力巧克力']
        product_prices = [20, 25, 18, 22, 30, 15, 28, 26, 35, 40]

        # 创建物料单价数据
        material_price_data = {
            '物料代码': material_codes,
            '物料名称': material_names,
            '单价（元）': material_prices
        }
        df_material_price = pd.DataFrame(material_price_data)

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

    # 数据清理与预处理
    # 确保日期格式一致
    df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
    df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])

    # 确保文本列的数据类型一致
    text_columns_material = ['所属区域', '省份', '城市', '经销商名称', '客户代码', '物料代码', '物料名称', '申请人']
    text_columns_sales = ['所属区域', '省份', '城市', '经销商名称', '客户代码', '产品代码', '产品名称', '申请人']

    for col in text_columns_material:
        if col in df_material.columns:
            df_material[col] = df_material[col].astype(str)

    for col in text_columns_sales:
        if col in df_sales.columns:
            df_sales[col] = df_sales[col].astype(str)

    # 处理物料单价数据
    material_price_dict = dict(zip(df_material_price['物料代码'], df_material_price['单价（元）']))
    df_material['物料单价'] = df_material['物料代码'].map(material_price_dict)
    df_material['物料单价'].fillna(0, inplace=True)
    df_material['物料总成本'] = df_material['物料数量'] * df_material['物料单价']

    # 计算销售总额
    df_sales['销售总额'] = df_sales['求和项:数量（箱）'] * df_sales['求和项:单价（箱）']

    return df_material, df_sales, df_material_price


# 辅助函数
def calculate_fee_ratio(cost, sales):
    """安全地计算费比 = (物料成本 / 销售总额) * 100%"""
    if sales is None or cost is None or sales == 0:
        return 0
    return (cost / sales) * 100 if sales > 0 else 0


def filter_data(df, regions=None, provinces=None, start_date=None, end_date=None):
    """过滤数据"""
    filtered_df = df.copy()

    # 区域筛选
    if regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df['所属区域'].isin(regions)]

    # 省份筛选
    if provinces and len(provinces) > 0:
        filtered_df = filtered_df[filtered_df['省份'].isin(provinces)]

    # 日期筛选
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['发运月份'] >= pd.to_datetime(start_date)) &
                                  (filtered_df['发运月份'] <= pd.to_datetime(end_date))]

    return filtered_df


# 显示KPI卡片
def display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness):
    """显示核心KPI指标卡片"""
    st.markdown("<h3 class='section-header'>核心绩效指标</h3>", unsafe_allow_html=True)

    # 卡片颜色和进度条
    fee_ratio_color = "#f5365c" if overall_cost_sales_ratio > 5 else "#fb6340" if overall_cost_sales_ratio > 3 else "#2dce89"
    fee_ratio_percentage = min(overall_cost_sales_ratio * 10, 100)

    # 创建四个并列的卡片
    cols = st.columns(4)

    # 总物料成本卡片
    with cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总物料成本</p>
            <p class="card-value">￥{total_material_cost:,.0f}</p>
            <div class="progress-bar">
                <div class="progress-value" style="width: 100%; background-color: #1f3867;"></div>
            </div>
            <p style="font-size: 0.9rem; color: #6c757d; margin-top: 10px;">总投入物料资金</p>
        </div>
        """, unsafe_allow_html=True)

    # 总销售额卡片
    with cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总销售额</p>
            <p class="card-value">￥{total_sales:,.0f}</p>
            <div class="progress-bar">
                <div class="progress-value" style="width: 100%; background-color: #2dce89;"></div>
            </div>
            <p style="font-size: 0.9rem; color: #6c757d; margin-top: 10px;">总体销售收入</p>
        </div>
        """, unsafe_allow_html=True)

    # 总体费比卡片
    with cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">总体费比</p>
            <p class="card-value">{overall_cost_sales_ratio:.2f}%</p>
            <div class="progress-bar">
                <div class="progress-value" style="width: {fee_ratio_percentage}%; background-color: {fee_ratio_color};"></div>
            </div>
            <p style="font-size: 0.9rem; color: #6c757d; margin-top: 10px;">物料成本占销售额比例</p>
        </div>
        """, unsafe_allow_html=True)

    # 平均物料效益卡片
    with cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <p class="card-header">平均物料效益</p>
            <p class="card-value">￥{avg_material_effectiveness:,.0f}</p>
            <div class="progress-bar">
                <div class="progress-value" style="width: 100%; background-color: #11cdef;"></div>
            </div>
            <p style="font-size: 0.9rem; color: #6c757d; margin-top: 10px;">每单位物料平均产生销售额</p>
        </div>
        """, unsafe_allow_html=True)


# 区域分析图表函数
def create_region_analysis(filtered_material, filtered_sales):
    """创建区域分析图表"""
    st.markdown("<h3 class='section-header'>区域分析</h3>", unsafe_allow_html=True)

    # 按区域聚合数据
    region_material = filtered_material.groupby('所属区域').agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    region_sales = filtered_sales.groupby('所属区域').agg({
        '销售总额': 'sum'
    }).reset_index()

    # 合并区域数据
    region_metrics = pd.merge(region_material, region_sales, on='所属区域', how='outer')
    region_metrics['费比'] = calculate_fee_ratio(region_metrics['物料总成本'], region_metrics['销售总额'])
    region_metrics['物料效率'] = region_metrics['销售总额'] / region_metrics['物料数量'].where(
        region_metrics['物料数量'] > 0, np.nan)

    # 计算销售额百分比
    total_sales = region_metrics['销售总额'].sum() if not region_metrics.empty else 0
    region_metrics['销售额百分比'] = (region_metrics['销售总额'] / total_sales * 100) if total_sales > 0 else 0

    # 创建两列布局
    col1, col2 = st.columns(2)

    with col1:
        # 区域销售额柱状图
        fig_sales = px.bar(
            region_metrics.sort_values('销售总额', ascending=False),
            x='所属区域',
            y='销售总额',
            title="各区域销售总额",
            color='所属区域',
            text='销售总额'
        )

        fig_sales.update_traces(
            texttemplate='￥%{y:,.0f}',
            textposition='outside'
        )

        fig_sales.update_layout(
            xaxis_title="区域",
            yaxis_title="销售总额 (元)",
            yaxis=dict(tickprefix="￥"),
            height=400,
            template="plotly_white"
        )

        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        # 区域费比气泡图
        fig_cost_ratio = px.scatter(
            region_metrics,
            x='销售额百分比',
            y='费比',
            size='物料总成本',
            color='所属区域',
            title="区域费比分析",
            labels={
                '销售额百分比': '销售贡献度 (%)',
                '费比': '费比 (%)',
                '物料总成本': '物料成本 (元)'
            },
            size_max=50
        )

        # 添加平均费比参考线
        avg_fee_ratio = region_metrics['费比'].mean()
        fig_cost_ratio.add_hline(
            y=avg_fee_ratio,
            line_dash="dash",
            line_color="#ff5a36",
            annotation=dict(text=f"平均费比: {avg_fee_ratio:.2f}%")
        )

        fig_cost_ratio.update_layout(
            xaxis=dict(ticksuffix="%"),
            yaxis=dict(ticksuffix="%"),
            height=400,
            template="plotly_white"
        )

        st.plotly_chart(fig_cost_ratio, use_container_width=True)


# 时间趋势分析函数
def create_time_trend_analysis(filtered_material, filtered_sales):
    """创建时间趋势分析图表"""
    st.markdown("<h3 class='section-header'>时间趋势分析</h3>", unsafe_allow_html=True)

    # 按月份聚合数据
    material_monthly = filtered_material.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
        '物料总成本': 'sum'
    }).reset_index()

    sales_monthly = filtered_sales.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
        '销售总额': 'sum'
    }).reset_index()

    # 合并月度数据
    monthly_data = pd.merge(material_monthly, sales_monthly, on='发运月份', how='outer')
    monthly_data = monthly_data.sort_values('发运月份')

    # 计算费比
    monthly_data['费比'] = calculate_fee_ratio(monthly_data['物料总成本'], monthly_data['销售总额'])

    # 格式化日期显示
    monthly_data['月份'] = monthly_data['发运月份'].dt.strftime('%Y-%m')

    # 创建销售额和物料成本趋势图
    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

    # 添加销售额线
    fig_trend.add_trace(
        go.Scatter(
            x=monthly_data['月份'],
            y=monthly_data['销售总额'],
            mode='lines+markers',
            name='销售总额',
            line=dict(color='#5e72e4', width=2),
            marker=dict(size=8)
        ),
        secondary_y=False
    )

    # 添加物料成本线
    fig_trend.add_trace(
        go.Scatter(
            x=monthly_data['月份'],
            y=monthly_data['物料总成本'],
            mode='lines+markers',
            name='物料成本',
            line=dict(color='#fb6340', width=2),
            marker=dict(size=8)
        ),
        secondary_y=True
    )

    # 设置图表布局
    fig_trend.update_layout(
        title='销售额与物料成本月度趋势',
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", y=1.1),
        hovermode='x unified'
    )

    # 设置y轴
    fig_trend.update_yaxes(title_text="销售总额 (元)", secondary_y=False, tickprefix="￥")
    fig_trend.update_yaxes(title_text="物料成本 (元)", secondary_y=True, tickprefix="￥")

    # 设置x轴
    fig_trend.update_xaxes(title_text="月份", tickangle=-45)

    st.plotly_chart(fig_trend, use_container_width=True)

    # 创建费比趋势图
    fig_fee_ratio = px.line(
        monthly_data,
        x='月份',
        y='费比',
        title='月度费比变化趋势',
        markers=True
    )

    # 添加平均费比参考线
    avg_fee_ratio = monthly_data['费比'].mean()
    fig_fee_ratio.add_hline(
        y=avg_fee_ratio,
        line_dash="dash",
        line_color="#ff5a36",
        annotation=dict(text=f"平均费比: {avg_fee_ratio:.2f}%")
    )

    fig_fee_ratio.update_layout(
        xaxis_title="月份",
        yaxis_title="费比 (%)",
        yaxis=dict(ticksuffix="%"),
        height=350,
        template="plotly_white"
    )

    st.plotly_chart(fig_fee_ratio, use_container_width=True)


# 客户价值分析函数
def create_customer_value_analysis(filtered_material, filtered_sales):
    """创建客户价值分析图表"""
    st.markdown("<h3 class='section-header'>客户价值分析</h3>", unsafe_allow_html=True)

    # 合并客户的物料和销售数据
    customer_material = filtered_material.groupby(['客户代码', '经销商名称']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    customer_sales = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
        '销售总额': 'sum'
    }).reset_index()

    customer_value = pd.merge(customer_material, customer_sales, on=['客户代码', '经销商名称'], how='outer')

    # 计算客户价值指标
    customer_value['费比'] = calculate_fee_ratio(customer_value['物料总成本'], customer_value['销售总额'])
    customer_value['物料效率'] = customer_value['销售总额'] / customer_value['物料数量'].where(
        customer_value['物料数量'] > 0, np.nan)
    customer_value['客户价值'] = customer_value['销售总额'] - customer_value['物料总成本']

    # 计算排名
    customer_value['价值排名'] = customer_value['客户价值'].rank(ascending=False, method='min')

    # 创建客户价值分布图
    if not customer_value.empty:
        # 取前20名客户
        top_customers = customer_value.sort_values('客户价值', ascending=False).head(20)

        # 客户价值柱状图
        fig_value = px.bar(
            top_customers,
            x='经销商名称',
            y='客户价值',
            color='费比',
            title="客户价值分布 (前20名)",
            labels={'经销商名称': '经销商', '客户价值': '客户价值 (元)', '费比': '费比 (%)'},
            color_continuous_scale='RdYlGn_r',
            text='客户价值'
        )

        fig_value.update_traces(
            texttemplate='￥%{y:,.0f}',
            textposition='outside'
        )

        fig_value.update_layout(
            xaxis=dict(tickangle=-45),
            yaxis=dict(title='客户价值 (元)', tickprefix='￥'),
            coloraxis_colorbar=dict(title='费比 (%)'),
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig_value, use_container_width=True)

        # 客户分群散点图
        fig_segments = px.scatter(
            customer_value,
            x='客户价值',
            y='物料效率',
            size='销售总额',
            color='费比',
            hover_name='经销商名称',
            title="客户分群矩阵",
            labels={
                '客户价值': '客户价值 (元)',
                '物料效率': '物料效率 (元/件)',
                '销售总额': '销售总额 (元)',
                '费比': '费比 (%)'
            },
            color_continuous_scale='RdYlGn_r',
            size_max=50
        )

        # 添加参考线
        avg_value = customer_value['客户价值'].median()
        avg_efficiency = customer_value['物料效率'].median()

        fig_segments.add_vline(x=avg_value, line_dash="dash", line_color="#888")
        fig_segments.add_hline(y=avg_efficiency, line_dash="dash", line_color="#888")

        fig_segments.update_layout(
            xaxis=dict(title='客户价值 (元)', tickprefix='￥'),
            yaxis=dict(title='物料效率 (元/件)', tickprefix='￥'),
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig_segments, use_container_width=True)

        # 显示TOP10客户明细表
        st.markdown("### 客户价值TOP10明细")
        top10 = customer_value.sort_values('客户价值', ascending=False).head(10)
        top10_display = top10[['经销商名称', '客户代码', '销售总额', '物料总成本', '客户价值', '费比', '物料效率']]
        # 格式化数值列为易读格式
        top10_display['销售总额'] = top10_display['销售总额'].map('￥{:,.0f}'.format)
        top10_display['物料总成本'] = top10_display['物料总成本'].map('￥{:,.0f}'.format)
        top10_display['客户价值'] = top10_display['客户价值'].map('￥{:,.0f}'.format)
        top10_display['费比'] = top10_display['费比'].map('{:.2f}%'.format)
        top10_display['物料效率'] = top10_display['物料效率'].map('￥{:,.0f}/件'.format)

        st.dataframe(top10_display, use_container_width=True)
    else:
        st.warning("没有足够的数据来生成客户价值分析图表。")


# 物料效益分析函数
def create_material_effectiveness_analysis(filtered_material, filtered_sales):
    """创建物料效益分析图表"""
    st.markdown("<h3 class='section-header'>物料效益分析</h3>", unsafe_allow_html=True)

    # 按物料分组
    material_effectiveness = filtered_material.groupby(['物料代码', '物料名称']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    # 创建物料-销售映射关系
    # 先按客户和月份合并物料和销售数据
    material_sales_map = pd.merge(
        filtered_material[['发运月份', '客户代码', '物料代码', '物料名称', '物料总成本']],
        filtered_sales[['发运月份', '客户代码', '销售总额']],
        on=['发运月份', '客户代码'],
        how='inner'
    )

    # 按物料聚合销售额
    material_sales = material_sales_map.groupby(['物料代码', '物料名称']).agg({
        '销售总额': 'sum'
    }).reset_index()

    # 合并物料效益数据
    material_roi = pd.merge(material_effectiveness, material_sales, on=['物料代码', '物料名称'], how='left')
    material_roi['销售总额'].fillna(0, inplace=True)

    # 计算ROI
    material_roi['ROI'] = material_roi['销售总额'] / material_roi['物料总成本'].where(material_roi['物料总成本'] > 0,
                                                                                      np.nan)
    material_roi = material_roi.dropna(subset=['ROI'])

    if not material_roi.empty:
        # 创建物料ROI矩阵
        fig_roi = px.scatter(
            material_roi,
            x='物料总成本',
            y='销售总额',
            size='物料数量',
            color='ROI',
            hover_name='物料名称',
            text='物料名称',
            labels={
                '物料总成本': '物料总成本 (元)',
                '销售总额': '销售总额 (元)',
                '物料数量': '物料数量 (件)',
                'ROI': '投资回报率'
            },
            color_continuous_scale='RdYlGn',
            size_max=50,
            log_x=True,
            log_y=True
        )

        # 添加ROI=1参考线
        max_cost = material_roi['物料总成本'].max() * 1.2
        min_cost = material_roi['物料总成本'].min() / 1.2

        fig_roi.add_shape(
            type="line",
            x0=min_cost,
            y0=min_cost,
            x1=max_cost,
            y1=max_cost,
            line=dict(color="#ff5a36", width=2, dash="dash"),
            name="ROI=1"
        )

        fig_roi.update_layout(
            title="物料ROI矩阵",
            xaxis=dict(title='物料总成本 (元) - 对数刻度', tickprefix='￥'),
            yaxis=dict(title='销售总额 (元) - 对数刻度', tickprefix='￥'),
            height=500,
            template="plotly_white"
        )

        st.plotly_chart(fig_roi, use_container_width=True)

        # 显示物料ROI排名表
        st.markdown("### 物料ROI排名")

        # 创建物料ROI条形图 (TOP10)
        top_roi = material_roi.sort_values('ROI', ascending=False).head(10)

        fig_top_roi = px.bar(
            top_roi,
            y='物料名称',
            x='ROI',
            color='物料总成本',
            title="ROI最高的10种物料",
            orientation='h',
            text='ROI',
            color_continuous_scale='Viridis'
        )

        fig_top_roi.update_traces(
            texttemplate='%{x:.2f}',
            textposition='outside'
        )

        fig_top_roi.update_layout(
            xaxis=dict(title='投资回报率'),
            yaxis=dict(title='物料名称', autorange="reversed"),
            height=400,
            template="plotly_white"
        )

        st.plotly_chart(fig_top_roi, use_container_width=True)
    else:
        st.warning("没有足够的数据来生成物料效益分析图表。")


# 物料-产品关联分析函数
def create_material_product_correlation(filtered_material, filtered_sales):
    """创建物料-产品关联分析图表"""
    st.markdown("<h3 class='section-header'>物料-产品关联分析</h3>", unsafe_allow_html=True)

    # 合并物料和销售数据，按客户代码和月份
    material_product = pd.merge(
        filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
        filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
        on=['发运月份', '客户代码', '经销商名称'],
        how='inner'
    )

    if not material_product.empty:
        # 按物料名称和产品名称分组，聚合数据
        material_product_sales = material_product.groupby(['物料名称', '产品名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        # 计算物料-产品的关联强度
        material_product_sales['投入产出比'] = material_product_sales['销售总额'] / material_product_sales[
            '物料总成本'].where(
            material_product_sales['物料总成本'] > 0, np.nan)

        # 创建物料-产品透视表，用于热力图
        pivot_data = material_product_sales.pivot_table(
            index='物料名称',
            columns='产品名称',
            values='销售总额',
            aggfunc='sum',
            fill_value=0
        )

        # 获取前8种物料和前8种产品
        top_materials = material_product_sales.groupby('物料名称')['销售总额'].sum().nlargest(8).index
        top_products = material_product_sales.groupby('产品名称')['销售总额'].sum().nlargest(8).index

        # 筛选数据
        filtered_pivot = pivot_data.loc[pivot_data.index.isin(top_materials), pivot_data.columns.isin(top_products)]

        if not filtered_pivot.empty:
            # 创建热力图
            fig_heatmap = px.imshow(
                filtered_pivot,
                labels=dict(x="产品名称", y="物料名称", color="销售额 (元)"),
                x=filtered_pivot.columns,
                y=filtered_pivot.index,
                color_continuous_scale="Blues",
                aspect="auto"
            )

            fig_heatmap.update_layout(
                title="物料-产品销售关联热力图",
                xaxis=dict(title="产品名称"),
                yaxis=dict(title="物料名称"),
                height=500,
                template="plotly_white"
            )

            st.plotly_chart(fig_heatmap, use_container_width=True)

            # 创建最佳物料-产品组合排名
            top_pairs = material_product_sales.sort_values('投入产出比', ascending=False).head(10)

            fig_pairs = px.bar(
                top_pairs,
                y='投入产出比',
                x=top_pairs['物料名称'] + " - " + top_pairs['产品名称'],  # 组合名称
                title="最佳物料-产品组合 (TOP10)",
                color='销售总额',
                color_continuous_scale='Viridis',
                text='投入产出比'
            )

            fig_pairs.update_traces(
                texttemplate='%{y:.2f}',
                textposition='outside'
            )

            fig_pairs.update_layout(
                xaxis=dict(title='物料-产品组合', tickangle=-45),
                yaxis=dict(title='投入产出比 (销售额/物料成本)'),
                height=450,
                template="plotly_white"
            )

            st.plotly_chart(fig_pairs, use_container_width=True)
        else:
            st.warning("没有足够的物料-产品组合数据来创建热力图。")
    else:
        st.warning("没有足够的数据来生成物料-产品关联分析图表。")


# 创建侧边栏筛选器
def create_sidebar_filters(df_material, df_sales):
    """创建侧边栏筛选条件"""
    st.sidebar.header("数据筛选")

    # 获取所有过滤选项
    regions = sorted(df_material['所属区域'].unique())
    provinces = sorted(df_material['省份'].unique())

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
        value=(min_date, max_date),
        min_value=min_date - timedelta(days=365),
        max_value=datetime.now().date() + timedelta(days=30),
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # 添加使用说明
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
    """主函数"""
    # 页面标题
    st.markdown("<h1 class='main-header'>口力营销物料与销售分析仪表盘</h1>", unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载数据，请稍候..."):
        df_material, df_sales, df_material_price = load_data()

    # 如果数据加载失败，显示错误并退出
    if df_material is None or df_sales is None:
        st.error("数据加载失败。请检查数据文件是否存在并格式正确。")
        return

    # 创建侧边栏筛选器
    selected_regions, selected_provinces, start_date, end_date = create_sidebar_filters(df_material, df_sales)

    # 应用筛选
    filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
    filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

    # 检查筛选后的数据是否为空
    if filtered_material.empty or filtered_sales.empty:
        st.warning("筛选条件下没有数据。请尝试更改筛选条件。")
        return

    # 计算KPI
    total_material_cost = filtered_material['物料总成本'].sum()
    total_sales = filtered_sales['销售总额'].sum()
    overall_cost_sales_ratio = calculate_fee_ratio(total_material_cost, total_sales)
    avg_material_effectiveness = total_sales / filtered_material['物料数量'].sum() if filtered_material[
                                                                                          '物料数量'].sum() > 0 else 0

    # 显示KPI卡片
    display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness)

    # 创建选项卡
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "区域分析",
        "时间趋势分析",
        "客户价值分析",
        "物料效益分析",
        "物料-产品关联"
    ])

    # 在各选项卡中渲染内容
    with tab1:
        create_region_analysis(filtered_material, filtered_sales)

    with tab2:
        create_time_trend_analysis(filtered_material, filtered_sales)

    with tab3:
        create_customer_value_analysis(filtered_material, filtered_sales)

    with tab4:
        create_material_effectiveness_analysis(filtered_material, filtered_sales)

    with tab5:
        create_material_product_correlation(filtered_material, filtered_sales)

    # 添加页脚信息
    st.markdown("""
    <div style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 0.8rem;">
        <p>口力营销物料与销售分析仪表盘 | 版本 1.0.0 | 最后更新: 2025年4月</p>
        <p>使用Streamlit和Plotly构建 | 数据更新频率: 每月</p>
    </div>
    """, unsafe_allow_html=True)


# 执行主函数
if __name__ == "__main__":
    main()