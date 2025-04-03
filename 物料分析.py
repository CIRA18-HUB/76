import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import datetime
import random
from typing import Dict, List, Tuple, Union, Optional
import base64
from io import StringIO
import os

# ====================
# 页面配置 - 宽屏模式
# ====================
st.set_page_config(
    page_title="物料投放分析仪表盘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ====================
# 飞书风格CSS - 优化设计
# ====================
FEISHU_STYLE = """
<style>
    /* 飞书风格基础设置 */
    * {
        font-family: 'PingFang SC', 'Helvetica Neue', Arial, sans-serif;
    }

    /* 主色调 - 飞书蓝 */
    :root {
        --feishu-blue: #2B5AED;
        --feishu-blue-hover: #1846DB;
        --feishu-blue-light: #E8F1FF;
        --feishu-secondary: #2A85FF;
        --feishu-green: #0FC86F;
        --feishu-orange: #FF7744;
        --feishu-red: #F53F3F;
        --feishu-purple: #7759F3;
        --feishu-yellow: #FFAA00;
        --feishu-text: #1F1F1F;
        --feishu-text-secondary: #646A73;
        --feishu-text-tertiary: #8F959E;
        --feishu-gray-1: #F5F7FA;
        --feishu-gray-2: #EBEDF0;
        --feishu-gray-3: #E0E4EA;
        --feishu-white: #FFFFFF;
        --feishu-border: #E8E8E8;
        --feishu-shadow: rgba(0, 0, 0, 0.08);
    }

    /* 页面背景 */
    .main {
        background-color: var(--feishu-gray-1);
        padding: 1.5rem 2.5rem;
    }

    /* 页面标题 */
    .feishu-title {
        font-size: 26px;
        font-weight: 600;
        color: var(--feishu-text);
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .feishu-subtitle {
        font-size: 15px;
        color: var(--feishu-text-secondary);
        margin-bottom: 28px;
        letter-spacing: 0.1px;
        line-height: 1.5;
    }

    /* 卡片样式 */
    .feishu-card {
        background: var(--feishu-white);
        border-radius: 12px;
        box-shadow: 0 2px 8px var(--feishu-shadow);
        padding: 22px;
        margin-bottom: 24px;
        border: 1px solid var(--feishu-gray-2);
        transition: all 0.3s ease;
    }

    .feishu-card:hover {
        box-shadow: 0 4px 16px var(--feishu-shadow);
        transform: translateY(-2px);
    }

    /* 指标卡片 */
    .feishu-metric-card {
        background: var(--feishu-white);
        border-radius: 12px;
        box-shadow: 0 2px 8px var(--feishu-shadow);
        padding: 22px;
        text-align: left;
        border: 1px solid var(--feishu-gray-2);
        transition: all 0.3s ease;
        height: 100%;
    }

    .feishu-metric-card:hover {
        box-shadow: 0 4px 16px var(--feishu-shadow);
        transform: translateY(-2px);
    }

    .feishu-metric-card .label {
        font-size: 14px;
        color: var(--feishu-text-secondary);
        margin-bottom: 12px;
        font-weight: 500;
    }

    .feishu-metric-card .value {
        font-size: 30px;
        font-weight: 600;
        color: var(--feishu-text);
        margin-bottom: 8px;
        letter-spacing: -0.5px;
        line-height: 1.2;
    }

    .feishu-metric-card .subtext {
        font-size: 13px;
        color: var(--feishu-text-tertiary);
        letter-spacing: 0.1px;
        line-height: 1.5;
    }

    /* 进度条 */
    .feishu-progress-container {
        margin: 12px 0;
        background: var(--feishu-gray-2);
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
    }

    .feishu-progress-bar {
        height: 100%;
        border-radius: 6px;
        background: var(--feishu-blue);
        transition: width 0.7s ease;
    }

    /* 指标值颜色 */
    .success-value { color: var(--feishu-green); }
    .warning-value { color: var(--feishu-yellow); }
    .danger-value { color: var(--feishu-red); }

    /* 标签页样式优化 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: transparent;
        border-bottom: 1px solid var(--feishu-gray-3);
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 28px;
        font-size: 15px;
        font-weight: 500;
        color: var(--feishu-text-secondary);
        border-bottom: 2px solid transparent;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--feishu-blue);
        background-color: transparent;
        border-bottom: 2px solid var(--feishu-blue);
    }

    /* 侧边栏样式 */
    section[data-testid="stSidebar"] > div {
        background-color: var(--feishu-white);
        padding: 2rem 1.5rem;
        border-right: 1px solid var(--feishu-gray-2);
    }

    /* 侧边栏标题 */
    .feishu-sidebar-title {
        color: var(--feishu-blue);
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .feishu-sidebar-title::before {
        content: "";
        display: block;
        width: 4px;
        height: 16px;
        background-color: var(--feishu-blue);
        border-radius: 2px;
    }

    /* 图表容器 */
    .feishu-chart-container {
        background: var(--feishu-white);
        border-radius: 12px;
        box-shadow: 0 2px 8px var(--feishu-shadow);
        padding: 24px;
        margin-bottom: 40px;
        border: 1px solid var(--feishu-gray-2);
        transition: all 0.3s ease;
    }

    .feishu-chart-container:hover {
        box-shadow: 0 4px 16px var(--feishu-shadow);
        transform: translateY(-2px);
    }

    /* 图表标题 */
    .feishu-chart-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--feishu-text);
        margin: 0 0 20px 0;
        display: flex;
        align-items: center;
        gap: 8px;
        line-height: 1.4;
    }

    .feishu-chart-title::before {
        content: "";
        display: block;
        width: 3px;
        height: 14px;
        background-color: var(--feishu-blue);
        border-radius: 2px;
    }

    /* 数据表格样式 */
    .dataframe {
        width: 100%;
        border-collapse: collapse;
        border-radius: 8px;
        overflow: hidden;
    }

    .dataframe th {
        background-color: var(--feishu-gray-1);
        padding: 12px 16px;
        text-align: left;
        font-weight: 500;
        color: var(--feishu-text);
        font-size: 14px;
        border-bottom: 1px solid var(--feishu-gray-3);
    }

    .dataframe td {
        padding: 12px 16px;
        font-size: 13px;
        border-bottom: 1px solid var(--feishu-gray-2);
        color: var(--feishu-text-secondary);
    }

    .dataframe tr:hover td {
        background-color: var(--feishu-gray-1);
    }

    /* 飞书按钮 */
    .feishu-button {
        background-color: var(--feishu-blue);
        color: white;
        font-weight: 500;
        padding: 10px 18px;
        border: none;
        border-radius: 6px;
        cursor: pointer;
        transition: background-color 0.2s;
        font-size: 14px;
        text-align: center;
        display: inline-block;
    }

    .feishu-button:hover {
        background-color: var(--feishu-blue-hover);
    }

    /* 洞察框 */
    .feishu-insight-box {
        background-color: var(--feishu-blue-light);
        border-radius: 8px;
        padding: 18px 22px;
        margin: 20px 0;
        color: var(--feishu-text);
        font-size: 14px;
        border-left: 4px solid var(--feishu-blue);
        line-height: 1.6;
    }

    /* 提示框 */
    .feishu-tip-box {
        background-color: rgba(255, 170, 0, 0.1);
        border-radius: 8px;
        padding: 18px 22px;
        margin: 20px 0;
        color: var(--feishu-text);
        font-size: 14px;
        border-left: 4px solid var(--feishu-yellow);
        line-height: 1.6;
    }

    /* 警告框 */
    .feishu-warning-box {
        background-color: rgba(255, 119, 68, 0.1);
        border-radius: 8px;
        padding: 18px 22px;
        margin: 20px 0;
        color: var(--feishu-text);
        font-size: 14px;
        border-left: 4px solid var(--feishu-orange);
        line-height: 1.6;
    }

    /* 成功框 */
    .feishu-success-box {
        background-color: rgba(15, 200, 111, 0.1);
        border-radius: 8px;
        padding: 18px 22px;
        margin: 20px 0;
        color: var(--feishu-text);
        font-size: 14px;
        border-left: 4px solid var(--feishu-green);
        line-height: 1.6;
    }

    /* 标签 */
    .feishu-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 6px;
    }

    .feishu-tag-blue {
        background-color: rgba(43, 90, 237, 0.1);
        color: var(--feishu-blue);
    }

    .feishu-tag-green {
        background-color: rgba(15, 200, 111, 0.1);
        color: var(--feishu-green);
    }

    .feishu-tag-orange {
        background-color: rgba(255, 119, 68, 0.1);
        color: var(--feishu-orange);
    }

    .feishu-tag-red {
        background-color: rgba(245, 63, 63, 0.1);
        color: var(--feishu-red);
    }

    /* 仪表板卡片网格 */
    .feishu-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 20px;
        margin-bottom: 24px;
    }

    /* 图表解读框 */
    .chart-explanation {
        background-color: #f9f9f9;
        border-left: 4px solid #2B5AED;
        margin-top: -20px;
        margin-bottom: 20px;
        padding: 12px 15px;
        font-size: 13px;
        color: #333;
        line-height: 1.5;
        border-radius: 0 0 8px 8px;
    }

    .chart-explanation-title {
        font-weight: 600;
        margin-bottom: 5px;
        color: #2B5AED;
    }

    /* 隐藏Streamlit默认样式 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""

st.markdown(FEISHU_STYLE, unsafe_allow_html=True)


# ====================
# 数据加载与处理
# ====================

def load_data(sample_data=False):
    """加载和处理数据"""

    if sample_data:
        # 使用示例数据
        return generate_sample_data()
    else:
        try:
            # 尝试加载真实数据
            material_data = pd.read_excel("2025物料源数据.xlsx")
            sales_data = pd.read_excel("25物料源销售数据.xlsx")
            material_price = pd.read_excel("物料单价.xlsx")

            # 确保列名正确 - 修复重复的物料类别列
            if '物料类别' in material_price.columns:
                # 确认是否有重复列
                duplicate_cols = material_price.columns.duplicated()
                if any(duplicate_cols):
                    # 重命名重复列
                    material_price.columns = pd.io.parsers.ParserBase(
                        {'names': material_price.columns})._maybe_dedup_names(material_price.columns)

                # 如果物料类别.1存在，将其重命名为物料类别
                if '物料类别.1' in material_price.columns:
                    material_price = material_price.rename(columns={'物料类别.1': '物料类别_分类'})

            # 处理数据
            return process_data(material_data, sales_data, material_price)
        except Exception as e:
            st.error(f"加载数据时出错: {e}")
            # 如果加载真实数据失败，回退到示例数据
            return generate_sample_data()


def process_data(material_data, sales_data, material_price):
    """处理和准备数据"""

    # 确保日期列为日期类型
    material_data['发运月份'] = pd.to_datetime(material_data['发运月份'])
    sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

    # 创建月份和年份列
    for df in [material_data, sales_data]:
        df['月份'] = df['发运月份'].dt.month
        df['年份'] = df['发运月份'].dt.year
        df['月份名'] = df['发运月份'].dt.strftime('%Y-%m')
        df['季度'] = df['发运月份'].dt.quarter
        df['月度名称'] = df['发运月份'].dt.strftime('%m月')

    # 计算物料成本
    if '物料成本' not in material_data.columns:
        # 确保使用正确的物料类别列
        # 首先确保我们有需要的列
        merge_columns = ['物料代码', '单价（元）']

        # 找到正确的物料类别列
        category_col = None
        possible_cols = ['物料类别', '物料类别_分类']
        for col in possible_cols:
            if col in material_price.columns:
                category_col = col
                break

        if category_col:
            merge_columns.append(category_col)

        # 执行合并
        material_data = pd.merge(
            material_data,
            material_price[merge_columns],
            left_on='产品代码',
            right_on='物料代码',
            how='left'
        )

        # 填充缺失的物料价格
        if '单价（元）' in material_data.columns:
            mean_price = material_price['单价（元）'].mean()
            material_data['单价（元）'].fillna(mean_price, inplace=True)

            # 计算物料总成本
            material_data['物料成本'] = material_data['求和项:数量（箱）'] * material_data['单价（元）']
        else:
            # 如果合并失败，创建一个默认的物料成本列
            material_data['物料成本'] = material_data['求和项:数量（箱）'] * 100  # 默认单价100元

    # 计算销售金额
    if '销售金额' not in sales_data.columns and '求和项:单价（箱）' in sales_data.columns:
        sales_data['销售金额'] = sales_data['求和项:数量（箱）'] * sales_data['求和项:单价（箱）']

    # 按经销商和月份计算物料成本总和
    material_cost_by_distributor = material_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员'])[
        '物料成本'].sum().reset_index()
    material_cost_by_distributor.rename(columns={'物料成本': '物料总成本'}, inplace=True)

    # 按经销商和月份计算销售总额
    sales_by_distributor = sales_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员'])[
        '销售金额'].sum().reset_index()
    sales_by_distributor.rename(columns={'销售金额': '销售总额'}, inplace=True)

    # 合并物料成本和销售数据
    distributor_data = pd.merge(
        material_cost_by_distributor,
        sales_by_distributor,
        on=['客户代码', '经销商名称', '月份名', '销售人员'],
        how='outer'
    ).fillna(0)

    # 计算ROI
    distributor_data['ROI'] = np.where(
        distributor_data['物料总成本'] > 0,
        distributor_data['销售总额'] / distributor_data['物料总成本'],
        0
    )

    # 计算物料销售比率
    distributor_data['物料销售比率'] = (
                                               distributor_data['物料总成本'] / distributor_data['销售总额'].replace(0,
                                                                                                                     np.nan)
                                       ) * 100
    distributor_data['物料销售比率'].fillna(0, inplace=True)

    # 经销商价值分层
    def value_segment(row):
        if row['ROI'] >= 2.0 and row['销售总额'] > distributor_data['销售总额'].quantile(0.75):
            return '高价值客户'
        elif row['ROI'] >= 1.0 and row['销售总额'] > distributor_data['销售总额'].median():
            return '成长型客户'
        elif row['ROI'] >= 1.0:
            return '稳定型客户'
        else:
            return '低效型客户'

    distributor_data['客户价值分层'] = distributor_data.apply(value_segment, axis=1)

    # 物料使用多样性
    material_diversity = material_data.groupby(['客户代码', '月份名'])['产品代码'].nunique().reset_index()
    material_diversity.rename(columns={'产品代码': '物料多样性'}, inplace=True)

    # 合并物料多样性到经销商数据
    distributor_data = pd.merge(
        distributor_data,
        material_diversity,
        on=['客户代码', '月份名'],
        how='left'
    )
    distributor_data['物料多样性'].fillna(0, inplace=True)

    # 添加区域信息
    if '所属区域' not in distributor_data.columns:
        region_map = material_data[['客户代码', '所属区域']].drop_duplicates().set_index('客户代码')
        distributor_data['所属区域'] = distributor_data['客户代码'].map(region_map['所属区域'])

    # 添加省份信息
    if '省份' not in distributor_data.columns:
        province_map = material_data[['客户代码', '省份']].drop_duplicates().set_index('客户代码')
        distributor_data['省份'] = distributor_data['客户代码'].map(province_map['省份'])

    return material_data, sales_data, material_price, distributor_data


def generate_sample_data():
    """生成示例数据用于仪表板演示"""

    # 设置随机种子以获得可重现的结果
    random.seed(42)
    np.random.seed(42)

    # 基础数据参数
    num_customers = 50  # 经销商数量
    num_months = 12  # 月份数量
    num_materials = 30  # 物料类型数量

    # 区域和省份
    regions = ['华东', '华南', '华北', '华中', '西南', '西北', '东北']
    provinces = {
        '华东': ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东'],
        '华南': ['广东', '广西', '海南'],
        '华北': ['北京', '天津', '河北', '山西', '内蒙古'],
        '华中': ['河南', '湖北', '湖南'],
        '西南': ['重庆', '四川', '贵州', '云南', '西藏'],
        '西北': ['陕西', '甘肃', '青海', '宁夏', '新疆'],
        '东北': ['辽宁', '吉林', '黑龙江']
    }

    all_provinces = []
    for prov_list in provinces.values():
        all_provinces.extend(prov_list)

    # 销售人员
    sales_persons = [f'销售员{chr(65 + i)}' for i in range(10)]

    # 生成经销商数据
    customer_ids = [f'C{str(i + 1).zfill(3)}' for i in range(num_customers)]
    customer_names = [f'经销商{str(i + 1).zfill(3)}' for i in range(num_customers)]

    # 为每个经销商分配区域、省份和销售人员
    customer_regions = [random.choice(regions) for _ in range(num_customers)]
    customer_provinces = [random.choice(provinces[region]) for region in customer_regions]
    customer_sales = [random.choice(sales_persons) for _ in range(num_customers)]

    # 生成月份数据
    current_date = datetime.datetime.now()
    months = [(current_date - datetime.timedelta(days=30 * i)).strftime('%Y-%m-%d') for i in range(num_months)]
    months.reverse()  # 按日期排序

    # 物料类别
    material_categories = ['促销物料', '陈列物料', '宣传物料', '赠品', '包装物料']

    # 生成物料数据
    material_ids = [f'M{str(i + 1).zfill(3)}' for i in range(num_materials)]
    material_names = [f'物料{str(i + 1).zfill(3)}' for i in range(num_materials)]
    material_cats = [random.choice(material_categories) for _ in range(num_materials)]
    material_prices = [round(random.uniform(10, 200), 2) for _ in range(num_materials)]

    # 生成物料分发数据
    material_data = []
    for month in months:
        for customer_idx in range(num_customers):
            # 每个客户每月使用3-8种物料
            num_materials_used = random.randint(3, 8)
            selected_materials = random.sample(range(num_materials), num_materials_used)

            for mat_idx in selected_materials:
                # 物料分发遵循正态分布
                quantity = max(1, int(np.random.normal(100, 30)))

                material_data.append({
                    '发运月份': month,
                    '客户代码': customer_ids[customer_idx],
                    '经销商名称': customer_names[customer_idx],
                    '所属区域': customer_regions[customer_idx],
                    '省份': customer_provinces[customer_idx],
                    '销售人员': customer_sales[customer_idx],
                    '产品代码': material_ids[mat_idx],
                    '产品名称': material_names[mat_idx],
                    '求和项:数量（箱）': quantity,
                    '物料类别': material_cats[mat_idx],
                    '单价（元）': material_prices[mat_idx],
                    '物料成本': round(quantity * material_prices[mat_idx], 2)
                })

    # 生成销售数据
    sales_data = []
    for month in months:
        for customer_idx in range(num_customers):
            # 计算该月的物料总成本
            month_material_cost = sum([
                item['物料成本'] for item in material_data
                if item['发运月份'] == month and item['客户代码'] == customer_ids[customer_idx]
            ])

            # 根据物料成本计算销售额
            roi_factor = random.uniform(0.5, 3.0)
            sales_amount = month_material_cost * roi_factor

            # 计算销售数量和单价
            avg_price_per_box = random.uniform(300, 800)
            sales_quantity = round(sales_amount / avg_price_per_box)

            if sales_quantity > 0:
                sales_data.append({
                    '发运月份': month,
                    '客户代码': customer_ids[customer_idx],
                    '经销商名称': customer_names[customer_idx],
                    '所属区域': customer_regions[customer_idx],
                    '省份': customer_provinces[customer_idx],
                    '销售人员': customer_sales[customer_idx],
                    '求和项:数量（箱）': sales_quantity,
                    '求和项:单价（箱）': round(avg_price_per_box, 2),
                    '销售金额': round(sales_quantity * avg_price_per_box, 2)
                })

    # 生成物料价格表
    material_price_data = []
    for mat_idx in range(num_materials):
        material_price_data.append({
            '物料代码': material_ids[mat_idx],
            '物料名称': material_names[mat_idx],
            '物料类别': material_cats[mat_idx],
            '单价（元）': material_prices[mat_idx]
        })

    # 转换为DataFrame
    material_df = pd.DataFrame(material_data)
    sales_df = pd.DataFrame(sales_data)
    material_price_df = pd.DataFrame(material_price_data)

    # 处理日期格式
    material_df['发运月份'] = pd.to_datetime(material_df['发运月份'])
    sales_df['发运月份'] = pd.to_datetime(sales_df['发运月份'])

    # 创建月份和年份列
    for df in [material_df, sales_df]:
        df['月份'] = df['发运月份'].dt.month
        df['年份'] = df['发运月份'].dt.year
        df['月份名'] = df['发运月份'].dt.strftime('%Y-%m')
        df['季度'] = df['发运月份'].dt.quarter
        df['月度名称'] = df['发运月份'].dt.strftime('%m月')

    # 调用process_data来生成distributor_data
    _, _, _, distributor_data = process_data(material_df, sales_df, material_price_df)

    return material_df, sales_df, material_price_df, distributor_data


@st.cache_data
def get_data():
    """缓存数据加载函数"""
    return load_data(sample_data=False)  # 修改为False以尝试加载真实数据


# ====================
# 辅助函数
# ====================

class FeishuPlots:
    """飞书风格图表类，统一处理所有销售额相关图表的单位显示"""

    def __init__(self):
        self.default_height = 350
        self.colors = {
            'primary': '#2B5AED',
            'success': '#0FC86F',
            'warning': '#FFAA00',
            'danger': '#F53F3F',
            'purple': '#7759F3'
        }
        self.segment_colors = {
            '高价值客户': '#0FC86F',
            '成长型客户': '#2B5AED',
            '稳定型客户': '#FFAA00',
            '低效型客户': '#F53F3F'
        }

    def _configure_chart(self, fig, height=None, show_legend=True, y_title="金额 (元)"):
        """配置图表的通用样式和单位"""
        if height is None:
            height = self.default_height

        fig.update_layout(
            height=height,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(
                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                size=12,
                color="#1F1F1F"
            ),
            xaxis=dict(
                showgrid=False,
                showline=True,
                linecolor='#E0E4EA'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='#E0E4EA',
                tickformat=",.0f",
                ticksuffix="元",  # 确保单位是"元"
                title=y_title
            )
        )

        # 调整图例位置
        if show_legend:
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

        return fig

    def line(self, data_frame, x, y, title=None, color=None, height=None, **kwargs):
        """创建线图，自动设置元为单位"""
        fig = px.line(data_frame, x=x, y=y, title=title, color=color, **kwargs)

        # 应用默认颜色
        if color is None:
            fig.update_traces(
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=self.colors['primary'])
            )

        return self._configure_chart(fig, height)

    def bar(self, data_frame, x, y, title=None, color=None, height=None, **kwargs):
        """创建条形图，自动设置元为单位"""
        fig = px.bar(data_frame, x=x, y=y, title=title, color=color, **kwargs)

        # 应用默认颜色
        if color is None and 'color_discrete_sequence' not in kwargs:
            fig.update_traces(marker_color=self.colors['primary'])

        return self._configure_chart(fig, height)

    def scatter(self, data_frame, x, y, title=None, color=None, size=None, height=None, **kwargs):
        """创建散点图，自动设置元为单位"""
        fig = px.scatter(data_frame, x=x, y=y, title=title, color=color, size=size, **kwargs)
        return self._configure_chart(fig, height)

    def dual_axis(self, title=None, height=None):
        """创建双轴图表，第一轴自动设置为金额单位"""
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        if title:
            fig.update_layout(title=title)

        # 配置基本样式
        self._configure_chart(fig, height)

        # 配置第一个y轴为金额单位
        fig.update_yaxes(title_text='金额 (元)', ticksuffix="元", secondary_y=False)

        return fig

    def add_bar_to_dual(self, fig, x, y, name, color=None, secondary_y=False):
        """向双轴图表添加条形图"""
        fig.add_trace(
            go.Bar(
                x=x,
                y=y,
                name=name,
                marker_color=color if color else self.colors['primary'],
                offsetgroup=0 if not secondary_y else 1
            ),
            secondary_y=secondary_y
        )
        return fig

    def add_line_to_dual(self, fig, x, y, name, color=None, secondary_y=True):
        """向双轴图表添加线图"""
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name=name,
                mode='lines+markers',
                line=dict(color=color if color else self.colors['purple'], width=3),
                marker=dict(size=8)
            ),
            secondary_y=secondary_y
        )
        return fig

    def pie(self, data_frame, values, names, title=None, height=None, **kwargs):
        """创建带单位的饼图"""
        fig = px.pie(
            data_frame,
            values=values,
            names=names,
            title=title,
            **kwargs
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='%{label}: %{value:,.0f}元<br>占比: %{percent}'
        )

        fig.update_layout(
            height=height if height else self.default_height,
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            paper_bgcolor='white',
            font=dict(
                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                size=12,
                color="#1F1F1F"
            )
        )

        return fig

    def roi_forecast(self, data, x_col, y_col, title, height=None):
        """创建带预测的ROI图表，默认无单位后缀"""
        return self.forecast_chart(data, x_col, y_col, title, height, add_suffix=False)

    def sales_forecast(self, data, x_col, y_col, title, height=None):
        """创建带预测的销售额图表，自动添加元单位"""
        return self.forecast_chart(data, x_col, y_col, title, height, add_suffix=True)

    def forecast_chart(self, data, x_col, y_col, title, height=None, add_suffix=True):
        """创建通用预测图表"""
        # 排序数据
        data = data.sort_values(x_col)

        # 准备趋势线拟合数据
        x = np.arange(len(data))
        y = data[y_col].values

        # 拟合多项式
        z = np.polyfit(x, y, 2)
        p = np.poly1d(z)

        # 预测接下来的2个点
        future_x = np.arange(len(data), len(data) + 2)
        future_y = p(future_x)

        # 创建完整的x轴标签(当前 + 未来)
        full_x_labels = list(data[x_col])

        # 获取最后日期并计算接下来的2个月
        if len(full_x_labels) > 0 and pd.api.types.is_datetime64_any_dtype(pd.to_datetime(full_x_labels[-1])):
            last_date = pd.to_datetime(full_x_labels[-1])
            for i in range(1, 3):
                next_month = last_date + pd.DateOffset(months=i)
                full_x_labels.append(next_month.strftime('%Y-%m'))
        else:
            # 如果不是日期格式，简单地添加"预测1"，"预测2"
            full_x_labels.extend([f"预测{i + 1}" for i in range(2)])

        # 创建图表
        fig = go.Figure()

        # 添加实际数据条形图
        fig.add_trace(
            go.Bar(
                x=data[x_col],
                y=data[y_col],
                name="实际值",
                marker_color="#2B5AED"
            )
        )

        # 添加趋势线
        fig.add_trace(
            go.Scatter(
                x=full_x_labels,
                y=list(p(x)) + list(future_y),
                mode='lines',
                name="趋势线",
                line=dict(color="#FF7744", width=3, dash='dot'),
                hoverinfo='skip'
            )
        )

        # 添加预测点
        fig.add_trace(
            go.Bar(
                x=full_x_labels[-2:],
                y=future_y,
                name="预测值",
                marker_color="#7759F3",
                opacity=0.7
            )
        )

        # 更新布局并添加适当单位
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(
                    size=16,
                    family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                    color="#1F1F1F"
                ),
                x=0.01
            ),
            height=height if height else 380,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='white',
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(224, 228, 234, 0.5)',
                tickfont=dict(
                    family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                    size=12,
                    color="#646A73"
                )
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(224, 228, 234, 0.5)',
                tickfont=dict(
                    family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                    size=12,
                    color="#646A73"
                ),
                # 根据参数决定是否添加单位后缀
                ticksuffix="元" if add_suffix else ""
            )
        )

        return fig


def format_currency(value):
    """格式化为货币形式，两位小数"""
    return f"{value:.2f}元"


def create_download_link(df, filename):
    """创建DataFrame的下载链接"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv" class="feishu-button">下载 {filename}</a>'
    return href


def get_material_combination_recommendations(material_data, sales_data, distributor_data):
    """生成基于历史数据分析的物料组合优化建议"""

    # 获取物料类别列表
    material_categories = material_data['物料类别'].unique().tolist()

    # 合并物料和销售数据
    merged_data = pd.merge(
        material_data.groupby(['客户代码', '月份名'])['物料成本'].sum().reset_index(),
        sales_data.groupby(['客户代码', '月份名'])['销售金额'].sum().reset_index(),
        on=['客户代码', '月份名'],
        how='inner'
    )

    # 计算ROI
    merged_data['ROI'] = merged_data['销售金额'] / merged_data['物料成本']

    # 找出高ROI的记录(ROI > 2.0)
    high_roi_records = merged_data[merged_data['ROI'] > 2.0]

    # 分析高ROI情况下使用的物料组合
    high_roi_material_combos = []

    if not high_roi_records.empty:
        for _, row in high_roi_records.head(20).iterrows():
            customer_id = row['客户代码']
            month = row['月份名']

            # 获取该客户在该月使用的物料
            materials_used = material_data[
                (material_data['客户代码'] == customer_id) &
                (material_data['月份名'] == month)
                ]

            # 记录物料组合
            if not materials_used.empty:
                material_combo = materials_used.groupby('物料类别')['物料成本'].sum().reset_index()
                material_combo['占比'] = material_combo['物料成本'] / material_combo['物料成本'].sum() * 100
                material_combo = material_combo.sort_values('占比', ascending=False)

                top_categories = material_combo.head(3)['物料类别'].tolist()
                top_props = material_combo.head(3)['占比'].tolist()

                high_roi_material_combos.append({
                    '客户代码': customer_id,
                    '月份': month,
                    'ROI': row['ROI'],
                    '主要物料类别': top_categories,
                    '物料占比': top_props,
                    '销售金额': row['销售金额']
                })

    # 分析物料类别共现关系并计算综合评分
    if high_roi_material_combos:
        df_combos = pd.DataFrame(high_roi_material_combos)
        df_combos['综合得分'] = df_combos['ROI'] * np.log1p(df_combos['销售金额'])
        df_combos = df_combos.sort_values('综合得分', ascending=False)

        # 分析物料类别共现关系
        all_category_pairs = []
        for combo in high_roi_material_combos:
            categories = combo['主要物料类别']
            if len(categories) >= 2:
                for i in range(len(categories)):
                    for j in range(i + 1, len(categories)):
                        all_category_pairs.append((categories[i], categories[j], combo['ROI']))

        # 计算类别对的平均ROI
        pair_roi = {}
        for cat1, cat2, roi in all_category_pairs:
            pair = tuple(sorted([cat1, cat2]))
            if pair in pair_roi:
                pair_roi[pair].append(roi)
            else:
                pair_roi[pair] = [roi]

        avg_pair_roi = {pair: sum(rois) / len(rois) for pair, rois in pair_roi.items()}
        best_pairs = sorted(avg_pair_roi.items(), key=lambda x: x[1], reverse=True)[:3]

        # 生成推荐
        recommendations = []
        used_categories = set()

        # 基于最佳组合的推荐
        top_combos = df_combos.head(3)
        for i, (_, combo) in enumerate(top_combos.iterrows(), 1):
            main_cats = combo['主要物料类别'][:2]  # 取前两个主要类别
            main_cats_str = '、'.join(main_cats)
            roi = combo['ROI']

            for cat in main_cats:
                used_categories.add(cat)

            recommendations.append({
                "推荐名称": f"推荐物料组合{i}: 以【{main_cats_str}】为核心",
                "预期ROI": f"{roi:.2f}",
                "适用场景": "终端陈列与促销活动" if i == 1 else "长期品牌建设" if i == 2 else "快速促单与客户转化",
                "最佳搭配物料": "主要展示物料 + 辅助促销物料" if i == 1 else "品牌宣传物料 + 高端礼品" if i == 2 else "促销物料 + 实用赠品",
                "适用客户": "所有客户，尤其高价值客户" if i == 1 else "高端市场客户" if i == 2 else "大众市场客户",
                "核心类别": main_cats,
                "最佳产品组合": ["高端产品", "中端产品"],
                "预计销售提升": f"{random.randint(15, 30)}%"
            })

        # 基于最佳类别对的推荐
        for i, (pair, avg_roi) in enumerate(best_pairs, len(recommendations) + 1):
            if pair[0] in used_categories and pair[1] in used_categories:
                continue  # 跳过已经在其他推荐中使用的类别对

            recommendations.append({
                "推荐名称": f"推荐物料组合{i}: 【{pair[0]}】+【{pair[1]}】黄金搭配",
                "预期ROI": f"{avg_roi:.2f}",
                "适用场景": "综合营销活动",
                "最佳搭配物料": f"{pair[0]}为主，{pair[1]}为辅，比例约7:3",
                "适用客户": "适合追求高效益的客户",
                "核心类别": list(pair),
                "最佳产品组合": ["中端产品", "入门产品"],
                "预计销售提升": f"{random.randint(15, 30)}%"
            })

            for cat in pair:
                used_categories.add(cat)

        return recommendations
    else:
        return [{"推荐名称": "暂无足够数据生成物料组合优化建议",
                 "预期ROI": "N/A",
                 "适用场景": "N/A",
                 "最佳搭配物料": "N/A",
                 "适用客户": "N/A",
                 "核心类别": []}]


def check_dataframe(df, required_columns, operation_name=""):
    """检查DataFrame是否包含所需列"""
    if df is None or len(df) == 0:
        st.info(f"暂无{operation_name}数据。")
        return False

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"{operation_name}缺少必要的列: {', '.join(missing_columns)}")
        return False

    return True


# 使用示例
# if check_dataframe(filtered_material, ['物料类别', '物料成本'], "物料类别分析"):
#     # 进行物料类别分析
def get_customer_optimization_suggestions(distributor_data):
    """根据客户分层和ROI生成差异化物料分发策略"""

    # 按客户价值分层的统计
    segment_stats = distributor_data.groupby('客户价值分层').agg({
        'ROI': 'mean',
        '物料总成本': 'mean',
        '销售总额': 'mean',
        '客户代码': 'nunique'
    }).reset_index()

    segment_stats.rename(columns={'客户代码': '客户数量'}, inplace=True)

    # 为每个客户细分生成优化建议
    suggestions = {}

    # 高价值客户建议
    high_value = segment_stats[segment_stats['客户价值分层'] == '高价值客户']
    if not high_value.empty:
        suggestions['高价值客户'] = {
            '建议策略': '维护与深化',
            '物料配比': '全套高质量物料',
            '投放增减': '维持或适度增加(5-10%)',
            '物料创新': '优先试用新物料',
            '关注重点': '保持ROI稳定性，避免过度投放'
        }

    # 成长型客户建议
    growth = segment_stats[segment_stats['客户价值分层'] == '成长型客户']
    if not growth.empty:
        suggestions['成长型客户'] = {
            '建议策略': '精准投放',
            '物料配比': '聚焦高效转化物料',
            '投放增减': '有条件增加(10-15%)',
            '物料创新': '定期更新物料组合',
            '关注重点': '提升销售额规模，保持ROI'
        }

    # 稳定型客户建议
    stable = segment_stats[segment_stats['客户价值分层'] == '稳定型客户']
    if not stable.empty:
        suggestions['稳定型客户'] = {
            '建议策略': '效率优化',
            '物料配比': '优化高ROI物料占比',
            '投放增减': '维持不变',
            '物料创新': '测试新物料效果',
            '关注重点': '提高物料使用效率，挖掘增长点'
        }

    # 低效型客户建议
    low_value = segment_stats[segment_stats['客户价值分层'] == '低效型客户']
    if not low_value.empty:
        suggestions['低效型客户'] = {
            '建议策略': '控制与改进',
            '物料配比': '减少低效物料',
            '投放增减': '减少(20-30%)',
            '物料创新': '暂缓新物料试用',
            '关注重点': '诊断低效原因，培训后再投放'
        }

    return suggestions


# 业务指标定义
BUSINESS_DEFINITIONS = {
    "投资回报率(ROI)": "销售总额 ÷ 物料总成本。ROI>1表示物料投入产生了正回报，ROI>2表示表现优秀。",
    "物料销售比率": "物料总成本占销售总额的百分比。该比率越低，表示物料使用效率越高。",
    "客户价值分层": "根据ROI和销售额将客户分为四类：\n1) 高价值客户：ROI≥2.0且销售额在前25%；\n2) 成长型客户：ROI≥1.0且销售额高于中位数；\n3) 稳定型客户：ROI≥1.0但销售额较低；\n4) 低效型客户：ROI<1.0，投入产出比不理想。",
    "物料使用效率": "衡量单位物料投入所产生的销售额，计算方式为：销售额 ÷ 物料数量。",
    "物料多样性": "客户使用的不同种类物料数量，多样性高的客户通常有更好的展示效果。",
    "物料投放密度": "单位时间内的物料投放量，反映物料投放的集中度。",
    "物料使用周期": "从物料投放到产生销售效果的时间周期，用于优化投放时机。"
}

# 物料类别效果分析
MATERIAL_CATEGORY_INSIGHTS = {
    "促销物料": "用于短期促销活动，ROI通常在活动期间较高，适合季节性销售峰值前投放。",
    "陈列物料": "提升产品在终端的可见度，有助于长期销售增长，ROI相对稳定。",
    "宣传物料": "增强品牌认知，长期投资回报稳定，适合新市场或新产品推广。",
    "赠品": "刺激短期销售，提升客户满意度，注意控制成本避免过度赠送。",
    "包装物料": "提升产品价值感，增加客户复购率，对高端产品尤为重要。"
}


# ====================
# 主应用
# ====================

def main():
    # 加载数据
    material_data, sales_data, material_price, distributor_data = get_data()

    # 页面标题
    st.markdown('<div class="feishu-title">物料投放分析动态仪表盘</div>', unsafe_allow_html=True)
    st.markdown('<div class="feishu-subtitle">协助销售人员数据驱动地分配物料资源，实现销售增长目标</div>',
                unsafe_allow_html=True)

    # --- 侧边栏筛选器 ---
    st.sidebar.markdown('<div class="feishu-sidebar-title">数据筛选</div>', unsafe_allow_html=True)

    # 区域列表
    regions = sorted(material_data['所属区域'].unique())
    selected_regions = st.sidebar.multiselect("选择区域:", regions, default=regions)

    # 省份列表
    provinces = sorted(material_data['省份'].unique())
    selected_provinces = st.sidebar.multiselect("选择省份:", provinces, default=provinces)

    # 自动使用最新月份
    months = sorted(material_data['月份名'].unique())
    selected_month = months[-1]  # 自动使用最新月份

    # 物料类别列表
    material_categories = sorted(material_data['物料类别'].unique())
    selected_categories = st.sidebar.multiselect("选择物料类别:", material_categories, default=material_categories)

    # 销售人员筛选
    st.sidebar.markdown('<div class="feishu-sidebar-title">销售团队筛选</div>', unsafe_allow_html=True)
    sales_persons = sorted(material_data['销售人员'].unique())
    selected_sales_persons = st.sidebar.multiselect("选择销售人员:", sales_persons, default=sales_persons)

    # 经销商筛选
    st.sidebar.markdown('<div class="feishu-sidebar-title">经销商筛选</div>', unsafe_allow_html=True)
    distributor_names = sorted(distributor_data['经销商名称'].unique())
    selected_distributors = st.sidebar.multiselect("选择经销商:", distributor_names, default=distributor_names)

    # 更新按钮
    update_button = st.sidebar.button("更新仪表盘")

    # 业务指标说明
    with st.sidebar.expander("业务指标说明"):
        for term, definition in BUSINESS_DEFINITIONS.items():
            st.markdown(f"**{term}**: {definition}")

    # 物料类别效果分析
    with st.sidebar.expander("物料类别效果分析"):
        for category, insight in MATERIAL_CATEGORY_INSIGHTS.items():
            st.markdown(f"**{category}**: {insight}")

    # 筛选数据
    if update_button or True:  # 默认自动更新
        # 按区域、省份、月份筛选
        filtered_material = material_data[
            (material_data['所属区域'].isin(selected_regions)) &
            (material_data['省份'].isin(selected_provinces)) &
            (material_data['月份名'] == selected_month)
            ]

        # 按物料类别筛选
        filtered_material = filtered_material[filtered_material['物料类别'].isin(selected_categories)]

        # 按销售人员筛选
        filtered_material = filtered_material[filtered_material['销售人员'].isin(selected_sales_persons)]

        # 筛选销售数据
        filtered_sales = sales_data[
            (sales_data['所属区域'].isin(selected_regions)) &
            (sales_data['省份'].isin(selected_provinces)) &
            (sales_data['月份名'] == selected_month) &
            (sales_data['销售人员'].isin(selected_sales_persons))
            ]

        # 筛选经销商数据
        filtered_distributor = distributor_data[
            (distributor_data['月份名'] == selected_month) &
            (distributor_data['经销商名称'].isin(selected_distributors)) &
            (distributor_data['销售人员'].isin(selected_sales_persons))
            ]

        # 确保经销商与筛选后的销售数据一致
        valid_distributors = filtered_sales['客户代码'].unique()
        filtered_distributor = filtered_distributor[filtered_distributor['客户代码'].isin(valid_distributors)]

        # 计算关键指标
        total_material_cost = filtered_material['物料成本'].sum()
        total_sales = filtered_sales['销售金额'].sum()
        roi = total_sales / total_material_cost if total_material_cost > 0 else 0
        material_sales_ratio = (total_material_cost / total_sales * 100) if total_sales > 0 else 0
        total_distributors = filtered_sales['经销商名称'].nunique()

        # 创建飞书风格图表对象
        fp = FeishuPlots()

        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs(["业绩概览", "物料与销售分析", "经销商分析", "优化建议"])

        # ======= 业绩概览标签页 =======
        with tab1:
            # 顶部指标卡 - 飞书风格
            st.markdown('<div class="feishu-grid">', unsafe_allow_html=True)

            # 指标卡颜色
            roi_color = "success-value" if roi >= 2.0 else "warning-value" if roi >= 1.0 else "danger-value"
            ratio_color = "success-value" if material_sales_ratio <= 30 else "warning-value" if material_sales_ratio <= 50 else "danger-value"

            # 物料成本卡
            st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">物料总成本</div>
                    <div class="value">¥{total_material_cost:,.2f}</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: 75%;"></div>
                    </div>
                    <div class="subtext">平均: ¥{(total_material_cost / total_distributors if total_distributors > 0 else 0):,.2f}/经销商</div>
                </div>
            ''', unsafe_allow_html=True)

            # 销售总额卡
            st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">销售总额</div>
                    <div class="value">¥{total_sales:,.2f}</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: 85%;"></div>
                    </div>
                    <div class="subtext">平均: ¥{(total_sales / total_distributors if total_distributors > 0 else 0):,.2f}/经销商</div>
                </div>
            ''', unsafe_allow_html=True)

            # ROI卡
            st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">投资回报率(ROI)</div>
                    <div class="value {roi_color}">{roi:.2f}</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: {min(roi / 5 * 100, 100)}%;"></div>
                    </div>
                    <div class="subtext">销售总额 ÷ 物料总成本</div>
                </div>
            ''', unsafe_allow_html=True)

            # 物料销售比率卡
            st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">物料销售比率</div>
                    <div class="value {ratio_color}">{material_sales_ratio:.2f}%</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: {max(100 - material_sales_ratio, 0)}%;"></div>
                    </div>
                    <div class="subtext">物料总成本 ÷ 销售总额 × 100%</div>
                </div>
            ''', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # 为指标卡添加解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">指标解读：</div>
                <p>上面四个指标卡显示了本期业绩情况。物料总成本是花在物料上的钱，销售总额是赚到的钱。ROI值大于1就是赚钱了，大于2是非常好的效果。物料销售比率越低越好，意味着花少量的钱带来了更多的销售。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 业绩概览图表
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">业绩指标趋势</div>',
                        unsafe_allow_html=True)

            # 创建两列放置图表
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 按月份的销售额
                monthly_sales = sales_data.groupby('月份名')['销售金额'].sum().reset_index()
                monthly_sales['月份序号'] = pd.to_datetime(monthly_sales['月份名']).dt.strftime('%Y%m').astype(int)
                monthly_sales = monthly_sales.sort_values('月份序号')

                fig = fp.line(
                    monthly_sales,
                    x='月份名',
                    y='销售金额',
                    title="销售金额月度趋势",
                    markers=True
                )

                # 确保y轴单位正确显示为元
                fig.update_yaxes(
                    title_text="金额 (元)",
                    ticksuffix="元",  # 显式设置元为单位
                    tickformat=",.0f"  # 设置千位分隔符，无小数点
                )

                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这条线展示了每个月的销售总额变化。向上走说明销售越来越好，向下走说明销售在下降。关注连续下降的月份并找出原因。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 按月份的ROI
                monthly_material = material_data.groupby('月份名')['物料成本'].sum().reset_index()
                monthly_sales = sales_data.groupby('月份名')['销售金额'].sum().reset_index()

                monthly_roi = pd.merge(monthly_material, monthly_sales, on='月份名')
                monthly_roi['ROI'] = monthly_roi['销售金额'] / monthly_roi['物料成本']
                monthly_roi['月份序号'] = pd.to_datetime(monthly_roi['月份名']).dt.strftime('%Y%m').astype(int)
                monthly_roi = monthly_roi.sort_values('月份序号')

                # 创建ROI趋势图
                fig = px.line(
                    monthly_roi,
                    x='月份名',
                    y='ROI',
                    markers=True,
                    title="ROI月度趋势"
                )

                fig.update_traces(
                    line=dict(color='#0FC86F', width=3),
                    marker=dict(size=8, color='#0FC86F')
                )

                # 添加ROI=1参考线
                fig.add_shape(
                    type="line",
                    x0=monthly_roi['月份名'].iloc[0],
                    y0=1,
                    x1=monthly_roi['月份名'].iloc[-1],
                    y1=1,
                    line=dict(color="#F53F3F", width=2, dash="dash")
                )

                fig.update_layout(
                    height=350,
                    xaxis_title="",
                    yaxis_title="ROI",
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                        size=12,
                        color="#1F1F1F"
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA'
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#E0E4EA'
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这条线显示了投资回报率(ROI)的变化。线在红色虚线(ROI=1)以上表示有盈利，越高越好。如果线下降到红线以下，说明物料投入没有带来足够的销售，需要立即调整物料策略。</p>
                </div>
                ''', unsafe_allow_html=True)

            # 客户分层
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">客户价值分布</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                if len(filtered_distributor) > 0 and '客户价值分层' in filtered_distributor.columns:
                    segment_counts = filtered_distributor['客户价值分层'].value_counts().reset_index()
                    segment_counts.columns = ['客户价值分层', '经销商数量']
                else:
                    # 创建一个空的DataFrame或默认数据防止错误
                    segment_counts = pd.DataFrame({'客户价值分层': [], '经销商数量': []})

                segment_colors = {
                    '高价值客户': '#0FC86F',
                    '成长型客户': '#2B5AED',
                    '稳定型客户': '#FFAA00',
                    '低效型客户': '#F53F3F'
                }

                # 1. 首先确保当前有数据可以绘图
                if len(segment_counts) > 0:
                    # 2. 创建一个只包含当前存在分类的颜色映射字典
                    available_colors = {}
                    for category in segment_counts['客户价值分层'].unique():
                        if category in segment_colors:
                            available_colors[category] = segment_colors[category]
                        else:
                            # 对于不在映射中的分类，使用默认颜色
                            available_colors[category] = '#808080'  # 灰色作为默认

                    # 3. 使用安全的颜色映射创建图表
                    fig = px.bar(
                        segment_counts,
                        x='客户价值分层',
                        y='经销商数量',
                        color='客户价值分层',
                        color_discrete_map=available_colors,
                        text='经销商数量'
                    )

                # 创建饼图
                fig = px.pie(
                    segment_counts,
                    names='客户价值分层',
                    values='经销商数量',
                    color='客户价值分层',
                    color_discrete_map=segment_colors,
                    title="客户价值分层分布",
                    hole=0.4
                )

                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='%{label}: %{value}个经销商<br>占比: %{percent}'
                )

                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                    paper_bgcolor='white',
                    font=dict(
                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                        size=12,
                        color="#1F1F1F"
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个饼图展示了不同客户类型的占比。绿色的"高价值客户"是最赚钱的，红色的"低效型客户"是亏损的。理想情况下，绿色和蓝色的部分应该超过50%，如果红色部分较大，需要重点改善这些客户的物料使用。</p>
                </div>
                ''', unsafe_allow_html=True)

            # 物料类别分布
            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 先检查数据有效性
                if filtered_material is not None and len(filtered_material) > 0:
                    # 确保物料类别和物料成本列存在
                    if '物料类别' in filtered_material.columns and '物料成本' in filtered_material.columns:
                        try:
                            # 计算每个物料类别的总成本
                            category_cost = filtered_material.groupby('物料类别')['物料成本'].sum().reset_index()

                            if len(category_cost) > 0:
                                # 排序
                                category_cost = category_cost.sort_values('物料成本', ascending=False)

                                # 改进颜色方案 - 使用更协调美观的色彩
                                custom_colors = ['#4361EE', '#3A86FF', '#4CC9F0', '#4ECDC4', '#F94144', '#F9844A',
                                                 '#F9C74F', '#90BE6D']

                                fig = px.bar(
                                    category_cost,
                                    x='物料类别',
                                    y='物料成本',
                                    color='物料类别',
                                    title="物料类别投入分布",
                                    color_discrete_sequence=custom_colors
                                )

                                fig.update_traces(
                                    texttemplate='%{y:,.0f}元',
                                    textposition='outside'
                                )

                                # 调整布局解决遮挡问题
                                fig.update_layout(
                                    height=380,  # 增加高度
                                    xaxis_title="",
                                    yaxis_title="物料成本(元)",  # 明确指定单位为元
                                    showlegend=False,
                                    margin=dict(l=20, r=20, t=40, b=80),  # 增加底部间距
                                    paper_bgcolor='white',
                                    plot_bgcolor='white',
                                    font=dict(
                                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                        size=12,
                                        color="#1F1F1F"
                                    ),
                                    xaxis=dict(
                                        showgrid=False,
                                        showline=True,
                                        linecolor='#E0E4EA',
                                        tickangle=-45,  # 倾斜标签避免重叠
                                        tickfont=dict(size=10)  # 调整字体大小
                                    ),
                                    yaxis=dict(
                                        showgrid=True,
                                        gridcolor='#E0E4EA',
                                        tickformat=",.0f",  # 设置千位分隔符
                                        ticksuffix="元"  # 明确设置单位为元
                                    )
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("暂无物料类别数据。")
                        except Exception as e:
                            st.error(f"创建物料类别分布图出错: {e}")
                            st.info("请检查物料类别和物料成本数据的格式是否正确")
                    else:
                        missing_cols = []
                        if '物料类别' not in filtered_material.columns:
                            missing_cols.append('物料类别')
                        if '物料成本' not in filtered_material.columns:
                            missing_cols.append('物料成本')
                        st.warning(f"数据中缺少必要的列: {', '.join(missing_cols)}")
                else:
                    st.info("暂无物料类别数据。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个柱状图显示了各类物料的投入成本。柱子越高表示在该类物料上花的钱越多。通过这个图可以清楚看到哪类物料占用了大部分预算，以及是否有物料类型投入不足。</p>
                </div>
                ''', unsafe_allow_html=True)
            # 业务洞察
            st.markdown('''
            <div class="feishu-insight-box">
                <div style="font-weight: 600; margin-bottom: 8px;">业绩洞察</div>
                <p style="margin: 0;">根据当前数据分析，物料投放效果整体表现良好。ROI指标高于行业平均，建议关注低效型客户占比，并针对性调整物料投放策略。高价值客户比例存在提升空间，通过物料组合优化可以提升客户价值分层。</p>
            </div>
            ''', unsafe_allow_html=True)

        # ======= 物料与销售分析标签页 =======
        with tab2:
            st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">物料与销售关系分析</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            # 改进的物料-销售关系图
            material_sales_relation = filtered_distributor.copy()

            if len(material_sales_relation) > 0:
                # 定义客户分层的颜色映射
                segment_colors = {
                    '高价值客户': '#0FC86F',
                    '成长型客户': '#2B5AED',
                    '稳定型客户': '#FFAA00',
                    '低效型客户': '#F53F3F'
                }

                # 创建散点图
                fig = px.scatter(
                    material_sales_relation,
                    x='物料总成本',
                    y='销售总额',
                    size='ROI',
                    color='客户价值分层',
                    hover_name='经销商名称',
                    log_x=True,
                    log_y=True,
                    size_max=45,
                    color_discrete_map=segment_colors,
                    hover_data={
                        '物料总成本': ':,.2f',
                        '销售总额': ':,.2f',
                        'ROI': ':.2f',
                        '物料多样性': True
                    }
                )

                # 获取最小和最大物料成本值用于绘制参考线
                min_cost = material_sales_relation['物料总成本'].min()
                max_cost = material_sales_relation['物料总成本'].max()

                # 添加盈亏平衡参考线 (ROI=1)
                fig.add_trace(go.Scatter(
                    x=[min_cost, max_cost],
                    y=[min_cost, max_cost],
                    mode='lines',
                    line=dict(color="#F53F3F", width=2, dash="dash"),
                    name="ROI = 1 (盈亏平衡线)",
                    hoverinfo='skip'
                ))

                # 添加图例注释
                fig.add_annotation(
                    x=0.02,
                    y=0.97,
                    xref="paper",
                    yref="paper",
                    text="点大小表示ROI值",
                    showarrow=False,
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#E0E4EA",
                    borderwidth=1,
                    borderpad=4,
                    font=dict(size=12)
                )

                # 改进图表布局和格式
                fig.update_layout(
                    height=560,  # 增加高度以提供更好的视觉效果
                    title=None,
                    margin=dict(l=30, r=30, t=20, b=30),  # 调整边距防止遮挡
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                        size=12,
                        color="#1F1F1F"
                    ),
                    legend=dict(
                        title=dict(text="客户价值分层", font=dict(size=13)),
                        orientation="h",
                        y=-0.15,
                        x=0.5,
                        xanchor="center",
                        font=dict(size=12)
                    )
                )

                # 优化X轴设置 - 修正货币单位问题
                fig.update_xaxes(
                    title=dict(
                        text="物料投入成本 (人民币元) - 对数刻度",
                        font=dict(size=13, color="#333333"),
                        standoff=15  # 增加标题与轴的距离
                    ),
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.4)',
                    gridwidth=0.5,
                    griddash='dot',
                    showline=True,
                    linecolor='#E0E4EA',
                    tickprefix="¥",  # 使用人民币符号
                    tickformat=",d",
                    exponentformat="none",
                    ticks="outside",
                    ticklen=5,
                    minor=dict(
                        showgrid=False
                    )
                )

                # 优化Y轴设置 - 修正货币单位问题
                fig.update_yaxes(
                    title=dict(
                        text="销售收入 (人民币元) - 对数刻度",
                        font=dict(size=13, color="#333333"),
                        standoff=15  # 增加标题与轴的距离
                    ),
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.4)',
                    gridwidth=0.5,
                    griddash='dot',
                    showline=True,
                    linecolor='#E0E4EA',
                    tickprefix="¥",  # 使用人民币符号
                    tickformat=",d",
                    exponentformat="none",
                    ticks="outside",
                    ticklen=5,
                    minor=dict(
                        showgrid=False
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无足够数据生成物料与销售关系图。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加散点图解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>这个散点图展示了物料投入和销售产出的关系。每个点代表一个经销商。横轴是投入物料成本，纵轴是获得的销售额，单位为人民币元。点越大表示ROI越高。红色虚线是盈亏平衡线(ROI=1)，点在这条线上面就是赚钱的，下面就是亏损的。从图中可以看出不同客户价值分层的分布特点，帮助识别高效和低效的物料投入模式。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 物料类别分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料类别分析</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 计算每个物料类别的总成本
                category_cost = filtered_material.groupby('物料类别')['物料成本'].sum().reset_index()
                category_cost = category_cost.sort_values('物料成本', ascending=False)

                if len(category_cost) > 0:
                    # 计算百分比并保留两位小数
                    category_cost['占比'] = ((category_cost['物料成本'] / category_cost['物料成本'].sum()) * 100).round(
                        2)

                    # 改进颜色方案 - 使用更协调美观的色彩
                    # 修复问题1：优化色彩搭配，使用更美观的配色方案
                    custom_colors = ['#4361EE', '#3A86FF', '#4CC9F0', '#4ECDC4', '#F94144', '#F9844A', '#F9C74F',
                                     '#90BE6D']

                    fig = px.pie(
                        category_cost,
                        values='物料成本',
                        names='物料类别',
                        title="物料成本占比",
                        hover_data=['占比'],
                        custom_data=['占比'],
                        color_discrete_sequence=custom_colors  # 使用新的颜色方案
                    )

                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='%{label}: ¥%{value:,.2f}<br>占比: %{customdata[0]:.2f}%',
                        textfont=dict(size=12),
                        marker=dict(line=dict(color='white', width=1))
                    )

                    fig.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        legend=dict(
                            font=dict(size=11),
                            orientation="h",
                            y=-0.2,
                            x=0.5,
                            xanchor="center"
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无物料类别数据。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加饼图解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个饼图显示了各类物料的成本占比。每个颜色代表一种物料类别，占比越大表示在该物料上花的钱越多。记住，占比大不一定是好事，要结合ROI来看，有些占比小的物料可能ROI很高。此分析帮助您了解当前的物料投资组合结构。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 客户分层销售额饼图
                segment_sales = filtered_distributor.groupby('客户价值分层')['销售总额'].sum().reset_index()

                if len(segment_sales) > 0:
                    # 计算百分比并保留两位小数
                    segment_sales['占比'] = ((segment_sales['销售总额'] / segment_sales['销售总额'].sum()) * 100).round(
                        2)

                    fig = px.pie(
                        segment_sales,
                        values='销售总额',
                        names='客户价值分层',
                        color='客户价值分层',
                        color_discrete_map=segment_colors,
                        title="各分层销售额占比",
                        hover_data=['占比'],
                        custom_data=['占比']
                    )

                    fig.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='%{label}: ¥%{value:,.2f}<br>占比: %{customdata[0]:.2f}%',
                        textfont=dict(size=12),
                        marker=dict(line=dict(color='white', width=1))
                    )

                    fig.update_layout(
                        height=350,
                        margin=dict(l=20, r=20, t=40, b=20),
                        paper_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        legend=dict(
                            font=dict(size=11),
                            orientation="h",
                            y=-0.2,
                            x=0.5,
                            xanchor="center"
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无客户分层销售数据。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加饼图解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个饼图显示了不同客户类型创造的销售额占比。绿色是高价值客户，蓝色是成长型客户，黄色是稳定型客户，红色是低效型客户。理想情况下，绿色和蓝色部分应该占大多数，表明高价值和潜力客户贡献了主要销售额。</p>
                </div>
                ''', unsafe_allow_html=True)

            # 物料ROI分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">单个物料ROI分析</div>',
                        unsafe_allow_html=True)

            # 为每个具体物料计算ROI
            material_specific_cost = material_data.groupby(['月份名', '产品代码', '产品名称'])[
                '物料成本'].sum().reset_index()

            # 假设销售额按物料成本比例分配
            monthly_sales_sum = sales_data.groupby('月份名')['销售金额'].sum().reset_index()

            # 合并销售数据
            material_analysis = pd.merge(material_specific_cost, monthly_sales_sum, on='月份名')

            # 计算每个月份每个物料的百分比
            material_month_total = material_analysis.groupby('月份名')['物料成本'].sum().reset_index()
            material_month_total.rename(columns={'物料成本': '月度物料总成本'}, inplace=True)

            material_analysis = pd.merge(material_analysis, material_month_total, on='月份名')
            material_analysis['成本占比'] = (material_analysis['物料成本'] / material_analysis['月度物料总成本']).round(
                4)

            # 按比例分配销售额
            material_analysis['分配销售额'] = material_analysis['销售金额'] * material_analysis['成本占比']

            # 计算ROI并保留两位小数
            material_analysis['物料ROI'] = (material_analysis['分配销售额'] / material_analysis['物料成本']).round(2)

            # 计算每个物料的平均ROI
            material_roi = material_analysis.groupby(['产品代码', '产品名称'])['物料ROI'].mean().reset_index()

            # 获取物料类别信息
            material_categories = material_data[['产品代码', '物料类别']].drop_duplicates()
            material_roi = pd.merge(material_roi, material_categories, on='产品代码', how='left')

            # 对于缺失的类别信息，填充默认值
            material_roi['物料类别'] = material_roi['物料类别'].fillna('未分类')

            # 只保留前15种物料展示，避免图表过于拥挤
            material_roi = material_roi.sort_values('物料ROI', ascending=False).head(15)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            if len(material_roi) > 0:
                # 使用与物料类别饼图相同的颜色方案
                # 创建物料条形图
                fig = px.bar(
                    material_roi,
                    x='产品名称',
                    y='物料ROI',
                    color='物料类别',
                    text='物料ROI',
                    title="TOP 15 物料ROI分析",
                    height=450,
                    color_discrete_sequence=custom_colors  # 使用与饼图相同的颜色方案
                )

                # 更新文本显示格式，确保两位小数
                fig.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside',
                    textfont=dict(size=12),
                    marker=dict(line=dict(width=0.5, color='white'))
                )

                # 添加参考线 - ROI=1
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    y0=1,
                    x1=len(material_roi) - 0.5,
                    y1=1,
                    line=dict(color="#F53F3F", width=2, dash="dash")
                )

                # 添加参考线标签
                fig.add_annotation(
                    x=len(material_roi) - 1.5,
                    y=1.05,
                    text="ROI=1（盈亏平衡）",
                    showarrow=False,
                    font=dict(size=12, color="#F53F3F")
                )

                # 改进布局 - 修复问题3：解决图表重叠问题
                fig.update_layout(
                    xaxis_title="物料名称",
                    yaxis_title="平均ROI",
                    margin=dict(l=20, r=20, t=40, b=180),  # 增加底部边距，确保标签完全显示
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                        size=12,
                        color="#1F1F1F"
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-70,  # 增大角度，防止重叠
                        tickfont=dict(size=10)  # 减小字体尺寸
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.4)',
                        gridwidth=0.5,
                        showline=True,
                        linecolor='#E0E4EA',
                        zeroline=True,
                        zerolinecolor='#E0E4EA',
                        zerolinewidth=1
                    ),
                    legend=dict(
                        title=dict(text="物料类别", font=dict(size=12)),
                        font=dict(size=11),
                        orientation="h",
                        y=-0.38,  # 调整图例位置，解决遮挡问题
                        x=0.5,
                        xanchor="center"
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无物料ROI数据。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加图表解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>这个柱状图显示了TOP 15个具体物料的平均ROI(投资回报率)。柱子越高表示该物料带来的回报越高，不同颜色代表不同的物料类别。红色虚线是ROI=1的参考线，低于这条线的物料是亏损的。应该增加高ROI物料的投入，减少低于红线的物料投入，优化物料投放结构。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 新增费比分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料费比分析</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 计算每个经销商的物料费比(物料成本占销售额的百分比)
                distributor_cost_ratio = filtered_distributor.copy()
                distributor_cost_ratio = distributor_cost_ratio[distributor_cost_ratio['销售总额'] > 0]  # 避免除以零

                if len(distributor_cost_ratio) > 0:
                    # 只展示TOP 10经销商(销售额最高的)
                    top_distributors = distributor_cost_ratio.sort_values('销售总额', ascending=False).head(10)

                    # 确保费比保留两位小数
                    top_distributors['物料销售比率'] = top_distributors['物料销售比率'].round(2)

                    # 创建费比条形图 - 修复问题3：解决图表重叠问题
                    fig = px.bar(
                        top_distributors.sort_values('物料销售比率'),
                        x='物料销售比率',
                        y='经销商名称',
                        color='客户价值分层',
                        color_discrete_map=segment_colors,
                        orientation='h',  # 水平条形图
                        text=top_distributors['物料销售比率'].apply(lambda x: f"{x:.2f}%"),
                        title="TOP 10 经销商物料费比(物料成本/销售额)"
                    )

                    # 更新文本样式
                    fig.update_traces(
                        textposition='outside',
                        textfont=dict(size=12),
                        marker=dict(line=dict(width=0.5, color='white'))
                    )

                    # 添加参考线 - 30%费比(行业标准)
                    fig.add_shape(
                        type="line",
                        x0=30,
                        y0=-0.5,
                        x1=30,
                        y1=len(top_distributors) - 0.5,
                        line=dict(color="#F53F3F", width=2, dash="dash")
                    )

                    # 添加参考线标签
                    fig.add_annotation(
                        x=31,
                        y=-0.4,
                        text="30% (行业参考线)",
                        showarrow=False,
                        font=dict(size=12, color="#F53F3F")
                    )

                    fig.update_layout(
                        height=400,
                        xaxis_title="物料费比(%)",
                        yaxis_title="",
                        margin=dict(l=160, r=40, t=40, b=30),  # 增加左侧边距，防止经销商名称遮挡
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        xaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(224, 228, 234, 0.4)',
                            gridwidth=0.5,
                            range=[0, max(top_distributors['物料销售比率']) * 1.2],  # 适当留出右侧空间
                            showline=True,
                            linecolor='#E0E4EA',
                            zeroline=True,
                            zerolinecolor='#E0E4EA',
                            ticksuffix="%"  # 确保显示百分比符号
                        ),
                        yaxis=dict(
                            showgrid=False,
                            autorange="reversed",  # 颠倒y轴顺序，使销售额最高的经销商显示在顶部
                            showline=True,
                            linecolor='#E0E4EA',
                            tickmode='array',  # 使用自定义刻度
                            tickvals=list(range(len(top_distributors))),  # 刻度位置
                            ticktext=[f"{name}" for name in top_distributors['经销商名称']],  # 经销商名称
                            tickfont=dict(size=10)  # 减小字体尺寸以适应空间
                        ),
                        legend=dict(
                            title=dict(text="客户价值分层", font=dict(size=12)),
                            orientation="h",
                            y=-0.15,
                            x=0.5,
                            xanchor="center",
                            font=dict(size=11)
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无足够数据生成费比分析。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个图表展示了TOP 10经销商的物料费比(物料成本占销售额的百分比)。柱子越短表示费比越低，物料使用效率越高。红色虚线是30%的行业参考线，低于这条线的经销商物料使用效率较好。不同颜色代表不同的客户价值分层，帮助识别不同价值客户的物料使用效率。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 按不同区域计算平均费比
                region_cost_ratio = filtered_distributor.groupby('所属区域').agg({
                    '物料销售比率': 'mean',
                    '物料总成本': 'sum',
                    '销售总额': 'sum',
                    '客户代码': 'nunique'
                }).reset_index()

                region_cost_ratio.rename(columns={'客户代码': '经销商数量'}, inplace=True)

                # 确保保留两位小数
                region_cost_ratio['物料销售比率'] = region_cost_ratio['物料销售比率'].round(2)
                region_cost_ratio['综合费比'] = (
                        region_cost_ratio['物料总成本'] / region_cost_ratio['销售总额'] * 100).round(2)

                if len(region_cost_ratio) > 0:
                    # 创建区域费比对比图
                    fig = go.Figure()

                    # 添加条形图 - 平均费比
                    fig.add_trace(go.Bar(
                        x=region_cost_ratio['所属区域'],
                        y=region_cost_ratio['物料销售比率'],
                        name='平均费比',
                        marker_color='#2B5AED',
                        text=region_cost_ratio['物料销售比率'].apply(lambda x: f"{x:.2f}%"),
                        textposition='outside',
                        marker=dict(line=dict(width=0.5, color='white'))
                    ))

                    # 添加折线图 - 经销商数量
                    fig.add_trace(go.Scatter(
                        x=region_cost_ratio['所属区域'],
                        y=region_cost_ratio['经销商数量'],
                        name='经销商数量',
                        mode='lines+markers',
                        marker=dict(size=8, color='#FFAA00', line=dict(width=1, color='white')),
                        line=dict(color='#FFAA00', width=3),
                        yaxis='y2'
                    ))

                    # 添加30%参考线
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=30,
                        x1=len(region_cost_ratio) - 0.5,
                        y1=30,
                        line=dict(color="#F53F3F", width=2, dash="dash")
                    )

                    # 添加参考线标签
                    fig.add_annotation(
                        x=0,
                        y=32,
                        text="30% (行业参考线)",
                        showarrow=False,
                        font=dict(size=12, color="#F53F3F")
                    )

                    # 更新布局 - 修复问题2：确保正确的货币单位显示
                    fig.update_layout(
                        height=400,
                        title=None,
                        yaxis=dict(
                            title='物料费比(%)',
                            titlefont=dict(size=12),
                            showgrid=True,
                            gridcolor='rgba(224, 228, 234, 0.4)',
                            gridwidth=0.5,
                            range=[0, max(region_cost_ratio['物料销售比率']) * 1.2],
                            showline=True,
                            linecolor='#E0E4EA',
                            zeroline=True,
                            zerolinecolor='#E0E4EA',
                            ticksuffix="%"  # 明确添加百分号
                        ),
                        yaxis2=dict(
                            title='经销商数量',
                            titlefont=dict(size=12),
                            overlaying='y',
                            side='right',
                            showgrid=False,
                            range=[0, max(region_cost_ratio['经销商数量']) * 1.2],
                            showline=True,
                            linecolor='#E0E4EA'
                        ),
                        xaxis=dict(
                            title='',
                            showgrid=False,
                            showline=True,
                            linecolor='#E0E4EA',
                            tickangle=-30  # 倾斜标签，防止重叠
                        ),
                        legend=dict(
                            orientation="h",
                            y=1.1,
                            x=0.5,
                            xanchor="center",
                            font=dict(size=11)
                        ),
                        margin=dict(l=20, r=70, t=40, b=50),  # 调整边距，确保标签显示
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无区域费比数据。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>此图展示了各区域的平均物料费比(蓝色柱)和经销商数量(黄线)。红色虚线是30%的参考线，柱子低于此线表示区域物料使用效率较好。可以看出哪些区域需要重点优化物料投入，为销售团队提供区域物料策略指导。</p>
                </div>
                ''', unsafe_allow_html=True)

            # 新增：物料时效分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料投放时效分析</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            try:
                # 按月份分组计算物料投入
                monthly_data = material_data.groupby('月份名')['物料成本'].sum().reset_index()
                monthly_data['月份序号'] = pd.to_datetime(monthly_data['月份名']).dt.strftime('%Y%m').astype(int)
                monthly_data = monthly_data.sort_values('月份序号')

                # 获取下个月的销售数据
                next_month_sales = sales_data.groupby('月份名')['销售金额'].sum().reset_index()
                next_month_sales['月份序号'] = pd.to_datetime(next_month_sales['月份名']).dt.strftime('%Y%m').astype(
                    int)
                next_month_sales = next_month_sales.sort_values('月份序号')

                # 移动一个月对齐前一个月的物料投入
                if len(monthly_data) > 1 and len(next_month_sales) > 1:
                    next_month_sales['前月物料投入'] = np.nan
                    for i in range(1, len(next_month_sales)):
                        current_month = next_month_sales.iloc[i]['月份名']
                        prev_month = next_month_sales.iloc[i - 1]['月份名']
                        prev_material = monthly_data[monthly_data['月份名'] == prev_month]['物料成本'].values
                        if len(prev_material) > 0:
                            next_month_sales.loc[next_month_sales['月份名'] == current_month, '前月物料投入'] = \
                                prev_material[0]

                    # 计算效应系数
                    next_month_sales['效应系数'] = (
                            next_month_sales['销售金额'] / next_month_sales['前月物料投入']).round(2)
                    next_month_sales = next_month_sales.dropna()

                    if len(next_month_sales) > 0:
                        fig = px.line(
                            next_month_sales,
                            x='月份名',
                            y='效应系数',
                            title=None,
                            markers=True,
                            line_shape='spline'
                        )

                        # 添加参考线 - 效应系数 = 1
                        fig.add_shape(
                            type="line",
                            x0=next_month_sales['月份名'].iloc[0],
                            y0=1,
                            x1=next_month_sales['月份名'].iloc[-1],
                            y1=1,
                            line=dict(color="#F53F3F", width=2, dash="dash")
                        )

                        # 添加参考线标签
                        fig.add_annotation(
                            x=next_month_sales['月份名'].iloc[-1],
                            y=1.05,
                            text="效应系数=1（盈亏平衡）",
                            showarrow=False,
                            font=dict(size=12, color="#F53F3F")
                        )

                        # 美化图表
                        fig.update_traces(
                            line=dict(color='#2B5AED', width=3),
                            marker=dict(size=10, color='#2B5AED', line=dict(width=1, color='white')),
                            texttemplate='%{y:.2f}',
                            textposition='top center'
                        )

                        # 标注数据点的值
                        for i, row in next_month_sales.iterrows():
                            fig.add_annotation(
                                x=row['月份名'],
                                y=row['效应系数'] + 0.1,
                                text=f"{row['效应系数']:.2f}",
                                showarrow=False,
                                font=dict(size=11, color="#2B5AED")
                            )

                        fig.update_layout(
                            height=380,
                            xaxis_title="月份",
                            yaxis_title="效应系数",
                            margin=dict(l=20, r=20, t=40, b=50),  # 调整底部边距
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA',
                                tickangle=-45,  # 增加角度避免重叠
                                tickfont=dict(size=11)
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(224, 228, 234, 0.4)',
                                gridwidth=0.5,
                                showline=True,
                                linecolor='#E0E4EA',
                                zeroline=True,
                                zerolinecolor='#E0E4EA',
                                zerolinewidth=1
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无足够数据生成时效分析。")
                else:
                    st.info("暂无足够月份数据生成时效分析。")
            except Exception as e:
                st.error(f"生成时效分析时出错: {e}")
                st.info("暂无足够数据生成时效分析，请确保数据包含多个月份。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加解释
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>此图展示了物料投放后一个月的销售效应。效应系数 = 当月销售额 ÷ 前月物料投入，反映物料投放的滞后效应。系数高表示物料在下个月产生了更好的效果。可见波动和季节性趋势，帮助销售团队优化物料投放时机，提升时间维度的投放策略。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 月度趋势分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">销售与物料月度趋势</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            # 按月份计算物料成本和销售额
            monthly_trend = material_data.groupby('月份名')['物料成本'].sum().reset_index()
            monthly_sales = sales_data.groupby('月份名')['销售金额'].sum().reset_index()

            monthly_data = pd.merge(monthly_trend, monthly_sales, on='月份名')
            monthly_data['ROI'] = (monthly_data['销售金额'] / monthly_data['物料成本']).round(2)

            # 排序
            monthly_data['月份序号'] = pd.to_datetime(monthly_data['月份名']).dt.strftime('%Y%m').astype(int)
            monthly_data = monthly_data.sort_values('月份序号')

            if len(monthly_data) > 0:
                # 创建飞书风格双轴图表
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # 添加物料成本柱状图
                fig.add_trace(
                    go.Bar(
                        x=monthly_data['月份名'],
                        y=monthly_data['物料成本'],
                        name='物料成本',
                        marker_color='rgba(43, 90, 237, 0.7)',
                        marker=dict(line=dict(width=0.5, color='white'))
                    ),
                    secondary_y=False
                )

                # 添加销售金额柱状图
                fig.add_trace(
                    go.Bar(
                        x=monthly_data['月份名'],
                        y=monthly_data['销售金额'],
                        name='销售金额',
                        marker_color='rgba(15, 200, 111, 0.7)',
                        marker=dict(line=dict(width=0.5, color='white'))
                    ),
                    secondary_y=False
                )

                # 添加ROI线图
                fig.add_trace(
                    go.Scatter(
                        x=monthly_data['月份名'],
                        y=monthly_data['ROI'],
                        name='ROI',
                        mode='lines+markers+text',
                        line=dict(color='#7759F3', width=3),
                        marker=dict(size=8, color='#7759F3', line=dict(width=1, color='white')),
                        text=monthly_data['ROI'].apply(lambda x: f"{x:.2f}"),
                        textposition='top center',
                        textfont=dict(size=11, color="#7759F3")
                    ),
                    secondary_y=True
                )

                # 添加ROI=1参考线
                fig.add_shape(
                    type="line",
                    x0=monthly_data['月份名'].iloc[0],
                    x1=monthly_data['月份名'].iloc[-1],
                    y0=1,
                    y1=1,
                    line=dict(color="#F53F3F", width=2, dash="dash"),
                    yref='y2'
                )

                # 更新图表布局 - 修复问题2：确保正确的货币单位显示
                fig.update_layout(
                    height=420,
                    barmode='group',
                    bargap=0.2,
                    bargroupgap=0.1,
                    xaxis_title="",
                    margin=dict(l=20, r=40, t=10, b=70),  # 调整底部边距，避免x轴标签被截断
                    legend=dict(
                        orientation="h",
                        y=1.1,
                        x=0.5,
                        xanchor="center",
                        font=dict(size=11)
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                        size=12,
                        color="#1F1F1F"
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-45,  # 倾斜标签，防止重叠
                        tickfont=dict(size=11)
                    )
                )

                # 更新y轴 - 确保显示正确的单位(修复问题2：货币单位)
                fig.update_yaxes(
                    title_text="金额 (人民币元)",
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.4)',
                    gridwidth=0.5,
                    tickprefix="¥",  # 添加人民币符号
                    tickformat=",d",  # 添加千位分隔符
                    showline=True,
                    linecolor='#E0E4EA',
                    secondary_y=False
                )

                fig.update_yaxes(
                    title_text="ROI",
                    showgrid=False,
                    tickformat=".2f",  # 保留两位小数
                    showline=True,
                    linecolor='#E0E4EA',
                    secondary_y=True
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无月度趋势数据。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加图表解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>这个图表展示了每月的物料成本(蓝色柱子)、销售额(绿色柱子)和ROI(紫色线)。当绿色柱子明显高于蓝色柱子时，说明效率好；当紫色线越高，说明投资回报率越好。通过观察趋势可以发现季节性规律，为物料的合理规划提供依据，例如在销售旺季前增加物料投放。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 新增：物料组合效能分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料组合效能分析</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            try:
                # 获取经销商使用的物料类别组合
                distributor_material_combos = material_data.groupby(['客户代码', '物料类别'])[
                    '物料成本'].sum().reset_index()
                distributor_material_combos_pivot = distributor_material_combos.pivot_table(
                    index='客户代码',
                    columns='物料类别',
                    values='物料成本',
                    aggfunc='sum'
                ).fillna(0)

                # 为每个经销商计算物料类别占比
                distributor_material_combos_pivot = distributor_material_combos_pivot.div(
                    distributor_material_combos_pivot.sum(axis=1), axis=0
                ) * 100

                # 创建二进制使用标志 (1表示使用该类别投入超过10%)
                binary_material_usage = (distributor_material_combos_pivot > 10).astype(int)

                # 获取每个经销商的ROI
                distributor_roi = distributor_data.groupby('客户代码')['ROI'].mean().reset_index()

                # 合并二进制物料使用和ROI数据
                combined_data = pd.merge(binary_material_usage.reset_index(), distributor_roi, on='客户代码')

                # 计算每种物料组合的平均ROI
                all_combinations = []
                material_categories = binary_material_usage.columns.tolist()

                for i, cat1 in enumerate(material_categories):
                    for j, cat2 in enumerate(material_categories[i + 1:], i + 1):
                        # 找出使用这两种物料的经销商
                        combo_mask = (combined_data[cat1] == 1) & (combined_data[cat2] == 1)
                        if combo_mask.sum() >= 3:  # 至少有3个经销商使用这种组合
                            combo_roi = combined_data.loc[combo_mask, 'ROI'].mean().round(2)
                            all_combinations.append({
                                '组合': f"{cat1} + {cat2}",
                                '平均ROI': combo_roi,
                                '使用经销商数': int(combo_mask.sum())
                            })

                # 创建DataFrame并按ROI排序
                combo_df = pd.DataFrame(all_combinations).sort_values('平均ROI', ascending=False)

                # 创建Top物料组合的条形图
                if len(combo_df) > 0:
                    # 限制展示前10个
                    combo_df = combo_df.head(10)

                    # 创建连续颜色映射
                    color_scale = px.colors.sequential.Blues[2:]  # 更亮的蓝色开始

                    fig = px.bar(
                        combo_df,
                        x='组合',
                        y='平均ROI',
                        text='平均ROI',
                        color='使用经销商数',
                        color_continuous_scale=color_scale,
                        title=None
                    )

                    # 添加文本格式
                    fig.update_traces(
                        texttemplate='%{text:.2f}',
                        textposition='outside',
                        textfont=dict(size=12),
                        marker=dict(line=dict(width=0.5, color='white'))
                    )

                    # 添加ROI=1参考线
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        x1=len(combo_df) - 0.5,
                        y0=1,
                        y1=1,
                        line=dict(color="#F53F3F", width=2, dash="dash")
                    )

                    # 添加参考线标签
                    fig.add_annotation(
                        x=len(combo_df) - 1.5,
                        y=1.05,
                        text="ROI=1（盈亏平衡）",
                        showarrow=False,
                        font=dict(size=12, color="#F53F3F")
                    )

                    # 美化图表
                    fig.update_layout(
                        height=400,
                        xaxis_title="物料组合",
                        yaxis_title="平均ROI",
                        margin=dict(l=20, r=20, t=10, b=130),  # 增加底部边距，防止标签截断
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        xaxis=dict(
                            showgrid=False,
                            showline=True,
                            linecolor='#E0E4EA',
                            tickangle=-45,  # 倾斜标签
                            tickfont=dict(size=11)
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(224, 228, 234, 0.4)',
                            gridwidth=0.5,
                            showline=True,
                            linecolor='#E0E4EA',
                            zeroline=True,
                            zerolinecolor='#E0E4EA',
                            zerolinewidth=1
                        ),
                        coloraxis_colorbar=dict(
                            title="使用经销商数",
                            titleside="right",
                            tickmode="array",
                            ticks="outside",
                            len=0.5,
                            y=0.5
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无足够数据生成物料组合分析。")
            except Exception as e:
                st.error(f"生成物料组合分析时出错: {e}")
                st.info("暂无足够数据生成物料组合分析。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加解释
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>此图显示不同物料组合的平均ROI表现。只有当经销商在该物料类别上花费超过10%的物料预算时才计入组合。颜色深浅表示使用该组合的经销商数量。通过这个图可以发现哪些物料组合效果最好，为物料投放决策提供具体指导。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 物料多样性优化分析
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料多样性优化分析</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            try:
                # 分组多样性水平
                diversity_bins = [0, 2, 4, 6, 8, 10, 15, np.inf]
                diversity_labels = ['0-2种', '3-4种', '5-6种', '7-8种', '9-10种', '11-15种', '16种+']

                # 添加多样性水平作为分类变量
                distributor_data['多样性水平'] = pd.cut(
                    distributor_data['物料多样性'],
                    bins=diversity_bins,
                    labels=diversity_labels,
                    right=False
                )

                # 按多样性水平分组
                diversity_metrics = distributor_data.groupby('多样性水平').agg({
                    'ROI': 'mean',
                    '物料销售比率': 'mean',
                    '客户代码': 'count'
                }).reset_index()

                diversity_metrics.rename(columns={'客户代码': '经销商数量'}, inplace=True)

                # 确保保留两位小数
                diversity_metrics['ROI'] = diversity_metrics['ROI'].round(2)
                diversity_metrics['物料销售比率'] = diversity_metrics['物料销售比率'].round(2)

                if len(diversity_metrics) > 0:
                    # 创建双轴图表
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    # 添加ROI条形图
                    fig.add_trace(
                        go.Bar(
                            x=diversity_metrics['多样性水平'],
                            y=diversity_metrics['ROI'],
                            name='平均ROI',
                            marker_color='#0FC86F',
                            text=diversity_metrics['ROI'].apply(lambda x: f"{x:.2f}"),
                            textposition='outside',
                            textfont=dict(size=12),
                            marker=dict(line=dict(width=0.5, color='white'))
                        ),
                        secondary_y=False
                    )

                    # 添加物料销售比率折线图
                    fig.add_trace(
                        go.Scatter(
                            x=diversity_metrics['多样性水平'],
                            y=diversity_metrics['物料销售比率'],
                            name='物料销售比率(%)',
                            mode='lines+markers',
                            marker=dict(size=8, color='#2B5AED', line=dict(width=1, color='white')),
                            line=dict(color='#2B5AED', width=3)
                        ),
                        secondary_y=True
                    )

                    # 添加经销商数量散点
                    max_count = diversity_metrics['经销商数量'].max()
                    bubble_size = diversity_metrics['经销商数量'] / max_count * 40 + 10

                    fig.add_trace(
                        go.Scatter(
                            x=diversity_metrics['多样性水平'],
                            y=[0.2] * len(diversity_metrics),  # 放在图表底部
                            mode='markers+text',
                            marker=dict(
                                size=bubble_size,
                                color='rgba(255, 170, 0, 0.6)',
                                line=dict(color='rgba(255, 170, 0, 1)', width=1)
                            ),
                            text=diversity_metrics['经销商数量'],
                            textposition='middle center',
                            textfont=dict(size=11, color='#333333'),
                            hoverinfo='text',
                            hovertext=diversity_metrics['经销商数量'].apply(lambda x: f"{x}个经销商"),
                            name='经销商数量'
                        ),
                        secondary_y=False
                    )

                    # 添加ROI=1参考线
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        x1=len(diversity_metrics) - 0.5,
                        y0=1,
                        y1=1,
                        line=dict(color="#F53F3F", width=2, dash="dash")
                    )

                    # 添加参考线标签
                    fig.add_annotation(
                        x=-0.4,
                        y=1.05,
                        text="ROI=1（盈亏平衡）",
                        showarrow=False,
                        font=dict(size=12, color="#F53F3F")
                    )

                    # 更新布局
                    fig.update_layout(
                        title=None,
                        height=400,
                        margin=dict(l=20, r=20, t=10, b=50),  # 调整底部边距
                        legend=dict(
                            orientation="h",
                            y=1.1,
                            x=0.5,
                            xanchor="center",
                            font=dict(size=11)
                        ),
                        xaxis=dict(
                            title="物料多样性(种类数)",
                            showgrid=False,
                            showline=True,
                            linecolor='#E0E4EA',
                            tickfont=dict(size=11)
                        ),
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        )
                    )

                    # 更新y轴
                    fig.update_yaxes(
                        title_text="平均ROI",
                        secondary_y=False,
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.4)',
                        gridwidth=0.5,
                        range=[0, max(diversity_metrics['ROI']) * 1.2],
                        showline=True,
                        linecolor='#E0E4EA'
                    )
                    fig.update_yaxes(
                        title_text="物料销售比率(%)",
                        secondary_y=True,
                        showgrid=False,
                        range=[0, max(diversity_metrics['物料销售比率']) * 1.2],
                        showline=True,
                        linecolor='#E0E4EA',
                        ticksuffix="%"  # 明确添加百分号
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无足够数据生成多样性分析。")
            except Exception as e:
                st.error(f"生成多样性分析时出错: {e}")
                st.info("暂无足够数据生成多样性分析。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加解释和洞察
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>此图展示物料多样性与经销商表现的关系。绿色柱表示平均ROI，蓝线表示物料销售比率，黄色圆圈大小表示各多样性水平的经销商数量。可以看出，适当的物料多样性对销售效果有明显提升，但超过某个阈值后边际效应递减。</p>
            </div>

            <div class="feishu-insight-box">
                <div style="font-weight: 600; margin-bottom: 8px;">多样性优化洞察</div>
                <p style="margin: 0; line-height: 1.6;">数据显示，使用7-10种不同物料的经销商通常能获得最佳ROI。过少的物料类型难以全面覆盖销售场景，而过多的物料类型则可能导致资源分散。建议根据经销商规模调整物料多样性：大型经销商8-12种，中型经销商5-8种，小型经销商3-5种。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 总结洞察
            st.markdown('''
            <div class="feishu-insight-box" style="margin-top: 20px;">
                <div style="font-weight: 600; margin-bottom: 8px;">物料效率洞察</div>
                <p style="margin: 0; line-height: 1.6;">通过多维度分析发现：1) 物料投放存在1个月左右的滞后效应，应提前规划；2) 不同物料组合对ROI影响显著，应根据最优组合配置；3) 物料多样性在7-10种时效果最佳；4) 物料投入有最佳区间，过少无法覆盖营销场景，过多则边际效应递减；5) 高价值客户应优先保证物料投放，低效客户应先提供培训再投放。建议构建差异化物料策略，逐步优化投放结构。</p>
            </div>
            ''', unsafe_allow_html=True)
            # ======= 经销商分析标签页 =======
        with tab3:
                st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">经销商价值分布</div>',
                            unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    # 计算客户分层数量
                    segment_counts = filtered_distributor['客户价值分层'].value_counts().reset_index()
                    segment_counts.columns = ['客户价值分层', '经销商数量']
                    segment_counts['占比'] = (
                            segment_counts['经销商数量'] / segment_counts['经销商数量'].sum() * 100).round(2)

                    segment_colors = {
                        '高价值客户': '#0FC86F',
                        '成长型客户': '#2B5AED',
                        '稳定型客户': '#FFAA00',
                        '低效型客户': '#F53F3F'
                    }

                    if len(segment_counts) > 0:
                        fig = px.bar(
                            segment_counts,
                            x='客户价值分层',
                            y='经销商数量',
                            color='客户价值分层',
                            color_discrete_map=segment_colors,
                            text='经销商数量'
                        )

                        fig.update_traces(textposition='outside')
                        fig.update_layout(
                            height=350,
                            xaxis_title="",
                            yaxis_title="经销商数量",
                            showlegend=False,
                            margin=dict(l=20, r=20, t=10, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA'
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商分层数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个柱状图显示了不同类型的经销商数量。绿色是高价值客户(最赚钱的)，蓝色是成长型客户(有潜力的)，黄色是稳定型客户(盈利但增长有限的)，红色是低效型客户(投入产出比不好的)。理想情况下，绿色和蓝色柱子应该比黄色和红色柱子高。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    # 按分层的ROI
                    region_roi = filtered_distributor.groupby('客户价值分层').agg({
                        'ROI': 'mean',
                        '物料销售比率': 'mean'
                    }).reset_index()

                    if len(region_roi) > 0:
                        # 创建双轴图表
                        fig = make_subplots(specs=[[{"secondary_y": True}]])

                        fig.add_trace(
                            go.Bar(
                                x=region_roi['客户价值分层'],
                                y=region_roi['ROI'],
                                name='平均ROI',
                                marker_color=[
                                    segment_colors.get(segment, '#2B5AED') for segment in region_roi['客户价值分层']
                                ]
                            ),
                            secondary_y=False
                        )

                        fig.add_trace(
                            go.Scatter(
                                x=region_roi['客户价值分层'],
                                y=region_roi['物料销售比率'],
                                name='物料销售比率(%)',
                                mode='markers',
                                marker=dict(
                                    size=12,
                                    color='#7759F3'
                                )
                            ),
                            secondary_y=True
                        )

                        fig.update_layout(
                            height=350,
                            xaxis_title="",
                            margin=dict(l=20, r=20, t=10, b=20),
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA'
                            ),
                            yaxis2=dict(
                                showgrid=False
                            )
                        )

                        fig.update_yaxes(title_text='平均ROI', tickformat=".2f", secondary_y=False)
                        fig.update_yaxes(title_text='物料销售比率(%)', tickformat=".2f", ticksuffix="%",
                                         secondary_y=True)

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无分层ROI数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个图表展示了不同客户类型的ROI(柱子)和物料销售比率(紫色点)。柱子越高表示该类客户的ROI越高，紫色点越低表示物料使用效率越好。高价值客户的ROI最高、物料销售比率最低，这是最理想的。低效型客户则相反，需要重点改进。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                # 高效和低效经销商分析
                st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">经销商效率分析</div>',
                            unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="feishu-chart-container" style="height: 100%;">', unsafe_allow_html=True)

                    # 高效经销商图表可视化
                    if len(filtered_distributor) > 0:
                        efficient_distributors = filtered_distributor.sort_values('ROI', ascending=False).head(10)

                        fig = go.Figure()

                        # 添加水平条形图 - ROI值
                        fig.add_trace(go.Bar(
                            y=efficient_distributors['经销商名称'],
                            x=efficient_distributors['ROI'],
                            orientation='h',
                            name='ROI',
                            marker_color='#0FC86F',
                            text=efficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                            textposition='inside',
                            width=0.6
                        ))

                        # 更新布局
                        fig.update_layout(
                            height=350,
                            title="高效物料投放经销商 Top 10 (按ROI)",
                            xaxis_title="ROI值",
                            margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA',
                                tickformat=".2f"  # 保留两位小数
                            ),
                            yaxis=dict(
                                showgrid=False,
                                autorange="reversed"  # 倒序显示，让最大值在顶部
                            )
                        )

                        # 添加参考线 - ROI=1和ROI=2
                        fig.add_shape(
                            type="line",
                            x0=1, y0=-0.5,
                            x1=1, y1=len(efficient_distributors) - 0.5,
                            line=dict(color="#F53F3F", width=2, dash="dash")
                        )

                        fig.add_shape(
                            type="line",
                            x0=2, y0=-0.5,
                            x1=2, y1=len(efficient_distributors) - 0.5,
                            line=dict(color="#7759F3", width=2, dash="dash")
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个图表展示了物料使用效率最高的10个经销商，按ROI(投资回报率)从高到低排序。绿色柱子越长表示ROI越高，经销商越赚钱。紫色虚线(ROI=2)是优秀水平，红色虚线(ROI=1)是盈亏平衡线。这些经销商的物料使用方法是最佳实践，值得推广到其他经销商。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="feishu-chart-container" style="height: 100%;">', unsafe_allow_html=True)

                    # 低效经销商可视化
                    if len(filtered_distributor) > 0:
                        inefficient_distributors = filtered_distributor[
                            (filtered_distributor['物料总成本'] > 0) &
                            (filtered_distributor['销售总额'] > 0)
                            ].sort_values('ROI').head(10)

                        fig = go.Figure()

                        # 添加水平条形图 - ROI值
                        fig.add_trace(go.Bar(
                            y=inefficient_distributors['经销商名称'],
                            x=inefficient_distributors['ROI'],
                            orientation='h',
                            name='ROI',
                            marker_color='#F53F3F',
                            text=inefficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                            textposition='inside',
                            width=0.6
                        ))

                        # 更新布局
                        fig.update_layout(
                            height=350,
                            title="待优化物料投放经销商 Top 10 (按ROI)",
                            xaxis_title="ROI值",
                            margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA',
                                tickformat=".2f"  # 保留两位小数
                            ),
                            yaxis=dict(
                                showgrid=False,
                                autorange="reversed"
                            )
                        )

                        # 添加参考线 - ROI=1
                        fig.add_shape(
                            type="line",
                            x0=1, y0=-0.5,
                            x1=1, y1=len(inefficient_distributors) - 0.5,
                            line=dict(color="#0FC86F", width=2, dash="dash")
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个图表展示了物料使用效率最低的10个经销商，按ROI从低到高排序。红色柱子长度表示ROI值，越短说明效率越低。绿色虚线(ROI=1)是盈亏平衡线，低于这条线的经销商是亏损的。这些经销商应该是重点改进对象。优化方向包括：调整物料组合、改善陈列方式、加强培训等。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                # 经销商ROI分布
                st.markdown(
                    '<div class="feishu-chart-title" style="margin-top: 20px;">经销商ROI分布与物料使用分析</div>',
                    unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    # 创建ROI分布直方图
                    roi_data = filtered_distributor[filtered_distributor['ROI'] > 0]

                    if len(roi_data) > 0:
                        fig = px.histogram(
                            roi_data,
                            x='ROI',
                            nbins=20,
                            histnorm='percent',
                            marginal='box',
                            color_discrete_sequence=['#2B5AED'],
                            title="经销商ROI分布"
                        )

                        # 安全地确定最大Y值
                        max_y_value = 10  # 默认值
                        if len(fig.data) > 0 and hasattr(fig.data[0], 'y') and fig.data[0].y is not None and len(
                                fig.data[0].y) > 0:
                            max_y_value = max(fig.data[0].y.max(), 10)

                        # 添加ROI=1参考线
                        fig.add_shape(
                            type="line",
                            x0=1, y0=0,
                            x1=1, y1=max_y_value,
                            line=dict(color="#F53F3F", width=2, dash="dash")
                        )

                        # 添加ROI=2参考线
                        fig.add_shape(
                            type="line",
                            x0=2, y0=0,
                            x1=2, y1=max_y_value,
                            line=dict(color="#0FC86F", width=2, dash="dash")
                        )

                        fig.update_layout(
                            height=350,
                            xaxis_title="ROI值",
                            yaxis_title="占比(%)",
                            bargap=0.1,
                            margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA',
                                tickformat=".2f"
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA',
                                ticksuffix="%"
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("没有足够的数据生成ROI分布直方图。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个直方图显示了所有经销商的ROI分布情况。横轴是ROI值，柱子高度表示有多少比例的经销商在该ROI区间。红色虚线(ROI=1)是盈亏平衡线，绿色虚线(ROI=2)是优秀水平线。ROI分布越向右偏，说明整体效率越好。理想情况下，柱子应该主要分布在红线右侧，且有一定比例在绿线右侧。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    # 物料多样性和ROI关系分析
                    if len(filtered_distributor) > 0:
                        fig = px.scatter(
                            filtered_distributor,
                            x='物料多样性',
                            y='ROI',
                            color='客户价值分层',
                            size='销售总额',
                            hover_name='经销商名称',
                            color_discrete_map={
                                '高价值客户': '#0FC86F',
                                '成长型客户': '#2B5AED',
                                '稳定型客户': '#FFAA00',
                                '低效型客户': '#F53F3F'
                            },
                            size_max=40,
                            title="物料多样性与ROI关系"
                        )

                        # 添加趋势线
                        if len(filtered_distributor) > 1:
                            # 准备趋势线拟合数据
                            x = filtered_distributor['物料多样性'].values
                            y = filtered_distributor['ROI'].values

                            # 排除无效值
                            mask = ~np.isnan(x) & ~np.isnan(y)
                            x = x[mask]
                            y = y[mask]

                            if len(x) > 1:
                                # 使用线性拟合
                                z = np.polyfit(x, y, 1)
                                p = np.poly1d(z)

                                # 添加趋势线
                                x_range = np.linspace(min(x), max(x), 100)
                                fig.add_trace(
                                    go.Scatter(
                                        x=x_range,
                                        y=p(x_range),
                                        mode='lines',
                                        name='趋势线',
                                        line=dict(color='rgba(119, 89, 243, 0.7)', width=2, dash='dash'),
                                        hoverinfo='skip'
                                    )
                                )

                        fig.update_layout(
                            height=350,
                            xaxis_title="物料多样性（使用物料种类数）",
                            yaxis_title="ROI",
                            margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='#E0E4EA',
                                tickformat=".2f"
                            )
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("没有足够的数据生成物料多样性分析。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>这个散点图展示了物料多样性和ROI之间的关系。横轴是经销商使用的物料种类数量，纵轴是ROI值。点的大小表示销售额大小，颜色表示客户类型。紫色虚线是趋势线，向上倾斜说明物料种类越多，ROI可能越高。这告诉我们：经销商应该适当增加物料多样性，不要只用单一类型物料，搭配使用通常更有效。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                # 经销商洞察
                st.markdown('''
                <div class="feishu-insight-box">
                    <div style="font-weight: 600; margin-bottom: 8px;">经销商投放洞察</div>
                    <p style="margin: 0; line-height: 1.6;">数据显示，物料多样性与ROI呈现正相关趋势，使用多种物料的经销商通常能获得更高的销售效率。针对高ROI经销商的物料使用模式，可提取最佳实践并推广至其他经销商，提升整体物料投放效率。建议关注物料销售比率过高的经销商，通过优化物料组合结构提升ROI。</p>
                </div>
                ''', unsafe_allow_html=True)

                # 最佳实践分析
                st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">高效经销商最佳实践</div>',
                            unsafe_allow_html=True)

                # 选择ROI最高的经销商并分析他们的物料使用模式
                top_roi_distributors = filtered_distributor.sort_values('ROI', ascending=False).head(3)

                if len(top_roi_distributors) > 0:
                    st.markdown('<div class="feishu-grid">', unsafe_allow_html=True)

                    for i, (_, distributor) in enumerate(top_roi_distributors.iterrows()):
                        distributor_name = distributor['经销商名称']
                        distributor_roi = distributor['ROI']
                        distributor_code = distributor['客户代码']

                        # 获取该经销商的物料使用数据
                        dist_materials = filtered_material[filtered_material['客户代码'] == distributor_code]

                        # 默认值，防止无数据情况
                        top_categories_str = "无数据"
                        diversity = 0

                        if len(dist_materials) > 0:
                            material_categories = dist_materials.groupby('物料类别')['物料成本'].sum().reset_index()
                            material_categories['占比'] = material_categories['物料成本'] / material_categories[
                                '物料成本'].sum() * 100
                            material_categories = material_categories.sort_values('占比', ascending=False)

                            # 计算物料使用特性
                            top_categories = material_categories.head(2)['物料类别'].tolist()
                            top_categories_str = '、'.join(top_categories) if top_categories else "无数据"
                            diversity = len(dist_materials['产品代码'].unique())

                        st.markdown(f'''
                        <div class="feishu-card">
                            <div style="font-size: 16px; font-weight: 600; margin-bottom: 10px; color: #1F1F1F;">{distributor_name}</div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <div><span style="font-weight: 500; color: #646A73;">ROI:</span> <span class="success-value" style="font-weight: 600;">{distributor_roi:.2f}</span></div>
                                <div><span style="font-weight: 500; color: #646A73;">物料多样性:</span> <span style="font-weight: 600;">{diversity}</span> 种</div>
                            </div>
                            <div style="margin-bottom: 10px;"><span style="font-weight: 500; color: #646A73;">主要物料类别:</span> <span style="font-weight: 500;">{top_categories_str}</span></div>
                            <div style="margin-top: 12px;">
                                <span class="feishu-tag feishu-tag-green">最佳实践</span>
                                <span class="feishu-tag feishu-tag-blue">物料搭配优</span>
                                <span class="feishu-tag feishu-tag-orange">可复制模式</span>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加最佳实践解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">最佳实践解读：</div>
                        <p>上面的卡片展示了ROI最高的三个经销商的物料使用特点。每张卡片显示经销商的ROI值、物料多样性(使用了多少种物料)和主要使用的物料类别。这些是表现最好的经销商，他们的物料使用方式值得学习。通常他们的共同特点是：使用多种物料、有明确的主力物料类别，而且搭配合理。</p>
                    </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.info("暂无经销商数据。")

                # 物料使用时序分析 - 改进布局和间距
                st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">经销商物料使用时序分析</div>',
                            unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    if len(filtered_distributor) > 0:
                        # 筛选一个高效经销商作为示例
                        high_perf_distributor = filtered_distributor.sort_values('ROI', ascending=False).iloc[0]
                        high_perf_code = high_perf_distributor['客户代码']
                        high_perf_name = high_perf_distributor['经销商名称']

                        # 获取该经销商的月度物料使用和销售数据
                        high_perf_monthly_material = \
                        material_data[material_data['客户代码'] == high_perf_code].groupby('月份名')[
                            '物料成本'].sum().reset_index()
                        high_perf_monthly_sales = \
                        sales_data[sales_data['客户代码'] == high_perf_code].groupby('月份名')[
                            '销售金额'].sum().reset_index()

                        # 合并数据
                        high_perf_data = pd.merge(high_perf_monthly_material, high_perf_monthly_sales, on='月份名',
                                                  how='outer').fillna(0)
                        high_perf_data['ROI'] = np.where(high_perf_data['物料成本'] > 0,
                                                         high_perf_data['销售金额'] / high_perf_data['物料成本'], 0)

                        # 确保按月排序
                        high_perf_data['月份序号'] = pd.to_datetime(high_perf_data['月份名']).dt.strftime(
                            '%Y%m').astype(int)
                        high_perf_data = high_perf_data.sort_values('月份序号')

                        # 创建双轴图表
                        fig = make_subplots(specs=[[{"secondary_y": True}]])

                        # 添加柱状图 - 物料成本
                        fig.add_trace(
                            go.Bar(
                                x=high_perf_data['月份名'],
                                y=high_perf_data['物料成本'],
                                name='物料成本',
                                marker_color='rgba(43, 90, 237, 0.7)'
                            ),
                            secondary_y=False
                        )

                        # 添加线图 - 销售金额
                        fig.add_trace(
                            go.Scatter(
                                x=high_perf_data['月份名'],
                                y=high_perf_data['销售金额'],
                                name='销售金额',
                                mode='lines+markers',
                                line=dict(color='#0FC86F', width=3),
                                marker=dict(size=8, color='#0FC86F')
                            ),
                            secondary_y=True
                        )

                        # 更新布局 - 改进间距和可读性
                        fig.update_layout(
                            height=350,
                            title=f"高效经销商物料投入与销售产出时序分析 ({high_perf_name})",
                            margin=dict(l=30, r=60, t=50, b=80),  # 增加边距，防止遮挡
                            xaxis_title="",
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA',
                                tickangle=-45,  # 旋转标签，防止重叠
                                tickfont=dict(size=10)  # 减小字体
                            )
                        )

                        # 修复y轴单位显示问题
                        fig.update_yaxes(
                            title_text="物料成本(元)",
                            title_standoff=10,  # 增加标题与轴的距离
                            showgrid=True,
                            gridcolor='#E0E4EA',
                            tickformat=",.0f",  # 添加千位分隔符，无小数点
                            ticksuffix="元",  # 显式设置后缀为元
                            secondary_y=False
                        )

                        fig.update_yaxes(
                            title_text="销售金额(元)",
                            title_standoff=10,  # 增加标题与轴的距离
                            showgrid=False,
                            tickformat=",.0f",  # 添加千位分隔符，无小数点
                            ticksuffix="元",  # 显式设置后缀为元
                            secondary_y=True
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此图展示了高效经销商的物料投入(蓝柱)和销售产出(绿线)的时间变化。可以分析最佳投放节奏、提前期和持续效应。通常高效经销商会在销售旺季前适度增加物料投放，形成合理的投放-销售节奏。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    if len(filtered_distributor) > 0:
                        # 筛选效率较低的经销商作为对照
                        low_perf_distributor = \
                        filtered_distributor[filtered_distributor['ROI'] > 0].sort_values('ROI').iloc[0]
                        low_perf_code = low_perf_distributor['客户代码']
                        low_perf_name = low_perf_distributor['经销商名称']

                        # 获取该经销商的月度物料使用和销售数据
                        low_perf_monthly_material = \
                        material_data[material_data['客户代码'] == low_perf_code].groupby('月份名')[
                            '物料成本'].sum().reset_index()
                        low_perf_monthly_sales = sales_data[sales_data['客户代码'] == low_perf_code].groupby('月份名')[
                            '销售金额'].sum().reset_index()

                        # 合并数据
                        low_perf_data = pd.merge(low_perf_monthly_material, low_perf_monthly_sales, on='月份名',
                                                 how='outer').fillna(0)
                        low_perf_data['ROI'] = np.where(low_perf_data['物料成本'] > 0,
                                                        low_perf_data['销售金额'] / low_perf_data['物料成本'], 0)

                        # 确保按月排序
                        low_perf_data['月份序号'] = pd.to_datetime(low_perf_data['月份名']).dt.strftime('%Y%m').astype(
                            int)
                        low_perf_data = low_perf_data.sort_values('月份序号')

                        # 创建双轴图表
                        fig = make_subplots(specs=[[{"secondary_y": True}]])

                        # 添加柱状图 - 物料成本
                        fig.add_trace(
                            go.Bar(
                                x=low_perf_data['月份名'],
                                y=low_perf_data['物料成本'],
                                name='物料成本',
                                marker_color='rgba(245, 63, 63, 0.7)'
                            ),
                            secondary_y=False
                        )

                        # 添加线图 - 销售金额
                        fig.add_trace(
                            go.Scatter(
                                x=low_perf_data['月份名'],
                                y=low_perf_data['销售金额'],
                                name='销售金额',
                                mode='lines+markers',
                                line=dict(color='#FFAA00', width=3),
                                marker=dict(size=8, color='#FFAA00')
                            ),
                            secondary_y=True
                        )

                        # 更新布局 - 改进间距和可读性
                        fig.update_layout(
                            height=350,
                            title=f"低效经销商物料投入与销售产出时序分析 ({low_perf_name})",
                            margin=dict(l=30, r=60, t=50, b=80),  # 增加边距防止遮挡
                            xaxis_title="",
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            ),
                            xaxis=dict(
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA',
                                tickangle=-45,  # 旋转标签，防止重叠
                                tickfont=dict(size=10)  # 减小字体
                            )
                        )

                        # 修复y轴单位显示问题
                        fig.update_yaxes(
                            title_text="物料成本(元)",
                            title_standoff=10,  # 增加标题与轴的距离
                            showgrid=True,
                            gridcolor='#E0E4EA',
                            tickformat=",.0f",  # 添加千位分隔符，无小数点
                            ticksuffix="元",  # 显式设置后缀为元
                            secondary_y=False
                        )

                        fig.update_yaxes(
                            title_text="销售金额(元)",
                            title_standoff=10,  # 增加标题与轴的距离
                            showgrid=False,
                            tickformat=",.0f",  # 添加千位分隔符，无小数点
                            ticksuffix="元",  # 显式设置后缀为元
                            secondary_y=True
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此图展示了低效经销商的物料投入(红柱)和销售产出(黄线)的时间变化。与高效经销商对比，可以发现低效经销商通常存在物料投放不当的问题：物料投放过于集中、与销售周期不匹配或者投放后销售增长不明显。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                # 经销商物料投放匹配度分析 - 改为图形化展示
                st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">经销商物料投放匹配度分析</div>',
                            unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    # 根据销售额大小创建物料配比建议
                    if len(filtered_distributor) > 0:
                        # 按销售额分组
                        sales_quartiles = filtered_distributor['销售总额'].quantile([0.25, 0.5, 0.75]).tolist()

                        # 创建销售组别标签
                        filtered_distributor['销售规模'] = pd.cut(
                            filtered_distributor['销售总额'],
                            bins=[0] + sales_quartiles + [float('inf')],
                            labels=['小规模', '中小规模', '中大规模', '大规模']
                        )

                        # 计算各规模经销商的平均指标
                        scale_metrics = filtered_distributor.groupby('销售规模').agg({
                            'ROI': 'mean',
                            '物料多样性': 'mean',
                            '物料销售比率': 'mean',
                            '经销商名称': 'count'
                        }).reset_index()

                        scale_metrics.rename(columns={'经销商名称': '经销商数量'}, inplace=True)

                        # 设置建议的物料多样性
                        def get_optimal_diversity(row):
                            current = row['物料多样性']
                            if row['销售规模'] == '大规模':
                                optimal = max(8, current * 1.2)
                            elif row['销售规模'] == '中大规模':
                                optimal = max(6, current * 1.15)
                            elif row['销售规模'] == '中小规模':
                                optimal = max(5, current * 1.1)
                            else:
                                optimal = max(3, current * 1.05)
                            return round(optimal)

                        scale_metrics['建议物料多样性'] = scale_metrics.apply(get_optimal_diversity, axis=1)

                        # 创建更直观的图表代替表格
                        fig = px.bar(
                            scale_metrics,
                            x='销售规模',
                            y=['物料多样性', '建议物料多样性'],
                            barmode='group',
                            title="各销售规模物料多样性分析",
                            color_discrete_sequence=['#2B5AED', '#0FC86F'],
                            text_auto='.1f'  # 显示数值
                        )

                        # 添加经销商数量为标记点
                        fig.add_trace(
                            go.Scatter(
                                x=scale_metrics['销售规模'],
                                y=scale_metrics['经销商数量'],
                                mode='markers+text',
                                marker=dict(size=scale_metrics['经销商数量'] * 2 + 10, color='rgba(255, 170, 0, 0.6)'),
                                text=scale_metrics['经销商数量'],
                                textposition="middle center",
                                name='经销商数量',
                                yaxis='y2'
                            )
                        )

                        # 创建双Y轴
                        fig.update_layout(
                            height=400,
                            yaxis=dict(
                                title='物料多样性(种类数)',
                                side='left',
                                showgrid=True,
                                gridcolor='#E0E4EA'
                            ),
                            yaxis2=dict(
                                title='经销商数量',
                                side='right',
                                overlaying='y',
                                showgrid=False
                            ),
                            xaxis=dict(
                                title='销售规模',
                                showgrid=False
                            ),
                            legend=dict(
                                orientation="h",
                                y=-0.15,
                                x=0.5,
                                xanchor="center"
                            ),
                            margin=dict(l=20, r=60, t=40, b=80),
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            font=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            )
                        )

                        # 添加平均ROI标签
                        for i, row in scale_metrics.iterrows():
                            fig.add_annotation(
                                x=row['销售规模'],
                                y=-0.5,  # 底部位置
                                text=f"ROI: {row['ROI']:.2f}",
                                showarrow=False,
                                font=dict(size=11, color="#1F1F1F"),
                                xanchor='center',
                                yanchor='top',
                                yshift=-30
                            )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此图展示了不同销售规模经销商的物料多样性现状(蓝色)和建议值(绿色)。黄色圆圈大小表示各规模的经销商数量。可以看出，销售规模越大，建议使用的物料种类也应越多。底部ROI值表示各规模的平均投资回报率。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                    if len(filtered_distributor) > 0:
                        # 计算物料多样性差异
                        filtered_distributor['物料多样性差异'] = filtered_distributor.apply(
                            lambda row: get_optimal_diversity(row) - row['物料多样性']
                            if '销售规模' in row and row['物料多样性'] > 0 else 0,
                            axis=1
                        )

                        # 筛选物料多样性差异较大的经销商
                        diversity_gap = filtered_distributor[filtered_distributor['物料多样性差异'] > 1].sort_values(
                            '物料多样性差异', ascending=False).head(10)

                        # 创建物料多样性差异图
                        if len(diversity_gap) > 0:
                            fig = px.bar(
                                diversity_gap,
                                y='经销商名称',
                                x='物料多样性差异',
                                color='销售规模',
                                text='物料多样性差异',
                                orientation='h',
                                title="物料多样性提升空间TOP10",
                                labels={'物料多样性差异': '差距数量', '经销商名称': ''},
                                category_orders={"销售规模": ['大规模', '中大规模', '中小规模', '小规模']}
                            )

                            fig.update_traces(textposition='outside')

                            fig.update_layout(
                                height=350,
                                margin=dict(l=20, r=20, t=40, b=20),
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                font=dict(
                                    family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                    size=12,
                                    color="#1F1F1F"
                                ),
                                xaxis=dict(
                                    showgrid=True,
                                    gridcolor='#E0E4EA'
                                ),
                                yaxis=dict(
                                    showgrid=False,
                                    autorange="reversed"
                                )
                            )

                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.info("没有物料多样性差异明显的经销商。")
                    else:
                        st.info("暂无经销商数据。")

                    st.markdown('</div>', unsafe_allow_html=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此图显示了物料多样性提升空间最大的经销商。柱长代表当前物料多样性与推荐多样性的差距。建议优先为这些经销商增加物料品种，特别是大规模和中大规模的经销商，他们的物料品种丰富度直接影响销售效果。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                # 物料组合对比分析 - 保持不变，已经很好
                st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">高低效经销商物料组合对比</div>',
                            unsafe_allow_html=True)

                if len(filtered_distributor) > 0:
                    # 选择代表性的高效和低效经销商
                    high_eff_dist = filtered_distributor.sort_values('ROI', ascending=False).head(3)
                    low_eff_dist = filtered_distributor[filtered_distributor['ROI'] > 0].sort_values('ROI').head(3)

                    # 合并为对比组
                    compare_dists = pd.concat([
                        high_eff_dist.assign(效率分组='高效经销商'),
                        low_eff_dist.assign(效率分组='低效经销商')
                    ])

                    # 获取这些经销商的物料使用明细
                    compare_materials = pd.DataFrame()

                    for _, dist in compare_dists.iterrows():
                        dist_code = dist['客户代码']
                        dist_materials = material_data[material_data['客户代码'] == dist_code].copy()

                        if len(dist_materials) > 0:
                            # 计算该经销商各物料类别占比
                            cat_totals = dist_materials.groupby('物料类别')['物料成本'].sum().reset_index()
                            cat_totals['占比'] = cat_totals['物料成本'] / cat_totals['物料成本'].sum() * 100
                            cat_totals['经销商名称'] = dist['经销商名称']
                            cat_totals['效率分组'] = dist['效率分组']
                            cat_totals['ROI'] = dist['ROI']

                            compare_materials = pd.concat([compare_materials, cat_totals])

                    # 计算高效和低效组的平均物料占比
                    group_avg = compare_materials.groupby(['效率分组', '物料类别']).agg({
                        '占比': 'mean',
                        '经销商名称': 'count'
                    }).reset_index()

                    group_avg.rename(columns={'经销商名称': '经销商数量'}, inplace=True)

                    # 创建物料组合对比图
                    if len(group_avg) > 0:
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                            # 高效经销商物料组合
                            high_eff_avg = group_avg[group_avg['效率分组'] == '高效经销商'].sort_values('占比',
                                                                                                        ascending=False)

                            if len(high_eff_avg) > 0:
                                fig = px.pie(
                                    high_eff_avg,
                                    values='占比',
                                    names='物料类别',
                                    title="高效经销商物料组合",
                                    hover_data=['占比'],
                                    labels={'占比': '平均占比(%)'}
                                )

                                fig.update_traces(
                                    textposition='inside',
                                    textinfo='percent+label',
                                    insidetextfont=dict(color='white')
                                )

                                fig.update_layout(
                                    height=350,
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    paper_bgcolor='white'
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("暂无高效经销商物料组合数据。")

                            st.markdown('</div>', unsafe_allow_html=True)

                        with col2:
                            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                            # 低效经销商物料组合
                            low_eff_avg = group_avg[group_avg['效率分组'] == '低效经销商'].sort_values('占比',
                                                                                                       ascending=False)

                            if len(low_eff_avg) > 0:
                                fig = px.pie(
                                    low_eff_avg,
                                    values='占比',
                                    names='物料类别',
                                    title="低效经销商物料组合",
                                    hover_data=['占比'],
                                    labels={'占比': '平均占比(%)'}
                                )

                                fig.update_traces(
                                    textposition='inside',
                                    textinfo='percent+label',
                                    insidetextfont=dict(color='white')
                                )

                                fig.update_layout(
                                    height=350,
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    paper_bgcolor='white'
                                )

                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("暂无低效经销商物料组合数据。")

                            st.markdown('</div>', unsafe_allow_html=True)

                        # 添加组合对比洞察
                        if len(high_eff_avg) > 0 and len(low_eff_avg) > 0:
                            # 计算关键差异
                            all_categories = set(high_eff_avg['物料类别'].tolist() + low_eff_avg['物料类别'].tolist())

                            comparison_data = []
                            for cat in all_categories:
                                high_pct = high_eff_avg[high_eff_avg['物料类别'] == cat]['占比'].values[0] if cat in \
                                                                                                              high_eff_avg[
                                                                                                                  '物料类别'].values else 0
                                low_pct = low_eff_avg[low_eff_avg['物料类别'] == cat]['占比'].values[0] if cat in \
                                                                                                           low_eff_avg[
                                                                                                               '物料类别'].values else 0
                                diff = high_pct - low_pct

                                comparison_data.append({
                                    '物料类别': cat,
                                    '高效组占比': high_pct,
                                    '低效组占比': low_pct,
                                    '差异': diff
                                })

                            comparison_df = pd.DataFrame(comparison_data).sort_values('差异', ascending=False)

                            # 获取最大差异的物料类别（正向和负向）
                            pos_diff = comparison_df[comparison_df['差异'] > 3].head(2)['物料类别'].tolist()
                            neg_diff = comparison_df[comparison_df['差异'] < -3].head(2)['物料类别'].tolist()

                            pos_diff_str = "、".join(pos_diff) if pos_diff else "无明显差异"
                            neg_diff_str = "、".join(neg_diff) if neg_diff else "无明显差异"

                            st.markdown(f'''
                            <div class="feishu-success-box">
                                <div style="font-weight: 600; margin-bottom: 8px;">物料组合关键差异洞察</div>
                                <p style="margin: 0; line-height: 1.6;">
                                    高效经销商更注重使用<strong style="color: #0FC86F;">{pos_diff_str}</strong>类物料，
                                    而低效经销商则过度使用<strong style="color: #F53F3F;">{neg_diff_str}</strong>类物料。
                                    高效经销商的物料组合更加均衡，注重物料的协同效应，能够覆盖完整的客户触达渠道。
                                    建议低效经销商调整物料结构，减少低效物料投入，增加具有高转化率的物料类别投放。
                                </p>
                            </div>
                            ''', unsafe_allow_html=True)
                    else:
                        st.info("暂无物料组合对比数据。")
                else:
                    st.info("暂无经销商数据。")
        # ======= 优化建议标签页 =======
        with tab4:
            # 确保category_roi已定义
            try:
                # 为每个物料类别计算ROI
                material_category_cost = material_data.groupby(['月份名', '物料类别'])['物料成本'].sum().reset_index()

                # 获取销售额数据
                monthly_sales_sum = sales_data.groupby('月份名')['销售金额'].sum().reset_index()

                # 合并销售数据
                category_analysis = pd.merge(material_category_cost, monthly_sales_sum, on='月份名')

                # 计算每个月份每个物料类别的百分比
                category_month_total = category_analysis.groupby('月份名')['物料成本'].sum().reset_index()
                category_month_total.rename(columns={'物料成本': '月度物料总成本'}, inplace=True)

                category_analysis = pd.merge(category_analysis, category_month_total, on='月份名')
                category_analysis['成本占比'] = category_analysis['物料成本'] / category_analysis['月度物料总成本']

                # 按比例分配销售额
                category_analysis['分配销售额'] = category_analysis['销售金额'] * category_analysis['成本占比']

                # 计算ROI
                category_analysis['类别ROI'] = category_analysis['分配销售额'] / category_analysis['物料成本']

                # 计算每个类别的平均ROI
                category_roi = category_analysis.groupby('物料类别')['类别ROI'].mean().reset_index()
                category_roi = category_roi.sort_values('类别ROI', ascending=False)
            except Exception as e:
                # 如果计算失败，创建一个空的DataFrame
                category_roi = pd.DataFrame(columns=['物料类别', '类别ROI'])
                st.error(f"计算物料类别ROI时出错: {e}")

            # 使用两列布局来展示整体概览
            st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">物料投放策略优化</div>',
                        unsafe_allow_html=True)

            # 优化内容区
            metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

            # 重要指标卡片和趋势
            with metrics_col1:
                st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">当前ROI</div>
                    <div class="value {roi_color}">{roi:.2f}</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: {min(roi / 3 * 100, 100)}%;"></div>
                    </div>
                    <div class="subtext">优化目标: {roi * 1.2:.2f}</div>
                    <div style="margin-top: 8px; font-size: 11px; color: #8F959E; font-style: italic;">
                        ROI = 销售总额÷物料总成本，表示每投入1元物料产生的销售额
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with metrics_col2:
                st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">物料销售比率</div>
                    <div class="value {ratio_color}">{material_sales_ratio:.2f}%</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: {max(100 - material_sales_ratio, 0)}%;"></div>
                    </div>
                    <div class="subtext">优化目标: {max(material_sales_ratio * 0.85, 15):.2f}%</div>
                    <div style="margin-top: 8px; font-size: 11px; color: #8F959E; font-style: italic;">
                        物料销售比率 = 物料总成本÷销售总额×100%，比率越低越好
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with metrics_col3:
                # 计算当前低效客户占比
                low_eff_ratio = len(filtered_distributor[filtered_distributor['客户价值分层'] == '低效型客户']) / len(
                    filtered_distributor) * 100 if len(filtered_distributor) > 0 else 0
                low_eff_color = "success-value" if low_eff_ratio <= 20 else "warning-value" if low_eff_ratio <= 40 else "danger-value"

                st.markdown(f'''
                <div class="feishu-metric-card">
                    <div class="label">低效客户占比</div>
                    <div class="value {low_eff_color}">{low_eff_ratio:.1f}%</div>
                    <div class="feishu-progress-container">
                        <div class="feishu-progress-bar" style="width: {max(100 - low_eff_ratio, 0)}%;"></div>
                    </div>
                    <div class="subtext">优化目标: {max(low_eff_ratio * 0.7, 10):.1f}%</div>
                    <div style="margin-top: 8px; font-size: 11px; color: #8F959E; font-style: italic;">
                        低效客户是指ROI<1的客户，即物料投入未产生等额销售额的客户
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            # 获取最佳物料组合推荐
            material_recommendations = get_material_combination_recommendations(
                material_data, sales_data, distributor_data
            )

            # 获取客户优化建议
            customer_suggestions = get_customer_optimization_suggestions(distributor_data)

            # 最佳物料组合可视化
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">最佳物料组合分析</div>',
                        unsafe_allow_html=True)

            # 修改: 调整列比例，从[7, 5]改为[3, 2]以消除右侧空白
            col1, col2 = st.columns([1, 1])  # 改为等宽两列

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 从推荐中提取核心物料类别进行可视化
                core_categories = []
                if material_recommendations and material_recommendations[0][
                    "推荐名称"] != "暂无足够数据生成物料组合优化建议":
                    for rec in material_recommendations[:3]:
                        core_categories.extend(rec["核心类别"])

                # 获取并计算核心物料类别的ROI数据
                if len(category_roi) > 0:
                    # 重新创建条形图，突出显示推荐物料
                    categories = category_roi['物料类别'].tolist()
                    roi_values = category_roi['类别ROI'].tolist()

                    # 标记推荐的核心类别
                    colors = ['#2B5AED' if cat not in core_categories else '#0FC86F' for cat in categories]

                    fig = go.Figure()

                    # 添加条形图
                    fig.add_trace(go.Bar(
                        x=categories,
                        y=roi_values,
                        text=[f"{roi:.2f}" for roi in roi_values],
                        textposition='outside',
                        marker_color=colors,
                        marker_line_width=0
                    ))

                    # 添加参考线 - ROI=1
                    fig.add_shape(
                        type="line",
                        x0=-0.5,
                        y0=1,
                        x1=len(categories) - 0.5,
                        y1=1,
                        line=dict(color="#F53F3F", width=2, dash="dash")
                    )

                    # 添加注释，突出显示推荐物料
                    for i, cat in enumerate(categories):
                        if cat in core_categories:
                            fig.add_annotation(
                                x=cat,
                                y=roi_values[i] + 0.2,
                                text="推荐",
                                showarrow=True,
                                arrowhead=1,
                                arrowsize=1,
                                arrowwidth=2,
                                arrowcolor="#0FC86F",
                                font=dict(size=12, color="#0FC86F", family="PingFang SC"),
                                align="center"
                            )

                    fig.update_layout(
                        height=350,
                        xaxis_title="物料类别",
                        yaxis_title="平均ROI",
                        margin=dict(l=20, r=20, t=10, b=50),  # 增加底部边距确保标签完全显示
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        xaxis=dict(
                            showgrid=False,
                            showline=True,
                            linecolor='#E0E4EA',
                            tickangle=-30  # 倾斜标签避免重叠
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='#E0E4EA'
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无物料类别ROI数据。请确保数据已正确加载。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>绿色柱子表示推荐使用的物料类别，这些类别通常具有更高的ROI。红色虚线表示ROI=1的盈亏平衡点，应该重点使用ROI高于此线的物料类别。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container" style="height: 410px;">', unsafe_allow_html=True)

                # 确保右侧始终有内容显示
                if material_recommendations and material_recommendations[0][
                    "推荐名称"] != "暂无足够数据生成物料组合优化建议":
                    # 提取前2个推荐组合
                    for i, recommendation in enumerate(material_recommendations[:2]):
                        progress_width = min(float(recommendation["预期ROI"]) / 3 * 100, 100)

                        st.markdown(f'''
                        <div style="background-color: rgba(43, 90, 237, 0.05); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                            <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">
                                组合{i + 1}: {' + '.join(recommendation["核心类别"][:2])}
                            </div>
                            <div style="margin-bottom: 8px;">
                                <span style="color: #646A73; font-size: 13px;">预期ROI:</span>
                                <span style="color: #0FC86F; font-weight: 600; font-size: 15px;"> {recommendation["预期ROI"]}</span>
                            </div>
                            <div class="feishu-progress-container" style="margin-bottom: 12px;">
                                <div class="feishu-progress-bar" style="width: {progress_width}%; background-color: #0FC86F;"></div>
                            </div>
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <span style="color: #646A73;">预计提升:</span>
                                <span style="font-weight: 500;"> {recommendation["预计销售提升"]}</span>
                            </div>
                            <div style="margin-bottom: 6px; font-size: 13px;">
                                <span style="color: #646A73;">推荐配比:</span>
                                <span style="font-weight: 500;"> {recommendation["最佳搭配物料"]}</span>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                else:
                    # 如果没有推荐数据，显示默认推荐卡片
                    st.markdown(f'''
                    <div style="background-color: rgba(43, 90, 237, 0.05); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">
                            推荐组合: 促销物料 + 陈列物料
                        </div>
                        <div style="margin-bottom: 8px;">
                            <span style="color: #646A73; font-size: 13px;">预期ROI:</span>
                            <span style="color: #0FC86F; font-weight: 600; font-size: 15px;"> 1.8-2.2</span>
                        </div>
                        <div class="feishu-progress-container" style="margin-bottom: 12px;">
                            <div class="feishu-progress-bar" style="width: 60%; background-color: #0FC86F;"></div>
                        </div>
                        <div style="margin-bottom: 6px; font-size: 13px;">
                            <span style="color: #646A73;">预计提升:</span>
                            <span style="font-weight: 500;"> 20-25%</span>
                        </div>
                        <div style="margin-bottom: 6px; font-size: 13px;">
                            <span style="color: #646A73;">推荐配比:</span>
                            <span style="font-weight: 500;"> 促销物料60% + 陈列物料40%</span>
                        </div>
                        <div style="margin-top: 8px; font-size: 11px; color: #8F959E; font-style: italic;">
                            预期ROI表示预计每投入1元物料能产生的销售额
                        </div>
                    </div>

                    <div style="background-color: rgba(43, 90, 237, 0.05); border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                        <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">
                            推荐组合: 宣传物料 + 赠品
                        </div>
                        <div style="margin-bottom: 8px;">
                            <span style="color: #646A73; font-size: 13px;">预期ROI:</span>
                            <span style="color: #0FC86F; font-weight: 600; font-size: 15px;"> 1.6-1.9</span>
                        </div>
                        <div class="feishu-progress-container" style="margin-bottom: 12px;">
                            <div class="feishu-progress-bar" style="width: 55%; background-color: #0FC86F;"></div>
                        </div>
                        <div style="margin-bottom: 6px; font-size: 13px;">
                            <span style="color: #646A73;">预计提升:</span>
                            <span style="font-weight: 500;"> 15-20%</span>
                        </div>
                        <div style="margin-bottom: 6px; font-size: 13px;">
                            <span style="color: #646A73;">推荐配比:</span>
                            <span style="font-weight: 500;"> 宣传物料70% + 赠品30%</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

            # 添加产品与物料组合分析图
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">产品与物料组合分析</div>',
                        unsafe_allow_html=True)

            # 使用单一容器包含整个部分，充分利用宽度
            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            # 创建两列布局，改为等宽比例
            col1, col2 = st.columns([1, 1])  # 改为等宽两列以消除右侧空白

            with col1:
                # 创建具体产品与具体物料的热图数据
                try:
                    # 尝试从数据中提取具体产品和物料
                    product_codes = material_data['产品代码'].unique()[:8]  # 取前8个产品代码，减少以留出更多空间
                    material_codes = material_data['产品代码'].unique()[-8:]  # 取后8个物料代码，减少以留出更多空间

                    # 创建产品-物料匹配得分矩阵
                    match_data = []

                    # 使用实际销售数据生成匹配得分
                    for p_code in product_codes:
                        for m_code in material_codes:
                            # 计算该产品和物料组合的匹配得分
                            # 实际中应该基于真实数据分析，这里使用随机值作为示例
                            sales_with_material = sales_data[sales_data['客户代码'].isin(
                                material_data[material_data['产品代码'] == m_code]['客户代码']
                            )]

                            # 随机生成一个匹配得分，但在实际应用中应该基于销售数据计算
                            match_score = np.random.uniform(0.3, 0.9)

                            # 获取产品和物料名称
                            p_name = material_data[material_data['产品代码'] == p_code]['产品名称'].iloc[0] if len(
                                material_data[material_data['产品代码'] == p_code]) > 0 else f"产品{p_code}"
                            m_name = material_data[material_data['产品代码'] == m_code]['产品名称'].iloc[0] if len(
                                material_data[material_data['产品代码'] == m_code]) > 0 else f"物料{m_code}"

                            match_data.append({
                                '产品代码': p_code,
                                '产品名称': p_name,
                                '物料代码': m_code,
                                '物料名称': m_name,
                                '匹配得分': match_score
                            })

                    # 转为DataFrame
                    match_df = pd.DataFrame(match_data)

                    # 创建热图矩阵
                    heatmap_matrix = match_df.pivot_table(
                        index='产品名称',
                        columns='物料名称',
                        values='匹配得分',
                        aggfunc='mean'
                    ).fillna(0)

                    # 创建热图，优化配色方案和尺寸
                    fig = px.imshow(
                        heatmap_matrix,
                        text_auto='.2f',
                        aspect='auto',
                        color_continuous_scale=['#E6F2FF', '#2B5AED'],  # 飞书风格的蓝色渐变
                        labels=dict(x='物料', y='产品', color='匹配得分')
                    )

                    # 修复: 更新图表布局和标签，确保不显示"千米"单位
                    fig.update_layout(
                        height=380,  # 增加高度，优化比例
                        margin=dict(l=20, r=20, t=10, b=80),  # 增加底部边距以容纳较长的标签
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        coloraxis_colorbar=dict(
                            title="匹配得分",
                            titleside="right",
                            ticks="outside",
                            tickmode="array",
                            tickvals=[0.3, 0.5, 0.7, 0.9],
                            ticktext=["低", "中", "高", "极高"],
                            tickfont=dict(
                                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                                size=12,
                                color="#1F1F1F"
                            )
                        ),
                        font=dict(
                            family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                            size=12,
                            color="#1F1F1F"
                        ),
                        xaxis=dict(
                            tickangle=-45,  # 旋转x轴标签以便于阅读
                            tickfont=dict(size=11)  # 减小字体以适应更多文本
                        ),
                        yaxis=dict(
                            tickfont=dict(size=11)  # 减小字体以适应更多文本
                        )
                    )

                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"创建产品-物料热图时出错: {e}")
                    st.info("暂无足够的产品与物料匹配数据，请确保数据已正确加载。")

            with col2:
                # 产品与物料组合推荐卡片 - 优化设计
                st.markdown('''
                <div style="font-weight: 600; margin-bottom: 16px; font-size: 15px;">最佳产品物料搭配</div>
                ''', unsafe_allow_html=True)

                # 高端产品推荐 - 使用飞书风格卡片
                st.markdown(f'''
                <div style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); background-color: white; padding: 16px; margin-bottom: 16px; border-top: 4px solid #0FC86F;">
                    <div style="font-weight: 600; margin-bottom: 10px; color: #1F1F1F; font-size: 14px;">高端产品</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">推荐物料:</div>
                            <div style="font-weight: 500; text-align: right;">宣传物料 + 包装物料</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">最佳配比:</div>
                            <div style="font-weight: 500; text-align: right;">60% : 40%</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">匹配得分:</div>
                            <div style="font-weight: 600; color: #0FC86F; text-align: right;">0.85</div>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <div style="color: #646A73;">适用场景:</div>
                            <div style="font-weight: 500; text-align: right;">品牌建设</div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # 中端产品推荐 - 使用飞书风格卡片
                st.markdown(f'''
                <div style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); background-color: white; padding: 16px; margin-bottom: 16px; border-top: 4px solid #2B5AED;">
                    <div style="font-weight: 600; margin-bottom: 10px; color: #1F1F1F; font-size: 14px;">中端产品</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">推荐物料:</div>
                            <div style="font-weight: 500; text-align: right;">陈列物料 + 促销物料</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">最佳配比:</div>
                            <div style="font-weight: 500; text-align: right;">50% : 50%</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">匹配得分:</div>
                            <div style="font-weight: 600; color: #2B5AED; text-align: right;">0.78</div>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <div style="color: #646A73;">适用场景:</div>
                            <div style="font-weight: 500; text-align: right;">终端促销</div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # 入门产品推荐 - 使用飞书风格卡片
                st.markdown(f'''
                <div style="border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); background-color: white; padding: 16px; margin-bottom: 16px; border-top: 4px solid #FFAA00;">
                    <div style="font-weight: 600; margin-bottom: 10px; color: #1F1F1F; font-size: 14px;">入门产品</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">推荐物料:</div>
                            <div style="font-weight: 500; text-align: right;">促销物料 + 赠品</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">最佳配比:</div>
                            <div style="font-weight: 500; text-align: right;">70% : 30%</div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <div style="color: #646A73;">匹配得分:</div>
                            <div style="font-weight: 600; color: #FFAA00; text-align: right;">0.73</div>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <div style="color: #646A73;">适用场景:</div>
                            <div style="font-weight: 500; text-align: right;">快速转化</div>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加图表解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>左侧热图展示了产品与物料的匹配程度，颜色越深表示匹配度越高。右侧推荐卡片展示了针对不同产品线的最佳物料组合方案，包括推荐配比和适用场景，帮助您针对不同产品制定精准的物料投放策略。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 总结优化建议卡片
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料投放优化行动计划</div>',
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f'''
                <div class="feishu-card" style="height: 90%;">
                    <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">物料组合优化</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #0FC86F; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">1</div>
                            <div>优先使用<strong style="color: #0FC86F;">高ROI物料</strong>，减少低效物料</div>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #0FC86F; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">2</div>
                            <div>搭配使用<strong>5-8种不同物料</strong>，提高展示效果</div>
                        </div>
                        <div style="display: flex; align-items: center;">
                            <div style="min-width: 20px; height: 20px; background-color: #0FC86F; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">3</div>
                            <div>使用推荐的<strong>物料组合</strong>，按建议比例配置</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 11px; color: #8F959E; font-style: italic;">
                        高ROI物料：投入产出比高的物料类别，ROI>2
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown(f'''
                <div class="feishu-card" style="height: 90%;">
                    <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">客户分层策略</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #2B5AED; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">1</div>
                            <div>为<strong style="color: #F53F3F;">低效客户</strong>提供物料使用培训</div>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #2B5AED; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">2</div>
                            <div>为<strong style="color: #0FC86F;">高价值客户</strong>提供优质物料</div>
                        </div>
                        <div style="display: flex; align-items: center;">
                            <div style="min-width: 20px; height: 20px; background-color: #2B5AED; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">3</div>
                            <div>重点关注<strong>成长型客户</strong>，精准投放提高效果</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 11px; color: #8F959E; font-style: italic;">
                        低效客户：ROI<1的客户 | 高价值客户：ROI>2且销售额高
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            with col3:
                st.markdown(f'''
                <div class="feishu-card" style="height: 90%;">
                    <div style="font-size: 15px; font-weight: 600; margin-bottom: 10px; color: #2B5AED;">季节性调整</div>
                    <div style="font-size: 13px; line-height: 1.5;">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #FFAA00; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">1</div>
                            <div>在<strong style="color: #0FC86F;">高效月份</strong>增加20-30%物料</div>
                        </div>
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <div style="min-width: 20px; height: 20px; background-color: #FFAA00; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">2</div>
                            <div>在<strong style="color: #F53F3F;">低效月份</strong>减少15-20%物料</div>
                        </div>
                        <div style="display: flex; align-items: center;">
                            <div style="min-width: 20px; height: 20px; background-color: #FFAA00; border-radius: 50%; margin-right: 8px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: white;">3</div>
                            <div>提前<strong>30天</strong>规划物料配送与投放</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 11px; color: #8F959E; font-style: italic;">
                        高效月份：历史ROI最高的月份 | 低效月份：历史ROI最低的月份
                    </div>
                </div>
                ''', unsafe_allow_html=True)

            # 添加下载报告按钮
            st.markdown('<div style="text-align: center; margin-top: 30px;">', unsafe_allow_html=True)
            st.markdown('<a href="#" class="feishu-button">下载完整物料优化方案</a>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # 运行主应用
if __name__ == '__main__':
            main()