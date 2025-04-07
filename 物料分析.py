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
        st.warning(f"无法加载Excel文件: {e}，创建模拟数据用于演示...")

        # 创建模拟数据
        # 生成日期范围
        date_range = pd.date_range(start='2024-01-01', end='2024-12-31', freq='MS')

        # 区域、省份、城市和经销商数据 - 根据您的数据调整
        regions = ['南', '东', '西', '北']  # 简化区域名称
        provinces = ['广东', '江苏', '福建', '浙江', '北京', '上海', '四川', '辽宁']
        cities = ['广州', '佛山', '无锡', '福州', '杭州', '南京', '成都', '沈阳']
        distributors = [f'经销商{i}' for i in range(1, 21)]
        customer_codes = [f'CU{i:04d}' for i in range(1, 21)]
        sales_persons = [f'销售{i}' for i in range(1, 11)]

        # 物料数据 - 适配您的数据格式
        material_codes = [f'M10{i:03d}' for i in range(1, 11)]
        material_names = ['口力利是封（大红）-中国', '口力贴纸-中国', '口力特惠装OPP袋-内销',
                          '口力汉堡公仔（带中盒）-中国', '口力春联-内销', '口力emoji不倒翁单盒装-内销',
                          '口力CNY堆头-内销', '口力新版贴纸（四主题随机发）-内销', '口力午餐袋-中国', '口力扭扭虫-中国']
        material_prices = [2.35, 1.50, 0.80, 20.0, 4.5, 12.0, 80.0, 1.2, 15.0, 10.0]

        # 产品数据 - 适配您的数据格式
        product_codes = ['F0104L', 'F01E4B', 'F01H9B', 'F01L3A', 'F01L4A', 'F3411A', 'F3415C', 'F3421C', 'F0110A',
                         'F01D6B']
        product_names = ['口力比萨68G袋装-中国', '口力汉堡108G袋装-中国', '口力粒粒Q葡萄味60G袋装-中国',
                         '口力彩蝶虫48G袋装-中国', '口力扭扭虫48G袋装-中国', '口力午餐袋77G袋装-中国',
                         '口力酸小虫60G袋装-中国', '口力可乐瓶60G袋装-中国', '口力薯条1KG散装-中国',
                         '口力大眼仔爆浆软糖90G袋装-中国']
        product_prices = [126.72, 137.04, 182.4, 182.4, 182.4, 137.04, 182.4, 182.4, 174.0, 307.2]

        # 创建物料单价数据
        df_material_price = pd.DataFrame({
            '物料代码': material_codes,
            '单价（元）': material_prices
        })

        # 创建物料数据
        material_data = []
        for _ in range(500):  # 生成500条记录
            date = np.random.choice(date_range)
            month_str = date.strftime('%Y-%m')  # 格式化为2025-01格式
            region = np.random.choice(regions)
            province = np.random.choice(provinces)
            city = np.random.choice(cities)
            distributor_idx = np.random.randint(0, len(distributors))
            distributor = distributors[distributor_idx]
            customer_code = customer_codes[distributor_idx]
            material_idx = np.random.randint(0, len(material_codes))
            material_code = material_codes[material_idx]
            material_name = material_names[material_idx]
            material_quantity = np.random.randint(10, 1000)
            sales_person = np.random.choice(sales_persons)

            material_data.append({
                '发运月份': month_str,  # 使用字符串格式
                '客户代码': customer_code,
                '所属区域': region,
                '省份': province,
                '城市': city,
                '申请人': sales_person,
                '经销商名称': distributor,
                '物料代码': material_code,
                '物料名称': material_name,
                '物料数量': material_quantity
            })

        df_material = pd.DataFrame(material_data)

        # 创建销售数据
        sales_data = []
        for _ in range(600):  # 生成600条记录
            date = np.random.choice(date_range)
            month_str = date.strftime('%Y-%m')  # 格式化为2025-01格式
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
            product_quantity = np.random.randint(1, 100)
            sales_person = np.random.choice(sales_persons)

            sales_data.append({
                '发运月份': month_str,  # 使用字符串格式
                '客户代码': customer_code,
                '所属区域': region,
                '省份': province,
                '城市': city,
                '申请人': sales_person,
                '经销商名称': distributor,
                '产品代码': product_code,
                '产品名称': product_name,
                '求和项:数量（箱）': product_quantity,
                '求和项:单价（箱）': product_price
            })

        df_sales = pd.DataFrame(sales_data)

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

    # 安全地计算ROI，避免除以零
    customer_value['ROI'] = 0  # 默认值
    mask = customer_value['物料总成本'] > 0
    if mask.any():
        customer_value.loc[mask, 'ROI'] = customer_value.loc[mask, '销售总额'] / customer_value.loc[mask, '物料总成本']

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

                # 添加图表解读
                st.markdown("""
                **图表解读：**
                - 散点图展示了客户的投入(物料成本)与产出(销售额)关系。
                - 点的大小表示ROI(投资回报率)，越大表示回报率越高。
                - 点的颜色表示费比，颜色越浅表示物料使用效率越高。
                - 红色虚线是ROI=1的参考线，点位于此线上方表示有正向回报。
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
            # 简化的客户分群 - 使用排名而不是qcut，避免数据错误
            customer_value['价值排名'] = customer_value['客户价值'].rank(method='min')
            customer_value['效率排名'] = customer_value['物料效率'].rank(method='min')

            # 根据排名计算评分
            n_customers = len(customer_value)
            customer_value['价值得分'] = (customer_value['价值排名'] / n_customers * 4).apply(
                lambda x: min(max(int(x), 1), 4))
            customer_value['效率得分'] = (customer_value['效率排名'] / n_customers * 4).apply(
                lambda x: min(max(int(x), 1), 4))

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
                xaxis=dict(tickprefix="￥", tickformat=",.2f"),  # 修改为保留两位小数
                yaxis=dict(tickprefix="￥", tickformat=",.2f")  # 修改为保留两位小数
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 此矩阵根据客户价值和物料效率将客户分为四类：
              * 核心客户(绿色)：高价值且高效率，是最优质的客户群体
              * 高潜力客户(黄色)：高价值但效率较低，有提升空间
              * 高效率客户(蓝色)：价值较低但效率高，有成长潜力
              * 一般客户(灰色)：价值和效率均低，需评估合作价值
            - 点的大小表示销售总额，越大表示销售规模越大。
            - 灰色虚线表示客户价值和物料效率的中位数水平。
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

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - ROI表示每投入1元物料成本产生的销售额，是衡量物料投资回报的关键指标。
            - ROI越高表示物料的销售转化效果越好，投资回报越高。
            - TOP10中的物料是最具投资价值的物料类型，应优先考虑增加投放。
            - ROI低于1的物料意味着投入大于产出，需要审视其投放策略或调整目标客户。
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
                yaxis=dict(autorange="reversed"),
                xaxis=dict(tickformat=".2f")  # 修改为保留两位小数
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
            - 此图展示了投入产出比最高的物料-产品组合。
            - 投入产出比 = 销售总额/物料总成本，表示每单位物料成本带来的销售额。
            - 同一物料可能与不同产品组合时效果不同，不同颜色代表不同产品。
            - 图表越长表示投入产出比越高，此组合的物料投资回报越高。
            - 在促销活动设计中，建议优先选择这些高效组合进行推广。
            - 业务人员应学习这些高效组合的成功经验，复制到其他客户。
            """)
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
            # 替换表格为可视化图表
            top_combos = frequent_combos.nlargest(10, '平均投入产出比')

            # 创建组合效率条形图
            fig = px.bar(
                top_combos,
                x='平均投入产出比',
                y='物料组合',
                color='使用次数',
                color_continuous_scale='Viridis',
                title="高效物料组合TOP10",
                orientation='h',
                labels={
                    '平均投入产出比': '平均投入产出比',
                    '物料组合': '物料组合',
                    '使用次数': '使用次数'
                },
                hover_data=['物料总成本', '销售总额']
            )

            fig.update_layout(
                xaxis_title="平均投入产出比",
                yaxis_title="物料组合",
                yaxis=dict(autorange="reversed"),
                xaxis=dict(tickformat=".2f"),  # 修改为保留两位小数
                height=500
            )

            # 为悬停数据添加格式化
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>平均投入产出比: %{x:.2f}<br>使用次数: %{marker.color}<br>物料总成本: ￥%{customdata[0]:.2f}<br>销售总额: ￥%{customdata[1]:.2f}'
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图表解读
            st.markdown("""
            **图表解读：**
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
        else:
            st.warning("没有足够的物料组合数据来进行分析")


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
    avg_material_effectiveness = total_sales / filtered_material['物料数量'].sum() if filtered_material['物料数量'].sum() > 0 else 0

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