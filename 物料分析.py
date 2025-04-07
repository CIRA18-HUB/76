import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import warnings
from scipy import stats
from datetime import datetime
import json

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="口力营销物料与销售分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
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
    .alert-green {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 0.5rem solid #4CAF50;
        margin-bottom: 1rem;
    }
    .alert-orange {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 0.5rem solid #FF9800;
        margin-bottom: 1rem;
    }
    .alert-red {
        padding: 0.75rem;
        border-radius: 0.5rem;
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 0.5rem solid #F44336;
        margin-bottom: 1rem;
    }
    .explanation {
        padding: 1rem;
        background-color: #f9f9f9;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #1f3867;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# 加载数据
@st.cache_data(ttl=3600)
def load_data():
    try:
        # 尝试加载真实数据
        df_material = pd.read_excel("2025物料源数据.xlsx")
        df_sales = pd.read_excel("25物料源销售数据.xlsx")
        df_material_price = pd.read_excel("物料单价.xlsx")

        st.success("成功加载真实数据文件")

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

    # 清理和标准化数据
    # 确保日期格式一致
    df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
    df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])

    # 确保所有文本列的数据类型一致 - 修复类型错误
    df_material['所属区域'] = df_material['所属区域'].astype(str)
    df_sales['所属区域'] = df_sales['所属区域'].astype(str)
    df_material['省份'] = df_material['省份'].astype(str)
    df_sales['省份'] = df_sales['省份'].astype(str)
    df_material['城市'] = df_material['城市'].astype(str)
    df_sales['城市'] = df_sales['城市'].astype(str)
    df_material['经销商名称'] = df_material['经销商名称'].astype(str)
    df_sales['经销商名称'] = df_sales['经销商名称'].astype(str)
    df_material['客户代码'] = df_material['客户代码'].astype(str)
    df_sales['客户代码'] = df_sales['客户代码'].astype(str)
    df_material['物料代码'] = df_material['物料代码'].astype(str)
    df_material['物料名称'] = df_material['物料名称'].astype(str)
    df_sales['产品代码'] = df_sales['产品代码'].astype(str)
    df_sales['产品名称'] = df_sales['产品名称'].astype(str)
    df_material['申请人'] = df_material['申请人'].astype(str)
    df_sales['申请人'] = df_sales['申请人'].astype(str)

    # 处理物料单价数据，创建查找字典
    material_price_dict = dict(zip(df_material_price['物料代码'], df_material_price['单价（元）']))

    # 将物料单价添加到物料数据中
    df_material['物料单价'] = df_material['物料代码'].map(material_price_dict)

    # 计算物料总成本
    df_material['物料总成本'] = df_material['物料数量'] * df_material['物料单价']

    # 计算销售总额
    df_sales['销售总额'] = df_sales['求和项:数量（箱）'] * df_sales['求和项:单价（箱）']

    return df_material, df_sales, df_material_price


# 创建聚合数据和计算指标
@st.cache_data(ttl=3600)
def create_aggregations(df_material, df_sales):
    # 按区域、省份、城市、客户代码、经销商名称进行聚合物料数据
    material_by_region = df_material.groupby('所属区域').agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    material_by_province = df_material.groupby('省份').agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    material_by_customer = df_material.groupby(['客户代码', '经销商名称']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    material_by_time = df_material.groupby(['发运月份']).agg({
        '物料数量': 'sum',
        '物料总成本': 'sum'
    }).reset_index()

    # 按区域、省份、城市、客户代码、经销商名称聚合销售数据
    sales_by_region = df_sales.groupby('所属区域').agg({
        '求和项:数量（箱）': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    sales_by_province = df_sales.groupby('省份').agg({
        '求和项:数量（箱）': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    sales_by_customer = df_sales.groupby(['客户代码', '经销商名称']).agg({
        '求和项:数量（箱）': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    sales_by_time = df_sales.groupby(['发运月份']).agg({
        '求和项:数量（箱）': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    # 合并区域数据计算费比
    region_metrics = pd.merge(material_by_region, sales_by_region, on='所属区域', how='outer')
    region_metrics['费比'] = (region_metrics['物料总成本'] / region_metrics['销售总额']) * 100
    region_metrics['物料单位效益'] = region_metrics['销售总额'] / region_metrics['物料数量']

    # 合并省份数据计算费比
    province_metrics = pd.merge(material_by_province, sales_by_province, on='省份', how='outer')
    province_metrics['费比'] = (province_metrics['物料总成本'] / province_metrics['销售总额']) * 100
    province_metrics['物料单位效益'] = province_metrics['销售总额'] / province_metrics['物料数量']

    # 合并客户数据计算费比
    customer_metrics = pd.merge(material_by_customer, sales_by_customer, on=['客户代码', '经销商名称'], how='outer')
    customer_metrics['费比'] = (customer_metrics['物料总成本'] / customer_metrics['销售总额']) * 100
    customer_metrics['物料单位效益'] = customer_metrics['销售总额'] / customer_metrics['物料数量']

    # 合并时间数据计算费比
    time_metrics = pd.merge(material_by_time, sales_by_time, on='发运月份', how='outer')
    time_metrics['费比'] = (time_metrics['物料总成本'] / time_metrics['销售总额']) * 100
    time_metrics['物料单位效益'] = time_metrics['销售总额'] / time_metrics['物料数量']

    # 按销售人员聚合
    salesperson_metrics = pd.merge(
        df_material.groupby('申请人').agg({'物料总成本': 'sum'}),
        df_sales.groupby('申请人').agg({'销售总额': 'sum'}),
        on='申请人'
    )
    salesperson_metrics['费比'] = (salesperson_metrics['物料总成本'] / salesperson_metrics['销售总额']) * 100
    salesperson_metrics = salesperson_metrics.reset_index()

    # 物料-产品关联分析
    # 合并物料数据和销售数据，按客户代码和月份
    material_product_link = pd.merge(
        df_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量']],
        df_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '求和项:数量（箱）', '销售总额']],
        on=['发运月份', '客户代码', '经销商名称'],
        how='inner'
    )

    # 创建物料-产品关联度量
    material_product_corr = material_product_link.groupby(['物料代码', '物料名称', '产品代码', '产品名称']).agg({
        '物料数量': 'sum',
        '求和项:数量（箱）': 'sum',
        '销售总额': 'sum'
    }).reset_index()

    material_product_corr['关联强度'] = material_product_corr['销售总额'] / material_product_corr['物料数量']

    # 计算物料组合效益
    material_combinations = material_product_link.groupby(['客户代码', '发运月份']).agg({
        '物料代码': lambda x: ','.join(sorted(set(x))),
        '销售总额': 'sum'
    }).reset_index()

    material_combo_performance = material_combinations.groupby('物料代码').agg({
        '销售总额': ['mean', 'sum', 'count']
    }).reset_index()
    material_combo_performance.columns = ['物料组合', '平均销售额', '总销售额', '使用次数']
    material_combo_performance = material_combo_performance.sort_values('平均销售额', ascending=False)

    return {
        'region_metrics': region_metrics,
        'province_metrics': province_metrics,
        'customer_metrics': customer_metrics,
        'time_metrics': time_metrics,
        'salesperson_metrics': salesperson_metrics,
        'material_product_corr': material_product_corr,
        'material_combo_performance': material_combo_performance
    }


# 辅助函数：按区域、省份和日期筛选数据
def filter_data(df, regions=None, provinces=None, start_date=None, end_date=None):
    filtered_df = df.copy()

    if regions and len(regions) > 0:
        filtered_df = filtered_df[filtered_df['所属区域'].isin(regions)]

    if provinces and len(provinces) > 0:
        filtered_df = filtered_df[filtered_df['省份'].isin(provinces)]

    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['发运月份'] >= pd.to_datetime(start_date)) &
                                  (filtered_df['发运月份'] <= pd.to_datetime(end_date))]

    return filtered_df


# 主函数
def main():
    # 加载数据
    df_material, df_sales, df_material_price = load_data()

    # 创建聚合数据
    aggregations = create_aggregations(df_material, df_sales)

    # 页面标题
    st.markdown("<h1 class='main-header'>口力营销物料与销售分析仪表盘</h1>", unsafe_allow_html=True)

    # 创建侧边栏筛选器
    st.sidebar.header("数据筛选")

    # 获取所有过滤选项
    regions = sorted(df_material['所属区域'].unique())
    provinces = sorted(df_material['省份'].unique())
    materials = sorted(df_material['物料名称'].unique())
    df_sales['产品名称'] = df_sales['产品名称'].astype(str)
    products = sorted(df_sales['产品名称'].unique())

    # 侧边栏筛选器
    selected_regions = st.sidebar.multiselect(
        "选择区域:",
        options=regions,
        default=[]
    )

    selected_provinces = st.sidebar.multiselect(
        "选择省份:",
        options=provinces,
        default=[]
    )

    # 日期范围筛选器
    date_range = st.sidebar.date_input(
        "选择日期范围:",
        value=[df_material['发运月份'].min().date(), df_material['发运月份'].max().date()],
        min_value=df_material['发运月份'].min().date(),
        max_value=df_material['发运月份'].max().date()
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = date_range[0]
        end_date = date_range[0]

    # 应用筛选
    filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
    filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

    # 计算KPI
    total_material_cost = filtered_material['物料总成本'].sum()
    total_sales = filtered_sales['销售总额'].sum()
    overall_cost_sales_ratio = (total_material_cost / total_sales) * 100 if total_sales > 0 else 0
    avg_material_effectiveness = total_sales / filtered_material['物料数量'].sum() if filtered_material[
                                                                                          '物料数量'].sum() > 0 else 0

    # 显示KPI卡片
    st.markdown("### 关键绩效指标")
    kpi_cols = st.columns(4)

    with kpi_cols[0]:
        st.markdown(f"""
        <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px;'>
            <p class='card-header'>总物料成本</p>
            <p class='card-value'>￥{total_material_cost:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[1]:
        st.markdown(f"""
        <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px;'>
            <p class='card-header'>总销售额</p>
            <p class='card-value'>￥{total_sales:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[2]:
        st.markdown(f"""
        <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px;'>
            <p class='card-header'>总体费比</p>
            <p class='card-value'>{overall_cost_sales_ratio:.2f}%</p>
        </div>
        """, unsafe_allow_html=True)

    with kpi_cols[3]:
        st.markdown(f"""
        <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px;'>
            <p class='card-header'>平均物料效益</p>
            <p class='card-value'>￥{avg_material_effectiveness:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # 创建选项卡
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "区域性能分析",
        "时间趋势分析",
        "客户价值分析",
        "物料效益分析",
        "地理分布可视化",
        "物料-产品关联分析",
        "经销商绩效对比",
        "费比分析",
        "利润最大化分析"
    ])

    # 区域性能分析选项卡
    with tab1:
        st.markdown("<h2 class='section-header'>区域性能分析</h2>", unsafe_allow_html=True)

        # 区域销售表现图表
        region_cols = st.columns(2)

        with region_cols[0]:
            st.markdown("#### 区域销售表现")
            region_sales = filtered_sales.groupby('所属区域').agg({
                '销售总额': 'sum'
            }).reset_index().sort_values('销售总额', ascending=False)

            fig_region_sales = px.bar(
                region_sales,
                x='所属区域',
                y='销售总额',
                labels={'销售总额': '销售总额 (元)', '所属区域': '区域'},
                color='所属区域',
                text='销售总额',
                color_discrete_sequence=px.colors.qualitative.G10,
            )

            fig_region_sales.update_traces(
                texttemplate='%{text:,.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>销售总额: ¥%{y:,.2f}<extra></extra>'
            )

            fig_region_sales.update_layout(
                title={
                    'text': "各区域销售总额",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={'categoryorder': 'total descending'},
                yaxis={'gridcolor': '#f4f4f4'},
                uniformtext_minsize=10,
                uniformtext_mode='hide',
                height=500
            )

            st.plotly_chart(fig_region_sales, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了各区域的销售总额排名。柱形越高，表示该区域销售额越大，业绩越好。通过此图可以直观了解哪些区域的销售表现最佳，哪些区域需要加强。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停在柱形上可查看详细销售金额</li>
                    <li>通过左侧过滤器选择不同区域或时间段进行比较分析</li>
                    <li>重点关注排名靠前的区域，分析其成功经验</li>
                    <li>对于排名靠后的区域，考虑改进销售策略或增加物料投入</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with region_cols[1]:
            st.markdown("#### 区域物料效率")
            region_material = filtered_material.groupby('所属区域').agg({
                '物料数量': 'sum'
            }).reset_index()

            region_sales = filtered_sales.groupby('所属区域').agg({
                '销售总额': 'sum'
            }).reset_index()

            region_efficiency = pd.merge(region_material, region_sales, on='所属区域', how='outer')
            region_efficiency['物料效率'] = region_efficiency['销售总额'] / region_efficiency['物料数量']
            region_efficiency = region_efficiency.sort_values('物料效率', ascending=False)

            fig_region_efficiency = px.bar(
                region_efficiency,
                x='所属区域',
                y='物料效率',
                labels={'物料效率': '物料效率 (元/件)', '所属区域': '区域'},
                color='所属区域',
                text='物料效率',
                color_discrete_sequence=px.colors.qualitative.Vivid
            )

            fig_region_efficiency.update_traces(
                texttemplate='%{text:,.2f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' +
                              '物料效率: ¥%{y:,.2f}/件<br>' +
                              '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                              '物料数量: %{customdata[1]:,}件<extra></extra>',
                customdata=region_efficiency[['销售总额', '物料数量']].values
            )

            fig_region_efficiency.update_layout(
                title={
                    'text': "各区域物料效率 (销售额/物料数量)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={'categoryorder': 'total descending', 'tickangle': -45 if len(region_efficiency) > 6 else 0},
                yaxis={'gridcolor': '#f4f4f4', 'title': {'font': {'size': 16}}},
                uniformtext_minsize=10,
                uniformtext_mode='hide',
                height=500
            )

            st.plotly_chart(fig_region_efficiency, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了各区域的物料使用效率。每个柱形代表该区域每单位物料所产生的销售额，数值越高表示物料利用效率越高。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看详细的物料效率、总销售额和物料数量</li>
                    <li>重点关注物料效率最高的区域，分析其成功经验</li>
                    <li>物料效率低的区域可能需要改进物料使用策略或培训销售人员更有效地使用物料</li>
                    <li>比较物料效率与销售总额，有些区域虽然总销售额高，但物料效率可能不高</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 区域费比对比图表
        st.markdown("#### 区域费比对比")
        region_material = filtered_material.groupby('所属区域').agg({
            '物料总成本': 'sum'
        }).reset_index()

        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index()

        region_cost_sales = pd.merge(region_material, region_sales, on='所属区域', how='outer')
        region_cost_sales['费比'] = (region_cost_sales['物料总成本'] / region_cost_sales['销售总额']) * 100
        region_cost_sales = region_cost_sales.sort_values('费比')

        # 添加平均费比线
        avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales['销售总额'].sum()) * 100 if \
        region_cost_sales['销售总额'].sum() > 0 else 0

        fig_region_cost_sales = px.bar(
            region_cost_sales,
            x='所属区域',
            y='费比',
            labels={'费比': '费比 (%)', '所属区域': '区域'},
            text='费比',
            color='费比',
            color_continuous_scale='RdYlGn_r',
            range_color=[min(region_cost_sales['费比'].min() * 0.9, 0.1) if not region_cost_sales.empty else 0,
                         max(region_cost_sales['费比'].max() * 1.1, 0.1) if not region_cost_sales.empty else 10]
        )

        fig_region_cost_sales.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '费比: %{y:.2f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=region_cost_sales[['物料总成本', '销售总额']].values
        )

        fig_region_cost_sales.add_hline(
            y=avg_cost_sales_ratio,
            line_dash="dash",
            line_color="#ff5a36",
            line_width=2,
            annotation=dict(
                text=f"平均: {avg_cost_sales_ratio:.2f}%",
                font=dict(size=14, color="#ff5a36"),
                bgcolor="#ffffff",
                bordercolor="#ff5a36",
                borderwidth=1,
                borderpad=4,
                x=1,
                y=avg_cost_sales_ratio,
                xanchor="right",
                yanchor="middle"
            )
        )

        fig_region_cost_sales.update_layout(
            title={
                'text': "各区域费比对比 (物料成本/销售额)",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=50),
            xaxis={
                'categoryorder': 'array',
                'categoryarray': region_cost_sales['所属区域'].tolist(),
                'tickangle': -45 if len(region_cost_sales) > 6 else 0
            },
            yaxis={'gridcolor': '#f4f4f4'},
            uniformtext_minsize=10,
            uniformtext_mode='hide',
            height=600
        )

        st.plotly_chart(fig_region_cost_sales, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了各区域的费比情况（物料成本占销售额的百分比）。费比越低越好，表示投入的物料成本产生了更多的销售额。</p>
            <p>颜色说明: 绿色表示费比较低（好），红色表示费比较高（需要改进）。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>红色虚线表示平均费比基准线，可用于快速判断区域表现</li>
                <li>低于平均线的区域表现较好，高于平均线的区域需要关注</li>
                <li>鼠标悬停可查看详细的费比、物料成本和销售总额数据</li>
                <li>对于费比过高的区域，建议分析物料使用是否合理，或者销售策略是否需要调整</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 时间趋势分析选项卡
    with tab2:
        st.markdown("<h2 class='section-header'>时间趋势分析</h2>", unsafe_allow_html=True)

        # 销售额和物料投放趋势图表
        st.markdown("#### 销售额和物料投放趋势")
        time_material = filtered_material.groupby('发运月份').agg({
            '物料总成本': 'sum'
        }).reset_index()

        time_sales = filtered_sales.groupby('发运月份').agg({
            '销售总额': 'sum'
        }).reset_index()

        time_trends = pd.merge(time_material, time_sales, on='发运月份', how='outer')
        time_trends = time_trends.sort_values('发运月份')

        # 计算月度同比增长率
        time_trends['销售同比'] = time_trends['销售总额'].pct_change(12) * 100
        time_trends['物料同比'] = time_trends['物料总成本'].pct_change(12) * 100

        fig_time_trend = make_subplots(specs=[[{"secondary_y": True}]])

        fig_time_trend.add_trace(
            go.Scatter(
                x=time_trends['发运月份'],
                y=time_trends['销售总额'],
                name="销售总额",
                line=dict(color='#4CAF50', width=3),
                fill='tozeroy',
                fillcolor='rgba(76, 175, 80, 0.1)',
                hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                              '销售总额: ¥%{y:,.2f}<br>' +
                              '同比增长: %{customdata:.2f}%<extra></extra>',
                customdata=time_trends['销售同比']
            ),
            secondary_y=False
        )

        fig_time_trend.add_trace(
            go.Scatter(
                x=time_trends['发运月份'],
                y=time_trends['物料总成本'],
                name="物料总成本",
                line=dict(color='#F44336', width=3, dash='dot'),
                hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                              '物料总成本: ¥%{y:,.2f}<br>' +
                              '同比增长: %{customdata:.2f}%<extra></extra>',
                customdata=time_trends['物料同比']
            ),
            secondary_y=True
        )

        fig_time_trend.update_layout(
            title={
                'text': "销售额和物料投放趋势",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#CCCCCC',
                borderwidth=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#f4f4f4',
                tickformat='%Y-%m',
                tickangle=-45
            ),
            height=600
        )

        fig_time_trend.update_yaxes(
            title_text="销售总额 (元)",
            secondary_y=False,
            gridcolor='#f4f4f4',
            tickprefix="¥",
            tickformat=",.0f"
        )
        fig_time_trend.update_yaxes(
            title_text="物料总成本 (元)",
            secondary_y=True,
            gridcolor='#f4f4f4',
            tickprefix="¥",
            tickformat=",.0f"
        )

        st.plotly_chart(fig_time_trend, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了销售额(绿色实线)和物料成本(红色虚线)随时间的变化趋势。左侧Y轴代表销售额，右侧Y轴代表物料成本。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看每月详细数据和同比增长率</li>
                <li>观察销售额与物料成本的变化关系，理想情况是销售额增长快于物料成本增长</li>
                <li>注意季节性波动和长期趋势，判断物料投放的时机</li>
                <li>关注销售额与物料成本线之间的距离变化，距离越大表示利润空间越大</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 月度费比变化和物料效益趋势
        trend_cols = st.columns(2)

        with trend_cols[0]:
            st.markdown("#### 月度费比变化")
            time_material = filtered_material.groupby('发运月份').agg({
                '物料总成本': 'sum'
            }).reset_index()

            time_sales = filtered_sales.groupby('发运月份').agg({
                '销售总额': 'sum'
            }).reset_index()

            time_cost_sales = pd.merge(time_material, time_sales, on='发运月份', how='outer')
            time_cost_sales['费比'] = (time_cost_sales['物料总成本'] / time_cost_sales['销售总额']) * 100
            time_cost_sales = time_cost_sales.sort_values('发运月份')

            # 添加平均费比
            avg_cost_sales_ratio = (time_cost_sales['物料总成本'].sum() / time_cost_sales['销售总额'].sum()) * 100 if \
            time_cost_sales['销售总额'].sum() > 0 else 0

            fig_monthly_cost_sales = go.Figure()

            fig_monthly_cost_sales.add_trace(
                go.Scatter(
                    x=time_cost_sales['发运月份'],
                    y=time_cost_sales['费比'],
                    mode='lines+markers',
                    name='月度费比',
                    line=dict(
                        color='#5e72e4',
                        width=3,
                        shape='spline'
                    ),
                    marker=dict(
                        size=8,
                        color='#5e72e4',
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                                  '费比: %{y:.2f}%<br>' +
                                  '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                                  '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
                    customdata=time_cost_sales[['物料总成本', '销售总额']].values
                )
            )

            fig_monthly_cost_sales.add_trace(
                go.Scatter(
                    x=time_cost_sales['发运月份'],
                    y=[avg_cost_sales_ratio] * len(time_cost_sales),
                    fill='tonexty',
                    fillcolor='rgba(255, 99, 71, 0.2)',
                    line=dict(width=0),
                    hoverinfo='skip',
                    showlegend=False
                )
            )

            fig_monthly_cost_sales.add_hline(
                y=avg_cost_sales_ratio,
                line_dash="dash",
                line_color="#ff5a36",
                line_width=2,
                annotation=dict(
                    text=f"平均: {avg_cost_sales_ratio:.2f}%",
                    font=dict(size=14, color="#ff5a36"),
                    bgcolor="#ffffff",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4,
                    x=1,
                    y=avg_cost_sales_ratio,
                    xanchor="right",
                    yanchor="middle"
                )
            )

            fig_monthly_cost_sales.update_layout(
                title={
                    'text': "月度费比变化趋势",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis=dict(
                    title="月份",
                    showgrid=True,
                    gridcolor='#f4f4f4',
                    tickformat='%Y-%m',
                    tickangle=-45
                ),
                yaxis=dict(
                    title="费比 (%)",
                    showgrid=True,
                    gridcolor='#f4f4f4',
                    ticksuffix="%"
                ),
                showlegend=False,
                height=500
            )

            st.plotly_chart(fig_monthly_cost_sales, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表显示了月度费比的变化趋势。费比是物料成本占销售额的百分比，费比越低表示物料投入产出效率越高。</p>
                <p>红色虚线表示平均费比基准线，高于此线的月份表现不佳（红色区域），低于此线的月份表现较好（白色区域）。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看每月详细的费比、物料成本和销售额数据</li>
                    <li>关注费比的波动趋势，判断物料使用效率是否正在改善</li>
                    <li>分析高于平均线的月份，查找原因并提出改进措施</li>
                    <li>结合销售旺季和促销活动时间，评估物料投入的合理性</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with trend_cols[1]:
            st.markdown("#### 物料效益趋势")
            time_material = filtered_material.groupby('发运月份').agg({
                '物料数量': 'sum'
            }).reset_index()

            time_sales = filtered_sales.groupby('发运月份').agg({
                '销售总额': 'sum'
            }).reset_index()

            time_effectiveness = pd.merge(time_material, time_sales, on='发运月份', how='outer')
            time_effectiveness['物料效益'] = time_effectiveness['销售总额'] / time_effectiveness['物料数量']
            time_effectiveness = time_effectiveness.sort_values('发运月份')

            # 计算平均物料效益
            avg_effectiveness = time_effectiveness['物料效益'].mean()

            # 计算变化率
            time_effectiveness['环比变化'] = time_effectiveness['物料效益'].pct_change() * 100

            fig_material_effectiveness = go.Figure()

            fig_material_effectiveness.add_trace(
                go.Scatter(
                    x=time_effectiveness['发运月份'],
                    y=time_effectiveness['物料效益'],
                    mode='none',
                    fill='tozeroy',
                    fillcolor='rgba(33, 150, 243, 0.1)',
                    hoverinfo='skip',
                    showlegend=False
                )
            )

            fig_material_effectiveness.add_trace(
                go.Scatter(
                    x=time_effectiveness['发运月份'],
                    y=time_effectiveness['物料效益'],
                    mode='lines+markers',
                    name='物料效益',
                    line=dict(
                        color='#2196F3',
                        width=3,
                        shape='spline'
                    ),
                    marker=dict(
                        size=8,
                        color='#2196F3',
                        line=dict(width=2, color='white')
                    ),
                    hovertemplate='<b>%{x|%Y-%m}</b><br>' +
                                  '物料效益: ¥%{y:.2f}/件<br>' +
                                  '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                                  '物料数量: %{customdata[1]:,}件<br>' +
                                  '环比变化: %{customdata[2]:.2f}%<extra></extra>',
                    customdata=time_effectiveness[['销售总额', '物料数量', '环比变化']].values
                )
            )

            fig_material_effectiveness.add_hline(
                y=avg_effectiveness,
                line_dash="dash",
                line_color="#03A9F4",
                line_width=2,
                annotation=dict(
                    text=f"平均: ¥{avg_effectiveness:.2f}/件",
                    font=dict(size=14, color="#03A9F4"),
                    bgcolor="#ffffff",
                    bordercolor="#03A9F4",
                    borderwidth=1,
                    borderpad=4,
                    x=1,
                    y=avg_effectiveness,
                    xanchor="right",
                    yanchor="middle"
                )
            )

            fig_material_effectiveness.update_layout(
                title={
                    'text': "物料效益趋势 (销售额/物料数量)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis=dict(
                    title="月份",
                    showgrid=True,
                    gridcolor='#f4f4f4',
                    tickformat='%Y-%m',
                    tickangle=-45
                ),
                yaxis=dict(
                    title="物料效益 (元/件)",
                    showgrid=True,
                    gridcolor='#f4f4f4',
                    tickprefix="¥",
                    tickformat=",.2f"
                ),
                showlegend=False,
                height=500
            )

            st.plotly_chart(fig_material_effectiveness, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了物料效益(每单位物料带来的销售额)随时间的变化趋势。物料效益越高，表示物料使用越有效率。</p>
                <p>蓝色虚线表示平均物料效益水平，可用作基准线比较不同时期的表现。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看每月详细的物料效益、销售总额、物料数量和环比变化</li>
                    <li>注意物料效益的上升或下降趋势，判断物料使用效率是否在提高</li>
                    <li>关注环比变化较大的月份，分析原因并总结经验</li>
                    <li>将月度物料效益与销售活动、促销策略等结合分析，找出最有效的物料使用方式</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # 客户价值分析选项卡
    with tab3:
        st.markdown("<h2 class='section-header'>客户价值分析</h2>", unsafe_allow_html=True)

        # 客户价值排名图表
        st.markdown("#### 客户价值排名")
        customer_value = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
            '销售总额': 'sum'
        }).reset_index().sort_values('销售总额', ascending=False).head(10)

        # 为了更好的展示，添加销售占比
        total_sales = filtered_sales['销售总额'].sum()
        customer_value['销售占比'] = customer_value['销售总额'] / total_sales * 100 if total_sales > 0 else 0

        fig_customer_value = px.bar(
            customer_value,
            x='销售总额',
            y='经销商名称',
            labels={'销售总额': '销售总额 (元)', '经销商名称': '经销商'},
            orientation='h',
            color='销售总额',
            color_continuous_scale='Blues',
            text='销售占比'
        )

        fig_customer_value.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '销售总额: ¥%{x:,.2f}<br>' +
                          '销售占比: %{text:.2f}%<br>' +
                          '客户代码: %{customdata}<extra></extra>',
            customdata=customer_value['客户代码'].values
        )

        fig_customer_value.update_layout(
            title={
                'text': "前10名高价值客户",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis={
                'title': '销售总额 (元)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥',
                'tickformat': ',.0f'
            },
            yaxis={
                'title': '',
                'autorange': 'reversed',
                'categoryorder': 'total ascending'
            },
            height=600
        )

        st.plotly_chart(fig_customer_value, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了销售额最高的前10名客户。横条越长，表示该客户的销售额越高。横条上的数字表示该客户销售额占总销售额的百分比。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看客户详细的销售总额、销售占比和客户代码</li>
                <li>关注销售额占比高的重点客户，确保维护好客户关系</li>
                <li>分析前10名客户占总销售额的比例，评估客户集中度风险</li>
                <li>研究高价值客户的物料使用情况，找出物料与销售的最佳配比</li>
                <li>考虑为高价值客户提供更加个性化的物料支持</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 客户投入产出比图表
        st.markdown("#### 客户投入产出比")
        customer_material = filtered_material.groupby(['客户代码', '经销商名称']).agg({
            '物料总成本': 'sum'
        }).reset_index()

        customer_sales = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
            '销售总额': 'sum'
        }).reset_index()

        customer_roi = pd.merge(customer_material, customer_sales, on=['客户代码', '经销商名称'], how='inner')
        customer_roi['投入产出比'] = customer_roi['销售总额'] / customer_roi['物料总成本']

        # 筛选条件：只显示物料成本至少超过1000元的客户，避免小额客户ROI过高
        customer_roi = customer_roi[customer_roi['物料总成本'] > 1000]
        customer_roi = customer_roi.sort_values('投入产出比', ascending=False).head(10)

        fig_customer_roi = px.bar(
            customer_roi,
            x='投入产出比',
            y='经销商名称',
            labels={'投入产出比': 'ROI (销售额/物料成本)', '经销商名称': '经销商'},
            orientation='h',
            color='投入产出比',
            color_continuous_scale='Viridis',
            text='投入产出比'
        )

        fig_customer_roi.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          'ROI: %{x:.2f}<br>' +
                          '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料总成本: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=customer_roi[['销售总额', '物料总成本']].values
        )

        fig_customer_roi.update_layout(
            title={
                'text': "前10名高ROI客户 (销售额/物料成本)",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis={
                'title': 'ROI (销售额/物料成本)',
                'showgrid': True,
                'gridcolor': '#f4f4f4'
            },
            yaxis={
                'title': '',
                'autorange': 'reversed',
                'categoryorder': 'total ascending'
            },
            height=600
        )

        st.plotly_chart(fig_customer_roi, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了投入产出比(ROI)最高的前10名客户。ROI是销售额与物料成本的比值，表示每投入1元物料成本产生的销售额。ROI越高，表示物料使用效率越高。</p>
            <p>注意: 此图表只包含物料成本超过1000元的客户，避免小额投入造成的ROI虚高。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看客户详细的ROI、销售总额和物料成本</li>
                <li>分析高ROI客户的物料使用和销售策略，总结成功经验</li>
                <li>考虑将更多物料资源向高ROI客户倾斜，提高整体投资回报</li>
                <li>比较高ROI客户与高销售额客户的重合度，找出最具价值的核心客户</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 物料效益分析选项卡
    with tab4:
        st.markdown("<h2 class='section-header'>物料效益分析</h2>", unsafe_allow_html=True)

        # 物料投放效果评估图表
        st.markdown("#### 物料投放效果评估")
        # 按客户和月份聚合数据
        material_by_customer = filtered_material.groupby(['客户代码', '经销商名称', '发运月份']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        sales_by_customer = filtered_sales.groupby(['客户代码', '经销商名称', '发运月份']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        effectiveness_data = pd.merge(
            material_by_customer,
            sales_by_customer,
            on=['客户代码', '经销商名称', '发运月份'],
            how='inner'
        )

        # 计算效益比率
        effectiveness_data['物料效益'] = effectiveness_data['销售总额'] / effectiveness_data['物料数量']

        fig_material_effectiveness_chart = px.scatter(
            effectiveness_data,
            x='物料数量',
            y='销售总额',
            size='物料总成本',
            color='物料效益',
            hover_name='经销商名称',
            labels={
                '物料数量': '物料数量 (件)',
                '销售总额': '销售总额 (元)',
                '物料总成本': '物料成本 (元)',
                '物料效益': '物料效益 (元/件)'
            },
            color_continuous_scale='viridis',
            opacity=0.8,
            size_max=50
        )

        fig_material_effectiveness_chart.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                          '物料数量: %{x:,}件<br>' +
                          '销售总额: ¥%{y:,.2f}<br>' +
                          '物料成本: ¥%{marker.size:,.2f}<br>' +
                          '物料效益: ¥%{marker.color:.2f}/件<br>' +
                          '月份: %{customdata}<extra></extra>',
            customdata=effectiveness_data['发运月份'].dt.strftime('%Y-%m').values
        )

        # 计算回归线
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            effectiveness_data['物料数量'],
            effectiveness_data['销售总额']
        )

        x_range = np.linspace(
            effectiveness_data['物料数量'].min(),
            effectiveness_data['物料数量'].max(),
            100
        )
        y_range = slope * x_range + intercept

        fig_material_effectiveness_chart.add_trace(
            go.Scatter(
                x=x_range,
                y=y_range,
                mode='lines',
                line=dict(color='rgba(255, 99, 132, 0.8)', width=2, dash='dash'),
                name=f'趋势线 (r²={r_value ** 2:.2f})',
                hoverinfo='skip'
            )
        )

        fig_material_effectiveness_chart.update_layout(
            title={
                'text': "物料投放量与销售额关系",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis={
                'title': '物料数量 (件)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickformat': ',d',
                'zeroline': True,
                'zerolinecolor': '#e0e0e0',
                'zerolinewidth': 1
            },
            yaxis={
                'title': '销售总额 (元)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥',
                'tickformat': ',.0f',
                'zeroline': True,
                'zerolinecolor': '#e0e0e0',
                'zerolinewidth': 1
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            height=700
        )

        st.plotly_chart(fig_material_effectiveness_chart, use_container_width=True)

        st.markdown(f"""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该散点图展示了物料投放量与销售额之间的关系。每个点代表一个客户的某月表现，点的大小表示物料成本，颜色表示物料效益(销售额/物料数量)。</p>
            <p>红色虚线是趋势线，显示了物料投放量与销售额的一般关系。决定系数(r²)为{r_value ** 2:.2f}，表示物料投放量与销售额的相关程度。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看详细的客户名称、物料数量、销售额、物料成本和物料效益</li>
                <li>关注位于趋势线上方的点，这些是物料使用效率高于平均的客户和月份</li>
                <li>大而明亮的点表示物料成本高且效益好的情况，值得学习</li>
                <li>小而暗淡的点表示物料成本低且效益较差的情况，需要改进</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 物料与销售相关性图表
        st.markdown("#### 物料与销售相关性")
        # 按物料类型聚合数据
        material_by_type = filtered_material.groupby('物料名称').agg({
            '物料数量': 'sum'
        }).reset_index()

        # 合并客户物料和销售数据
        material_sales_link = pd.merge(
            filtered_material[['客户代码', '发运月份', '物料名称', '物料数量']],
            filtered_sales[['客户代码', '发运月份', '销售总额']],
            on=['客户代码', '发运月份'],
            how='inner'
        )

        # 计算每种物料的相关销售额
        material_sales_corr = material_sales_link.groupby('物料名称').agg({
            '物料数量': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        material_sales_corr['单位物料销售额'] = material_sales_corr['销售总额'] / material_sales_corr['物料数量']
        material_sales_corr = material_sales_corr.sort_values('单位物料销售额', ascending=False).head(10)

        fig_material_sales_correlation = px.bar(
            material_sales_corr,
            x='单位物料销售额',
            y='物料名称',
            orientation='h',
            text='单位物料销售额',
            labels={
                '单位物料销售额': '单位物料销售额 (元/件)',
                '物料名称': '物料名称'
            },
            color='单位物料销售额',
            color_continuous_scale='teal',
        )

        fig_material_sales_correlation.update_traces(
            texttemplate='¥%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '单位物料销售额: ¥%{x:.2f}/件<br>' +
                          '总销售额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料总数量: %{customdata[1]:,}件<extra></extra>',
            customdata=material_sales_corr[['销售总额', '物料数量']].values
        )

        fig_material_sales_correlation.update_layout(
            title={
                'text': "物料效益排名 (每单位物料带来的销售额)",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis={
                'title': '单位物料销售额 (元/件)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥'
            },
            yaxis={
                'title': '',
                'autorange': 'reversed',
                'categoryorder': 'total ascending'
            },
            height=600
        )

        st.plotly_chart(fig_material_sales_correlation, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了每种物料带来的单位销售额排名。横条越长，表示该物料每单位带来的销售额越高，效益越好。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看详细的单位物料销售额、总销售额和物料总数量</li>
                <li>分析排名靠前的物料特点，了解为什么这些物料能带来更高的销售额</li>
                <li>考虑增加高效益物料的投入，减少低效益物料的使用</li>
                <li>结合物料成本信息，进一步计算投资回报率</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 地理分布可视化选项卡
    with tab5:
        st.markdown("<h2 class='section-header'>地理分布可视化</h2>", unsafe_allow_html=True)

        # 省份销售热力图
        st.markdown("#### 省份销售热力图")
        province_sales = filtered_sales.groupby('省份').agg({
            '销售总额': 'sum'
        }).reset_index()

        fig_province_sales_map = px.bar(
            province_sales.sort_values('销售总额', ascending=False),
            x='省份',
            y='销售总额',
            color='销售总额',
            color_continuous_scale='Reds',
            text='销售总额',
            labels={
                '销售总额': '销售总额 (元)',
                '省份': '省份'
            }
        )

        fig_province_sales_map.update_traces(
            texttemplate='¥%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '销售总额: ¥%{y:,.2f}<extra></extra>'
        )

        fig_province_sales_map.update_layout(
            title={
                'text': "各省份销售额分布",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=80),
            xaxis={
                'title': '省份',
                'tickangle': -45,
                'categoryorder': 'total descending'
            },
            yaxis={
                'title': '销售总额 (元)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥',
                'tickformat': ',.0f'
            },
            height=600
        )

        st.plotly_chart(fig_province_sales_map, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了各省份的销售额分布。柱形越高，颜色越深，表示该省份销售额越大。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看详细的省份销售额数据</li>
                <li>关注销售额较高的省份，确保资源投入充足</li>
                <li>分析销售额较低的省份，寻找增长机会</li>
                <li>结合区域划分，评估区域销售策略的效果</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 城市物料分布图
        st.markdown("#### 城市物料分布")
        city_material = filtered_material.groupby('城市').agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 只显示前15个城市，避免图表过于拥挤
        top_cities = city_material.sort_values('物料数量', ascending=False).head(15)

        fig_city_material_map = px.bar(
            top_cities,
            x='城市',
            y='物料数量',
            color='物料总成本',
            color_continuous_scale='Blues',
            text='物料数量',
            labels={
                '物料数量': '物料数量 (件)',
                '城市': '城市',
                '物料总成本': '物料总成本 (元)'
            }
        )

        fig_city_material_map.update_traces(
            texttemplate='%{text:,}件',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '物料数量: %{y:,}件<br>' +
                          '物料总成本: ¥%{marker.color:,.2f}<extra></extra>'
        )

        fig_city_material_map.update_layout(
            title={
                'text': "前15个城市物料分布",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=80),
            xaxis={
                'title': '城市',
                'tickangle': -45,
                'categoryorder': 'total descending'
            },
            yaxis={
                'title': '物料数量 (件)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickformat': ',d'
            },
            height=600
        )

        st.plotly_chart(fig_city_material_map, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了物料数量最多的前15个城市。柱形高度表示物料数量，颜色深浅表示物料总成本，颜色越深表示成本越高。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看详细的物料数量和总成本数据</li>
                <li>注意对比物料数量和物料成本的关系，颜色较浅但高度较高的城市表示单位物料成本较低</li>
                <li>结合销售数据分析各城市物料使用效率</li>
                <li>关注物料投入较多的城市，评估物料分配是否合理</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # 物料-产品关联分析选项卡
    with tab6:
        st.markdown("<h2 class='section-header'>物料-产品关联分析</h2>", unsafe_allow_html=True)

        # 物料-产品关联热力图
        st.markdown("#### 物料-产品关联热力图")
        # 合并物料和销售数据
        material_product_link = pd.merge(
            filtered_material[['发运月份', '客户代码', '物料名称', '物料数量']],
            filtered_sales[['发运月份', '客户代码', '产品名称', '销售总额']],
            on=['发运月份', '客户代码'],
            how='inner'
        )

        # 计算每种物料-产品组合的销售额
        material_product_sales = material_product_link.groupby(['物料名称', '产品名称']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 为了生成热力图，将数据转换为透视表格式
        pivot_data = material_product_sales.pivot_table(
            index='物料名称',
            columns='产品名称',
            values='销售总额',
            fill_value=0
        )

        # 获取前8种物料和前8种产品，避免图表过于拥挤
        try:
            top_materials = material_product_sales.groupby('物料名称')['销售总额'].sum().nlargest(8).index
            top_products = material_product_sales.groupby('产品名称')['销售总额'].sum().nlargest(8).index

            # 筛选数据
            filtered_pivot = pivot_data.loc[pivot_data.index.isin(top_materials), pivot_data.columns.isin(top_products)]

            fig_material_product_heatmap = px.imshow(
                filtered_pivot,
                labels=dict(x="产品名称", y="物料名称", color="销售总额 (元)"),
                x=filtered_pivot.columns,
                y=filtered_pivot.index,
                color_continuous_scale='YlGnBu',
                text_auto='.2s',
                aspect="auto"
            )

            fig_material_product_heatmap.update_traces(
                hovertemplate='<b>物料名称: %{y}</b><br>' +
                              '<b>产品名称: %{x}</b><br>' +
                              '销售总额: ¥%{z:,.2f}<extra></extra>',
                showscale=True
            )

            fig_material_product_heatmap.update_layout(
                title={
                    'text': "物料-产品关联热力图 (销售额)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=80),
                xaxis={
                    'title': '产品名称',
                    'tickangle': -45,
                    'side': 'bottom'
                },
                yaxis={
                    'title': '物料名称',
                    'tickangle': 0
                },
                height=600
            )

            st.plotly_chart(fig_material_product_heatmap, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该热力图展示了物料与产品之间的关联强度，颜色越深表示该组合带来的销售额越高。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看具体物料-产品组合的销售总额数据</li>
                    <li>关注颜色最深的组合，了解哪些物料对哪些产品的销售贡献最大</li>
                    <li>分析同一物料对不同产品的促销效果差异</li>
                    <li>根据热力图结果优化物料分配，提高销售效率</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.warning("数据不足，无法生成物料-产品关联热力图。请尝试减少筛选条件。")

        # 最佳物料组合图表
        st.markdown("#### 最佳物料组合")
        # 合并物料和销售数据
        material_sales_link = pd.merge(
            filtered_material[['发运月份', '客户代码', '物料代码', '物料名称']],
            filtered_sales[['发运月份', '客户代码', '销售总额']],
            on=['发运月份', '客户代码'],
            how='inner'
        )

        # 创建物料组合
        material_combinations = material_sales_link.groupby(['客户代码', '发运月份']).agg({
            '物料名称': lambda x: ' + '.join(sorted(set(x))),
            '销售总额': 'mean'
        }).reset_index()

        # 分析物料组合表现
        combo_performance = material_combinations.groupby('物料名称').agg({
            '销售总额': ['mean', 'count']
        }).reset_index()

        combo_performance.columns = ['物料组合', '平均销售额', '使用次数']

        # 筛选使用次数>1的组合，并按平均销售额排序
        top_combos = combo_performance[combo_performance['使用次数'] > 1].sort_values('平均销售额',
                                                                                      ascending=False).head(10)

        if not top_combos.empty:
            fig_best_material_combinations = px.bar(
                top_combos,
                x='平均销售额',
                y='物料组合',
                labels={
                    '平均销售额': '平均销售额 (元)',
                    '物料组合': '物料组合',
                    '使用次数': '使用次数'
                },
                text='平均销售额',
                orientation='h',
                color='使用次数',
                color_continuous_scale='Teal',
                hover_data=['使用次数']
            )

            fig_best_material_combinations.update_traces(
                texttemplate='¥%{text:,.2f}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>' +
                              '平均销售额: ¥%{x:,.2f}<br>' +
                              '使用次数: %{customdata[0]}<extra></extra>',
                customdata=top_combos[['使用次数']].values
            )

            fig_best_material_combinations.update_layout(
                title={
                    'text': "最佳物料组合 (按平均销售额)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={
                    'title': '平均销售额 (元)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4',
                    'tickprefix': '¥',
                    'tickformat': ',.0f'
                },
                yaxis={
                    'title': '',
                    'autorange': 'reversed',
                    'categoryorder': 'total ascending'
                },
                height=600
            )

            st.plotly_chart(fig_best_material_combinations, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了平均销售额最高的物料组合。横条越长表示该组合平均产生的销售额越高，颜色越深表示该组合被使用的次数越多。</p>
                <p>注意: 只显示使用次数大于1的组合，以确保结果可靠性。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看组合的平均销售额和使用次数</li>
                    <li>关注排名靠前的物料组合，分析它们的共同特点</li>
                    <li>结合使用次数评估结果可靠性，使用次数越多越可靠</li>
                    <li>考虑推广表现最佳的物料组合，提高整体销售效果</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("数据不足，无法生成最佳物料组合图表。请尝试减少筛选条件或确保有重复使用的物料组合。")

    # 经销商绩效对比选项卡
    with tab7:
        st.markdown("<h2 class='section-header'>经销商绩效对比</h2>", unsafe_allow_html=True)

        # 经销商销售效率图表
        st.markdown("#### 经销商销售效率")
        distributor_material = filtered_material.groupby('经销商名称').agg({
            '物料数量': 'sum'
        }).reset_index()

        distributor_sales = filtered_sales.groupby('经销商名称').agg({
            '销售总额': 'sum',
            '求和项:数量（箱）': 'sum'
        }).reset_index()

        distributor_efficiency = pd.merge(distributor_material, distributor_sales, on='经销商名称', how='inner')
        distributor_efficiency['销售效率'] = distributor_efficiency['销售总额'] / distributor_efficiency['物料数量']

        # 选择前10名
        top_distributors = distributor_efficiency.sort_values('销售效率', ascending=False).head(10)

        fig_distributor_efficiency = px.bar(
            top_distributors,
            x='销售效率',
            y='经销商名称',
            labels={
                '销售效率': '销售效率 (元/件)',
                '经销商名称': '经销商',
                '销售总额': '销售总额 (元)',
                '物料数量': '物料数量 (件)'
            },
            text='销售效率',
            orientation='h',
            color='销售总额',
            color_continuous_scale='Purples',
            hover_data=['销售总额', '物料数量']
        )

        fig_distributor_efficiency.update_traces(
            texttemplate='¥%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '销售效率: ¥%{x:.2f}/件<br>' +
                          '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料数量: %{customdata[1]:,}件<extra></extra>',
            customdata=top_distributors[['销售总额', '物料数量']].values
        )

        fig_distributor_efficiency.update_layout(
            title={
                'text': "经销商销售效率排名 (销售额/物料数量)",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 22, 'color': '#1f3867'}
            },
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'color': '#444444'},
            margin=dict(l=40, r=40, t=80, b=40),
            xaxis={
                'title': '销售效率 (元/件)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥',
                'tickformat': ',.2f'
            },
            yaxis={
                'title': '',
                'autorange': 'reversed',
                'categoryorder': 'total ascending'
            },
            height=600
        )

        st.plotly_chart(fig_distributor_efficiency, use_container_width=True)

        st.markdown("""
        <div class='explanation'>
            <h6>图表解读:</h6>
            <p>该图表展示了销售效率最高的前10名经销商。销售效率是销售总额与物料数量的比值，表示单位物料带来的销售额。</p>
            <p>横条越长表示效率越高，颜色越深表示销售总额越大。</p>
            <p><strong>使用提示:</strong></p>
            <ul>
                <li>鼠标悬停可查看经销商的销售效率、销售总额和物料数量</li>
                <li>关注既有高销售效率又有高销售总额（颜色深）的经销商，他们是最有价值的合作伙伴</li>
                <li>分析高效率经销商的物料使用策略，用于培训其他经销商</li>
                <li>考虑向高效率经销商倾斜更多资源，提高整体投资回报</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # 经销商物料使用情况图表
        st.markdown("#### 经销商物料使用情况")
        # 获取数量最多的物料类型
        top_materials = filtered_material.groupby('物料名称')['物料数量'].sum().nlargest(5).index.tolist()

        # 筛选数据
        filtered_for_chart = filtered_material[filtered_material['物料名称'].isin(top_materials)]

        # 分析经销商物料使用情况
        try:
            distributor_material_usage = pd.pivot_table(
                filtered_for_chart,
                values='物料数量',
                index='经销商名称',
                columns='物料名称',
                fill_value=0
            ).reset_index()

            # 选择前10名经销商 - 按总物料使用量
            top_distributors_idx = distributor_material_usage.iloc[:, 1:].sum(axis=1).nlargest(10).index
            top_distributor_usage = distributor_material_usage.iloc[top_distributors_idx]

            # 融合数据为适合堆叠条形图的格式
            melted_data = pd.melt(
                top_distributor_usage,
                id_vars=['经销商名称'],
                value_vars=top_materials,
                var_name='物料名称',
                value_name='物料数量'
            )

            fig_distributor_material_usage = px.bar(
                melted_data,
                x='物料数量',
                y='经销商名称',
                color='物料名称',
                labels={
                    '物料数量': '物料数量 (件)',
                    '经销商名称': '经销商',
                    '物料名称': '物料类型'
                },
                orientation='h',
                barmode='stack',
                color_discrete_sequence=px.colors.qualitative.Bold
            )

            fig_distributor_material_usage.update_traces(
                hovertemplate='<b>%{y}</b><br>' +
                              '物料类型: %{customdata}<br>' +
                              '物料数量: %{x:,}件<extra></extra>',
                customdata=melted_data['物料名称'].values
            )

            fig_distributor_material_usage.update_layout(
                title={
                    'text': "经销商物料使用情况 (前5种物料)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={
                    'title': '物料数量 (件)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4',
                    'tickformat': ',d'
                },
                yaxis={
                    'title': '',
                    'autorange': 'reversed',
                    'categoryorder': 'total ascending'
                },
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.15,
                    xanchor="center",
                    x=0.5,
                    title=""
                ),
                height=600
            )

            st.plotly_chart(fig_distributor_material_usage, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了前10名经销商使用的前5种物料分布情况。每个横条代表一个经销商，不同颜色代表不同物料类型。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看详细的物料类型和数量</li>
                    <li>观察经销商物料使用的多样性，使用物料种类越多的颜色越丰富</li>
                    <li>分析顶级经销商的物料偏好，了解他们的成功策略</li>
                    <li>比较相似规模经销商的物料组合差异，找出最佳实践</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        except:
            st.warning("数据不足，无法生成经销商物料使用情况图表。请尝试减少筛选条件。")

    # 费比分析选项卡
    with tab8:
        st.markdown("<h2 class='section-header'>费比分析</h2>", unsafe_allow_html=True)

        # 区域费比分析和销售人员费比分析
        fee_cols = st.columns(2)

        with fee_cols[0]:
            st.markdown("#### 区域费比分析")
            region_material = filtered_material.groupby('所属区域').agg({
                '物料总成本': 'sum'
            }).reset_index()

            region_sales = filtered_sales.groupby('所属区域').agg({
                '销售总额': 'sum'
            }).reset_index()

            region_cost_sales = pd.merge(region_material, region_sales, on='所属区域', how='outer')
            region_cost_sales['费比'] = (region_cost_sales['物料总成本'] / region_cost_sales['销售总额']) * 100

            # 添加辅助列以便于绘制散点图
            region_cost_sales['销售额百分比'] = region_cost_sales['销售总额'] / region_cost_sales[
                '销售总额'].sum() * 100 if region_cost_sales['销售总额'].sum() > 0 else 0

            fig_region_cost_sales_analysis = px.scatter(
                region_cost_sales,
                x='销售额百分比',
                y='费比',
                size='物料总成本',
                color='所属区域',
                text='所属区域',
                labels={
                    '销售额百分比': '销售贡献度 (%)',
                    '费比': '费比 (%)',
                    '物料总成本': '物料成本 (元)',
                    '所属区域': '区域'
                },
                size_max=60,
                color_discrete_sequence=px.colors.qualitative.Safe
            )

            fig_region_cost_sales_analysis.update_traces(
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>' +
                              '销售贡献度: %{x:.2f}%<br>' +
                              '费比: %{y:.2f}%<br>' +
                              '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                              '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
                customdata=region_cost_sales[['物料总成本', '销售总额']].values
            )

            # 添加参考线 - 平均费比
            avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales[
                '销售总额'].sum()) * 100 if region_cost_sales['销售总额'].sum() > 0 else 0
            fig_region_cost_sales_analysis.add_hline(
                y=avg_cost_sales_ratio,
                line_dash="dash",
                line_color="#ff5a36",
                line_width=2,
                annotation=dict(
                    text=f"平均费比: {avg_cost_sales_ratio:.2f}%",
                    font=dict(size=14, color="#ff5a36"),
                    bgcolor="#ffffff",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4,
                    x=1,
                    y=avg_cost_sales_ratio,
                    xanchor="right",
                    yanchor="middle"
                )
            )

            # 添加象限区域
            max_x = region_cost_sales['销售额百分比'].max() * 1.1 if not region_cost_sales.empty else 100
            max_y = region_cost_sales['费比'].max() * 1.1 if not region_cost_sales.empty else 100

            fig_region_cost_sales_analysis.add_shape(
                type="rect",
                x0=0,
                y0=0,
                x1=max_x,
                y1=avg_cost_sales_ratio,
                fillcolor="rgba(144, 238, 144, 0.15)",
                line=dict(width=0),
                layer="below"
            )
            fig_region_cost_sales_analysis.add_shape(
                type="rect",
                x0=0,
                y0=avg_cost_sales_ratio,
                x1=max_x,
                y1=max_y,
                fillcolor="rgba(255, 182, 193, 0.15)",
                line=dict(width=0),
                layer="below"
            )

            fig_region_cost_sales_analysis.update_layout(
                title={
                    'text': "区域费比分析",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={
                    'title': '销售贡献度 (%)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4',
                    'ticksuffix': '%',
                    'zeroline': True,
                    'zerolinecolor': '#e0e0e0',
                    'zerolinewidth': 1
                },
                yaxis={
                    'title': '费比 (%)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4',
                    'ticksuffix': '%',
                    'zeroline': True,
                    'zerolinecolor': '#e0e0e0',
                    'zerolinewidth': 1
                },
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    title=""
                ),
                height=500
            )

            st.plotly_chart(fig_region_cost_sales_analysis, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该气泡图展示了各区域的费比与销售贡献度的关系。横轴表示区域销售额占总销售额的百分比，纵轴表示费比(物料成本/销售额)，气泡大小表示物料总成本。</p>
                <p>红色虚线表示平均费比，绿色区域表示费比低于平均（良好），粉色区域表示费比高于平均（需改进）。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看详细的区域、销售贡献度、费比、物料成本和销售总额数据</li>
                    <li>理想情况是气泡位于绿色区域且靠右侧，表示费比低且销售贡献大</li>
                    <li>重点关注位于粉色区域右侧的大气泡，这些区域费比高且销售额大，改进空间大</li>
                    <li>分析不同区域间的差异，找出费比低的区域的成功经验</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with fee_cols[1]:
            st.markdown("#### 销售人员费比分析")
            salesperson_material = filtered_material.groupby('申请人').agg({
                '物料总成本': 'sum'
            }).reset_index()

            salesperson_sales = filtered_sales.groupby('申请人').agg({
                '销售总额': 'sum'
            }).reset_index()

            salesperson_cost_sales = pd.merge(salesperson_material, salesperson_sales, on='申请人', how='outer')
            salesperson_cost_sales['费比'] = (salesperson_cost_sales['物料总成本'] / salesperson_cost_sales[
                '销售总额']) * 100

            # 处理可能的无穷大值
            salesperson_cost_sales.replace([np.inf, -np.inf], np.nan, inplace=True)
            salesperson_cost_sales.dropna(subset=['费比'], inplace=True)

            # 按费比排序，选择前15名销售人员展示
            top_salespersons = salesperson_cost_sales.sort_values('费比').head(15)

            # 计算平均费比
            avg_cost_sales_ratio = (salesperson_cost_sales['物料总成本'].sum() / salesperson_cost_sales[
                '销售总额'].sum()) * 100 if salesperson_cost_sales['销售总额'].sum() > 0 else 0

            fig_salesperson_cost_sales_analysis = px.bar(
                top_salespersons,
                x='申请人',
                y='费比',
                labels={
                    '费比': '费比 (%)',
                    '申请人': '销售人员',
                    '物料总成本': '物料成本 (元)',
                    '销售总额': '销售总额 (元)'
                },
                color='费比',
                text='费比',
                color_continuous_scale='RdYlGn_r',
                hover_data=['物料总成本', '销售总额']
            )

            fig_salesperson_cost_sales_analysis.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' +
                              '费比: %{y:.2f}%<br>' +
                              '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                              '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
                customdata=top_salespersons[['物料总成本', '销售总额']].values
            )

            fig_salesperson_cost_sales_analysis.add_hline(
                y=avg_cost_sales_ratio,
                line_dash="dash",
                line_color="#ff5a36",
                line_width=2,
                annotation=dict(
                    text=f"平均: {avg_cost_sales_ratio:.2f}%",
                    font=dict(size=14, color="#ff5a36"),
                    bgcolor="#ffffff",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4,
                    x=1,
                    y=avg_cost_sales_ratio,
                    xanchor="right",
                    yanchor="middle"
                )
            )

            fig_salesperson_cost_sales_analysis.update_layout(
                title={
                    'text': "销售人员费比分析 (前15名)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=100),
                xaxis={
                    'title': '销售人员',
                    'tickangle': -45,
                    'categoryorder': 'total ascending'
                },
                yaxis={
                    'title': '费比 (%)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4',
                    'ticksuffix': '%'
                },
                height=500
            )

            st.plotly_chart(fig_salesperson_cost_sales_analysis, use_container_width=True)

            st.markdown("""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了费比最低的15名销售人员。费比是物料成本占销售额的百分比，费比越低表示销售人员使用物料的效率越高。</p>
                <p>颜色说明: 绿色表示费比较低（好），红色表示费比较高（需要改进）。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>红色虚线表示全公司平均费比基准线</li>
                    <li>鼠标悬停可查看详细的费比、物料成本和销售总额数据</li>
                    <li>分析费比低的销售人员使用物料的策略，作为最佳实践推广</li>
                    <li>考虑为费比过高的销售人员提供培训，提高物料使用效率</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 经销商费比分析图表
        st.markdown("#### 经销商费比分析")
        distributor_material = filtered_material.groupby(['经销商名称', '所属区域']).agg({
            '物料总成本': 'sum'
        }).reset_index()

        distributor_sales = filtered_sales.groupby(['经销商名称', '所属区域']).agg({
            '销售总额': 'sum'
        }).reset_index()

        distributor_cost_sales = pd.merge(distributor_material, distributor_sales, on=['经销商名称', '所属区域'],
                                          how='outer')
        distributor_cost_sales['费比'] = (distributor_cost_sales['物料总成本'] / distributor_cost_sales[
            '销售总额']) * 100

        # 处理可能的无穷大值和异常值
        distributor_cost_sales.replace([np.inf, -np.inf], np.nan, inplace=True)
        distributor_cost_sales.dropna(subset=['费比'], inplace=True)

        # 剔除极端异常值，保留可视化效果
        if not distributor_cost_sales.empty:
            upper_limit = distributor_cost_sales['费比'].quantile(0.95)  # 只保留95%分位数以内的数据
            distributor_cost_sales = distributor_cost_sales[distributor_cost_sales['费比'] <= upper_limit]

            # 选择每个区域费比最低的3个经销商，总共不超过15个
            top_distributors = []
            for region in distributor_cost_sales['所属区域'].unique():
                region_distributors = distributor_cost_sales[distributor_cost_sales['所属区域'] == region]
                top_region = region_distributors.sort_values('费比').head(3)
                top_distributors.append(top_region)

            if top_distributors:
                top_distributors_df = pd.concat(top_distributors).sort_values(['所属区域', '费比'])

                # 计算平均费比
                avg_cost_sales_ratio = (distributor_cost_sales['物料总成本'].sum() / distributor_cost_sales[
                    '销售总额'].sum()) * 100

                fig_distributor_cost_sales_analysis = px.bar(
                    top_distributors_df,
                    x='经销商名称',
                    y='费比',
                    color='所属区域',
                    labels={
                        '费比': '费比 (%)',
                        '经销商名称': '经销商',
                        '所属区域': '区域',
                        '物料总成本': '物料成本 (元)',
                        '销售总额': '销售总额 (元)'
                    },
                    text='费比',
                    hover_data=['物料总成本', '销售总额'],
                    barmode='group',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )

                fig_distributor_cost_sales_analysis.update_traces(
                    texttemplate='%{text:.2f}%',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b> (%{customdata[2]})<br>' +
                                  '费比: %{y:.2f}%<br>' +
                                  '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                                  '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
                    customdata=top_distributors_df[['物料总成本', '销售总额', '所属区域']].values
                )

                fig_distributor_cost_sales_analysis.add_hline(
                    y=avg_cost_sales_ratio,
                    line_dash="dash",
                    line_color="#ff5a36",
                    line_width=2,
                    annotation=dict(
                        text=f"平均: {avg_cost_sales_ratio:.2f}%",
                        font=dict(size=14, color="#ff5a36"),
                        bgcolor="#ffffff",
                        bordercolor="#ff5a36",
                        borderwidth=1,
                        borderpad=4,
                        x=1,
                        y=avg_cost_sales_ratio,
                        xanchor="right",
                        yanchor="middle"
                    )
                )

                fig_distributor_cost_sales_analysis.update_layout(
                    title={
                        'text': "各区域最佳费比经销商分析",
                        'y': 0.95,
                        'x': 0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font': {'size': 22, 'color': '#1f3867'}
                    },
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font={'color': '#444444'},
                    margin=dict(l=40, r=40, t=80, b=120),
                    xaxis={
                        'title': '经销商',
                        'tickangle': -45,
                    },
                    yaxis={
                        'title': '费比 (%)',
                        'showgrid': True,
                        'gridcolor': '#f4f4f4',
                        'ticksuffix': '%'
                    },
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.25,
                        xanchor="center",
                        x=0.5,
                        title=""
                    ),
                    height=600
                )

                st.plotly_chart(fig_distributor_cost_sales_analysis, use_container_width=True)

                st.markdown("""
                <div class='explanation'>
                    <h6>图表解读:</h6>
                    <p>该图表展示了每个区域费比最低的经销商。费比越低表示经销商使用物料的效率越高，创造的销售价值越大。</p>
                    <p>不同颜色代表不同区域，同一区域的经销商并排展示，便于区域内和区域间比较。</p>
                    <p><strong>使用提示:</strong></p>
                    <ul>
                        <li>红色虚线表示全公司平均费比基准线</li>
                        <li>鼠标悬停可查看详细的经销商、区域、费比、物料成本和销售总额数据</li>
                        <li>分析低费比经销商的成功经验，形成可复制的最佳实践</li>
                        <li>比较不同区域的费比水平，找出区域间的差异和改进空间</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("数据不足，无法生成经销商费比分析图表。")
        else:
            st.warning("数据不足，无法生成经销商费比分析图表。")

        # 费比异常值提醒
        st.markdown("#### 费比异常值提醒")
        # 计算总体费比
        total_material_cost = filtered_material['物料总成本'].sum()
        total_sales = filtered_sales['销售总额'].sum()
        overall_cost_sales_ratio = (total_material_cost / total_sales) * 100 if total_sales > 0 else 0

        # 按经销商计算费比
        distributor_material = filtered_material.groupby('经销商名称').agg({
            '物料总成本': 'sum'
        }).reset_index()

        distributor_sales = filtered_sales.groupby('经销商名称').agg({
            '销售总额': 'sum'
        }).reset_index()

        distributor_cost_sales = pd.merge(distributor_material, distributor_sales, on='经销商名称', how='outer')
        distributor_cost_sales['费比'] = (distributor_cost_sales['物料总成本'] / distributor_cost_sales[
            '销售总额']) * 100

        # 处理可能的无穷大值
        distributor_cost_sales.replace([np.inf, -np.inf], np.nan, inplace=True)
        distributor_cost_sales.dropna(subset=['费比'], inplace=True)

        # 识别费比异常值 (高于平均值50%以上)
        high_cost_sales_threshold = overall_cost_sales_ratio * 1.5
        anomalies = distributor_cost_sales[distributor_cost_sales['费比'] > high_cost_sales_threshold]

        # 只考虑销售额大于一定阈值的经销商，避免小额销售导致的异常
        min_sales = 10000  # 最小销售额阈值
        anomalies = anomalies[anomalies['销售总额'] > min_sales]

        anomalies = anomalies.sort_values('费比', ascending=False)

        if len(anomalies) > 0:
            st.markdown(f"<h5 style='color: #d9534f;'⚠️ 费比异常值警告 ({len(anomalies)}个)</h5>",
                        unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)

            # 使用列布局展示异常卡片
            anomaly_cols = st.columns(3)

            for i, (_, row) in enumerate(anomalies.iterrows()):
                # 计算异常程度
                anomaly_level = row['费比'] / overall_cost_sales_ratio

                # 根据异常程度设置不同颜色
                if anomaly_level > 2:
                    card_color = "#f8d7da"  # 严重异常 - 红色
                else:
                    card_color = "#fff3cd"  # 中等异常 - 黄色

                with anomaly_cols[i % 3]:
                    st.markdown(f"""
                    <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 10px; margin-bottom: 10px; background-color: {card_color};'>
                        <h6 style='margin-top: 0;'>{row['经销商名称']}</h6>
                        <p style='margin-bottom: 5px;'><strong>费比:</strong> {row['费比']:.2f}% <span style='color: red; font-weight: bold;'>(高出平均{anomaly_level:.1f}倍)</span></p>
                        <p style='margin-bottom: 5px;'><strong>物料成本:</strong> ¥{row['物料总成本']:,.2f}</p>
                        <p style='margin-bottom: 0;'><strong>销售额:</strong> ¥{row['销售总额']:,.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # 添加总结和建议
            st.markdown("""
            <div style='border-radius: 10px; border: 1px solid #b8daff; padding: 15px; margin-top: 20px; background-color: #cce5ff;'>
                <h5 style='margin-top: 0;'>费比异常分析总结</h5>
                <p>共发现上述费比异常值。平均费比为 <strong>{:.2f}%</strong>，但这些经销商的费比远高于平均值。</p>
                <p><strong>可能的原因:</strong></p>
                <ul>
                    <li>物料使用效率低，未转化为有效销售</li>
                    <li>销售策略不当，导致投入产出比不佳</li>
                    <li>物料分配不合理，未针对客户需求定制</li>
                </ul>
                <p><strong>建议行动:</strong></p>
                <ul>
                    <li>与这些经销商沟通，了解物料使用情况</li>
                    <li>提供针对性培训，提高物料使用效率</li>
                    <li>调整物料分配策略，减少费比异常高的经销商的物料投入</li>
                </ul>
            </div>
            """.format(overall_cost_sales_ratio), unsafe_allow_html=True)
        else:
            # 返回正面信息卡片
            st.markdown("""
            <div style='border-radius: 10px; border: 1px solid #c3e6cb; padding: 15px; background-color: #d4edda;'>
                <h5 style='color: #155724; margin-top: 0;'>✅ 良好费比控制</h5>
                <p>恭喜! 未发现费比异常值。所有经销商的费比都在平均值的1.5倍范围内，表明物料使用效率整体良好。</p>
                <p>当前平均费比为 <strong>{:.2f}%</strong>，继续保持这一水平将有利于提高整体投资回报率。</p>
                <p><strong>建议行动:</strong></p>
                <ul>
                    <li>分享优秀经销商的物料使用经验</li>
                    <li>继续监控费比变化趋势，及时发现潜在问题</li>
                    <li>探索进一步优化物料投放策略的机会</li>
                </ul>
            </div>
            """.format(overall_cost_sales_ratio), unsafe_allow_html=True)

    # 利润最大化分析选项卡
    with tab9:
        st.markdown("<h2 class='section-header'>利润最大化分析</h2>", unsafe_allow_html=True)

        # 物料ROI分析图表
        st.markdown("#### 物料ROI分析")
        # 合并数据分析物料ROI
        material_sales_link = pd.merge(
            filtered_material[['发运月份', '客户代码', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '销售总额']],
            on=['发运月份', '客户代码'],
            how='inner'
        )

        # 按物料类型分析ROI
        material_roi = material_sales_link.groupby(['物料代码', '物料名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        material_roi['ROI'] = material_roi['销售总额'] / material_roi['物料总成本']

        # 处理可能的无穷大值和异常值
        material_roi.replace([np.inf, -np.inf], np.nan, inplace=True)
        material_roi.dropna(subset=['ROI'], inplace=True)

        if not material_roi.empty:
            # 剔除极端异常值，保留可视化效果
            upper_limit = material_roi['ROI'].quantile(0.95)  # 只保留95%分位数以内的数据
            material_roi = material_roi[material_roi['ROI'] <= upper_limit]

            # 筛选数据 - 只显示成本和销售额都大于一定阈值的物料
            min_cost = 1000  # 最小物料成本阈值
            min_sales = 10000  # 最小销售额阈值
            material_roi_filtered = material_roi[
                (material_roi['物料总成本'] > min_cost) &
                (material_roi['销售总额'] > min_sales)
                ].sort_values('ROI', ascending=False).head(15)  # 只选择前15名

            fig_material_roi = px.bar(
                material_roi_filtered,
                x='ROI',
                y='物料名称',
                labels={
                    'ROI': 'ROI (销售额/物料成本)',
                    '物料名称': '物料名称',
                    '物料总成本': '物料成本 (元)',
                    '销售总额': '销售总额 (元)',
                    '物料数量': '物料数量 (件)'
                },
                text='ROI',
                orientation='h',
                color='ROI',
                color_continuous_scale='Viridis',
                hover_data=['物料总成本', '销售总额', '物料数量']
            )

            fig_material_roi.update_traces(
                texttemplate='%{text:.2f}',
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>' +
                              'ROI: %{x:.2f}<br>' +
                              '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                              '销售总额: ¥%{customdata[1]:,.2f}<br>' +
                              '物料数量: %{customdata[2]:,}件<extra></extra>',
                customdata=material_roi_filtered[['物料总成本', '销售总额', '物料数量']].values
            )

            # 计算平均ROI作为参考线
            avg_roi = material_roi['销售总额'].sum() / material_roi['物料总成本'].sum() if material_roi[
                                                                                               '物料总成本'].sum() > 0 else 0

            fig_material_roi.add_vline(
                x=avg_roi,
                line_dash="dash",
                line_color="#4CAF50",
                line_width=2,
                annotation=dict(
                    text=f"平均ROI: {avg_roi:.2f}",
                    font=dict(size=14, color="#4CAF50"),
                    bgcolor="#ffffff",
                    bordercolor="#4CAF50",
                    borderwidth=1,
                    borderpad=4,
                    y=0.5,
                    x=avg_roi,
                    xanchor="center",
                    yanchor="middle"
                )
            )

            fig_material_roi.update_layout(
                title={
                    'text': "物料ROI分析 (销售额/物料成本)",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {'size': 22, 'color': '#1f3867'}
                },
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'color': '#444444'},
                margin=dict(l=40, r=40, t=80, b=40),
                xaxis={
                    'title': 'ROI (销售额/物料成本)',
                    'showgrid': True,
                    'gridcolor': '#f4f4f4'
                },
                yaxis={
                    'title': '',
                    'autorange': 'reversed',
                    'categoryorder': 'total ascending'
                },
                height=600
            )

            st.plotly_chart(fig_material_roi, use_container_width=True)

            st.markdown(f"""
            <div class='explanation'>
                <h6>图表解读:</h6>
                <p>该图表展示了投资回报率(ROI)最高的物料。ROI是销售额与物料成本的比值，表示每投入1元物料成本产生的销售额。</p>
                <p>绿色虚线表示平均ROI（{avg_roi:.2f}），显示所有物料的整体表现水平。</p>
                <p>注意: 此图表只包含物料成本>1000元且销售额>10000元的物料，以确保结果可靠性。</p>
                <p><strong>使用提示:</strong></p>
                <ul>
                    <li>鼠标悬停可查看详细的ROI、物料成本、销售总额和物料数量</li>
                    <li>关注ROI高于平均线的物料，这些是最值得投资的物料</li>
                    <li>分析高ROI物料的特点，了解为什么它们比其他物料更有效</li>
                    <li>建议增加高ROI物料的投入，减少低ROI物料的使用，提高整体投资回报</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("数据不足，无法生成物料ROI分析图表。请尝试减少筛选条件。")

        # 最优物料分配建议
        st.markdown("#### 最优物料分配建议")
        # 合并数据分析物料ROI
        material_sales_link = pd.merge(
            filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '经销商名称', '销售总额']],
            on=['发运月份', '客户代码', '经销商名称'],
            how='inner'
        )

        # 按物料类型分析ROI
        material_roi = material_sales_link.groupby(['物料代码', '物料名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        material_roi['ROI'] = material_roi['销售总额'] / material_roi['物料总成本']

        # 处理可能的无穷大值和异常值
        material_roi.replace([np.inf, -np.inf], np.nan, inplace=True)
        material_roi.dropna(subset=['ROI'], inplace=True)

        # 按客户分析物料效果
        customer_material_effect = material_sales_link.groupby(['客户代码', '经销商名称', '物料代码', '物料名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        customer_material_effect['ROI'] = customer_material_effect['销售总额'] / customer_material_effect['物料总成本']

        # 处理可能的无穷大值
        customer_material_effect.replace([np.inf, -np.inf], np.nan, inplace=True)
        customer_material_effect.dropna(subset=['ROI'], inplace=True)

        # 筛选数据 - 只考虑物料成本大于一定阈值的记录
        min_cost = 500  # 最小物料成本阈值
        material_roi = material_roi[material_roi['物料总成本'] > min_cost]
        customer_material_effect = customer_material_effect[customer_material_effect['物料总成本'] > min_cost]

        if not material_roi.empty:
            # 分析高效和低效物料
            high_roi_materials = material_roi.sort_values('ROI', ascending=False).head(5)
            low_roi_materials = material_roi.sort_values('ROI').head(5)

            # 计算整体ROI
            total_material_cost = filtered_material['物料总成本'].sum()
            total_sales = filtered_sales['销售总额'].sum()
            overall_roi = total_sales / total_material_cost if total_material_cost > 0 else 0

            # 使用列布局创建现代化的信息卡片
            # 1. 现状分析卡片
            st.markdown(f"""
            <div style='border-radius: 10px; border: 1px solid #e0e0e0; padding: 15px; margin-bottom: 20px; background-color: #f8f9fa;'>
                <h5 style='margin-top: 0;'>物料投入现状分析</h5>
                <p>当前整体ROI: <strong>{overall_roi:.2f}</strong> (总销售额: ¥{total_sales:,.2f} / 总物料成本: ¥{total_material_cost:,.2f})</p>
                <div style='background-color: #e9ecef; height: 20px; border-radius: 4px; margin-bottom: 15px;'>
                    <div style='width: {min(int(overall_roi * 10), 100)}%; height: 100%; background-color: {
            "#28a745" if overall_roi >= 5 else "#ffc107" if overall_roi >= 3 else "#dc3545"
            }; border-radius: 4px;'></div>
                </div>
                <p>通过优化物料分配，预估可将整体ROI提高15-20%，直接提升销售业绩。</p>
            </div>
            """, unsafe_allow_html=True)

            # 2. 高ROI物料和低ROI物料卡片
            roi_cols = st.columns(2)

            with roi_cols[0]:
                st.markdown("<h5 style='color: #28a745;'>高ROI物料 (建议增加投放)</h5>", unsafe_allow_html=True)
                for _, row in high_roi_materials.iterrows():
                    st.markdown(f"""
                    <div style='border-radius: 10px; border-left: 4px solid #28a745; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa;'>
                        <h6 style='margin-top: 0;'>{row['物料名称']}</h6>
                        <div style='display: flex; justify-content: space-between;'>
                            <span><strong>ROI:</strong> <span style='color: #28a745;'>{row['ROI']:.2f}</span></span>
                        </div>
                        <p style='margin-bottom: 5px; font-size: 0.9rem; color: #6c757d;'>
                            投入: ¥{row['物料总成本']:,.2f} | 销售: ¥{row['销售总额']:,.2f} | 数量: {row['物料数量']:,}件
                        </p>
                        <div style='background-color: #e9ecef; height: 8px; border-radius: 4px; margin-top: 5px;'>
                            <div style='width: {min(int(row['ROI'] * 10), 100)}%; height: 100%; background-color: #28a745; border-radius: 4px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with roi_cols[1]:
                st.markdown("<h5 style='color: #dc3545;'>低ROI物料 (建议减少或优化投放)</h5>", unsafe_allow_html=True)
                for _, row in low_roi_materials.iterrows():
                    st.markdown(f"""
                    <div style='border-radius: 10px; border-left: 4px solid #dc3545; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa;'>
                        <h6 style='margin-top: 0;'>{row['物料名称']}</h6>
                        <div style='display: flex; justify-content: space-between;'>
                            <span><strong>ROI:</strong> <span style='color: #dc3545;'>{row['ROI']:.2f}</span></span>
                        </div>
                        <p style='margin-bottom: 5px; font-size: 0.9rem; color: #6c757d;'>
                            投入: ¥{row['物料总成本']:,.2f} | 销售: ¥{row['销售总额']:,.2f} | 数量: {row['物料数量']:,}件
                        </p>
                        <div style='background-color: #e9ecef; height: 8px; border-radius: 4px; margin-top: 5px;'>
                            <div style='width: {min(int(row['ROI'] * 10), 100)}%; height: 100%; background-color: #dc3545; border-radius: 4px;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # 4. 优化建议卡片
            if not customer_material_effect.empty:
                # 找到物料ROI表现最好的客户
                best_customer_material = customer_material_effect.sort_values('ROI', ascending=False).head(3)

                st.markdown("""
                <div style='border-radius: 10px; border: 1px solid #b8daff; padding: 15px; margin-top: 20px; background-color: #cce5ff;'>
                    <h5 style='margin-top: 0;'>最佳实践与优化建议</h5>
                    <h6 style='margin-bottom: 15px;'>最佳客户-物料组合:</h6>
                """, unsafe_allow_html=True)

                for _, row in best_customer_material.iterrows():
                    st.markdown(f"""
                    <div style='border-radius: 10px; border-left: 4px solid #007bff; padding: 10px; margin-bottom: 10px; background-color: #f8f9fa;'>
                        <h6 style='margin-top: 0;'>经销商 '{row['经销商名称']}' + '{row['物料名称']}'</h6>
                        <div style='display: flex; justify-content: space-between;'>
                            <span><strong>ROI:</strong> <span style='color: #007bff;'>{row['ROI']:.2f}</span></span>
                        </div>
                        <p style='margin-bottom: 0; font-size: 0.9rem; color: #6c757d;'>
                            投入: ¥{row['物料总成本']:,.2f} | 销售: ¥{row['销售总额']:,.2f}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("""
                    <hr style='margin: 20px 0;'>
                    <h6 style='margin-bottom: 10px;'>优化策略:</h6>
                    <ul style='margin-bottom: 0;'>
                        <li><strong>投资重分配:</strong> 将物料预算从低ROI物料重新分配到高ROI物料，预计可提高整体ROI 15-20%</li>
                        <li><strong>客户定制策略:</strong> 根据最佳客户-物料组合的模式，为不同客户提供定制化的物料配置</li>
                        <li><strong>培训提升:</strong> 向所有销售人员和经销商分享高ROI物料的最佳使用方式</li>
                        <li><strong>持续监控:</strong> 定期评估各物料ROI变化，及时调整投资策略</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='border-radius: 10px; border: 1px solid #b8daff; padding: 15px; margin-top: 20px; background-color: #cce5ff;'>
                    <h5 style='margin-top: 0;'>优化建议</h5>
                    <p>暂无足够数据生成客户-物料组合分析，请确保数据完整性或调整筛选条件。</p>
                    <hr style='margin: 20px 0;'>
                    <h6 style='margin-bottom: 10px;'>一般优化策略:</h6>
                    <ul style='margin-bottom: 0;'>
                        <li><strong>投资重分配:</strong> 将物料预算从低ROI物料重新分配到高ROI物料</li>
                        <li><strong>持续监控:</strong> 定期评估各物料ROI变化，及时调整投资策略</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("数据不足，无法生成最优物料分配建议。请尝试减少筛选条件。")


if __name__ == "__main__":
    main()