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
    sample_data = False

    if sample_data:
        return generate_sample_data()
    else:
        try:
            # 移除这些提示信息
            file_paths = ["2025物料源数据.xlsx", "25物料源销售数据.xlsx", "物料单价.xlsx"]

            try:
                material_data = pd.read_excel("2025物料源数据.xlsx")
            except Exception as e1:
                st.error(f"× 加载 2025物料源数据.xlsx 失败: {e1}")
                raise

            try:
                sales_data = pd.read_excel("25物料源销售数据.xlsx")
            except Exception as e2:
                st.error(f"× 加载 25物料源销售数据.xlsx 失败: {e2}")
                raise

            try:
                material_price = pd.read_excel("物料单价.xlsx")

                # 处理物料单价表中的重复列问题
                if '物料类别' in material_price.columns and material_price.columns.tolist().count('物料类别') > 1:
                    # 重命名第二个物料类别列
                    column_names = material_price.columns.tolist()
                    duplicate_index = column_names.index('物料类别', column_names.index('物料类别') + 1)
                    new_column_names = column_names.copy()
                    new_column_names[duplicate_index] = '物料类别_描述'
                    material_price.columns = new_column_names
                    st.info("物料单价表中'物料类别'列出现多次，已将第二个重命名为'物料类别_描述'")

            except Exception as e3:
                st.error(f"× 加载 物料单价.xlsx 失败: {e3}")
                raise

            # 数据验证
            validate_data_columns(material_data, sales_data, material_price)

            return process_data(material_data, sales_data, material_price)

        except Exception as e:
            st.error(f"加载数据时出错: {e}")
            # 可以保留错误提示，因为这是必要的
            use_sample = st.button("使用示例数据继续")
            if use_sample:
                return generate_sample_data()
            else:
                st.stop()

# 在FEISHU_STYLE常量之后添加此函数
def set_global_font_styles(base_size=14, title_size=20, subtitle_size=16, chart_title_size=15,
                           text_size=13, small_text_size=12,
                           font_family="'PingFang SC', 'Helvetica Neue', Arial, sans-serif"):
    """设置全局字体样式，统一控制整个应用的字体大小

    参数:
        base_size (int): 基础字体大小，其他尺寸会按比例调整
        title_size (int): 主标题字体大小
        subtitle_size (int): 副标题字体大小
        chart_title_size (int): 图表标题字体大小
        text_size (int): 正文字体大小
        small_text_size (int): 小字体大小
        font_family (str): 字体系列
    """

    css = f"""
    <style>
        /* 全局字体设置 */
        html, body, [class*="st-"], .stMarkdown, .stText, p, div, h1, h2, h3, h4, h5, h6 {{
            font-family: {font_family};
            font-size: {base_size}px;
        }}

        /* 主标题样式 */
        .feishu-title {{
            font-size: {title_size}px !important;
            font-weight: 600;
            color: var(--feishu-text);
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }}

        /* 副标题样式 */
        .feishu-subtitle {{
            font-size: {subtitle_size}px !important;
            color: var(--feishu-text-secondary);
            margin-bottom: 24px;
            letter-spacing: 0.1px;
            line-height: 1.4;
        }}

        /* 图表标题 */
        .feishu-chart-title {{
            font-size: {chart_title_size}px !important;
            font-weight: 600;
            color: var(--feishu-text);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            line-height: 1.4;
        }}

        /* 表格和图表内容字体 */
        .plotly-graph-div text, .dataframe th, .dataframe td {{
            font-size: {text_size}px !important;
        }}

        /* 指标卡片样式调整 */
        .feishu-metric-card .label {{
            font-size: {small_text_size}px !important;
        }}

        .feishu-metric-card .value {{
            font-size: {title_size + 2}px !important;
        }}

        .feishu-metric-card .subtext {{
            font-size: {small_text_size - 1}px !important;
        }}

        /* 图表解读框 */
        .chart-explanation {{
            font-size: {small_text_size}px !important;
        }}

        .chart-explanation-title {{
            font-size: {small_text_size + 1}px !important;
        }}

        /* 侧边栏样式 */
        .sidebar-filter-heading {{
            font-size: {small_text_size}px !important;
        }}

        .sidebar-selection-info {{
            font-size: {small_text_size - 1}px !important;
        }}

        .sidebar-filter-description, .sidebar-badge {{
            font-size: {small_text_size - 2}px !important;
        }}

        /* 数据表格样式 */
        .dataframe th {{
            font-size: {small_text_size}px !important;
        }}

        .dataframe td {{
            font-size: {small_text_size - 1}px !important;
        }}

        /* 洞察框和提示框 */
        .feishu-insight-box, .feishu-tip-box, .feishu-warning-box, .feishu-success-box {{
            font-size: {small_text_size}px !important;
        }}

        /* 标签样式 */
        .feishu-tag {{
            font-size: {small_text_size - 2}px !important;
        }}

        /* 按钮样式 */
        .feishu-button {{
            font-size: {small_text_size}px !important;
        }}

        /* 修复Streamlit原生组件 */
        .stSelectbox label, .stSlider label, .stCheckbox label {{
            font-size: {small_text_size}px !important;
        }}

        .stMultiSelect span, .stSelectbox span {{
            font-size: {small_text_size - 1}px !important;
        }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


def process_data(material_data, sales_data, material_price):
    """处理和准备数据 - 修改为基于客户代码+月份的匹配策略"""

    # 确保日期列为日期类型
    material_data['发运月份'] = pd.to_datetime(material_data['发运月份'])
    sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

    # 将申请人列映射为销售人员列
    if '申请人' in material_data.columns and '销售人员' not in material_data.columns:
        material_data['销售人员'] = material_data['申请人']
    if '申请人' in sales_data.columns and '销售人员' not in sales_data.columns:
        sales_data['销售人员'] = sales_data['申请人']

    # 创建月份和年份列
    for df in [material_data, sales_data]:
        df['月份'] = df['发运月份'].dt.month
        df['年份'] = df['发运月份'].dt.year
        df['月份名'] = df['发运月份'].dt.strftime('%Y-%m')
        df['季度'] = df['发运月份'].dt.quarter
        df['月度名称'] = df['发运月份'].dt.strftime('%m月')

    # 计算物料成本
    if '物料成本' not in material_data.columns:
        # 合并物料单价数据 - 修复：使用物料代码匹配
        material_data = pd.merge(
            material_data,
            material_price[['物料代码', '单价（元）']],
            on='物料代码',  # 修复：直接用物料代码匹配，而非之前的产品代码
            how='left'
        )

        # 填充缺失的物料价格
        if '单价（元）' in material_data.columns:
            mean_price = material_price['单价（元）'].mean()
            material_data['单价（元）'] = material_data['单价（元）'].fillna(mean_price)
            # 计算物料总成本 - 修复：使用求和项:数量而非求和项:数量（箱）
            material_data['物料成本'] = material_data['求和项:数量'] * material_data['单价（元）']
        else:
            # 如果合并失败，创建一个默认的物料成本列
            material_data['物料成本'] = material_data['求和项:数量'] * 100  # 修复：使用求和项:数量

    # 计算销售金额 - 销售数据确实是按箱计算的，所以这里保持不变
    if '销售金额' not in sales_data.columns and '求和项:单价（箱）' in sales_data.columns:
        sales_data['销售金额'] = sales_data['求和项:数量（箱）'] * sales_data['求和项:单价（箱）']

    # 确保销售人员和经销商列存在
    for col, default in [('销售人员', '未知销售人员'), ('经销商名称', '未知经销商')]:
        for df in [material_data, sales_data]:
            if col not in df.columns:
                df[col] = default

    # 按客户代码和月份聚合数据 - 修改为按客户匹配而非产品
    material_by_customer = material_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员', '所属区域', '省份'])[
        '物料成本'].sum().reset_index()
    material_by_customer.rename(columns={'物料成本': '物料总成本'}, inplace=True)

    sales_by_customer = sales_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员', '所属区域', '省份'])[
        '销售金额'].sum().reset_index()
    sales_by_customer.rename(columns={'销售金额': '销售总额'}, inplace=True)

    # 合并客户级别的物料和销售数据
    common_cols = ['客户代码', '经销商名称', '月份名']
    distributor_data = pd.merge(
        material_by_customer,
        sales_by_customer,
        on=common_cols,
        how='outer'
    ).fillna(0)

    # 处理可能的列冲突（如销售人员_x, 销售人员_y）
    for col in ['销售人员', '所属区域', '省份']:
        if f'{col}_x' in distributor_data.columns and f'{col}_y' in distributor_data.columns:
            # 优先使用非空值
            distributor_data[col] = distributor_data[f'{col}_x'].combine_first(distributor_data[f'{col}_y'])
            distributor_data.drop([f'{col}_x', f'{col}_y'], axis=1, inplace=True)

    # 计算ROI
    distributor_data['ROI'] = np.where(
        distributor_data['物料总成本'] > 0,
        distributor_data['销售总额'] / distributor_data['物料总成本'],
        0
    )
    # 限制ROI的极端值
    distributor_data['ROI'] = distributor_data['ROI'].clip(upper=5.0)

    # 计算物料销售比率
    distributor_data['物料销售比率'] = np.where(
        distributor_data['销售总额'] > 0,
        (distributor_data['物料总成本'] / distributor_data['销售总额']) * 100,
        0
    )
    # 限制物料销售比率的极端值
    distributor_data['物料销售比率'] = distributor_data['物料销售比率'].clip(upper=100)

    # 计算物料多样性 - 基于客户的物料多样性 - 修复：使用物料代码而非产品代码
    material_diversity = material_data.groupby(['客户代码', '月份名'])['物料代码'].nunique().reset_index()
    material_diversity.rename(columns={'物料代码': '物料多样性'}, inplace=True)

    # 合并物料多样性到经销商数据
    distributor_data = pd.merge(
        distributor_data,
        material_diversity,
        on=['客户代码', '月份名'],
        how='left'
    )
    distributor_data['物料多样性'] = distributor_data['物料多样性'].fillna(0)

    # 经销商价值分层（基于合并后的客户级别数据）
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

    return material_data, sales_data, material_price, distributor_data


def validate_data_columns(material_data, sales_data, material_price):
    """验证数据列名是否符合预期"""

    # 检查物料数据
    material_required_cols = ['物料代码', '求和项:数量', '客户代码', '经销商名称', '发运月份']
    missing_material_cols = [col for col in material_required_cols if col not in material_data.columns]
    if missing_material_cols:
        st.warning(f"物料数据缺少必要列: {', '.join(missing_material_cols)}")
        # 检查是否有类似的列名
        for missing_col in missing_material_cols:
            if missing_col == '求和项:数量':
                if '求和项:数量（箱）' in material_data.columns:
                    st.info("找到替代列 '求和项:数量（箱）'，将使用此列")
                    material_data.rename(columns={'求和项:数量（箱）': '求和项:数量'}, inplace=True)
            elif missing_col == '物料代码':
                if '产品代码' in material_data.columns:
                    st.info("找到替代列 '产品代码'，将使用此列")
                    material_data.rename(columns={'产品代码': '物料代码'}, inplace=True)

    # 检查销售数据
    sales_required_cols = ['产品代码', '求和项:数量（箱）', '求和项:单价（箱）', '客户代码', '经销商名称', '发运月份']
    missing_sales_cols = [col for col in sales_required_cols if col not in sales_data.columns]
    if missing_sales_cols:
        st.warning(f"销售数据缺少必要列: {', '.join(missing_sales_cols)}")

    # 检查物料单价数据
    price_required_cols = ['物料代码', '单价（元）']
    missing_price_cols = [col for col in price_required_cols if col not in material_price.columns]
    if missing_price_cols:
        st.warning(f"物料单价数据缺少必要列: {', '.join(missing_price_cols)}")

    # 检查物料单价表中的重复列
    if '物料类别' in material_price.columns and material_price.columns.tolist().count('物料类别') > 1:
        st.info("警告: 物料单价表中'物料类别'列出现多次，将使用第一个")
        # 处理重复列
        column_names = material_price.columns.tolist()
        duplicate_index = column_names.index('物料类别', column_names.index('物料类别') + 1)
        new_column_names = column_names.copy()
        new_column_names[duplicate_index] = '物料类别_描述'
        material_price.columns = new_column_names

    return True
def create_distributor_analysis_tab(filtered_distributor, material_data, sales_data):
    """创建经销商分析标签页 - 基于客户级别的深度分析，现代化UI设计"""

    # 设置自定义CSS样式，确保现代化视觉效果
    st.markdown('''
    <style>
        /* 现代化卡片样式 */
        .modern-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 24px;
        }
        /* 图表标题样式 */
        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #1D2129;
            margin-bottom: 16px;
            padding-bottom: 8px;
            border-bottom: 1px solid #F0F0F0;
        }
        /* 图表解读框样式 */
        .chart-insight {
            background-color: #F7F8FA;
            padding: 16px;
            border-radius: 8px;
            margin-top: 12px;
            margin-bottom: 24px;
            border-left: 4px solid #4880FF;
        }
        /* 分隔线样式 */
        .section-divider {
            height: 1px;
            background-color: #F0F0F0;
            margin: 32px 0;
        }
    </style>
    ''', unsafe_allow_html=True)

    # 页面标题
    st.markdown(
        '<div style="font-size: 22px; font-weight: 600; color: #1D2129; margin: 20px 0 16px 0;">经销商深度分析</div>',
        unsafe_allow_html=True)

    # 检查数据有效性
    if filtered_distributor is None or len(filtered_distributor) == 0:
        st.info("暂无符合筛选条件的经销商数据，请调整筛选条件重试。")
        return None

    # 采用现代布局 - 使用2列结构避免拥挤
    col1, col2 = st.columns([1, 1])

    with col1:
        # ===== 物料多样性分析 - 优化为现代化图表 =====
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">客户物料组合多样性分析</div>', unsafe_allow_html=True)

        if '物料多样性' in filtered_distributor.columns and 'ROI' in filtered_distributor.columns:
            # 数据准备与异常值处理
            diversity_data = filtered_distributor.copy()
            diversity_data['ROI'] = diversity_data['ROI'].clip(upper=5.0)  # 限制极端值

            # 智能分组 - 根据数据范围动态调整
            if diversity_data['物料多样性'].max() > 10:
                bins = [0, 2, 4, 6, 8, 10, float('inf')]
                labels = ['0-2种', '3-4种', '5-6种', '7-8种', '9-10种', '10种以上']
            else:
                max_value = int(diversity_data['物料多样性'].max())
                bins = list(range(max_value + 2))
                labels = [f"{i}种" for i in range(max_value + 1)]

            diversity_data['多样性分组'] = pd.cut(diversity_data['物料多样性'], bins=bins, labels=labels)

            # 按多样性分组计算关键指标
            diversity_roi = diversity_data.groupby('多样性分组').agg({
                'ROI': ['mean', 'count'],
                '销售总额': ['mean', 'sum'],
                '物料总成本': ['mean', 'sum']
            }).reset_index()

            # 整理列名
            diversity_roi.columns = ['多样性分组', '平均产出比', '客户数量',
                                     '平均销售额(元)', '销售总额(元)',
                                     '平均物料成本(元)', '物料总成本(元)']

            # 计算每组销售额占比
            total_sales = diversity_roi['销售总额(元)'].sum()
            diversity_roi['销售占比'] = diversity_roi['销售总额(元)'] / total_sales

            if len(diversity_roi) > 0:
                # 创建高级双轴组合图表
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # 添加平均ROI柱状图
                fig.add_trace(
                    go.Bar(
                        x=diversity_roi['多样性分组'],
                        y=diversity_roi['平均产出比'],
                        name='平均产出比',
                        marker_color='#4880FF',
                        text=diversity_roi['平均产出比'].apply(lambda x: f"{x:.2f}"),
                        textposition='outside',
                        hovertemplate=(
                                '<b>%{x}</b><br>' +
                                '平均产出比: %{y:.2f}<br>' +
                                '客户数量: %{customdata[0]}家<br>' +
                                '平均销售额: %{customdata[1]:,.0f}元<br>' +
                                '平均物料成本: %{customdata[2]:,.0f}元<br>' +
                                '销售占比: %{customdata[3]:.1%}<extra></extra>'
                        ),
                        customdata=np.column_stack((
                            diversity_roi['客户数量'],
                            diversity_roi['平均销售额(元)'],
                            diversity_roi['平均物料成本(元)'],
                            diversity_roi['销售占比']
                        ))
                    ),
                    secondary_y=False
                )

                # 添加客户数量线图
                fig.add_trace(
                    go.Scatter(
                        x=diversity_roi['多样性分组'],
                        y=diversity_roi['客户数量'],
                        name='客户数量',
                        mode='lines+markers',
                        line=dict(color='#FF9500', width=3),
                        marker=dict(size=8, symbol='circle'),
                        hovertemplate='<b>%{x}</b><br>客户数量: %{y}家<extra></extra>'
                    ),
                    secondary_y=True
                )

                # 添加销售占比散点图 - 增加差异化分析
                fig.add_trace(
                    go.Scatter(
                        x=diversity_roi['多样性分组'],
                        y=diversity_roi['销售占比'],
                        name='销售占比',
                        mode='markers',
                        marker=dict(
                            size=diversity_roi['销售占比'] * 100,
                            sizemode='area',
                            sizeref=0.1,
                            color='#36CFC9',
                            symbol='diamond',
                            line=dict(width=1, color='#008B8B')
                        ),
                        hovertemplate='<b>%{x}</b><br>销售占比: %{y:.1%}<br>销售总额: %{customdata:,.0f}元<extra></extra>',
                        customdata=diversity_roi['销售总额(元)']
                    ),
                    secondary_y=True
                )

                # 现代化布局优化
                fig.update_layout(
                    height=420,
                    margin=dict(l=20, r=20, t=10, b=100),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.30,
                        xanchor="center",
                        x=0.5,
                        font=dict(size=12)
                    ),
                    plot_bgcolor='white',
                    hovermode='closest',
                    bargap=0.35,
                    barmode='group'
                )

                # 优化坐标轴
                fig.update_xaxes(
                    title_text="物料使用种类",
                    tickangle=-45,
                    title_font=dict(size=13),
                    gridcolor='#F5F5F5'
                )

                fig.update_yaxes(
                    title_text="平均产出比",
                    secondary_y=False,
                    title_font=dict(size=13),
                    gridcolor='#F5F5F5',
                    zeroline=True,
                    zerolinecolor='#E0E0E0'
                )

                fig.update_yaxes(
                    title_text="数量/占比",
                    tickformat='.0%',
                    secondary_y=True,
                    title_font=dict(size=13),
                    rangemode='nonnegative'
                )

                # 添加参考线
                fig.add_shape(
                    type="line",
                    x0=-0.5, y0=1, x1=len(diversity_roi) - 0.5, y1=1,
                    line=dict(color="#F53F3F", width=2, dash="dash"),
                    secondary_y=False
                )

                fig.add_shape(
                    type="line",
                    x0=-0.5, y0=2, x1=len(diversity_roi) - 0.5, y1=2,
                    line=dict(color="#0FC86F", width=2, dash="dash"),
                    secondary_y=False
                )

                # 添加参考线注释
                fig.add_annotation(
                    x=diversity_roi['多样性分组'].iloc[-1] if len(diversity_roi) > 0 else "",
                    y=1,
                    text="盈亏平衡(ROI=1)",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    arrowcolor="#F53F3F",
                    ax=-40,
                    ay=20,
                    font=dict(size=10, color="#F53F3F")
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # 简化业务解读 - 针对"蠢"业务员的说明
                st.markdown('''
                <div class="chart-insight">
                    <div style="font-weight: 600; margin-bottom: 8px;">📌 怎么看这个图？</div>
                    <p style="font-size: 14px; margin: 0;">
                        <b>看什么</b>：蓝色柱子表示客户使用不同种类物料的平均回报，橙线表示使用该组合的客户数量，绿色钻石表示该组合的销售占比大小。<br><br>
                        <b>怎么用</b>：
                        <ul style="margin-top: 5px; margin-bottom: 5px;">
                            <li>找蓝色柱子最高的物料组合 → 这是最赚钱的物料组合</li>
                            <li>注意红线位置 → 低于红线的组合在赔钱！</li>
                            <li>绿色钻石越大 → 该组合的销售额越高</li>
                        </ul>
                        <b>建议行动</b>：向客户推荐蓝柱最高的物料组合，减少红线以下的投入。
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.info("数据样本不足，无法生成多样性分析图表。请调整筛选条件。")
        else:
            st.warning("缺少必要数据列（物料多样性或ROI），无法生成多样性分析。")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # ===== 物料费率分布分析 - 强调销售占比和客户数量维度 =====
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">客户物料费率分布与业绩分析</div>', unsafe_allow_html=True)

        if '物料费率' in filtered_distributor.columns or '物料销售比率' in filtered_distributor.columns:
            # 获取正确的列名
            fee_rate_col = '物料费率' if '物料费率' in filtered_distributor.columns else '物料销售比率'

            # 数据准备与清洗
            expense_data = filtered_distributor.copy()

            # 异常值处理 - 根据费率列名调整
            expense_data = expense_data[expense_data[fee_rate_col] <= 0.5]  # 移除极端费率

            # 创建物料费率区间
            bins = [0, 0.02, 0.05, 0.08, 0.12, 0.2, 0.5]
            labels = ['0-2%', '2-5%', '5-8%', '8-12%', '12-20%', '20-50%']
            expense_data['费率区间'] = pd.cut(expense_data[fee_rate_col], bins=bins, labels=labels)

            # 计算每个区间的统计数据
            expense_stats = expense_data.groupby('费率区间').agg({
                'ROI': 'mean',
                '经销商名称': 'nunique',  # 使用'经销商名称'替代'客户名称'
                '销售总额': ['sum', 'mean'],
                '物料总成本': ['sum', 'mean']
            }).reset_index()

            # 整理列名
            flat_columns = []
            for col in expense_stats.columns:
                if isinstance(col, tuple):
                    flat_columns.append(f"{col[0]}_{col[1]}")
                else:
                    flat_columns.append(col)
            expense_stats.columns = flat_columns

            # 重命名列
            expense_stats = expense_stats.rename(columns={
                'ROI_mean': '平均ROI',
                '经销商名称_nunique': '客户数量',
                '销售总额_sum': '总销售额(元)',
                '销售总额_mean': '平均销售额(元)',
                '物料总成本_sum': '总物料成本(元)',
                '物料总成本_mean': '平均物料成本(元)'
            })

            # 计算销售占比
            total_sales = expense_stats['总销售额(元)'].sum()
            expense_stats['销售占比'] = expense_stats['总销售额(元)'] / total_sales
            expense_stats['客户占比'] = expense_stats['客户数量'] / expense_stats['客户数量'].sum()

            if len(expense_stats) > 0:
                # 创建三维气泡图 - 优化视觉表现，更现代化
                fig = go.Figure()

                # 添加气泡
                fig.add_trace(go.Scatter(
                    x=expense_stats['费率区间'],
                    y=expense_stats['平均ROI'],
                    mode='markers',
                    marker=dict(
                        size=expense_stats['销售占比'] * 150,  # 放大气泡尺寸以更明显显示销售占比
                        sizemode='area',
                        sizeref=0.05,
                        color=expense_stats['客户数量'],
                        colorscale='Viridis',
                        colorbar=dict(
                            title="客户数量(家)",
                            thickness=15,
                            len=0.7,
                            y=0.5
                        ),
                        showscale=True,
                        line=dict(width=1, color='darkblue')
                    ),
                    name='',
                    hovertemplate=(
                            '<b>%{x} 费率区间</b><br>' +
                            '平均ROI: %{y:.2f}<br>' +
                            '客户数量: %{customdata[0]}家 (%{customdata[1]:.1%})<br>' +
                            '平均销售额: %{customdata[2]:,.0f}元<br>' +
                            '总销售额: %{customdata[3]:,.0f}元<br>' +
                            '销售占比: %{customdata[4]:.1%}<extra></extra>'
                    ),
                    customdata=np.column_stack((
                        expense_stats['客户数量'],
                        expense_stats['客户占比'],
                        expense_stats['平均销售额(元)'],
                        expense_stats['总销售额(元)'],
                        expense_stats['销售占比']
                    ))
                ))

                # 添加数据标签 - 直接在气泡上显示客户占比
                for i, row in expense_stats.iterrows():
                    fig.add_annotation(
                        x=row['费率区间'],
                        y=row['平均ROI'] + 0.1,
                        text=f"{row['客户占比']:.0%}",
                        showarrow=False,
                        font=dict(color="black", size=11),
                        bgcolor="rgba(255,255,255,0.7)",
                        bordercolor="gray",
                        borderwidth=1,
                        borderpad=3,
                        opacity=0.8
                    )

                # 添加参考线 - 盈亏平衡
                fig.add_shape(
                    type="line",
                    x0=-0.5, y0=1, x1=len(expense_stats) - 0.5, y1=1,
                    line=dict(color="#F53F3F", width=2, dash="dash"),
                    name="盈亏平衡线"
                )

                # 参考线注释
                fig.add_annotation(
                    x=expense_stats['费率区间'].iloc[-1] if len(expense_stats) > 0 else "",
                    y=1.05,
                    text="盈亏平衡线",
                    showarrow=False,
                    font=dict(size=10, color="#F53F3F"),
                    bgcolor="rgba(255,255,255,0.7)",
                    bordercolor="#F53F3F",
                    borderwidth=1,
                    borderpad=3
                )

                # 现代化布局设置
                fig.update_layout(
                    height=420,
                    margin=dict(l=20, r=20, t=10, b=100),
                    xaxis=dict(
                        title="物料费率区间",
                        titlefont=dict(size=13),
                        tickangle=-45
                    ),
                    yaxis=dict(
                        title="平均产出比(ROI)",
                        titlefont=dict(size=13),
                        gridcolor='#F5F5F5',
                        zeroline=True,
                        zerolinecolor='#E0E0E0'
                    ),
                    plot_bgcolor='white',
                    showlegend=False,
                    hovermode='closest'
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # 简化业务解读
                st.markdown('''
                <div class="chart-insight">
                    <div style="font-weight: 600; margin-bottom: 8px;">📌 怎么看这个图？</div>
                    <p style="font-size: 14px; margin: 0;">
                        <b>看什么</b>：这个图展示不同物料费率区间的客户表现，气泡大小表示该区间销售占比，颜色深浅表示客户数量多少，气泡上方百分比是客户占比。<br><br>
                        <b>怎么用</b>：
                        <ul style="margin-top: 5px; margin-bottom: 5px;">
                            <li>寻找气泡位置最高的区间 → 这个费率区间ROI最高</li>
                            <li>寻找颜色最深的气泡 → 这个区间客户最多</li>
                            <li>关注大气泡 → 这个区间销售额占比大</li>
                        </ul>
                        <b>建议行动</b>：优先关注气泡又大又高的费率区间客户，他们最有价值；红线以下的客户需要调整投放策略。
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.info("数据样本不足，无法生成费率分布分析图表。请调整筛选条件。")
        else:
            st.warning("缺少必要数据列（物料费率或销售总额），无法生成费率分布分析。")

        st.markdown('</div>', unsafe_allow_html=True)

    # 分隔线
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ===== 客户物料使用策略分析 - 突出物料使用策略而非仅是ROI =====
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">客户物料使用策略效果排名</div>', unsafe_allow_html=True)

    if '物料多样性' in filtered_distributor.columns and 'ROI' in filtered_distributor.columns:
        # 准备策略分析数据
        strategy_data = filtered_distributor.copy()

        # 确保关键列存在
        required_cols = ['经销商名称', 'ROI', '物料多样性']
        if all(col in strategy_data.columns for col in required_cols):
            # 标准化处理
            strategy_data['ROI_norm'] = (strategy_data['ROI'] - strategy_data['ROI'].min()) / (
                    strategy_data['ROI'].max() - strategy_data['ROI'].min() + 1e-10)

            if '销售总额' in strategy_data.columns:
                strategy_data['销售_norm'] = (strategy_data['销售总额'] - strategy_data['销售总额'].min()) / (
                        strategy_data['销售总额'].max() - strategy_data['销售总额'].min() + 1e-10)
                # 计算综合策略评分 (60% ROI + 20% 销售额 + 20% 多样性)
                strategy_data['策略评分'] = 0.6 * strategy_data['ROI_norm'] + 0.2 * strategy_data['销售_norm'] + 0.2 * (
                        strategy_data['物料多样性'] / strategy_data['物料多样性'].max())
            else:
                # 如果没有销售额，则只用ROI和多样性评分
                strategy_data['策略评分'] = 0.7 * strategy_data['ROI_norm'] + 0.3 * (
                        strategy_data['物料多样性'] / strategy_data['物料多样性'].max())

            # 取前12名展示
            top_strategies = strategy_data.sort_values(by='策略评分', ascending=False).head(12)

            if len(top_strategies) > 0:
                # 创建创新的双条形图表 - 显示ROI和物料多样性
                fig = go.Figure()

                # 添加ROI条形图
                fig.add_trace(go.Bar(
                    y=top_strategies['经销商名称'],
                    x=top_strategies['ROI'],
                    orientation='h',
                    name='产出比(ROI)',
                    marker_color='#4880FF',
                    text=top_strategies['ROI'].apply(lambda x: f"{x:.2f}"),
                    textposition='outside',
                    width=0.5,
                    hovertemplate=(
                            '<b>%{y}</b><br>' +
                            'ROI: %{x:.2f}<br>' +
                            '策略评分: %{customdata[0]:.2f}<br>' +
                            '物料多样性: %{customdata[1]}种<br>' +
                            '物料成本: %{customdata[2]:,.0f}元<br>' +
                            '销售额: %{customdata[3]:,.0f}元<extra></extra>'
                    ),
                    customdata=np.column_stack((
                        top_strategies['策略评分'],
                        top_strategies['物料多样性'],
                        top_strategies['物料总成本'] if '物料总成本' in top_strategies.columns else np.zeros(
                            len(top_strategies)),
                        top_strategies['销售总额'] if '销售总额' in top_strategies.columns else np.zeros(
                            len(top_strategies))
                    ))
                ))

                # 添加物料多样性迷你条形图 - 显示不同客户的物料使用策略
                fig.add_trace(go.Bar(
                    y=top_strategies['经销商名称'],
                    x=top_strategies['物料多样性'] / top_strategies['物料多样性'].max() * max(
                        top_strategies['ROI']) * 0.25,  # 缩放使其与ROI图在同一刻度上可见
                    orientation='h',
                    name='物料多样性',
                    marker_color='#36CFC9',
                    text=top_strategies['物料多样性'].apply(lambda x: f"{int(x)}种"),
                    textposition='inside',
                    insidetextanchor='middle',
                    width=0.5,
                    opacity=0.7,
                    offset=-0.5,  # 与ROI条错开
                    hovertemplate='<b>%{y}</b><br>物料使用种类: %{customdata}种<extra></extra>',
                    customdata=top_strategies['物料多样性']
                ))

                # 添加参考线
                fig.add_shape(
                    type="line",
                    x0=1, y0=-0.5, x1=1, y1=len(top_strategies) - 0.5,
                    line=dict(color="#F53F3F", width=2, dash="dash")
                )

                # 参考线注释
                fig.add_annotation(
                    x=1.1,
                    y=top_strategies['经销商名称'].iloc[0],
                    text="盈亏平衡线",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=1,
                    arrowcolor="#F53F3F",
                    ax=30,
                    ay=20,
                    font=dict(size=10, color="#F53F3F")
                )

                # 添加排名标签
                for i, customer in enumerate(top_strategies['经销商名称']):
                    fig.add_annotation(
                        x=0,
                        y=customer,
                        text=f"#{i + 1}",
                        showarrow=False,
                        xshift=-40,
                        font=dict(size=11, color="#4E5969"),
                        align="right"
                    )

                # 现代化布局优化
                fig.update_layout(
                    height=min(500, 120 + len(top_strategies) * 30),  # 动态调整高度
                    margin=dict(l=50, r=20, t=10, b=50),
                    barmode='overlay',
                    xaxis=dict(
                        title="产出比(ROI) / 物料策略",
                        titlefont=dict(size=13),
                        zeroline=True,
                        zerolinecolor='#E0E0E0',
                        gridcolor='#F5F5F5'
                    ),
                    yaxis=dict(
                        title=None,
                        autorange="reversed",  # 从上到下按排名顺序排列
                        tickfont=dict(size=11)
                    ),
                    plot_bgcolor='white',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.2,
                        xanchor="center",
                        x=0.5
                    ),
                    hovermode='closest'
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

                # 简化业务解读
                st.markdown('''
                <div class="chart-insight">
                    <div style="font-weight: 600; margin-bottom: 8px;">📌 怎么看这个图？</div>
                    <p style="font-size: 14px; margin: 0;">
                        <b>看什么</b>：图表展示了最优秀客户的物料使用策略效果。蓝色长条表示ROI值，绿色短条表示物料使用多样性，数字是客户排名。<br><br>
                        <b>怎么用</b>：
                        <ul style="margin-top: 5px; margin-bottom: 5px;">
                            <li>看蓝条最长的客户 → 他们的投入产出比最高</li>
                            <li>看绿条长短 → 了解客户使用了多少种物料</li>
                            <li>对比蓝绿条长度 → 发现最佳物料种类搭配</li>
                        </ul>
                        <b>实际应用</b>：研究排名前三的客户如何搭配使用物料，并向其他客户推广这种最佳策略组合。比如，如果发现使用约3-4种物料的客户ROI普遍较高，就可以推荐其他客户采用类似组合。
                    </p>
                </div>
                ''', unsafe_allow_html=True)

                # 最佳实践提示 - 突出具体策略建议
                best_diversity = top_strategies.iloc[0:3]['物料多样性'].mean()

                st.markdown(f'''
                <div style="background-color: #EBF7FF; padding: 15px; border-radius: 8px; margin-top: 12px; border-left: 4px solid #0081FF;">
                    <div style="font-weight: 600; margin-bottom: 8px; color: #0081FF;">💡 最佳实践提示</div>
                    <p style="font-size: 14px; color: #333; margin: 0;">
                        根据排名前三的客户数据分析，目前最优秀的客户平均使用了<b>{best_diversity:.1f}种</b>物料，且搭配合理。您可以：
                        <ul style="margin-top: 5px;">
                            <li>向物料使用不足的客户推荐增加至{int(best_diversity)}种物料</li>
                            <li>对物料种类过多的客户，建议精简至最有效的{int(best_diversity)}种</li>
                            <li>定期回访榜单客户，了解他们的物料使用心得</li>
                        </ul>
                    </p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.info("数据样本不足，无法生成客户策略排名。请调整筛选条件。")
        else:
            st.warning("缺少必要数据列，无法生成客户策略分析。")
    else:
        st.warning("缺少必要数据列（物料多样性或ROI），无法生成策略分析。")

    st.markdown('</div>', unsafe_allow_html=True)

    return None
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
                    '物料代码': material_ids[mat_idx],  # 使用物料代码而非产品代码
                    '产品名称': material_names[mat_idx],
                    '求和项:数量': quantity,  # 修正：使用正确的字段名"求和项:数量"
                    '物料类别': material_cats[mat_idx],
                    '单价（元）': material_prices[mat_idx],
                    '物料成本': round(quantity * material_prices[mat_idx], 2)
                })

    # 生成销售数据 - 保持原样，因为销售数据中的"箱"单位是正确的
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


def validate_data_fields(material_data, sales_data, material_price):
    """验证数据字段是否存在并正确命名"""

    validation_results = {
        "status": True,
        "messages": []
    }

    # 检查物料数据必要字段
    material_required_fields = ['发运月份', '客户代码', '经销商名称', '物料代码', '求和项:数量']
    missing_material_fields = [field for field in material_required_fields if field not in material_data.columns]
    if missing_material_fields:
        validation_results["status"] = False
        validation_results["messages"].append(f"物料数据缺少必要字段: {', '.join(missing_material_fields)}")

    # 检查销售数据必要字段
    sales_required_fields = ['发运月份', '客户代码', '经销商名称', '产品代码', '求和项:数量（箱）', '求和项:单价（箱）']
    missing_sales_fields = [field for field in sales_required_fields if field not in sales_data.columns]
    if missing_sales_fields:
        validation_results["status"] = False
        validation_results["messages"].append(f"销售数据缺少必要字段: {', '.join(missing_sales_fields)}")

    # 检查物料价格表必要字段
    price_required_fields = ['物料代码', '单价（元）']
    missing_price_fields = [field for field in price_required_fields if field not in material_price.columns]
    if missing_price_fields:
        validation_results["status"] = False
        validation_results["messages"].append(f"物料价格表缺少必要字段: {', '.join(missing_price_fields)}")

    # 检查物料价格表中的重复列
    if '物料类别' in material_price.columns:
        duplicate_columns = material_price.columns[material_price.columns.duplicated()]
        if not duplicate_columns.empty:
            validation_results["messages"].append(
                f"警告: 物料价格表中发现重复列: {', '.join(duplicate_columns)}。将使用第一个出现的列。")

    return validation_results
@st.cache_data
def get_data():
    """缓存数据加载函数"""
    try:
        return load_data(sample_data=False)  # 尝试加载真实数据
    except Exception as e:
        st.error(f"加载数据时出错: {e}")
        st.warning("已降级使用示例数据")
        return load_data(sample_data=True)  # 出错时降级使用示例数据


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

# 物料与销售关系分析 - 改进版本

def create_material_sales_relationship(filtered_distributor):
    """创建改进版的物料投入与销售产出关系图表，优化气泡大小和悬停信息，修复间距问题"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">物料与销售产出关系分析</div>',
                unsafe_allow_html=True)

    # 高级专业版容器
    st.markdown('''
    <div class="feishu-chart-container" 
             style="background: linear-gradient(to bottom right, #FFFFFF, #F8FAFC); 
                    border-radius: 16px; 
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06); 
                    border: 1px solid rgba(224, 228, 234, 0.8);
                    padding: 28px;">
    ''', unsafe_allow_html=True)

    # 过滤控制区
    filter_cols = st.columns([3, 1])
    with filter_cols[0]:
        st.markdown("""
        <div style="font-weight: 600; color: #2B5AED; margin-bottom: 10px; font-size: 16px;">
            物料投入与销售产出关系
        </div>
        """, unsafe_allow_html=True)
    with filter_cols[1]:
        roi_filter = st.selectbox(
            "物料产出比筛选",
            ["全部", "物料产出比 > 1", "物料产出比 > 2", "物料产出比 < 1"],
            label_visibility="collapsed"
        )

    # 物料-销售关系图 - 优化版本
    material_sales_relation = filtered_distributor.copy()

    if len(material_sales_relation) > 0:
        # 应用ROI筛选
        if roi_filter == "物料产出比 > 1":
            material_sales_relation = material_sales_relation[material_sales_relation['ROI'] > 1]
        elif roi_filter == "物料产出比 > 2":
            material_sales_relation = material_sales_relation[material_sales_relation['ROI'] > 2]
        elif roi_filter == "物料产出比 < 1":
            material_sales_relation = material_sales_relation[material_sales_relation['ROI'] < 1]

        # 重设索引确保有效
        material_sales_relation = material_sales_relation.reset_index(drop=True)

        # 改进的颜色方案 - 专业配色
        segment_colors = {
            '高价值客户': '#10B981',  # 绿色
            '成长型客户': '#3B82F6',  # 蓝色
            '稳定型客户': '#F59E0B',  # 橙色
            '低效型客户': '#EF4444'   # 红色
        }

        # 设置气泡大小 - 降低整体大小，减少重叠
        # 使用对数值来缩放，但将系数从10降低到5，并进一步减小sizeref值来减小所有气泡
        size_values = np.log1p(material_sales_relation['ROI'].clip(0.1, 10)) * 4

        # 创建散点图 - 高级专业版
        fig = go.Figure()

        # 为每个客户价值分层创建散点图
        for segment, color in segment_colors.items():
            segment_data = material_sales_relation[material_sales_relation['客户价值分层'] == segment]

            if len(segment_data) > 0:
                segment_size = size_values.loc[segment_data.index]

                # 添加带有优化悬停模板的散点图 - 更丰富的悬停信息
                fig.add_trace(go.Scatter(
                    x=segment_data['物料总成本'],
                    y=segment_data['销售总额'],
                    mode='markers',
                    marker=dict(
                        size=segment_size,
                        color=color,
                        opacity=0.8,  # 提高不透明度以增强可见性
                        line=dict(width=1, color='white'),
                        symbol='circle',
                        sizemode='diameter',
                        sizeref=0.7,  # 增加此值可以缩小所有气泡
                    ),
                    name=segment,
                    hovertext=segment_data['经销商名称'],
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '<span style="font-weight:600;color:#333">基本信息:</span><br>' +
                                  '客户代码: %{customdata[7]}<br>' +
                                  '所属区域: %{customdata[3]}<br>' +
                                  '省份: %{customdata[4]}<br>' +
                                  '销售人员: %{customdata[5]}<br>' +
                                  '<span style="font-weight:600;color:#333">财务数据:</span><br>' +
                                  '物料成本: ¥%{x:,.2f}<br>' +
                                  '销售额: ¥%{y:,.2f}<br>' +
                                  '物料产出比: %{customdata[0]:.2f}<br>' +
                                  '物料销售比率: %{customdata[1]:.2f}%<br>' +
                                  '<span style="font-weight:600;color:#333">其他指标:</span><br>' +
                                  '物料多样性: %{customdata[2]} 种<br>' +
                                  '客户价值分层: %{customdata[6]}<br>' +
                                  '月份: %{customdata[8]}',
                    customdata=np.column_stack((
                        segment_data['ROI'],
                        segment_data['物料销售比率'],
                        segment_data['物料多样性'] if '物料多样性' in segment_data.columns else np.zeros(
                            len(segment_data)),
                        segment_data['所属区域'] if '所属区域' in segment_data.columns else ['未知'] * len(
                            segment_data),
                        segment_data['省份'] if '省份' in segment_data.columns else ['未知'] * len(segment_data),
                        segment_data['销售人员'] if '销售人员' in segment_data.columns else ['未知'] * len(
                            segment_data),
                        segment_data['客户价值分层'],
                        segment_data['客户代码'],
                        segment_data['月份名'] if '月份名' in segment_data.columns else ['未知'] * len(segment_data)
                    ))
                ))

        # 安全确定数据范围
        if len(material_sales_relation) > 0:
            min_cost = material_sales_relation['物料总成本'].min()
            max_cost = material_sales_relation['物料总成本'].max()

            # 安全调整范围
            min_cost = max(min_cost * 0.7, 1)
            max_cost = min(max_cost * 1.3, max_cost * 10)

            # 添加盈亏平衡参考线 (物料产出比=1)
            fig.add_trace(go.Scatter(
                x=[min_cost, max_cost],
                y=[min_cost, max_cost],
                mode='lines',
                line=dict(color="#EF4444", width=2.5, dash="dash"),
                name="物料产出比 = 1 (盈亏平衡线)",
                hoverinfo='skip'
            ))

            # 添加物料产出比=2参考线
            fig.add_trace(go.Scatter(
                x=[min_cost, max_cost],
                y=[min_cost * 2, max_cost * 2],
                mode='lines',
                line=dict(color="#10B981", width=2.5, dash="dash"),
                name="物料产出比 = 2 (优秀水平)",
                hoverinfo='skip'
            ))
        else:
            min_cost = 1
            max_cost = 1000

        # 优化专业布局
        fig.update_layout(
            legend=dict(
                orientation="h",
                y=-0.15,
                x=0.5,
                xanchor="center",
                font=dict(size=13, family="PingFang SC"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E0E4EA",
                borderwidth=1
            ),
            margin=dict(l=60, r=60, t=30, b=90),  # 增加边距，确保不会有遮挡
            height=580,  # 增加高度以确保足够空间显示
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.8)',
            font=dict(
                family="PingFang SC",
                size=13,
                color="#333333"
            ),
            hovermode='closest'  # 确保悬停时只显示最近的点
        )

        # 优化X轴设置
        fig.update_xaxes(
            title=dict(
                text="物料投入成本 (元) - 对数刻度",
                font=dict(size=14, family="PingFang SC", color="#333333"),
                standoff=20
            ),
            showgrid=True,
            gridcolor='rgba(224, 228, 234, 0.7)',
            gridwidth=1,
            tickprefix="¥",
            tickformat=",d",
            type="log",  # 使用对数刻度
            range=[np.log10(min_cost * 0.7), np.log10(max_cost * 1.3)]  # 增加范围防止遮挡
        )

        # 优化Y轴设置
        fig.update_yaxes(
            title=dict(
                text="销售收入 (元) - 对数刻度",
                font=dict(size=14, family="PingFang SC", color="#333333"),
                standoff=20
            ),
            showgrid=True,
            gridcolor='rgba(224, 228, 234, 0.7)',
            gridwidth=1,
            tickprefix="¥",
            tickformat=",d",
            type="log",  # 使用对数刻度
            range=[np.log10(min_cost * 0.7), np.log10(max_cost * 5.5)]  # 增加上限范围
        )

        # 添加区域标签 - 改进位置和样式，确保不会重叠
        fig.add_annotation(
            x=max_cost * 0.8,
            y=max_cost * 0.7,
            text="物料产出比 < 1<br>低效区",
            showarrow=False,
            font=dict(size=13, color="#EF4444", family="PingFang SC"),
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#EF4444",
            borderwidth=1.5,
            borderpad=5,
            opacity=0.9
        )

        fig.add_annotation(
            x=max_cost * 0.8,
            y=max_cost * 1.5,
            text="1 ≤ 物料产出比 < 2<br>良好区",
            showarrow=False,
            font=dict(size=13, color="#F59E0B", family="PingFang SC"),
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#F59E0B",
            borderwidth=1.5,
            borderpad=5,
            opacity=0.9
        )

        fig.add_annotation(
            x=max_cost * 0.8,
            y=max_cost * 3.2,
            text="物料产出比 ≥ 2<br>优秀区",
            showarrow=False,
            font=dict(size=13, color="#10B981", family="PingFang SC"),
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="#10B981",
            borderwidth=1.5,
            borderpad=5,
            opacity=0.9
        )

        st.plotly_chart(fig, use_container_width=True)

        # 计算并添加分布指标 - 优化版
        high_value_count = len(material_sales_relation[material_sales_relation['客户价值分层'] == '高价值客户'])
        growth_count = len(material_sales_relation[material_sales_relation['客户价值分层'] == '成长型客户'])
        stable_count = len(material_sales_relation[material_sales_relation['客户价值分层'] == '稳定型客户'])
        low_eff_count = len(material_sales_relation[material_sales_relation['客户价值分层'] == '低效型客户'])

        # 计算比例
        total = high_value_count + growth_count + stable_count + low_eff_count
        high_value_pct = (high_value_count / total * 100) if total > 0 else 0
        growth_pct = (growth_count / total * 100) if total > 0 else 0
        stable_pct = (stable_count / total * 100) if total > 0 else 0
        low_eff_pct = (low_eff_count / total * 100) if total > 0 else 0

        # 添加高级统计信息
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-top: 15px; background-color: rgba(255,255,255,0.8); border-radius: 10px; padding: 15px; font-size: 14px; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
            <div style="text-align: center; padding: 0 12px;">
                <div style="font-weight: 600; color: #10B981; font-size: 22px;">{high_value_count}</div>
                <div style="color: #333; font-weight: 500;">高价值客户</div>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">{high_value_pct:.1f}%</div>
            </div>
            <div style="text-align: center; padding: 0 12px; border-left: 1px solid #eee;">
                <div style="font-weight: 600; color: #3B82F6; font-size: 22px;">{growth_count}</div>
                <div style="color: #333; font-weight: 500;">成长型客户</div>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">{growth_pct:.1f}%</div>
            </div>
            <div style="text-align: center; padding: 0 12px; border-left: 1px solid #eee;">
                <div style="font-weight: 600; color: #F59E0B; font-size: 22px;">{stable_count}</div>
                <div style="color: #333; font-weight: 500;">稳定型客户</div>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">{stable_pct:.1f}%</div>
            </div>
            <div style="text-align: center; padding: 0 12px; border-left: 1px solid #eee;">
                <div style="font-weight: 600; color: #EF4444; font-size: 22px;">{low_eff_count}</div>
                <div style="color: #333; font-weight: 500;">低效型客户</div>
                <div style="font-size: 12px; color: #666; margin-top: 4px;">{low_eff_pct:.1f}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.info("暂无足够数据生成物料与销售关系图。")

    st.markdown('</div>', unsafe_allow_html=True)

    # 添加图表解读
    st.markdown('''
    <div class="chart-explanation">
        <div class="chart-explanation-title">图表解读：</div>
        <p>这个散点图展示了物料投入和销售产出的关系。每个点代表一个经销商，点的大小表示物料产出比值，颜色代表不同客户类型。
        横轴是物料成本，纵轴是销售额（对数刻度）。红色虚线是盈亏平衡线(物料产出比=1)，绿色虚线是优秀水平线(物料产出比=2)。
        背景区域划分了不同物料产出比的区域：低效区(物料产出比<1)、良好区(1≤物料产出比<2)和优秀区(物料产出比≥2)。悬停在点上可查看更多经销商详情。</p>
    </div>
    ''', unsafe_allow_html=True)


def create_material_category_analysis(filtered_material, filtered_sales):
    """创建改进版的物料类别分析图表，确保两个图表数据合理且无遮挡"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料类别分析</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
                    unsafe_allow_html=True)

        # 计算每个物料类别的总成本和使用频率
        if '物料类别' in filtered_material.columns and '物料成本' in filtered_material.columns:
            category_metrics = filtered_material.groupby('物料类别').agg({
                '物料成本': 'sum',
                '物料代码': 'nunique'  # 修正：使用物料代码而非产品代码
            }).reset_index()

            # 添加物料使用频率
            category_metrics['使用频率'] = category_metrics['物料代码']  # 修正：使用物料代码
            category_metrics = category_metrics.sort_values('物料成本', ascending=False)

            if len(category_metrics) > 0:
                # 计算百分比并保留两位小数
                category_metrics['占比'] = (
                        (category_metrics['物料成本'] / category_metrics['物料成本'].sum()) * 100).round(2)

                # 改进颜色方案 - 使用渐变色调
                custom_colors = ['#0052CC', '#2684FF', '#4C9AFF', '#00B8D9', '#00C7E6', '#36B37E', '#00875A',
                                 '#FF5630', '#FF7452']

                fig = px.bar(
                    category_metrics,
                    x='物料类别',
                    y='物料成本',
                    text='占比',
                    color='物料类别',
                    title="物料类别投入分布",
                    color_discrete_sequence=custom_colors,
                    labels={"物料类别": "物料类别", "物料成本": "物料成本 (元)"}
                )

                # 在柱子上显示百分比 - 改进文字样式
                fig.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside',
                    textfont=dict(size=12, color="#333333", family="PingFang SC"),
                    marker=dict(line=dict(width=0.8, color='white')),
                    hovertemplate='<b>%{x}</b><br>' +
                                  '<span style="font-weight:600;">详细数据:</span><br>' +
                                  '物料成本: ¥%{y:,.2f}<br>' +
                                  '占比: %{text}%<br>' +
                                  '物料种类: %{customdata[0]}种<br>' +
                                  '平均单价: ¥%{customdata[1]:,.2f}',  # 修正：移除"/箱"
                    customdata=np.column_stack((
                        category_metrics['使用频率'],
                        # 计算平均单价 (如果数据中没有，则使用估算值)
                        (category_metrics['物料成本'] / category_metrics['使用频率'].replace(0, 1)).round(2)
                    ))
                )

                fig.update_layout(
                    height=400,
                    xaxis_title="物料类别",
                    yaxis_title="物料成本 (元)",
                    margin=dict(l=40, r=40, t=50, b=60),
                    title_font=dict(size=16, family="PingFang SC", color="#333333"),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC",
                        size=13,
                        color="#333333"
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-20,  # 优化角度提高可读性
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.6)',
                        ticksuffix="元",
                        tickformat=",.0f",
                        title_font=dict(size=14)
                    ),
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无物料类别数据。")
        else:
            st.warning("物料数据缺少'物料类别'或'物料成本'列，无法进行分析。")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
                    unsafe_allow_html=True)

        # 创建物料类别使用次数分析而非ROI (避免重复分析)
        if '物料类别' in filtered_material.columns:
            # 统计各物料类别的使用次数和客户分布
            category_usage = filtered_material.groupby('物料类别').agg({
                '客户代码': 'nunique',
                '求和项:数量': 'sum'  # 修正：使用'求和项:数量'
            }).reset_index()

            category_usage.columns = ['物料类别', '使用客户数', '使用总量']

            if len(category_usage) > 0:
                # 排序
                category_usage = category_usage.sort_values('使用客户数', ascending=False)

                # 使用相同的颜色方案保持一致性
                fig = px.bar(
                    category_usage,
                    x='物料类别',
                    y='使用客户数',
                    text='使用客户数',
                    color='物料类别',
                    title="物料类别使用分布分析",
                    color_discrete_sequence=custom_colors,
                    labels={"物料类别": "物料类别", "使用客户数": "使用客户数量"}
                )

                # 更新文本显示 - 改进样式
                fig.update_traces(
                    texttemplate='%{text}',
                    textposition='outside',
                    textfont=dict(size=12, color="#333333", family="PingFang SC"),
                    marker=dict(line=dict(width=0.8, color='white')),
                    hovertemplate='<b>%{x}</b><br>' +
                                  '<span style="font-weight:600;">使用情况:</span><br>' +
                                  '使用客户数: <b>%{y}</b>家<br>' +
                                  '使用总量: %{customdata[0]:,.0f}<br>' +  # 修正：移除"箱"
                                  '平均每客户使用量: %{customdata[1]:.1f}',  # 修正：移除"箱"
                    customdata=np.column_stack((
                        category_usage['使用总量'],
                        (category_usage['使用总量'] / category_usage['使用客户数']).round(1)
                    ))
                )

                fig.update_layout(
                    height=400,
                    xaxis_title="物料类别",
                    yaxis_title="使用客户数量",
                    margin=dict(l=40, r=40, t=50, b=60),
                    title_font=dict(size=16, family="PingFang SC", color="#333333"),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC",
                        size=13,
                        color="#333333"
                    ),
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-20,  # 优化角度提高可读性
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.6)',
                        zeroline=True,
                        zerolinecolor='#E0E4EA',
                        zerolinewidth=1,
                        title_font=dict(size=14)
                    ),
                    showlegend=False
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无物料类别使用数据。")
        else:
            st.info("物料数据缺少'物料类别'列，无法进行分析。")

        st.markdown('</div>', unsafe_allow_html=True)

    # 添加图表解读
    st.markdown('''
    <div class="chart-explanation">
        <div class="chart-explanation-title">图表解读：</div>
        <p>左侧图表显示不同物料类别的投入成本占比，右侧图表展示各类物料的客户使用情况。通过对比分析，可以发现哪些物料类别投入较多且被广泛使用，以及哪些类别需要优化推广。鼠标悬停可查看详细数据，包括具体金额、使用频率以及客户使用情况等。</p>
    </div>
    ''', unsafe_allow_html=True)


def validate_data_consistency(material_data, sales_data, distributor_data=None):
    """验证数据集之间的一致性，并返回警告信息"""
    warnings = []

    # 检查共有的客户代码
    if 'customer_consistency' not in st.session_state:
        material_customers = set(material_data['客户代码'].unique()) if '客户代码' in material_data.columns else set()
        sales_customers = set(sales_data['客户代码'].unique()) if '客户代码' in sales_data.columns else set()

        if material_customers and sales_customers:
            common_customers = material_customers.intersection(sales_customers)
            match_percentage = len(common_customers) / min(len(material_customers), len(sales_customers)) * 100

            if match_percentage < 50:
                warnings.append(
                    f"物料数据和销售数据的客户代码匹配度低于50%。物料数据有{len(material_customers)}个客户，"
                    f"销售数据有{len(sales_customers)}个客户，但共有客户只有{len(common_customers)}个。")
            else:
                # 添加正向提示
                warnings.append(
                    f"客户匹配状态：物料数据与销售数据客户匹配度为{match_percentage:.1f}%。"
                    f"共有{len(common_customers)}个匹配客户，分析基于客户级别匹配。")

        st.session_state['customer_consistency'] = True  # 只检查一次

    # 删除产品代码匹配度检查，因为我们知道产品代码系统不同

    # 检查ROI极端值
    if distributor_data is not None and 'ROI' in distributor_data.columns:
        extreme_roi_count = (distributor_data['ROI'] > 5).sum()
        if extreme_roi_count > 0:
            warnings.append(
                f"检测到{extreme_roi_count}个经销商的ROI值超过5，这些值已被限制。如需调整限制上限，请修改process_data函数中的clip设置。")

    return warnings


def create_product_optimization_tab(filtered_material, filtered_sales, filtered_distributor):
    """
    创建物料与产品组合优化标签页，实现现代化UI设计，优化数据计算逻辑和图表布局

    参数:
    filtered_material: DataFrame - 经过筛选的物料数据
    filtered_sales: DataFrame - 经过筛选的销售数据
    filtered_distributor: DataFrame - 经过筛选的经销商数据

    返回:
    str - 标签页标识符
    """
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import streamlit as st

    # 标签页标题 - 现代化设计
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 16px; font-size: 18px; font-weight: 600; color: #2B5AED; padding-bottom: 8px; border-bottom: 2px solid #E8F1FF;">物料与产品组合优化分析</div>',
        unsafe_allow_html=True
    )

    # 检查数据有效性
    if filtered_material is None or len(filtered_material) == 0:
        st.info("暂无物料数据，无法进行分析。")
        return None

    if filtered_sales is None or len(filtered_sales) == 0:
        st.info("暂无销售数据，无法进行分析。")
        return None

    # ===================== 第一部分：产品绩效与物料组合分析 =====================
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 16px; color: #333;">产品绩效与物料组合分析</div>',
        unsafe_allow_html=True
    )

    # 创建卡片容器
    st.markdown(
        '<div class="feishu-chart-container" style="background: linear-gradient(to bottom right, #FFFFFF, #F8FAFC); border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid rgba(224, 228, 234, 0.8); padding: 24px; margin-bottom: 24px;">',
        unsafe_allow_html=True
    )

    # 检查所需列是否存在
    required_cols = ['产品代码', '物料成本', '销售金额']
    missing_material_cols = [col for col in required_cols[:2] if col not in filtered_material.columns]
    missing_sales_cols = [col for col in required_cols[2:] if col not in filtered_sales.columns]

    missing_cols = missing_material_cols + missing_sales_cols

    if missing_cols:
        st.warning(f"数据缺少以下列，无法进行完整分析: {', '.join(missing_cols)}")
        st.info("将显示备用分析视图")

        # 显示备用视图 - 产品销售热力图
        if '产品代码' in filtered_sales.columns and '销售金额' in filtered_sales.columns:
            # 分析热门产品销售情况
            product_sales = filtered_sales.groupby('产品代码').agg({
                '销售金额': 'sum',
                '求和项:数量（箱）': 'sum'
            }).reset_index()

            if len(product_sales) > 0:
                # 计算单价，确保除数不为零
                product_sales['平均单价'] = np.where(
                    product_sales['求和项:数量（箱）'] > 0,
                    product_sales['销售金额'] / product_sales['求和项:数量（箱）'],
                    0
                )

                # 排序
                product_sales = product_sales.sort_values('销售金额', ascending=False).head(15)

                # 创建热门产品销售图
                fig = px.bar(
                    product_sales,
                    x='产品代码',
                    y='销售金额',
                    color='平均单价',
                    color_continuous_scale=px.colors.sequential.Blues,
                    title="热门产品销售分析",
                    labels={"产品代码": "产品代码", "销售金额": "销售金额 (元)", "平均单价": "平均单价 (元/箱)"}
                )

                # 更新布局
                fig.update_layout(
                    height=450,
                    margin=dict(l=40, r=40, t=60, b=80),
                    coloraxis_colorbar=dict(title="平均单价 (元/箱)"),
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(ticksuffix=" 元"),
                    paper_bgcolor='white',
                    plot_bgcolor='rgba(240, 247, 255, 0.8)'
                )

                # 悬停信息优化
                fig.update_traces(
                    hovertemplate='<b>%{x}</b><br>' +
                                  '销售金额: ¥%{y:,.2f}<br>' +
                                  '销售数量: %{customdata[0]:,}<br>' +  # 修正：移除了"箱"
                                  '平均单价: ¥%{customdata[1]:,.2f}',  # 修正：移除了"/箱"
                    customdata=np.column_stack((
                        product_sales['求和项:数量（箱）'],
                        product_sales['平均单价']
                    ))
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("销售数据中没有足够的产品信息进行分析。")
        else:
            st.info("数据结构不支持备用分析视图，请检查数据格式。")
    else:
        # 可以执行完整分析 - 创建产品与物料关联分析
        try:
            # 准备数据 - 根据销售额分组产品
            product_sales = filtered_sales.groupby('产品代码')['销售金额'].sum().reset_index()
            product_sales.columns = ['产品代码', '销售总额']

            # 计算物料投入
            product_material = filtered_material.groupby('产品代码')['物料成本'].sum().reset_index()
            product_material.columns = ['产品代码', '物料总成本']

            # 合并数据
            product_analysis = pd.merge(product_sales, product_material, on='产品代码', how='inner')

            # 检查是否有足够的数据点
            if len(product_analysis) < 3:
                st.warning("匹配的产品数据不足3个，无法生成有意义的分析图表。")
                st.info(f"当前仅有{len(product_analysis)}个产品同时出现在物料数据和销售数据中。")

                # 显示可能的原因
                material_products = filtered_material['产品代码'].nunique()
                sales_products = filtered_sales['产品代码'].nunique()

                st.info(f"物料数据中有{material_products}个不同产品，销售数据中有{sales_products}个不同产品。")
                st.info("提示：检查产品代码在两个数据集中是否一致，或者放宽筛选条件。")
            else:
                # 计算物料与销售比率 - 修复计算逻辑，确保单位正确
                product_analysis['物料销售比率'] = np.where(
                    product_analysis['销售总额'] > 0,
                    (product_analysis['物料总成本'] / product_analysis['销售总额'] * 100).round(2),
                    0
                )

                # 修正产出比计算逻辑，避免异常高值
                product_analysis['物料产出比'] = np.where(
                    product_analysis['物料总成本'] > 0,
                    (product_analysis['销售总额'] / product_analysis['物料总成本']).round(2),
                    0
                )

                # 过滤异常值
                product_analysis = product_analysis[
                    (product_analysis['物料销售比率'] > 0) &
                    (product_analysis['物料销售比率'] < 100) &
                    (product_analysis['物料产出比'] < 10)  # 过滤极端值
                    ]

                # 再次检查过滤后的数据量
                if len(product_analysis) < 3:
                    st.warning("过滤异常值后，有效数据点不足3个，无法生成有意义的分析图表。")
                    st.info("请尝试放宽筛选条件或检查数据质量。")
                else:
                    # 创建两列布局
                    col1, col2 = st.columns([3, 2])

                    with col1:
                        # 创建物料产出比与销售额关系图
                        fig = px.scatter(
                            product_analysis,
                            x='物料销售比率',
                            y='物料产出比',
                            size='销售总额',
                            color='销售总额',
                            color_continuous_scale=px.colors.sequential.Blues,
                            hover_name='产品代码',
                            title="产品物料效率分析",
                            labels={
                                "物料销售比率": "物料销售比率 (%)",
                                "物料产出比": "物料产出比",
                                "销售总额": "销售总额 (元)"
                            },
                            height=480
                        )

                        # 添加水平和垂直参考线
                        fig.add_hline(y=2, line_dash="dash", line_color="#10B981", annotation_text="优良产出比(2倍)",
                                      annotation_position="top right")
                        fig.add_hline(y=1, line_dash="dash", line_color="#F59E0B", annotation_text="盈亏平衡(1倍)",
                                      annotation_position="top right")
                        fig.add_vline(x=40, line_dash="dash", line_color="#F59E0B", annotation_text="物料比率40%",
                                      annotation_position="top right")

                        # 区域背景
                        fig.add_shape(
                            type="rect",
                            x0=0, y0=2,
                            x1=40, y1=10,
                            fillcolor="rgba(16, 185, 129, 0.1)",
                            line=dict(width=0),
                        )

                        # 标记区域
                        fig.add_annotation(
                            x=20, y=5,
                            text="高效区域",
                            showarrow=False,
                            font=dict(size=14, color="#10B981")
                        )

                        # 更新布局
                        fig.update_layout(
                            margin=dict(l=40, r=40, t=50, b=40),
                            coloraxis_colorbar=dict(
                                title="销售总额 (元)",
                                tickprefix="¥",
                                len=0.8
                            ),
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(224, 228, 234, 0.5)',
                                ticksuffix="%",
                                range=[0, max(product_analysis['物料销售比率']) * 1.1]
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(224, 228, 234, 0.5)',
                                range=[0, max(product_analysis['物料产出比']) * 1.1]
                            ),
                            paper_bgcolor='white',
                            plot_bgcolor='rgba(240, 247, 255, 0.5)'
                        )

                        # 悬停信息优化
                        fig.update_traces(
                            hovertemplate='<b>%{hovertext}</b><br>' +
                                          '物料销售比率: %{x:.2f}%<br>' +
                                          '物料产出比: %{y:.2f}<br>' +
                                          '销售总额: ¥%{marker.color:,.2f}<br>'
                        )

                        st.plotly_chart(fig, use_container_width=True)

                    with col2:
                        # 添加分析洞察与建议卡片
                        st.markdown("""
                        <div style="background-color: rgba(16, 185, 129, 0.05); padding: 16px; border-radius: 8px; 
                        border-left: 4px solid #10B981; margin-bottom: 20px;">
                        <p style="font-weight: 600; color: #10B981; margin-bottom: 8px;">产品效率洞察</p>
                        <p style="font-size: 14px; color: #333; line-height: 1.6;">
                        散点图展示了各产品的物料使用效率，点的大小和颜色表示销售总额。位于图表左上角的产品(低物料比率、高产出比)效率最高，
                        这些产品在相对较少的物料投入下创造了较高的销售回报。
                        </p>
                        </div>
                        """, unsafe_allow_html=True)

                        # 创建产品效率排行榜
                        top_products = product_analysis.sort_values('物料产出比', ascending=False).head(5)
                        bottom_products = product_analysis.sort_values('物料产出比').head(5)

                        # 展示优秀产品卡片
                        st.markdown("""
                        <p style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">物料效率最高的产品</p>
                        """, unsafe_allow_html=True)

                        for i, (_, row) in enumerate(top_products.iterrows()):
                            bg_color = "rgba(16, 185, 129, 0.05)" if i % 2 == 0 else "rgba(16, 185, 129, 0.1)"
                            st.markdown(f"""
                            <div style="background-color: {bg_color}; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="font-weight: 600;">{row['产品代码']}</div>
                                    <div style="color: #10B981; font-weight: 600;">产出比: {row['物料产出比']:.2f}</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 13px;">
                                    <div>销售额: ¥{row['销售总额']:,.2f}</div>
                                    <div>物料比率: {row['物料销售比率']:.1f}%</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # 展示待优化产品卡片
                        st.markdown("""
                        <p style="font-weight: 600; color: #333; margin: 16px 0 12px 0; font-size: 15px;">物料效率待提升的产品</p>
                        """, unsafe_allow_html=True)

                        for i, (_, row) in enumerate(bottom_products.iterrows()):
                            bg_color = "rgba(245, 158, 11, 0.05)" if i % 2 == 0 else "rgba(245, 158, 11, 0.1)"
                            st.markdown(f"""
                            <div style="background-color: {bg_color}; padding: 12px; border-radius: 6px; margin-bottom: 8px;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div style="font-weight: 600;">{row['产品代码']}</div>
                                    <div style="color: #F59E0B; font-weight: 600;">产出比: {row['物料产出比']:.2f}</div>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-top: 5px; font-size: 13px;">
                                    <div>销售额: ¥{row['销售总额']:,.2f}</div>
                                    <div>物料比率: {row['物料销售比率']:.1f}%</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                        # 添加推荐建议
                        st.markdown("""
                        <div style="background-color: rgba(37, 99, 235, 0.05); padding: 16px; border-radius: 8px; 
                        border-left: 4px solid #2563EB; margin-top: 20px;">
                        <p style="font-weight: 600; color: #2563EB; margin-bottom: 8px;">优化建议</p>
                        <ul style="font-size: 14px; color: #333; padding-left: 20px; margin: 0;">
                            <li style="margin-bottom: 6px;">对于高效率产品，保持现有物料配比，考虑适度增加投放量</li>
                            <li style="margin-bottom: 6px;">对于低效率产品，重新评估物料组合，减少无效物料投入</li>
                            <li style="margin-bottom: 6px;">分析高效率产品的物料特征，并应用到类似产品中</li>
                            <li style="margin-bottom: 6px;">建议物料销售比率控制在40%以内以保证足够的利润空间</li>
                        </ul>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"创建产品物料效率分析时出错: {str(e)}")
            st.info("可能的原因：数据结构不一致或产品代码不匹配。请检查物料数据和销售数据。")

    st.markdown('</div>', unsafe_allow_html=True)

    # ===================== 第二部分：物料投放策略优化 =====================
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 16px; color: #333;">物料投放策略优化</div>',
        unsafe_allow_html=True
    )

    # 创建卡片容器
    st.markdown(
        '<div class="feishu-chart-container" style="background: linear-gradient(to bottom right, #FFFFFF, #F8FAFC); border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid rgba(224, 228, 234, 0.8); padding: 24px; margin-bottom: 24px;">',
        unsafe_allow_html=True
    )

    # 检查申请人列
    has_applicant = '申请人' in filtered_material.columns
    has_salesperson = '销售人员' in filtered_material.columns

    # 选择合适的列作为销售人员
    salesperson_col = '销售人员' if has_salesperson else ('申请人' if has_applicant else None)

    if salesperson_col is not None:
        # 创建销售人员物料分配分析
        salesperson_data = filtered_material.groupby(salesperson_col).agg({
            '物料成本': 'sum',
            '产品代码': 'nunique',
            '客户代码': 'nunique'
        }).reset_index()

        # 添加销售数据
        if salesperson_col in filtered_sales.columns:
            sales_by_person = filtered_sales.groupby(salesperson_col)['销售金额'].sum().reset_index()
            salesperson_data = pd.merge(salesperson_data, sales_by_person, on=salesperson_col, how='left')

            # 计算效率指标 - 修复计算逻辑，避免异常高值
            salesperson_data['物料产出比'] = (salesperson_data['销售金额'] / salesperson_data['物料成本']).round(2)
            # 限制极端值
            salesperson_data['物料产出比'] = salesperson_data['物料产出比'].clip(upper=10)

            salesperson_data['客均物料成本'] = (salesperson_data['物料成本'] / salesperson_data['客户代码']).round(2)

            # 排序并展示
            salesperson_data = salesperson_data.sort_values('物料产出比', ascending=False)

            # 设置列名显示
            column_name = '销售人员' if salesperson_col == '销售人员' else '申请人'

            # 创建两列布局
            col1, col2 = st.columns([3, 2])

            with col1:
                # 创建销售人员物料效率散点图
                fig = px.scatter(
                    salesperson_data,
                    x='客均物料成本',
                    y='物料产出比',
                    size='物料成本',
                    color='销售金额',
                    hover_name=salesperson_col,
                    title=f"{column_name}物料分配效率分析",
                    color_continuous_scale=px.colors.sequential.Bluyl,
                    labels={
                        "客均物料成本": "客均物料成本 (元/客户)",
                        "物料产出比": "物料产出比",
                        "物料成本": "物料总成本 (元)",
                        "销售金额": "销售总额 (元)"
                    },
                    height=500
                )

                # 添加参考线
                fig.add_hline(y=2, line_dash="dash", line_color="#10B981",
                              annotation_text="优良产出比(2倍)", annotation_position="top right")
                fig.add_hline(y=1, line_dash="dash", line_color="#F59E0B",
                              annotation_text="盈亏平衡(1倍)", annotation_position="top right")

                # 更新布局
                fig.update_layout(
                    margin=dict(l=40, r=40, t=50, b=40),
                    coloraxis_colorbar=dict(
                        title="销售总额 (元)",
                        tickprefix="¥",
                        len=0.8
                    ),
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.5)',
                        tickprefix="¥"
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.5)'
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='rgba(240, 247, 255, 0.5)'
                )

                # 悬停信息优化
                fig.update_traces(
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '客均物料成本: ¥%{x:,.2f}<br>' +
                                  '物料产出比: %{y:.2f}<br>' +
                                  '物料总成本: ¥%{marker.size:,.2f}<br>' +
                                  '销售总额: ¥%{marker.color:,.2f}<br>' +
                                  '产品种类: %{customdata[0]}<br>' +
                                  '客户数: %{customdata[1]}',
                    customdata=np.column_stack((
                        salesperson_data['产品代码'],
                        salesperson_data['客户代码']
                    ))
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # 添加物料分配洞察卡片
                st.markdown("""
                <div style="background-color: rgba(37, 99, 235, 0.05); padding: 16px; border-radius: 8px; 
                border-left: 4px solid #2563EB; margin-bottom: 16px;">
                <p style="font-weight: 600; color: #2563EB; margin-bottom: 8px;">物料分配洞察</p>
                <p style="font-size: 14px; color: #333; line-height: 1.6;">
                此图展示了销售团队的物料分配效率，点的大小表示物料总成本，颜色表示销售总额。
                横轴为每位客户平均分配的物料成本，纵轴为物料产出比。
                理想位置在图表右上方，表示客户获得充足的物料支持，同时产生了高回报。
                </p>
                </div>
                """, unsafe_allow_html=True)

                # 计算并展示各区间人数
                excellent_count = len(salesperson_data[salesperson_data['物料产出比'] >= 2])
                good_count = len(
                    salesperson_data[(salesperson_data['物料产出比'] >= 1) & (salesperson_data['物料产出比'] < 2)])
                poor_count = len(salesperson_data[salesperson_data['物料产出比'] < 1])

                # 创建效率分布卡片
                st.markdown("""
                <p style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">物料效率分布</p>
                """, unsafe_allow_html=True)

                # 显示分布图
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-bottom: 16px;">
                    <div style="flex: 1; background-color: rgba(16, 185, 129, 0.1); padding: 12px; border-radius: 6px; text-align: center; margin-right: 8px;">
                        <div style="font-size: 20px; font-weight: 600; color: #10B981;">{excellent_count}</div>
                        <div style="font-size: 12px; color: #333;">优秀 (≥2)</div>
                    </div>
                    <div style="flex: 1; background-color: rgba(245, 158, 11, 0.1); padding: 12px; border-radius: 6px; text-align: center; margin-right: 8px;">
                        <div style="font-size: 20px; font-weight: 600; color: #F59E0B;">{good_count}</div>
                        <div style="font-size: 12px; color: #333;">良好 (1-2)</div>
                    </div>
                    <div style="flex: 1; background-color: rgba(239, 68, 68, 0.1); padding: 12px; border-radius: 6px; text-align: center;">
                        <div style="font-size: 20px; font-weight: 600; color: #EF4444;">{poor_count}</div>
                        <div style="font-size: 12px; color: #333;">待改进 (<1)</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # 展示最高效的销售人员
                best_person = salesperson_data.iloc[0] if len(salesperson_data) > 0 else None

                if best_person is not None:
                    st.markdown("""
                    <p style="font-weight: 600; color: #333; margin: 16px 0 12px 0; font-size: 15px;">物料利用最高效的人员</p>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div style="background-color: rgba(16, 185, 129, 0.1); padding: 16px; border-radius: 6px; margin-bottom: 16px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-weight: 600; font-size: 16px;">{best_person[salesperson_col]}</div>
                            <div style="background-color: rgba(16, 185, 129, 0.2); color: #10B981; font-weight: 600; padding: 4px 8px; border-radius: 4px;">
                                产出比: {best_person['物料产出比']:.2f}
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                            <div>物料总成本: ¥{best_person['物料成本']:,.2f}</div>
                            <div>销售总额: ¥{best_person['销售金额']:,.2f}</div>
                            <div>客户数: {best_person['客户代码']}</div>
                            <div>产品种类: {best_person['产品代码']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # 如果有表现较差的销售人员，也展示出来作为对比
                if poor_count > 0:
                    worst_person = salesperson_data[salesperson_data['物料产出比'] < 1].iloc[0] if len(
                        salesperson_data[salesperson_data['物料产出比'] < 1]) > 0 else None

                    if worst_person is not None:
                        st.markdown("""
                        <p style="font-weight: 600; color: #333; margin: 16px 0 12px 0; font-size: 15px;">物料利用待改进的人员</p>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                        <div style="background-color: rgba(239, 68, 68, 0.1); padding: 16px; border-radius: 6px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <div style="font-weight: 600; font-size: 16px;">{worst_person[salesperson_col]}</div>
                                <div style="background-color: rgba(239, 68, 68, 0.2); color: #EF4444; font-weight: 600; padding: 4px 8px; border-radius: 4px;">
                                    产出比: {worst_person['物料产出比']:.2f}
                                </div>
                            </div>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                                <div>物料总成本: ¥{worst_person['物料成本']:,.2f}</div>
                                <div>销售总额: ¥{worst_person['销售金额']:,.2f}</div>
                                <div>客户数: {worst_person['客户代码']}</div>
                                <div>产品种类: {worst_person['产品代码']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info(f"缺少销售数据或{salesperson_col}不存在于销售数据中，无法计算完整指标。")
    else:
        # 替代视图 - 物料类别分析
        if '产品名称' in filtered_material.columns:
            # 分析物料使用频率
            material_usage = filtered_material.groupby('产品名称').agg({
                '物料成本': 'sum',
                '求和项:数量（箱）': 'sum',
                '客户代码': 'nunique'
            }).reset_index()

            # 排序
            material_usage = material_usage.sort_values('物料成本', ascending=False).head(10)

            # 计算平均单价
            material_usage['平均单价'] = material_usage['物料成本'] / material_usage['求和项:数量（箱）']

            # 创建柱状图
            fig = go.Figure()

            # 添加物料成本条形图
            fig.add_trace(go.Bar(
                x=material_usage['产品名称'],
                y=material_usage['物料成本'],
                name='物料成本',
                marker_color='#3B82F6',
                hovertemplate='<b>%{x}</b><br>' +
                              '物料成本: ¥%{y:,.2f}<br>' +
                              '数量: %{customdata[0]:,}<br>' +  # 修正：移除了"箱"
                              '客户数: %{customdata[1]}<br>' +
                              '平均单价: ¥%{customdata[2]:.2f}',  # 修正：移除了"/箱"
                customdata=np.column_stack((
                    material_usage['求和项:数量'],  # 修正：使用'求和项:数量'
                    material_usage['客户代码'],
                    material_usage['平均单价']
                ))
            ))

            # 添加客户数线图
            fig.add_trace(go.Scatter(
                x=material_usage['产品名称'],
                y=material_usage['客户代码'],
                name='使用客户数',
                yaxis='y2',
                mode='lines+markers',
                line=dict(color='#F59E0B', width=3),
                marker=dict(size=8, color='#F59E0B'),
                hovertemplate='<b>%{x}</b><br>使用客户数: %{y}<extra></extra>'
            ))

            # 更新布局
            fig.update_layout(
                title='热门物料使用分析',
                xaxis=dict(
                    title='物料名称',
                    tickangle=-45,
                    tickfont=dict(size=10)
                ),
                yaxis=dict(
                    title='物料成本 (元)',
                    titlefont=dict(color='#3B82F6'),
                    tickfont=dict(color='#3B82F6'),
                    tickprefix="¥"
                ),
                yaxis2=dict(
                    title='使用客户数',
                    titlefont=dict(color='#F59E0B'),
                    tickfont=dict(color='#F59E0B'),
                    anchor='x',
                    overlaying='y',
                    side='right'
                ),
                height=500,
                margin=dict(l=40, r=60, t=60, b=80),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                paper_bgcolor='white',
                plot_bgcolor='rgba(240, 247, 255, 0.5)'
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加分析洞察
            st.markdown("""
            <div style="background-color: rgba(37, 99, 235, 0.05); padding: 16px; border-radius: 8px; 
            border-left: 4px solid #2563EB; margin-top: 16px;">
            <p style="font-weight: 600; color: #2563EB; margin-bottom: 8px;">物料使用洞察</p>
            <p style="font-size: 14px; color: #333; line-height: 1.6;">
            图表展示了成本最高的10种物料及其客户覆盖情况。蓝色柱表示物料总成本，橙色线表示使用该物料的客户数量。
            理想物料应该在保持适当成本的同时覆盖较多客户。建议关注那些成本高但客户覆盖少的物料，评估其投放效率。
            </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("数据缺少必要列，无法生成物料使用分析图。")

    st.markdown('</div>', unsafe_allow_html=True)

    # ===================== 第三部分：客户物料需求分析 =====================
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 16px; color: #333;">客户物料需求分析</div>',
        unsafe_allow_html=True
    )

    # 创建卡片容器
    st.markdown(
        '<div class="feishu-chart-container" style="background: linear-gradient(to bottom right, #FFFFFF, #F8FAFC); border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid rgba(224, 228, 234, 0.8); padding: 24px; margin-bottom: 24px;">',
        unsafe_allow_html=True
    )

    # 检查是否有区域列
    has_region = '所属区域' in filtered_material.columns

    if has_region:
        # 按区域分析物料需求
        region_material = filtered_material.groupby('所属区域').agg({
            '物料成本': 'sum',
            '求和项:数量（箱）': 'sum',
            '客户代码': 'nunique',
            '产品代码': 'nunique'
        }).reset_index()

        # 添加销售数据
        if '所属区域' in filtered_sales.columns:
            region_sales = filtered_sales.groupby('所属区域')['销售金额'].sum().reset_index()
            region_material = pd.merge(region_material, region_sales, on='所属区域', how='left')

            # 计算效率指标 - 修复计算逻辑，避免异常高值
            region_material['物料产出比'] = (region_material['销售金额'] / region_material['物料成本']).round(2)
            # 限制极端值
            region_material['物料产出比'] = region_material['物料产出比'].clip(upper=10)

            region_material['客均物料成本'] = (region_material['物料成本'] / region_material['客户代码']).round(2)
            region_material['客均产品种类'] = (region_material['产品代码'] / region_material['客户代码']).round(1)

            # 创建区域物料需求分析
            col1, col2 = st.columns([3, 2])

            with col1:
                # 创建区域物料效率图表
                region_material_sorted = region_material.sort_values('物料产出比', ascending=False)

                # 创建双轴柱状图
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # 添加物料产出比条形图
                fig.add_trace(
                    go.Bar(
                        x=region_material_sorted['所属区域'],
                        y=region_material_sorted['物料产出比'],
                        name='物料产出比',
                        marker_color='#3B82F6',
                        text=region_material_sorted['物料产出比'].apply(lambda x: f"{x:.2f}"),
                        textposition='outside',
                        hovertemplate='<b>%{x}区域</b><br>' +
                                      '物料产出比: <b>%{y:.2f}</b><br>' +
                                      '物料总成本: ¥%{customdata[0]:,.2f}<br>' +
                                      '销售总额: ¥%{customdata[1]:,.2f}<br>' +
                                      '客户数: %{customdata[2]}<br>' +
                                      '产品种类: %{customdata[3]}',
                        customdata=np.column_stack((
                            region_material_sorted['物料成本'],
                            region_material_sorted['销售金额'],
                            region_material_sorted['客户代码'],
                            region_material_sorted['产品代码']
                        ))
                    ),
                    secondary_y=False
                )

                # 添加客均物料成本线图
                fig.add_trace(
                    go.Scatter(
                        x=region_material_sorted['所属区域'],
                        y=region_material_sorted['客均物料成本'],
                        name='客均物料成本',
                        mode='lines+markers',
                        marker=dict(size=8, color='#F59E0B'),
                        line=dict(width=3, color='#F59E0B'),
                        hovertemplate='<b>%{x}区域</b><br>' +
                                      '客均物料成本: ¥<b>%{y:,.2f}</b>/客户<br>',
                    ),
                    secondary_y=True
                )

                # 更新布局
                fig.update_layout(
                    title='区域物料效率分析',
                    height=450,
                    margin=dict(l=40, r=60, t=60, b=60),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='rgba(240, 247, 255, 0.5)'
                )

                # 更新X轴
                fig.update_xaxes(
                    title_text="区域",
                    tickangle=-0,
                    showgrid=False
                )

                # 更新Y轴
                fig.update_yaxes(
                    title_text="物料产出比",
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.5)',
                    zeroline=True,
                    zerolinecolor='#E0E4EA',
                    secondary_y=False
                )

                fig.update_yaxes(
                    title_text="客均物料成本 (元/客户)",
                    showgrid=False,
                    tickprefix="¥",
                    secondary_y=True
                )

                # 添加参考线
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    y0=1,
                    x1=len(region_material_sorted) - 0.5,
                    y1=1,
                    line=dict(color="#F59E0B", width=2, dash="dash"),
                    secondary_y=False
                )

                fig.add_annotation(
                    x=region_material_sorted['所属区域'].iloc[-1] if len(region_material_sorted) > 0 else "",
                    y=1,
                    text="产出比=1 (盈亏平衡)",
                    showarrow=False,
                    yshift=10,
                    font=dict(size=10, color="#F59E0B"),
                    bgcolor="rgba(255,255,255,0.7)",
                    bordercolor="#F59E0B",
                    borderwidth=1,
                    borderpad=4,
                    secondary_y=False
                )

                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # 添加区域物料洞察卡片
                st.markdown("""
                <div style="background-color: rgba(37, 99, 235, 0.05); padding: 16px; border-radius: 8px; 
                border-left: 4px solid #2563EB; margin-bottom: 16px;">
                <p style="font-weight: 600; color: #2563EB; margin-bottom: 8px;">区域物料洞察</p>
                <p style="font-size: 14px; color: #333; line-height: 1.6;">
                此图展示了各区域的物料效率指标，蓝色柱表示物料产出比，橙色线表示客均物料成本。
                产出比高且客均成本适中的区域效率最佳，表明物料投放得当且产生良好回报。
                黄色虚线代表盈亏平衡线（产出比=1）。
                </p>
                </div>
                """, unsafe_allow_html=True)

                # 创建区域物料需求特征卡片
                st.markdown("""
                <p style="font-weight: 600; color: #333; margin: 16px 0 12px 0; font-size: 15px;">区域物料需求特征</p>
                """, unsafe_allow_html=True)

                # 显示区域物料产出比
                for i, (_, row) in enumerate(region_material_sorted.iterrows()):
                    efficiency_color = "#10B981" if row['物料产出比'] >= 2 else (
                        "#2B5AED" if row['物料产出比'] >= 1.5 else
                        "#F59E0B" if row['物料产出比'] >= 1 else "#EF4444")

                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; 
                             background-color: rgba({i % 2 * 10}, {i % 2 * 10}, {i % 2 * 10}, 0.03); 
                             padding: 10px; border-radius: 6px; margin-bottom: 8px;">
                        <div style="font-weight: 600;">{row['所属区域']}</div>
                        <div style="color: {efficiency_color}; font-weight: 600;">产出比: {row['物料产出比']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # 添加优化建议
                st.markdown("""
                <div style="background-color: rgba(16, 185, 129, 0.05); padding: 16px; border-radius: 8px; 
                border-left: 4px solid #10B981; margin-top: 16px;">
                <p style="font-weight: 600; color: #10B981; margin-bottom: 8px;">区域优化建议</p>
                <ul style="font-size: 14px; color: #333; padding-left: 20px; margin: 0;">
                    <li style="margin-bottom: 6px;">高效区域：保持现有物料策略，作为标杆向其他区域推广</li>
                    <li style="margin-bottom: 6px;">高成本低效区域：重新评估物料分配策略，减少低效物料</li>
                    <li style="margin-bottom: 6px;">低成本低效区域：考虑适度增加高效物料的投放</li>
                    <li style="margin-bottom: 6px;">为不同区域制定差异化的物料投放标准</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

        else:
            st.info("缺少区域销售数据，无法计算完整指标。")
    else:
        # 创建客户类型物料使用对比
        if '客户代码' in filtered_material.columns and '物料成本' in filtered_material.columns:
            # 按客户计算物料使用情况
            customer_material = filtered_material.groupby('客户代码').agg({
                '物料成本': 'sum',
                '求和项:数量（箱）': 'sum',
                '产品代码': 'nunique'
            }).reset_index()

            # 按物料成本排序，分为高物料投入和低物料投入客户
            customer_material['物料投入分组'] = pd.qcut(
                customer_material['物料成本'],
                q=[0, 0.5, 1.0],
                labels=['低物料投入客户', '高物料投入客户']
            )

            # 分组统计
            group_stats = customer_material.groupby('物料投入分组').agg({
                '物料成本': 'mean',
                '求和项:数量（箱）': 'mean',
                '产品代码': 'mean',
                '客户代码': 'count'
            }).reset_index()

            group_stats.columns = ['客户类型', '平均物料成本', '平均物料数量', '平均产品种类', '客户数量']

            # 若存在销售数据，添加销售指标
            if '客户代码' in filtered_sales.columns and '销售金额' in filtered_sales.columns:
                customer_sales = filtered_sales.groupby('客户代码')['销售金额'].sum().reset_index()
                customer_material = pd.merge(customer_material, customer_sales, on='客户代码', how='left')

                # 分组统计
                with_sales_stats = customer_material.groupby('物料投入分组').agg({
                    '销售金额': 'mean'
                }).reset_index()

                with_sales_stats.columns = ['客户类型', '平均销售金额']

                # 合并数据
                group_stats = pd.merge(group_stats, with_sales_stats, on='客户类型', how='left')

                # 计算ROI - 修正计算逻辑，避免异常高值
                group_stats['平均物料产出比'] = (group_stats['平均销售金额'] / group_stats['平均物料成本']).round(2)
                # 限制极端值
                group_stats['平均物料产出比'] = group_stats['平均物料产出比'].clip(upper=10)

            # 创建物料使用对比图
            fig = go.Figure()

            # 设置数据项目
            metrics = ['平均物料成本', '平均物料数量', '平均产品种类']
            metric_names = ['物料成本 (元)', '物料数量 (箱)', '产品种类 (个)']

            if '平均销售金额' in group_stats.columns:
                metrics.append('平均销售金额')
                metric_names.append('销售金额 (元)')

                if '平均物料产出比' in group_stats.columns:
                    metrics.append('平均物料产出比')
                    metric_names.append('物料产出比')

            # 转换为长格式
            plot_data = pd.melt(
                group_stats,
                id_vars=['客户类型', '客户数量'],
                value_vars=metrics,
                var_name='指标',
                value_name='数值'
            )

            # 添加指标名称映射
            metric_map = dict(zip(metrics, metric_names))
            plot_data['指标名称'] = plot_data['指标'].map(metric_map)

            # 创建分组柱状图
            fig = px.bar(
                plot_data,
                x='指标名称',
                y='数值',
                color='客户类型',
                barmode='group',
                title='客户类型物料使用对比',
                color_discrete_map={
                    '高物料投入客户': '#3B82F6',
                    '低物料投入客户': '#F59E0B'
                },
                labels={
                    '指标名称': '',
                    '数值': '均值',
                    '客户类型': ''
                },
                height=450,
                text='数值'
            )

            # 更新文本显示
            fig.update_traces(
                texttemplate=lambda d: f"{d.y:.1f}" if d.x == '物料产出比' or d.x == '产品种类 (个)'
                else f"¥{d.y:,.0f}" if '元' in d.x
                else f"{d.y:,.0f}",
                textposition='outside',
                textfont=dict(size=11),
                hovertemplate='<b>%{x}</b><br>' +
                              '%{data.name}: <b>%{y:,.2f}</b><br>' +
                              '客户数量: %{customdata} 家',
                customdata=np.array([[c] for c in plot_data['客户数量']])
            )

            # 更新布局
            fig.update_layout(
                margin=dict(l=40, r=40, t=60, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                paper_bgcolor='white',
                plot_bgcolor='rgba(240, 247, 255, 0.5)',
                xaxis=dict(
                    tickangle=-15,
                    title='',
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.5)',
                    title='',
                )
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加物料使用洞察卡片
            st.markdown("""
            <div style="background-color: rgba(37, 99, 235, 0.05); padding: 16px; border-radius: 8px; 
            border-left: 4px solid #2563EB; margin-top: 16px;">
            <p style="font-weight: 600; color: #2563EB; margin-bottom: 8px;">客户物料使用洞察</p>
            <p style="font-size: 14px; color: #333; line-height: 1.6;">
            图表对比了高物料投入客户与低物料投入客户在各项指标上的差异。蓝色代表高物料投入客户，橙色代表低物料投入客户。
            通过对比可以发现，物料投入与销售额、产品多样性具有明显相关性。分析这些差异有助于优化物料分配策略，
            提高物料利用效率并识别不同客户群体的差异化需求。
            </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("数据缺少必要列，无法生成客户物料使用对比图。")

    st.markdown('</div>', unsafe_allow_html=True)

    # 图表解读指南 - 针对"蠢"业务员的简化说明
    st.markdown(
        '<div class="feishu-chart-container" style="background: linear-gradient(to right, #F0F7FF, #F8FAFC); border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); border: 1px solid rgba(224, 228, 234, 0.8); padding: 24px; margin-bottom: 24px;">',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div style="font-weight: 600; color: #2B5AED; margin-bottom: 16px; font-size: 18px;">📊 图表解读指南 - 如何发现物料投放优化机会</div>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="background-color: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #E8F1FF;">
            <div style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">产品物料效率分析</div>
            <p style="font-size: 14px; color: #4E5969; line-height: 1.5; margin-bottom: 10px;">
                <b>看什么</b>：看散点图中左上角的产品 - 物料占比低、回报率高！
            </p>
            <ul style="font-size: 14px; color: #4E5969; padding-left: 20px; margin: 0;">
                <li>绿色区域内的产品（又高又左）= 最高效产品</li>
                <li>点越大 = 销售额越高</li>
                <li>点在红线以下 = 赔钱产品，需调整投放</li>
            </ul>
        </div>

        <div style="background-color: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #E8F1FF;">
            <div style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">销售人员物料分配效率</div>
            <p style="font-size: 14px; color: #4E5969; line-height: 1.5; margin-bottom: 10px;">
                <b>看什么</b>：右上角的销售人员最优秀 - 给每个客户更多物料且产出高！
            </p>
            <ul style="font-size: 14px; color: #4E5969; padding-left: 20px; margin: 0;">
                <li>点越大 = 物料总成本越高</li>
                <li>颜色越深 = 销售额越高</li>
                <li>低于黄线的销售人员 = 需要培训</li>
            </ul>
        </div>
    </div>

    <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        <div style="background-color: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #E8F1FF;">
            <div style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">区域物料效率分析</div>
            <p style="font-size: 14px; color: #4E5969; line-height: 1.5; margin-bottom: 10px;">
                <b>看什么</b>：蓝柱最高的区域最有效，橙线表示客均物料投入。
            </p>
            <ul style="font-size: 14px; color: #4E5969; padding-left: 20px; margin: 0;">
                <li>蓝柱高 + 橙线低 = 高效率区域</li>
                <li>柱越高 = 物料产出比越高</li>
                <li>低于黄线区域 = 需调整物料策略</li>
            </ul>
        </div>

        <div style="background-color: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); border: 1px solid #E8F1FF;">
            <div style="font-weight: 600; color: #333; margin-bottom: 12px; font-size: 15px;">物料组合价值分析</div>
            <p style="font-size: 14px; color: #4E5969; line-height: 1.5; margin-bottom: 10px;">
                <b>实操建议</b>：用好这些图表做出更好的物料投放决策！
            </p>
            <ul style="font-size: 14px; color: #4E5969; padding-left: 20px; margin: 0;">
                <li>复制高效产品的物料组合策略</li>
                <li>向高效销售人员学习物料推荐方法</li>
                <li>参考高效区域的物料分配方式</li>
                <li>对比高低投入客户的物料使用差异</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    return "物料与产品组合优化"


def create_expense_ratio_analysis(filtered_distributor):
    """创建物料费比分析图表 - 修复版：解决间距和重叠问题"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料费比分析</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
        unsafe_allow_html=True)

    # 显示筛选后所有经销商的物料费比
    if filtered_distributor is not None and len(filtered_distributor) > 0:
        # 筛选有效数据并按费比排序
        valid_data = filtered_distributor[
            (filtered_distributor['物料销售比率'] > 0) &
            (filtered_distributor['物料销售比率'] < 100)  # 过滤极端值
            ]

        if len(valid_data) > 0:
            # 根据数据量判断是否需要显示全部
            data_length = len(valid_data)

            if data_length <= 30:  # 如果数据不多，显示全部
                plot_data = valid_data.sort_values('物料销售比率')
            else:
                # 修改为显示排序后的全部数据，但只标注重要的点
                # 先为所有数据点设置标签显示标志
                plot_data = valid_data.sort_values('物料销售比率')

                # 添加标签显示标志
                plot_data['显示标签'] = False

                # 将最高和最低的各10个标记为显示标签
                low_indices = plot_data.head(10).index
                high_indices = plot_data.tail(10).index
                plot_data.loc[low_indices, '显示标签'] = True
                plot_data.loc[high_indices, '显示标签'] = True

            # 完整显示经销商名称，不截断
            plot_data['经销商名称显示'] = plot_data['经销商名称']

            # 创建条形图
            fig = go.Figure()

            # 添加基本的条形图
            fig.add_trace(go.Bar(
                x=plot_data['物料销售比率'],
                y=plot_data['经销商名称显示'],
                orientation='h',
                text=plot_data['物料销售比率'].apply(lambda x: f"{x:.1f}%"),
                textposition='outside',
                marker=dict(
                    color=[
                        '#34C759' if x <= 30 else
                        '#FFCC00' if x <= 40 else
                        '#FF9500' if x <= 50 else
                        '#FF3B30' for x in plot_data['物料销售比率']
                    ],
                    line=dict(width=0.5, color='white')
                ),
                hovertemplate='<b>%{y}</b><br>' +
                              '物料费比: <b>%{x:.2f}%</b><br>' +
                              '物料总成本: ¥%{customdata[0]:,.2f}<br>' +
                              '销售总额: ¥%{customdata[1]:,.2f}<br>' +
                              '物料产出比: %{customdata[2]:.2f}',
                customdata=np.column_stack((
                    plot_data['物料总成本'] if '物料总成本' in plot_data.columns else np.zeros(len(plot_data)),
                    plot_data['销售总额'] if '销售总额' in plot_data.columns else np.zeros(len(plot_data)),
                    plot_data['ROI'] if 'ROI' in plot_data.columns else np.zeros(len(plot_data))
                ))
            ))

            # 添加参考线
            for threshold, color in [(30, '#34C759'), (40, '#FFCC00'), (50, '#FF9500')]:
                fig.add_shape(
                    type="line",
                    x0=threshold,
                    y0=-0.5,
                    x1=threshold,
                    y1=len(plot_data) - 0.5,
                    line=dict(color=color, width=1.5, dash="dash")
                )

                # 添加标签说明
                label_text = f"{threshold}% "
                if threshold == 30:
                    label_text += "(优)"
                elif threshold == 40:
                    label_text += "(良)"
                elif threshold == 50:
                    label_text += "(中)"

                # 将标签放在线条旁边
                fig.add_annotation(
                    x=threshold + 2,
                    y=0,
                    text=label_text,
                    showarrow=False,
                    font=dict(size=10, color=color),
                    bgcolor="rgba(255,255,255,0.7)",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=2
                )

            # 根据数据量动态设置图表高度和间距
            row_height = 35  # 每行所需的像素高度
            fig.update_layout(
                title=dict(
                    text=f"经销商物料费比分析 (共{len(plot_data)}家)",
                    font=dict(size=16, family="PingFang SC", color="#333333"),
                    x=0.01
                ),
                # 动态设置高度
                height=max(600, len(plot_data) * row_height),
                xaxis=dict(
                    title="物料费比 (%)",
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.6)',
                    ticksuffix="%",
                    range=[0, max(plot_data['物料销售比率']) * 1.2]  # 增加右侧边距
                ),
                yaxis=dict(
                    title="经销商",
                    showgrid=False,
                    autorange="reversed",
                    automargin=True,  # 自动调整边距
                    tickfont=dict(size=10)
                ),
                margin=dict(l=250, r=80, t=60, b=60),  # 大幅增加左侧边距
                showlegend=False,
                plot_bgcolor='white',
                bargap=0.2  # 调整条形间距
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加图例说明
            st.markdown("""
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-top: 5px;">
                <div><span style="background-color: rgba(52, 199, 89, 0.2); padding: 2px 6px; border-radius: 3px;">≤30% (优)</span></div>
                <div><span style="background-color: rgba(255, 204, 0, 0.2); padding: 2px 6px; border-radius: 3px;">31-40% (良)</span></div>
                <div><span style="background-color: rgba(255, 149, 0, 0.2); padding: 2px 6px; border-radius: 3px;">41-50% (中)</span></div>
                <div><span style="background-color: rgba(255, 59, 48, 0.2); padding: 2px 6px; border-radius: 3px;">>50% (差)</span></div>
            </div>
            """, unsafe_allow_html=True)

            # 添加计算逻辑说明
            st.info("""
            **物料费比计算逻辑说明**:
            1. 物料费比 = (物料总成本 ÷ 销售总额) × 100%
            2. 费比越低代表物料使用效率越高
            3. 优良中差划分标准: ≤30%(优)，31-40%(良)，41-50%(中)，>50%(差)
            """)
        else:
            st.info("暂无符合筛选条件的经销商物料费比数据。")
    else:
        st.info("暂无经销商物料费比数据。")

    st.markdown('</div>', unsafe_allow_html=True)


def create_modified_customer_roi_analysis(filtered_material, filtered_sales):
    """创建客户级别的物料投入产出分析（替代原产品级别分析）"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">客户物料投入产出分析</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
                unsafe_allow_html=True)

    # 检查是否有物料和销售数据
    if filtered_material is None or len(filtered_material) == 0:
        st.warning("缺少物料数据，无法进行分析。")
    elif filtered_sales is None or len(filtered_sales) == 0:
        st.warning("缺少销售数据，无法进行完整分析。")
    else:
        # 筛选选项
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            top_n = st.selectbox("显示TOP", [10, 15, 20, 30], index=1)
        with col2:
            show_option = st.selectbox("显示方式", ["最高物料产出比", "最低物料产出比"], index=0)

        # 按客户代码聚合数据
        customer_material = filtered_material.groupby(['客户代码', '经销商名称'])['物料成本'].sum().reset_index()
        customer_sales = filtered_sales.groupby(['客户代码', '经销商名称'])['销售金额'].sum().reset_index()

        # 合并数据
        customer_analysis = pd.merge(
            customer_material,
            customer_sales,
            on=['客户代码', '经销商名称'],
            how='inner'
        )

        # 计算客户ROI
        customer_analysis['ROI'] = np.where(
            customer_analysis['物料成本'] > 0,
            customer_analysis['销售金额'] / customer_analysis['物料成本'],
            0
        )
        customer_analysis['ROI'] = customer_analysis['ROI'].clip(upper=5.0)  # 限制极端值

        # 计算物料费比
        customer_analysis['物料费比'] = np.where(
            customer_analysis['销售金额'] > 0,
            (customer_analysis['物料成本'] / customer_analysis['销售金额'] * 100).round(2),
            0
        )

        # 按ROI排序并选择TOP N
        if show_option == "最高物料产出比":
            filtered_customer = customer_analysis.sort_values('ROI', ascending=False).head(top_n)
        else:
            filtered_customer = customer_analysis.sort_values('ROI').head(top_n)

        # 创建图表
        fig = px.bar(
            filtered_customer,
            x='经销商名称',
            y='ROI',
            color='物料费比',
            color_continuous_scale=[(0, '#0FC86F'), (0.5, '#FFAA00'), (1, '#F53F3F')],
            title=f"{'TOP' if show_option == '最高物料产出比' else '最低'} {top_n} 客户物料投入产出比",
            height=500,
            labels={"经销商名称": "经销商", "ROI": "物料产出比", "物料费比": "物料费比 (%)"},
            hover_data={
                "经销商名称": True,
                "ROI": ":.2f",
                "物料费比": ":.2f%",
                "物料成本": ":,.2f元",
                "销售金额": ":,.2f元"
            }
        )

        # 改进悬停信息
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>' +
                          '物料产出比: <b>%{y:.2f}</b><br>' +
                          '物料费比: %{marker.color:.1f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售金额: ¥%{customdata[1]:,.2f}',
            customdata=np.column_stack((
                filtered_customer['物料成本'],
                filtered_customer['销售金额']
            ))
        )

        # 添加盈亏平衡线
        fig.add_shape(
            type="line",
            x0=-0.5, y0=1,
            x1=len(filtered_customer) - 0.5, y1=1,
            line=dict(color="#FF3B30", width=2, dash="dash")
        )

        # 添加参考线注释
        fig.add_annotation(
            x=filtered_customer['经销商名称'].iloc[-1] if len(filtered_customer) > 0 else "",
            y=1.05,
            text="盈亏平衡线 (产出比=1)",
            showarrow=False,
            font=dict(size=12, color="#FF3B30"),
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#FF3B30",
            borderwidth=1,
            borderpad=4
        )

        # 更新布局
        fig.update_layout(
            xaxis=dict(
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=11)
            ),
            yaxis=dict(
                title="物料产出比",
                title_font=dict(size=14),
                gridcolor='rgba(224, 228, 234, 0.6)'
            ),
            margin=dict(l=50, r=50, t=50, b=150),
            paper_bgcolor='white',
            plot_bgcolor='white',
            coloraxis_colorbar=dict(
                title="物料费比 (%)",
                ticksuffix="%"
            )
        )

        st.plotly_chart(fig, use_container_width=True)

        # 添加图表解读
        st.markdown('''
        <div class="chart-explanation">
            <div class="chart-explanation-title">图表解读：</div>
            <p>此图展示了客户的物料投入产出效率。柱高表示物料产出比(销售额/物料成本)，颜色表示物料费比(物料成本/销售额×100%)。
            红色虚线是盈亏平衡线(产出比=1)，位于线上方的客户产生正回报，线下方的客户产生负回报。
            颜色从绿到红表示物料费比从低到高，绿色表示物料使用效率高。通过此图可以识别效率最高和最低的客户，有针对性地优化物料投放策略。
            鼠标悬停可查看详细财务数据。</p>
        </div>
        ''', unsafe_allow_html=True)

        st.info("""
        **客户物料产出比计算逻辑**:
        1. 物料产出比 = 客户销售总额 ÷ 客户物料总成本
        2. 物料费比 = (客户物料总成本 ÷ 客户销售总额) × 100%
        3. 该指标基于客户级别匹配计算，反映客户整体物料投入产出效率
        """)

    st.markdown('</div>', unsafe_allow_html=True)
def create_sidebar_filters(material_data, sales_data, distributor_data):
    """创建具有正确交叉筛选逻辑的侧边栏筛选器"""

    # 设置侧边栏标题和样式
    st.sidebar.markdown(
        '<div style="text-align: center; padding: 10px 0; margin-bottom: 18px; border-bottom: 1px solid #E0E4EA;">'
        '<h3 style="color: #2B5AED; font-size: 16px; margin: 0; font-weight: 600;">物料投放分析</h3>'
        '<p style="color: #646A73; font-size: 12px; margin: 5px 0 0 0;">筛选面板</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # 筛选区域样式改进
    filter_style = """
    <style>
        div[data-testid="stVerticalBlock"] > div:has(div.sidebar-filter-heading) {
            background-color: rgba(43, 90, 237, 0.03);
            border-radius: 6px;
            padding: 12px;
            margin-bottom: 14px;
            border-left: 2px solid #2B5AED;
        }
        .sidebar-filter-heading {
            font-weight: 600;
            color: #2B5AED;
            margin-bottom: 10px;
            font-size: 13px;
        }
        .sidebar-selection-info {
            font-size: 11px;
            color: #646A73;
            margin-top: 4px;
            margin-bottom: 6px;
        }
        .sidebar-filter-description {
            font-size: 11px;
            color: #8F959E;
            font-style: italic;
            margin-top: 6px;
            margin-bottom: 0;
        }
        .sidebar-badge {
            display: inline-block;
            background-color: rgba(43, 90, 237, 0.1);
            color: #2B5AED;
            border-radius: 4px;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: 500;
            margin-top: 6px;
        }
        /* 减小多选框的间距 */
        div[data-testid="stMultiSelect"] {
            margin-bottom: 0px;
        }
        /* 调整复选框和标签的大小 */
        .stCheckbox label, .stCheckbox label span p {
            font-size: 12px !important;
        }
        /* 减小筛选器之间的间距 */
        div.stSelectbox, div.stMultiSelect {
            margin-bottom: 0px;
        }
    </style>
    """
    st.sidebar.markdown(filter_style, unsafe_allow_html=True)

    # 初始化会话状态变量
    if 'filter_state' not in st.session_state:
        st.session_state.filter_state = {
            'regions': [],
            'provinces': [],
            'categories': [],
            'distributors': [],
            'show_provinces': False,
            'show_categories': False,
            'show_distributors': False
        }

    # 获取原始数据的所有唯一值（用于显示全量选项）
    all_regions = sorted(material_data['所属区域'].unique()) if '所属区域' in material_data.columns else []
    all_material_categories = sorted(material_data['物料类别'].unique()) if '物料类别' in material_data.columns else []

    # 区域筛选部分
    st.sidebar.markdown('<div class="sidebar-filter-heading">区域筛选</div>', unsafe_allow_html=True)

    # 全选按钮 - 区域
    col1, col2 = st.sidebar.columns([3, 1])
    with col1:
        st.markdown("<span style='font-weight: 500; font-size: 12px;'>选择区域</span>", unsafe_allow_html=True)
    with col2:
        all_regions_selected = st.checkbox("全选", value=True, key="all_regions")

    # 根据全选状态设置默认值
    if all_regions_selected:
        default_regions = all_regions
    else:
        default_regions = st.session_state.filter_state['regions'] if st.session_state.filter_state['regions'] else []

    # 区域多选框
    selected_regions = st.sidebar.multiselect(
        "区域列表",
        all_regions,
        default=default_regions,
        help="选择要分析的销售区域",
        label_visibility="collapsed"
    )

    # 更新会话状态
    st.session_state.filter_state['regions'] = selected_regions

    # 创建一个初步筛选的物料和销售数据集，基于区域选择
    if selected_regions:
        filtered_by_region_material = material_data[material_data['所属区域'].isin(selected_regions)]
        filtered_by_region_sales = sales_data[sales_data['所属区域'].isin(selected_regions)]

        # 更新可用的省份列表（基于选择的区域）
        available_provinces = sorted(
            filtered_by_region_material['省份'].unique()) if '省份' in filtered_by_region_material.columns else []

        # 显示已选区域数量
        st.sidebar.markdown(
            f'<div class="sidebar-selection-info">已选择 {len(selected_regions)}/{len(all_regions)} 个区域</div>',
            unsafe_allow_html=True
        )

        # 显示动态区域徽章
        badges_html = ""
        for region in selected_regions[:3]:
            badges_html += f'<span class="sidebar-badge">{region}</span>&nbsp;'
        if len(selected_regions) > 3:
            badges_html += f'<span class="sidebar-badge">+{len(selected_regions) - 3}个</span>'
        st.sidebar.markdown(badges_html, unsafe_allow_html=True)

        # 启用其他筛选器
        show_provinces = True
        show_categories = True
    else:
        filtered_by_region_material = pd.DataFrame()  # 空DataFrame
        filtered_by_region_sales = pd.DataFrame()  # 空DataFrame
        available_provinces = []
        show_provinces = False
        show_categories = False
        st.sidebar.markdown(
            '<div class="sidebar-filter-description">请至少选择一个区域以继续筛选</div>',
            unsafe_allow_html=True
        )

    # 省份筛选 - 仅当选择了区域时显示
    if show_provinces and len(available_provinces) > 0:
        st.sidebar.markdown('<div class="sidebar-filter-heading">省份筛选</div>', unsafe_allow_html=True)

        # 全选按钮 - 省份
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown("<span style='font-weight: 500; font-size: 12px;'>选择省份</span>", unsafe_allow_html=True)
        with col2:
            all_provinces_selected = st.checkbox("全选", value=True, key="all_provinces")

        # 根据全选状态设置默认值
        if all_provinces_selected:
            default_provinces = available_provinces
        else:
            # 确保之前选择的省份仍然存在于当前可选列表中
            previous_provinces = [p for p in st.session_state.filter_state['provinces'] if p in available_provinces]
            default_provinces = previous_provinces if previous_provinces else []

        # 省份多选框
        selected_provinces = st.sidebar.multiselect(
            "省份列表",
            available_provinces,
            default=default_provinces,
            help="选择要分析的省份",
            label_visibility="collapsed"
        )

        # 更新会话状态
        st.session_state.filter_state['provinces'] = selected_provinces

        # 基于区域和省份筛选
        if selected_provinces:
            filtered_by_province_material = filtered_by_region_material[
                filtered_by_region_material['省份'].isin(selected_provinces)]
            filtered_by_province_sales = filtered_by_region_sales[
                filtered_by_region_sales['省份'].isin(selected_provinces)]

            # 显示已选省份数量
            st.sidebar.markdown(
                f'<div class="sidebar-selection-info">已选择 {len(selected_provinces)}/{len(available_provinces)} 个省份</div>',
                unsafe_allow_html=True
            )

            # 显示动态省份徽章
            badges_html = ""
            for province in selected_provinces[:3]:
                badges_html += f'<span class="sidebar-badge">{province}</span>&nbsp;'
            if len(selected_provinces) > 3:
                badges_html += f'<span class="sidebar-badge">+{len(selected_provinces) - 3}个</span>'
            st.sidebar.markdown(badges_html, unsafe_allow_html=True)

            # 启用经销商筛选器
            show_distributors = True
        else:
            filtered_by_province_material = filtered_by_region_material  # 如果未选择省份，使用区域筛选的结果
            filtered_by_province_sales = filtered_by_region_sales  # 如果未选择省份，使用区域筛选的结果
            show_distributors = False
            st.sidebar.markdown(
                '<div class="sidebar-filter-description">请至少选择一个省份以继续筛选</div>',
                unsafe_allow_html=True
            )
    else:
        filtered_by_province_material = filtered_by_region_material  # 如果未启用省份筛选，使用区域筛选的结果
        filtered_by_province_sales = filtered_by_region_sales  # 如果未启用省份筛选，使用区域筛选的结果
        selected_provinces = []
        show_distributors = False

    # 物料类别筛选 - 仅当选择了区域时显示
    if show_categories:
        st.sidebar.markdown('<div class="sidebar-filter-heading">物料筛选</div>', unsafe_allow_html=True)

        # 获取经过区域和省份筛选后可用的物料类别
        available_categories = sorted(filtered_by_province_material[
                                          '物料类别'].unique()) if '物料类别' in filtered_by_province_material.columns else []

        # 全选按钮 - 物料类别
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown("<span style='font-weight: 500; font-size: 12px;'>选择物料类别</span>", unsafe_allow_html=True)
        with col2:
            all_categories_selected = st.checkbox("全选", value=True, key="all_categories")

        # 根据全选状态设置默认值
        if all_categories_selected:
            default_categories = available_categories
        else:
            # 确保之前选择的类别仍然存在于当前可选列表中
            previous_categories = [c for c in st.session_state.filter_state['categories'] if c in available_categories]
            default_categories = previous_categories if previous_categories else []

        # 物料类别多选框
        selected_categories = st.sidebar.multiselect(
            "物料类别列表",
            available_categories,
            default=default_categories,
            help="选择要分析的物料类别",
            label_visibility="collapsed"
        )

        # 更新会话状态
        st.session_state.filter_state['categories'] = selected_categories

        # 基于物料类别进一步筛选
        if selected_categories and len(filtered_by_province_material) > 0:
            filtered_by_category_material = filtered_by_province_material[
                filtered_by_province_material['物料类别'].isin(selected_categories)]

            # 获取经过类别筛选后剩余的经销商
            if '经销商名称' in filtered_by_category_material.columns:
                remaining_distributors = filtered_by_category_material['经销商名称'].unique()
                # 根据物料筛选结果筛选销售数据
                filtered_by_category_sales = filtered_by_province_sales[
                    filtered_by_province_sales['经销商名称'].isin(remaining_distributors)]
            else:
                filtered_by_category_sales = filtered_by_province_sales  # 如果没有经销商列，不做进一步筛选

            # 显示已选物料类别数量
            st.sidebar.markdown(
                f'<div class="sidebar-selection-info">已选择 {len(selected_categories)}/{len(available_categories)} 个物料类别</div>',
                unsafe_allow_html=True
            )

            # 显示动态类别徽章
            badges_html = ""
            for category in selected_categories[:3]:
                badges_html += f'<span class="sidebar-badge">{category}</span>&nbsp;'
            if len(selected_categories) > 3:
                badges_html += f'<span class="sidebar-badge">+{len(selected_categories) - 3}个</span>'
            st.sidebar.markdown(badges_html, unsafe_allow_html=True)
        else:
            filtered_by_category_material = filtered_by_province_material  # 如果未选择类别，使用省份筛选的结果
            filtered_by_category_sales = filtered_by_province_sales  # 如果未选择类别，使用省份筛选的结果

            if not selected_categories:
                st.sidebar.markdown(
                    '<div class="sidebar-filter-description">请至少选择一个物料类别</div>',
                    unsafe_allow_html=True
                )
    else:
        filtered_by_category_material = filtered_by_province_material  # 如果未启用类别筛选，使用省份筛选的结果
        filtered_by_category_sales = filtered_by_province_sales  # 如果未启用类别筛选，使用省份筛选的结果
        selected_categories = []

    # 经销商筛选 - 仅当选择了省份时显示
    if show_distributors:
        st.sidebar.markdown('<div class="sidebar-filter-heading">经销商筛选</div>', unsafe_allow_html=True)

        # 获取经过前面所有筛选后可用的经销商
        if '经销商名称' in filtered_by_category_material.columns:
            available_distributors = sorted(filtered_by_category_material['经销商名称'].unique())
        else:
            # 如果物料数据中没有经销商名称列，从销售数据中获取
            available_distributors = sorted(filtered_by_category_sales[
                                                '经销商名称'].unique()) if '经销商名称' in filtered_by_category_sales.columns else []

        # 全选按钮 - 经销商
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.markdown("<span style='font-weight: 500; font-size: 12px;'>选择经销商</span>", unsafe_allow_html=True)
        with col2:
            all_distributors_selected = st.checkbox("全选", value=True, key="all_distributors")

        # 根据全选状态设置默认值
        if all_distributors_selected:
            default_distributors = available_distributors
        else:
            # 确保之前选择的经销商仍然存在于当前可选列表中
            previous_distributors = [d for d in st.session_state.filter_state['distributors'] if
                                     d in available_distributors]
            default_distributors = previous_distributors if previous_distributors else []

        # 经销商多选框
        selected_distributors = st.sidebar.multiselect(
            "经销商列表",
            available_distributors,
            default=default_distributors,
            help="选择要分析的经销商",
            label_visibility="collapsed"
        )

        # 更新会话状态
        st.session_state.filter_state['distributors'] = selected_distributors

        # 基于经销商进一步筛选
        if selected_distributors:
            # 筛选物料和销售数据
            final_material = filtered_by_category_material[
                filtered_by_category_material['经销商名称'].isin(selected_distributors)]
            final_sales = filtered_by_category_sales[
                filtered_by_category_sales['经销商名称'].isin(selected_distributors)]

            # 显示已选经销商数量
            st.sidebar.markdown(
                f'<div class="sidebar-selection-info">已选择 {len(selected_distributors)}/{len(available_distributors)} 个经销商</div>',
                unsafe_allow_html=True
            )

            # 显示经销商选择数量信息
            if len(selected_distributors) > 3:
                st.sidebar.markdown(
                    f'<div class="sidebar-badge">已选择 {len(selected_distributors)} 个经销商</div>',
                    unsafe_allow_html=True
                )
            else:
                badges_html = ""
                for distributor in selected_distributors:
                    badges_html += f'<span class="sidebar-badge">{distributor[:10]}{"..." if len(distributor) > 10 else ""}</span>&nbsp;'
                st.sidebar.markdown(badges_html, unsafe_allow_html=True)
        else:
            final_material = filtered_by_category_material  # 如果未选择经销商，使用类别筛选的结果
            final_sales = filtered_by_category_sales  # 如果未选择经销商，使用类别筛选的结果

            st.sidebar.markdown(
                '<div class="sidebar-filter-description">请至少选择一个经销商</div>',
                unsafe_allow_html=True
            )
    else:
        final_material = filtered_by_category_material  # 如果未启用经销商筛选，使用类别筛选的结果
        final_sales = filtered_by_category_sales  # 如果未启用经销商筛选，使用类别筛选的结果
        selected_distributors = []

    # 筛选经销商统计数据
    if len(distributor_data) > 0:
        # 基于区域筛选
        distributor_filter = pd.Series(True, index=distributor_data.index)
        if selected_regions and '所属区域' in distributor_data.columns:
            distributor_filter &= distributor_data['所属区域'].isin(selected_regions)

        # 基于省份筛选
        if selected_provinces and '省份' in distributor_data.columns:
            distributor_filter &= distributor_data['省份'].isin(selected_provinces)

        # 基于经销商名称筛选
        if selected_distributors and '经销商名称' in distributor_data.columns:
            distributor_filter &= distributor_data['经销商名称'].isin(selected_distributors)

        # 如果物料筛选条件已设置，只保留有相关物料记录的经销商
        if selected_categories and len(final_material) > 0 and '经销商名称' in distributor_data.columns:
            active_distributors = final_material['经销商名称'].unique()
            distributor_filter &= distributor_data['经销商名称'].isin(active_distributors)

        final_distributor = distributor_data[distributor_filter]
    else:
        final_distributor = pd.DataFrame()  # 空DataFrame

    # 添加更新按钮
    st.sidebar.markdown('<br>', unsafe_allow_html=True)
    update_button = st.sidebar.button(
        "📊 更新仪表盘",
        help="点击后根据筛选条件更新仪表盘数据",
        use_container_width=True,
        type="primary",
    )

    # 添加重置按钮
    reset_button = st.sidebar.button(
        "♻️ 重置筛选条件",
        help="恢复默认筛选条件",
        use_container_width=True
    )

    if reset_button:
        # 重置会话状态
        st.session_state.filter_state = {
            'regions': all_regions,
            'provinces': [],
            'categories': [],
            'distributors': [],
            'show_provinces': False,
            'show_categories': False,
            'show_distributors': False
        }
        # 刷新页面
        st.experimental_rerun()

    # 添加数据下载区域
    st.sidebar.markdown(
        '<div style="background-color: rgba(43, 90, 237, 0.05); border-radius: 6px; padding: 12px; margin-top: 16px;">'
        '<p style="font-weight: 600; color: #2B5AED; margin-bottom: 8px; font-size: 13px;">数据导出</p>',
        unsafe_allow_html=True
    )

    cols = st.sidebar.columns(2)
    with cols[0]:
        # 修改按钮文字以及样式，保持一致的字体大小
        material_download = st.button(
            "📥 物料数据",
            key="dl_material",
            use_container_width=True,
            # 可以添加自定义CSS类来控制字体
        )
    with cols[1]:
        # 修改按钮文字以及样式，保持一致的字体大小
        sales_download = st.button(
            "📥 销售数据",
            key="dl_sales",
            use_container_width=True,
            # 可以添加自定义CSS类来控制字体
        )

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # 添加CSS样式来确保按钮文字大小一致
    st.markdown("""
    <style>
        /* 确保按钮内的文字大小统一 */
        .stButton button {
            font-size: 14px !important;
            text-align: center !important;
            padding: 0.25rem 0.5rem !important;
        }

        /* 可以调整按钮内emoji和文字的对齐方式 */
        .stButton button p {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 处理下载按钮逻辑
    if material_download:
        csv = final_material.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button(
            label="点击下载物料数据",
            data=csv,
            file_name=f"物料数据_筛选结果.csv",
            mime="text/csv",
        )

    if sales_download:
        csv = final_sales.to_csv(index=False).encode('utf-8-sig')
        st.sidebar.download_button(
            label="点击下载销售数据",
            data=csv,
            file_name=f"销售数据_筛选结果.csv",
            mime="text/csv",
        )

    # 业务指标说明 - 更简洁的折叠式设计
    with st.sidebar.expander("🔍 业务指标说明", expanded=False):
        for term, definition in BUSINESS_DEFINITIONS.items():
            st.markdown(f"**{term}**:<br>{definition}", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 6px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    # 物料类别效果分析
    with st.sidebar.expander("📊 物料类别效果分析", expanded=False):
        for category, insight in MATERIAL_CATEGORY_INSIGHTS.items():
            st.markdown(f"**{category}**:<br>{insight}", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 6px 0; opacity: 0.2;'>", unsafe_allow_html=True)

    return final_material, final_sales, final_distributor


def main():
    """主函数 - 控制仪表盘整体布局和数据流"""

    # 设置页面配置和样式
    st.set_page_config(
        page_title="物料投放分析动态仪表盘",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # 应用全局字体样式设置
    set_global_font_styles(base_size=14, title_size=20, subtitle_size=16, chart_title_size=15,
                       text_size=13, small_text_size=12,
                       font_family="'PingFang SC', 'Helvetica Neue', Arial, sans-serif")

    # 加载自定义CSS提升视觉效果
    st.markdown('''
    <style>
        .feishu-title {
            font-size: 26px;
            font-weight: 600;
            color: #1D2129;
            margin-bottom: 8px;
        }
        .feishu-subtitle {
            font-size: 16px;
            color: #4E5969;
            margin-bottom: 24px;
        }
        .feishu-chart-title {
            font-size: 18px;
            font-weight: 600;
            color: #1D2129;
            margin-bottom: 16px;
        }
        .feishu-chart-subtitle {
            font-size: 16px;
            color: #4E5969;
            margin-bottom: 12px;
        }
        /* 移除表格样式，全部使用图表 */
        .dataframe {
            display: none !important;
        }
        /* 提升图表容器样式 */
        .chart-container {
            background-color: white;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            margin-bottom: 24px;
        }
        /* 优化标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #F7F8FA;
            border-radius: 4px 4px 0px 0px;
            padding: 10px 16px;
            font-size: 16px;
        }
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-top: 3px solid #4880FF;
        }
    </style>
    ''', unsafe_allow_html=True)

    # 加载数据
    material_data, sales_data, material_price, distributor_data = get_data()

    # 验证数据一致性
    consistency_warnings = validate_data_consistency(material_data, sales_data, distributor_data)
    if consistency_warnings:
        with st.expander("ℹ️ 数据匹配状态", expanded=False):
            for warning in consistency_warnings:
                st.info(warning)  # 使用info而非warning，因为这是正常情况

    # 页面标题
    st.markdown('<div class="feishu-title">物料投放分析动态仪表盘</div>', unsafe_allow_html=True)
    st.markdown('<div class="feishu-subtitle">基于客户匹配的物料投入与销售产出分析</div>', unsafe_allow_html=True)

    # 应用侧边栏筛选
    filtered_material, filtered_sales, filtered_distributor = create_sidebar_filters(
        material_data, sales_data, distributor_data
    )

    # 创建标签页 - 优化为三个标签页
    tab1, tab2, tab3 = st.tabs(["物料与销售分析", "经销商分析", "产品与物料优化"])

    with tab1:
        # 物料与销售分析标签页
        create_material_sales_relationship(filtered_distributor)

        # 使用客户级别ROI分析替代产品级别分析，避免重复
        create_modified_customer_roi_analysis(filtered_material, filtered_sales)

        # 添加费用比率分析
        create_expense_ratio_analysis(filtered_distributor)

        # 增加物料类别分析
        create_material_category_analysis(filtered_material, filtered_sales)

    with tab2:
        # 经销商分析标签页
        create_distributor_analysis_tab(filtered_distributor, filtered_material, filtered_sales)

    with tab3:
        # 新增产品与物料优化标签页
        create_product_optimization_tab(filtered_material, filtered_sales, filtered_distributor)

# 运行主应用
if __name__ == '__main__':
    main()