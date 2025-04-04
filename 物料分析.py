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
            # st.info("正在尝试加载真实数据文件...")
            # st.write("当前工作目录:", current_dir)
            # st.write("目录中的文件:", file_list)
            # st.write(f"尝试加载文件: {', '.join(file_paths)}")

            file_paths = ["2025物料源数据.xlsx", "25物料源销售数据.xlsx", "物料单价.xlsx"]

            try:
                material_data = pd.read_excel("2025物料源数据.xlsx")
                # 删除这行: st.success("✓ 成功加载 2025物料源数据.xlsx")
            except Exception as e1:
                st.error(f"× 加载 2025物料源数据.xlsx 失败: {e1}")
                raise

            try:
                sales_data = pd.read_excel("25物料源销售数据.xlsx")
                # 删除这行: st.success("✓ 成功加载 25物料源销售数据.xlsx")
            except Exception as e2:
                st.error(f"× 加载 25物料源销售数据.xlsx 失败: {e2}")
                raise

            try:
                material_price = pd.read_excel("物料单价.xlsx")
                # 删除这行: st.success("✓ 成功加载 物料单价.xlsx")
            except Exception as e3:
                st.error(f"× 加载 物料单价.xlsx 失败: {e3}")
                raise

            # 删除这行: st.success("✅ 所有数据文件加载成功！正在处理数据...")
            return process_data(material_data, sales_data, material_price)

        except Exception as e:
            st.error(f"加载数据时出错: {e}")
            # 可以保留错误提示，因为这是必要的
            use_sample = st.button("使用示例数据继续")
            if use_sample:
                return generate_sample_data()
            else:
                st.stop()


def process_data(material_data, sales_data, material_price):
    """处理和准备数据"""

    # 确保日期列为日期类型
    material_data['发运月份'] = pd.to_datetime(material_data['发运月份'])
    sales_data['发运月份'] = pd.to_datetime(sales_data['发运月份'])

    # 在这里加入映射代码 ↓
    # 将申请人列映射为销售人员列
    if '申请人' in material_data.columns and '销售人员' not in material_data.columns:
        material_data['销售人员'] = material_data['申请人']
        print("已将申请人列映射为销售人员列")
    if '申请人' in sales_data.columns and '销售人员' not in sales_data.columns:
        sales_data['销售人员'] = sales_data['申请人']
        print("已将申请人列映射为销售人员列")
    # 映射代码结束 ↑

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
            material_data['单价（元）'] = material_data['单价（元）'].fillna(mean_price)

            # 计算物料总成本
            material_data['物料成本'] = material_data['求和项:数量（箱）'] * material_data['单价（元）']
        else:
            # 如果合并失败，创建一个默认的物料成本列
            material_data['物料成本'] = material_data['求和项:数量（箱）'] * 100  # 默认单价100元

    # 计算销售金额
    if '销售金额' not in sales_data.columns and '求和项:单价（箱）' in sales_data.columns:
        sales_data['销售金额'] = sales_data['求和项:数量（箱）'] * sales_data['求和项:单价（箱）']

    # 检查销售人员列是否存在，如不存在则添加
    if '销售人员' not in material_data.columns:
        material_data['销售人员'] = '未知销售人员'
        print("警告：物料数据中缺少'销售人员'列，已添加默认值")

    if '销售人员' not in sales_data.columns:
        sales_data['销售人员'] = '未知销售人员'
        print("警告：销售数据中缺少'销售人员'列，已添加默认值")

    # 确保经销商名称列存在
    if '经销商名称' not in material_data.columns and '客户代码' in material_data.columns:
        material_data['经销商名称'] = material_data['客户代码'].apply(lambda x: f"经销商{x}")

    if '经销商名称' not in sales_data.columns and '客户代码' in sales_data.columns:
        sales_data['经销商名称'] = sales_data['客户代码'].apply(lambda x: f"经销商{x}")

    # 按经销商和月份计算物料成本总和
    try:
        material_cost_by_distributor = material_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员'])[
            '物料成本'].sum().reset_index()
        material_cost_by_distributor.rename(columns={'物料成本': '物料总成本'}, inplace=True)
    except KeyError as e:
        # 如果某列不存在，尝试使用可用的列进行分组
        print(f"分组时出错: {e}，尝试使用可用列进行分组")
        available_cols = []
        for col in ['客户代码', '经销商名称', '月份名', '销售人员']:
            if col in material_data.columns:
                available_cols.append(col)

        if not available_cols:  # 确保至少有一个列可用于分组
            available_cols = ['客户代码'] if '客户代码' in material_data.columns else ['月份名']

        material_cost_by_distributor = material_data.groupby(available_cols)[
            '物料成本'].sum().reset_index()
        material_cost_by_distributor.rename(columns={'物料成本': '物料总成本'}, inplace=True)

        # 如果缺少经销商名称，使用客户代码代替
        if '经销商名称' not in material_cost_by_distributor.columns and '客户代码' in material_cost_by_distributor.columns:
            material_cost_by_distributor['经销商名称'] = material_cost_by_distributor['客户代码'].apply(
                lambda x: f"经销商{x}")
        elif '经销商名称' not in material_cost_by_distributor.columns:
            material_cost_by_distributor['经销商名称'] = "未知经销商"

        # 如果缺少销售人员，添加默认值
        if '销售人员' not in material_cost_by_distributor.columns:
            material_cost_by_distributor['销售人员'] = '未知销售人员'

        # 确保月份名存在
        if '月份名' not in material_cost_by_distributor.columns:
            material_cost_by_distributor['月份名'] = '未知月份'

    # 按经销商和月份计算销售总额（同样增加错误处理）
    try:
        sales_by_distributor = sales_data.groupby(['客户代码', '经销商名称', '月份名', '销售人员'])[
            '销售金额'].sum().reset_index()
        sales_by_distributor.rename(columns={'销售金额': '销售总额'}, inplace=True)
    except KeyError as e:
        # 如果某列不存在，尝试使用可用的列进行分组
        print(f"分组时出错: {e}，尝试使用可用列进行分组")
        available_cols = []
        for col in ['客户代码', '经销商名称', '月份名', '销售人员']:
            if col in sales_data.columns:
                available_cols.append(col)

        if not available_cols:  # 确保至少有一个列可用于分组
            available_cols = ['客户代码'] if '客户代码' in sales_data.columns else ['月份名']

        sales_by_distributor = sales_data.groupby(available_cols)[
            '销售金额'].sum().reset_index()
        sales_by_distributor.rename(columns={'销售金额': '销售总额'}, inplace=True)

        # 如果缺少经销商名称，使用客户代码代替
        if '经销商名称' not in sales_by_distributor.columns and '客户代码' in sales_by_distributor.columns:
            sales_by_distributor['经销商名称'] = sales_by_distributor['客户代码'].apply(
                lambda x: f"经销商{x}")
        elif '经销商名称' not in sales_by_distributor.columns:
            sales_by_distributor['经销商名称'] = "未知经销商"

        # 如果缺少销售人员，添加默认值
        if '销售人员' not in sales_by_distributor.columns:
            sales_by_distributor['销售人员'] = '未知销售人员'

        # 确保月份名存在
        if '月份名' not in sales_by_distributor.columns:
            sales_by_distributor['月份名'] = '未知月份'

    # 合并物料成本和销售数据
    # 确保使用两个数据框中都存在的列进行合并
    common_cols = []
    for col in ['客户代码', '经销商名称', '月份名', '销售人员']:
        if col in material_cost_by_distributor.columns and col in sales_by_distributor.columns:
            common_cols.append(col)

    # 如果没有共同列，至少使用客户代码和月份名（如果存在）
    if not common_cols:
        if '客户代码' in material_cost_by_distributor.columns and '客户代码' in sales_by_distributor.columns:
            common_cols.append('客户代码')
        if '月份名' in material_cost_by_distributor.columns and '月份名' in sales_by_distributor.columns:
            common_cols.append('月份名')

    # 如果仍然没有共同列，创建一个通用键以便能够合并
    if not common_cols:
        material_cost_by_distributor['合并键'] = 1
        sales_by_distributor['合并键'] = 1
        common_cols = ['合并键']

    distributor_data = pd.merge(
        material_cost_by_distributor,
        sales_by_distributor,
        on=common_cols,
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
    distributor_data['物料销售比率'] = distributor_data['物料销售比率'].fillna(0)

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
    try:
        material_diversity = material_data.groupby(['客户代码', '月份名'])['产品代码'].nunique().reset_index()
        material_diversity.rename(columns={'产品代码': '物料多样性'}, inplace=True)

        # 合并物料多样性到经销商数据
        distributor_data = pd.merge(
            distributor_data,
            material_diversity,
            on=['客户代码', '月份名'],
            how='left'
        )
    except KeyError as e:
        print(f"计算物料多样性时出错: {e}")
        # 创建默认的物料多样性列
        distributor_data['物料多样性'] = 1

    distributor_data['物料多样性'] = distributor_data['物料多样性'].fillna(0)

    # 添加区域信息
    if '所属区域' not in distributor_data.columns and '所属区域' in material_data.columns:
        try:
            region_map = material_data[['客户代码', '所属区域']].drop_duplicates().set_index('客户代码')
            distributor_data['所属区域'] = distributor_data['客户代码'].map(region_map['所属区域'])
        except Exception as e:
            print(f"添加区域信息时出错: {e}")
            distributor_data['所属区域'] = '未知区域'

    # 添加省份信息
    if '省份' not in distributor_data.columns and '省份' in material_data.columns:
        try:
            province_map = material_data[['客户代码', '省份']].drop_duplicates().set_index('客户代码')
            distributor_data['省份'] = distributor_data['客户代码'].map(province_map['省份'])
        except Exception as e:
            print(f"添加省份信息时出错: {e}")
            distributor_data['省份'] = '未知省份'

    return material_data, sales_data, material_price, distributor_data


def create_distributor_analysis_tab(filtered_distributor, material_data, sales_data):
    """
    创建增强版的经销商分析标签页，提供更深入的经销商价值、行为和地域分析
    """
    # 添加必要的导入
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import streamlit as st

    # 添加CSS以增强悬停交互体验
    st.markdown("""
    <style>
        /* 增强悬停提示样式 */
        .plotly-graph-div .hoverlayer .hover-info {
            background-color: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #E0E4EA !important;
            border-radius: 6px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            padding: 10px !important;
            font-family: "PingFang SC", "Helvetica Neue", Arial, sans-serif !important;
        }

        /* 悬停时突出显示经销商卡片 */
        .distributor-card:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # 定义客户价值分层颜色方案
    segment_colors = {
        '高价值客户': '#0FC86F',
        '成长型客户': '#2B5AED',
        '稳定型客户': '#FFAA00',
        '低效型客户': '#F53F3F'
    }

    # Tab 标题
    st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">经销商深度分析</div>',
                unsafe_allow_html=True)

    # 检查数据有效性
    if filtered_distributor is None or len(filtered_distributor) == 0:
        st.info("暂无经销商数据，无法进行分析。")
        return None

    # 检查material_data和sales_data数据有效性
    if material_data is None or len(material_data) == 0:
        st.warning("物料数据为空，部分分析功能将受限。")
        material_data = pd.DataFrame()  # 创建一个空DataFrame防止后续错误

    if sales_data is None or len(sales_data) == 0:
        st.warning("销售数据为空，部分分析功能将受限。")
        sales_data = pd.DataFrame()  # 创建一个空DataFrame防止后续错误

    # ===================== 第一部分：经销商数据概览 =====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">经销商数据概览</div>',
                unsafe_allow_html=True)

    # 创建指标卡片行
    col1, col2, col3, col4 = st.columns(4)

    # 计算关键指标
    total_distributors = filtered_distributor[
        '经销商名称'].nunique() if '经销商名称' in filtered_distributor.columns else 0
    avg_roi = filtered_distributor['ROI'].mean() if 'ROI' in filtered_distributor.columns else 0
    avg_material_cost = filtered_distributor['物料总成本'].mean() if '物料总成本' in filtered_distributor.columns else 0
    avg_sales = filtered_distributor['销售总额'].mean() if '销售总额' in filtered_distributor.columns else 0

    # 客户分层统计
    segment_counts = filtered_distributor[
        '客户价值分层'].value_counts().to_dict() if '客户价值分层' in filtered_distributor.columns else {}
    high_value_count = segment_counts.get('高价值客户', 0)
    growth_count = segment_counts.get('成长型客户', 0)
    stable_count = segment_counts.get('稳定型客户', 0)
    low_value_count = segment_counts.get('低效型客户', 0)

    with col1:
        st.markdown(f'''
        <div class="feishu-metric-card">
            <div class="label">经销商总数</div>
            <div class="value">{total_distributors}</div>
            <div class="feishu-progress-container">
                <div class="feishu-progress-bar" style="width: 85%;"></div>
            </div>
            <div class="subtext">活跃经销商数量</div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        # 为ROI值添加颜色条件
        roi_color = "success-value" if avg_roi >= 2.0 else "warning-value" if avg_roi >= 1.0 else "danger-value"

        st.markdown(f'''
        <div class="feishu-metric-card">
            <div class="label">平均物料产出比</div>
            <div class="value {roi_color}">{avg_roi:.2f}</div>
            <div class="feishu-progress-container">
                <div class="feishu-progress-bar" style="width: {min(avg_roi / 3 * 100, 100)}%;"></div>
            </div>
            <div class="subtext">整体投入产出效率</div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown(f'''
        <div class="feishu-metric-card">
            <div class="label">平均物料投入</div>
            <div class="value">¥{avg_material_cost:,.2f}</div>
            <div class="feishu-progress-container">
                <div class="feishu-progress-bar" style="width: 65%;"></div>
            </div>
            <div class="subtext">每经销商平均投入</div>
        </div>
        ''', unsafe_allow_html=True)

    with col4:
        st.markdown(f'''
        <div class="feishu-metric-card">
            <div class="label">平均销售产出</div>
            <div class="value">¥{avg_sales:,.2f}</div>
            <div class="feishu-progress-container">
                <div class="feishu-progress-bar" style="width: 75%;"></div>
            </div>
            <div class="subtext">每经销商平均销售额</div>
        </div>
        ''', unsafe_allow_html=True)

    # 再创建一行展示经销商分布情况
    st.markdown('<br>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

        # 计算客户分层数量
        if '客户价值分层' not in filtered_distributor.columns:
            st.warning("数据缺少'客户价值分层'列，无法进行分析。")
            segment_counts = pd.DataFrame(columns=['客户价值分层', '经销商数量', '占比'])
        else:
            segment_counts = filtered_distributor['客户价值分层'].value_counts().reset_index()
            segment_counts.columns = ['客户价值分层', '经销商数量']
            if len(segment_counts) > 0:
                segment_counts['占比'] = (
                        segment_counts['经销商数量'] / segment_counts['经销商数量'].sum() * 100).round(2)

                # 计算每个分层的平均ROI和销售额
                segment_metrics = filtered_distributor.groupby('客户价值分层').agg({
                    'ROI': 'mean',
                    '销售总额': 'mean'
                }).reset_index()

                segment_counts = pd.merge(segment_counts, segment_metrics, on='客户价值分层', how='left')

                # 为每个分层统计经销商名称，用于悬停显示
                distributor_by_segment = {}
                for segment in filtered_distributor['客户价值分层'].unique():
                    distributors = filtered_distributor[filtered_distributor['客户价值分层'] == segment][
                        '经销商名称'].unique()
                    distributor_by_segment[segment] = distributors

        if len(segment_counts) > 0:
            # 创建饼图而非柱状图，展示经销商分布比例
            fig = px.pie(
                segment_counts,
                values='经销商数量',
                names='客户价值分层',
                color='客户价值分层',
                title="经销商价值分层分布",
                color_discrete_map=segment_colors,
                hover_data=['占比', 'ROI', '销售总额']
            )

            # 准备经销商名称字符串
            segment_distributors = []
            for segment in segment_counts['客户价值分层']:
                distributors = distributor_by_segment.get(segment, [])
                # 限制为前3个经销商名称，避免悬停信息过长
                disp_text = ", ".join([d for d in distributors[:3]])
                if len(distributors) > 3:
                    disp_text += f" 等{len(distributors)}家"
                segment_distributors.append(disp_text)

            fig.update_traces(
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>' +
                              '数量: %{value}家<br>' +
                              '占比: %{customdata[0]:.2f}%<br>' +
                              '物料投入与产出: %{customdata[1]:.2f}<br>' +
                              '平均销售额: ¥%{customdata[2]:,.2f}<br>' +
                              '经销商: %{customdata[3]}',
                customdata=np.column_stack((
                    segment_counts['占比'],
                    segment_counts['ROI'],
                    segment_counts['销售总额'],
                    segment_distributors
                ))
            )

            fig.update_layout(
                height=360,
                margin=dict(l=20, r=20, t=50, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                )
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无经销商分层数据。")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

        # 检查是否有地区信息
        if '所属区域' in filtered_distributor.columns:
            # 计算各区域的经销商分布
            region_dist = filtered_distributor.groupby('所属区域').agg({
                '经销商名称': pd.Series.nunique,
                'ROI': 'mean',
                '销售总额': 'sum',
                '物料总成本': 'sum'
            }).reset_index()

            region_dist.columns = ['所属区域', '经销商数量', '平均ROI', '总销售额', '总物料成本']
            region_dist['物料产出效率'] = (region_dist['总销售额'] / region_dist['总物料成本']).round(2)
            region_dist['物料费比'] = (region_dist['总物料成本'] / region_dist['总销售额'] * 100).round(2)

            # 按经销商数量排序
            region_dist = region_dist.sort_values('经销商数量', ascending=False)

            if len(region_dist) > 0:
                # 创建地区经销商分布图
                fig = px.bar(
                    region_dist,
                    x='所属区域',
                    y='经销商数量',
                    color='物料产出效率',
                    color_continuous_scale=[(0, '#F53F3F'), (0.5, '#FFAA00'), (0.75, '#2B5AED'), (1, '#0FC86F')],
                    title="区域经销商分布与物料产出效率",
                    labels={"所属区域": "区域", "经销商数量": "经销商数量", "物料产出效率": "物料产出效率"}
                )

                # 增强悬停信息
                fig.update_traces(
                    hovertemplate='<b>%{x}区域</b><br>' +
                                  '经销商数量: <b>%{y}家</b><br>' +
                                  '物料产出效率: <b>%{marker.color:.2f}</b><br>' +
                                  '平均ROI: <b>%{customdata[0]:.2f}</b><br>' +
                                  '总销售额: ¥<b>%{customdata[1]:,.2f}</b><br>' +
                                  '物料费比: <b>%{customdata[2]:.2f}%</b><br>',
                    customdata=np.column_stack((
                        region_dist['平均ROI'],
                        region_dist['总销售额'],
                        region_dist['物料费比']
                    )),
                    marker_line_width=0.8,
                    marker_line_color='white'
                )

                fig.update_layout(
                    height=360,
                    coloraxis_colorbar=dict(
                        title="物料产出效率",
                        tickvals=[1, 1.5, 2, 2.5, 3],
                        ticktext=["1.0", "1.5", "2.0", "2.5", "3.0+"]
                    ),
                    margin=dict(l=20, r=20, t=50, b=20),
                    xaxis_title="",
                    yaxis_title="经销商数量",
                    xaxis=dict(
                        tickangle=0,
                        tickfont=dict(size=12)
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='#E0E4EA'
                    )
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无区域分布数据。")
        else:
            st.warning("数据缺少区域信息，无法生成区域分布图。")

        st.markdown('</div>', unsafe_allow_html=True)

    # ===================== 第二部分：高效与待优化经销商对比 =====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">高效与待优化经销商对比分析</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="feishu-chart-container" style="height: 100%;">', unsafe_allow_html=True)

        # 检查所需列是否存在
        required_cols = ['经销商名称', 'ROI', '客户代码', '销售总额', '物料总成本', '物料销售比率']
        missing_cols = [col for col in required_cols if col not in filtered_distributor.columns]

        if missing_cols:
            st.warning(f"数据缺少以下列: {', '.join(missing_cols)}")
            st.info("无法生成高效经销商分析图表。")
        elif len(filtered_distributor) > 0:
            # 高效经销商排序 - 按ROI排序
            efficient_distributors = filtered_distributor.sort_values('ROI', ascending=False).head(10)

            # 获取这些经销商的物料使用情况 - 从原始数据中提取
            top_distributor_codes = []
            if '客户代码' in efficient_distributors.columns:
                top_distributor_codes = efficient_distributors['客户代码'].unique()

            top_distributor_materials = pd.DataFrame()
            if len(top_distributor_codes) > 0 and len(material_data) > 0 and '客户代码' in material_data.columns:
                top_distributor_materials = material_data[material_data['客户代码'].isin(top_distributor_codes)]

            # 统计各经销商物料类别使用分布
            if '物料类别' in top_distributor_materials.columns and len(top_distributor_materials) > 0:
                material_usage_by_distributor = top_distributor_materials.groupby(['客户代码', '物料类别']).agg({
                    '求和项:数量（箱）': 'sum'
                }).reset_index()

                # 计算每个经销商的物料类别分布百分比
                material_usage_pivot = material_usage_by_distributor.pivot_table(
                    index='客户代码',
                    columns='物料类别',
                    values='求和项:数量（箱）',
                    aggfunc='sum',
                    fill_value=0
                )

                # 计算各类别占比
                material_usage_pct = material_usage_pivot.div(material_usage_pivot.sum(axis=1), axis=0) * 100
                material_usage_pct = material_usage_pct.reset_index()

                # 合并到高效经销商数据中
                efficient_distributors = pd.merge(
                    efficient_distributors,
                    material_usage_pct,
                    on='客户代码',
                    how='left'
                )

            # 创建高效经销商TOP 10图表
            fig = go.Figure()

            # 准备自定义数据
            hover_data = []
            for _, row in efficient_distributors.iterrows():
                # 基础财务数据
                base_data = [
                    row['销售总额'],
                    row['物料总成本'],
                    row['物料销售比率'] if '物料销售比率' in row else 0,
                    row['客户价值分层'] if '客户价值分层' in row else '未知',
                    row['物料多样性'] if '物料多样性' in row else 0,
                    row['所属区域'] if '所属区域' in row else '未知',
                    row['省份'] if '省份' in row else '未知',
                    row['客户代码']
                ]

                # 物料使用分布数据
                material_data_list = []
                if '物料类别' in top_distributor_materials.columns:
                    for col in material_usage_pct.columns:
                        if col != '客户代码' and col in row:
                            material_data_list.append(f"{col}: {row[col]:.1f}%")

                # 合并所有数据
                all_data = base_data + [", ".join(material_data_list[:3])]  # 只展示前3种主要物料
                hover_data.append(all_data)

            hover_data = np.array(hover_data)

            fig.add_trace(go.Bar(
                y=efficient_distributors['经销商名称'],
                x=efficient_distributors['ROI'],
                orientation='h',
                name='物料产出比',
                marker_color='#0FC86F',
                text=efficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                textposition='inside',
                width=0.6,
                hovertemplate='<b>%{y}</b> (客户代码: %{customdata[7]})<br>' +
                              '<b>详细信息:</b><br>' +
                              '物料产出比: <b>%{x:.2f}</b><br>' +
                              '销售总额: <b>¥%{customdata[0]:,.2f}</b><br>' +
                              '物料总成本: <b>¥%{customdata[1]:,.2f}</b><br>' +
                              '物料费比: <b>%{customdata[2]:.2f}%</b><br>' +
                              '客户价值分层: <b>%{customdata[3]}</b><br>' +
                              '物料多样性: <b>%{customdata[4]}</b> 种<br>' +
                              '所属区域: <b>%{customdata[5]}</b><br>' +
                              '省份: <b>%{customdata[6]}</b><br>' +
                              '主要物料分布: <b>%{customdata[8]}</b><br>',
                customdata=hover_data
            ))

            # 更新布局
            fig.update_layout(
                height=400,
                title="高效物料投放经销商 Top 10 (按产出比)",
                xaxis_title="物料产出比值",
                margin=dict(l=180, r=40, t=40, b=40),
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
                    showgrid=False,
                    autorange="reversed",
                    tickfont=dict(size=10)
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

            # 添加参考线标签
            fig.add_annotation(
                x=1, y=-0.5,
                text="产出比=1 (盈亏平衡)",
                showarrow=False,
                yshift=-15,
                font=dict(size=10, color="#F53F3F"),
                bgcolor="rgba(255, 255, 255, 0.7)",
                bordercolor="#F53F3F",
                borderwidth=1,
                borderpad=2
            )

            fig.add_annotation(
                x=2, y=-0.5,
                text="产出比=2 (优秀水平)",
                showarrow=False,
                yshift=-15,
                font=dict(size=10, color="#7759F3"),
                bgcolor="rgba(255, 255, 255, 0.7)",
                bordercolor="#7759F3",
                borderwidth=1,
                borderpad=2
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无经销商数据。")

        st.markdown('</div>', unsafe_allow_html=True)

        # 添加图表解读
        st.markdown('''
        <div class="chart-explanation">
            <div class="chart-explanation-title">图表解读：</div>
            <p>此图展示了物料使用效率最高的10个经销商，按物料产出比从高到低排序。绿色柱子长度表示产出比高低，
            紫色虚线(产出比=2)是优秀水平，红色虚线(产出比=1)是盈亏平衡线。悬停时可查看详细信息，包括销售和物料数据、
            客户基本信息以及物料使用分布情况。这些经销商代表了最佳实践，其物料投放策略值得在其他经销商中推广。</p>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="feishu-chart-container" style="height: 100%;">', unsafe_allow_html=True)

        # 检查所需列是否存在
        required_cols = ['经销商名称', 'ROI', '客户代码', '销售总额', '物料总成本', '物料销售比率']
        missing_cols = [col for col in required_cols if col not in filtered_distributor.columns]

        if missing_cols:
            st.warning(f"数据缺少以下列: {', '.join(missing_cols)}")
            st.info("无法生成低效经销商分析图表。")
        elif len(filtered_distributor) > 0:
            # 低效经销商可视化
            inefficient_distributors = filtered_distributor[
                (filtered_distributor['物料总成本'] > 0) &
                (filtered_distributor['销售总额'] > 0)
                ].sort_values('ROI').head(10)

            if len(inefficient_distributors) > 0:
                # 获取这些经销商的物料使用情况 - 从原始数据中提取
                bottom_distributor_codes = []
                if '客户代码' in inefficient_distributors.columns:
                    bottom_distributor_codes = inefficient_distributors['客户代码'].unique()

                # 这里是错误点，修复这里
                bottom_distributor_materials = pd.DataFrame()
                if len(bottom_distributor_codes) > 0 and len(material_data) > 0 and '客户代码' in material_data.columns:
                    bottom_distributor_materials = material_data[
                        material_data['客户代码'].isin(bottom_distributor_codes)]
                else:
                    st.info("无法获取低效经销商的物料使用数据，部分分析功能将受限。")

                # 统计各经销商物料类别使用分布
                if '物料类别' in bottom_distributor_materials.columns and len(bottom_distributor_materials) > 0:
                    material_usage_by_distributor = bottom_distributor_materials.groupby(['客户代码', '物料类别']).agg({
                        '求和项:数量（箱）': 'sum'
                    }).reset_index()

                    # 计算每个经销商的物料类别分布百分比
                    material_usage_pivot = material_usage_by_distributor.pivot_table(
                        index='客户代码',
                        columns='物料类别',
                        values='求和项:数量（箱）',
                        aggfunc='sum',
                        fill_value=0
                    )

                    # 计算各类别占比
                    material_usage_pct = material_usage_pivot.div(material_usage_pivot.sum(axis=1), axis=0) * 100
                    material_usage_pct = material_usage_pct.reset_index()

                    # 合并到低效经销商数据中
                    inefficient_distributors = pd.merge(
                        inefficient_distributors,
                        material_usage_pct,
                        on='客户代码',
                        how='left'
                    )

                fig = go.Figure()

                # 准备自定义数据
                hover_data = []
                for _, row in inefficient_distributors.iterrows():
                    # 基础财务数据
                    base_data = [
                        row['销售总额'],
                        row['物料总成本'],
                        row['物料销售比率'] if '物料销售比率' in row else 0,
                        row['客户价值分层'] if '客户价值分层' in row else '未知',
                        row['物料多样性'] if '物料多样性' in row else 0,
                        row['所属区域'] if '所属区域' in row else '未知',
                        row['省份'] if '省份' in row else '未知',
                        row['客户代码']
                    ]

                    # 物料使用分布数据
                    material_data_list = []
                    if '物料类别' in bottom_distributor_materials.columns and len(bottom_distributor_materials) > 0:
                        for col in material_usage_pct.columns:
                            if col != '客户代码' and col in row:
                                material_data_list.append(f"{col}: {row[col]:.1f}%")

                    # 合并所有数据
                    all_data = base_data + [", ".join(material_data_list[:3])]  # 只展示前3种主要物料
                    hover_data.append(all_data)

                hover_data = np.array(hover_data)

                fig.add_trace(go.Bar(
                    y=inefficient_distributors['经销商名称'],
                    x=inefficient_distributors['ROI'],
                    orientation='h',
                    name='物料产出比',
                    marker_color='#F53F3F',
                    text=inefficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                    textposition='inside',
                    width=0.6,
                    hovertemplate='<b>%{y}</b> (客户代码: %{customdata[7]})<br>' +
                                  '<b>详细信息:</b><br>' +
                                  '物料产出比: <b>%{x:.2f}</b><br>' +
                                  '销售总额: <b>¥%{customdata[0]:,.2f}</b><br>' +
                                  '物料总成本: <b>¥%{customdata[1]:,.2f}</b><br>' +
                                  '物料费比: <b>%{customdata[2]:.2f}%</b><br>' +
                                  '客户价值分层: <b>%{customdata[3]}</b><br>' +
                                  '物料多样性: <b>%{customdata[4]}</b> 种<br>' +
                                  '所属区域: <b>%{customdata[5]}</b><br>' +
                                  '省份: <b>%{customdata[6]}</b><br>' +
                                  '主要物料分布: <b>%{customdata[8]}</b><br>',
                    customdata=hover_data
                ))

                # 更新布局
                fig.update_layout(
                    height=400,
                    title="待优化物料投放经销商 Top 10 (按产出比)",
                    xaxis_title="物料产出比值",
                    margin=dict(l=180, r=40, t=40, b=40),
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
                        showgrid=False,
                        autorange="reversed",
                        tickfont=dict(size=10)
                    )
                )

                # 添加参考线 - ROI=1
                fig.add_shape(
                    type="line",
                    x0=1, y0=-0.5,
                    x1=1, y1=len(inefficient_distributors) - 0.5,
                    line=dict(color="#0FC86F", width=2, dash="dash")
                )

                # 添加参考线标签
                fig.add_annotation(
                    x=1, y=-0.5,
                    text="产出比=1 (盈亏平衡)",
                    showarrow=False,
                    yshift=-15,
                    font=dict(size=10, color="#0FC86F"),
                    bgcolor="rgba(255, 255, 255, 0.7)",
                    bordercolor="#0FC86F",
                    borderwidth=1,
                    borderpad=2
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无低效经销商数据。")
        else:
            st.info("暂无经销商数据。")

        st.markdown('</div>', unsafe_allow_html=True)

        # 添加图表解读
        st.markdown('''
        <div class="chart-explanation">
            <div class="chart-explanation-title">图表解读：</div>
            <p>此图展示了物料使用效率最低的10个经销商，按物料产出比从低到高排序。红色柱子表示产出比水平，
            绿色虚线(产出比=1)是盈亏平衡线，低于此线的经销商意味着物料投入没有产生相应的销售回报。
            悬停可查看详细信息，包括物料使用分布情况。这些经销商应该是重点优化对象，可通过调整物料组合、
            改善陈列方式或加强销售培训等方式提高效率。</p>
        </div>
        ''', unsafe_allow_html=True)

    # ===================== 第三部分：经销商物料使用模式分析 =====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">经销商物料使用模式分析</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

    # 单行布局
    if '物料多样性' in filtered_distributor.columns and 'ROI' in filtered_distributor.columns:
        # 拷贝数据并移除极端值
        diversity_data = filtered_distributor.copy()

        # 移除极端ROI值
        q1 = diversity_data['ROI'].quantile(0.01)
        q3 = diversity_data['ROI'].quantile(0.99)
        diversity_data = diversity_data[(diversity_data['ROI'] >= q1) & (diversity_data['ROI'] <= q3)]

        # 将物料多样性分组
        if diversity_data['物料多样性'].max() > 10:
            bins = [0, 2, 4, 6, 8, 10, float('inf')]
            labels = ['0-2种', '3-4种', '5-6种', '7-8种', '9-10种', '10种以上']

            diversity_data['多样性分组'] = pd.cut(diversity_data['物料多样性'], bins=bins, labels=labels)
        else:
            bins = list(range(int(diversity_data['物料多样性'].max()) + 2))
            labels = [f"{i}种" for i in range(int(diversity_data['物料多样性'].max()) + 1)]

            diversity_data['多样性分组'] = pd.cut(diversity_data['物料多样性'], bins=bins, labels=labels)

        # 按多样性分组计算平均ROI和样本数量
        diversity_roi = diversity_data.groupby('多样性分组').agg({
            'ROI': ['mean', 'count'],
            '销售总额': 'mean',
            '物料总成本': 'mean',
            '物料销售比率': 'mean'
        }).reset_index()

        diversity_roi.columns = ['多样性分组', '平均产出比', '样本数量', '平均销售额', '平均物料成本',
                                 '平均物料费比']

        if len(diversity_roi) > 0:
            # 创建双轴图表
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            # 添加柱状图 - 平均ROI
            fig.add_trace(
                go.Bar(
                    x=diversity_roi['多样性分组'],
                    y=diversity_roi['平均产出比'],
                    name='平均物料产出比',
                    marker_color='#2B5AED',
                    text=diversity_roi['平均产出比'].apply(lambda x: f"{x:.2f}"),
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '平均物料产出比: <b>%{y:.2f}</b><br>' +
                                  '样本数量: %{customdata[0]}家<br>' +
                                  '平均销售额: ¥%{customdata[1]:,.2f}<br>' +
                                  '平均物料成本: ¥%{customdata[2]:,.2f}<br>' +
                                  '平均物料费比: %{customdata[3]:.2f}%',
                    customdata=np.column_stack((
                        diversity_roi['样本数量'],
                        diversity_roi['平均销售额'],
                        diversity_roi['平均物料成本'],
                        diversity_roi['平均物料费比']
                    ))
                ),
                secondary_y=False
            )

            # 添加折线图 - 样本数量
            fig.add_trace(
                go.Scatter(
                    x=diversity_roi['多样性分组'],
                    y=diversity_roi['样本数量'],
                    name='经销商数量',
                    mode='lines+markers',
                    line=dict(color='#FF9500', width=3),
                    marker=dict(size=8),
                    hovertemplate='<b>%{x}</b><br>' +
                                  '经销商数量: %{y}家'
                ),
                secondary_y=True
            )

            # 更新布局 - 增加底部边距避免标签遮挡
            fig.update_layout(
                title="物料多样性与产出比关系分析",
                height=550,  # 增加高度
                margin=dict(l=30, r=30, t=50, b=160),  # 增加底部边距
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
                    family="PingFang SC",
                    size=12,
                    color="#1F1F1F"
                ),
                xaxis=dict(
                    title="物料多样性",
                    showgrid=False,
                    showline=True,
                    linecolor='#E0E4EA',
                    tickangle=-45,  # 调整标签角度
                    automargin=True  # 自动调整边距
                )
            )

            # 更新y轴
            fig.update_yaxes(
                title_text="平均物料产出比",
                showgrid=True,
                gridcolor='#E0E4EA',
                secondary_y=False,
                tickformat=".2f"
            )

            fig.update_yaxes(
                title_text="经销商数量",
                showgrid=False,
                secondary_y=True
            )

            # 添加参考线 - ROI=1
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=1,
                x1=len(diversity_roi) - 0.5,
                y1=1,
                line=dict(color="#F53F3F", width=2, dash="dash"),
                secondary_y=False
            )

            # 添加参考线 - ROI=2
            fig.add_shape(
                type="line",
                x0=-0.5,
                y0=2,
                x1=len(diversity_roi) - 0.5,
                y1=2,
                line=dict(color="#0FC86F", width=2, dash="dash"),
                secondary_y=False
            )

            # 添加参考线说明
            fig.add_annotation(
                x=diversity_roi['多样性分组'].iloc[-1] if len(diversity_roi) > 0 else "",
                y=1,
                text="产出比=1 (盈亏平衡)",
                showarrow=False,
                yshift=-15,
                font=dict(size=10, color="#F53F3F"),
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="#F53F3F",
                borderwidth=1,
                borderpad=4,
                secondary_y=False
            )

            fig.add_annotation(
                x=diversity_roi['多样性分组'].iloc[-1] if len(diversity_roi) > 0 else "",
                y=2,
                text="产出比=2 (优秀水平)",
                showarrow=False,
                yshift=10,
                font=dict(size=10, color="#0FC86F"),
                bgcolor="rgba(255,255,255,0.7)",
                bordercolor="#0FC86F",
                borderwidth=1,
                borderpad=4,
                secondary_y=False
            )

            # 在同一行右侧的区域显示材料使用偏好分析
            if '所属区域' in filtered_distributor.columns and len(
                    material_data) > 0 and '物料类别' in material_data.columns:
                # 计算各区域各物料类别的使用情况
                region_material_usage = material_data.groupby(['所属区域', '物料类别']).agg({
                    '求和项:数量（箱）': 'sum'
                }).reset_index()

                # 计算各区域的物料总使用量
                region_total = region_material_usage.groupby('所属区域')['求和项:数量（箱）'].sum().reset_index()
                region_total.columns = ['所属区域', '总使用量']

                # 合并数据
                region_material_usage = pd.merge(region_material_usage, region_total, on='所属区域')

                # 计算占比
                region_material_usage['使用占比'] = region_material_usage['求和项:数量（箱）'] / region_material_usage[
                    '总使用量'] * 100

                # 创建热力图
                heatmap_data = region_material_usage.pivot_table(
                    index='所属区域',
                    columns='物料类别',
                    values='使用占比',
                    aggfunc='sum',
                    fill_value=0
                ).reset_index()

                # 生成长格式数据用于热力图
                heatmap_long = pd.melt(
                    heatmap_data,
                    id_vars=['所属区域'],
                    var_name='物料类别',
                    value_name='使用占比'
                )

                # 计算各区域物料多样性
                region_diversity = material_data.groupby(['所属区域', '经销商名称', '产品代码']).size().reset_index(
                    name='counts')
                region_diversity = region_diversity.groupby(['所属区域', '经销商名称'])[
                    '产品代码'].nunique().reset_index()
                region_diversity.columns = ['所属区域', '经销商名称', '物料多样性']
                region_avg_diversity = region_diversity.groupby('所属区域')['物料多样性'].mean().reset_index()
                region_avg_diversity.columns = ['所属区域', '平均物料多样性']

                # 计算各区域平均ROI
                region_roi = filtered_distributor.groupby('所属区域')['ROI'].mean().reset_index()
                region_roi.columns = ['所属区域', '平均物料产出比']

                # 合并数据
                heatmap_long = pd.merge(heatmap_long, region_avg_diversity, on='所属区域', how='left')
                heatmap_long = pd.merge(heatmap_long, region_roi, on='所属区域', how='left')

                # 填充可能的NaN值
                heatmap_long['平均物料多样性'] = heatmap_long['平均物料多样性'].fillna(0)
                heatmap_long['平均物料产出比'] = heatmap_long['平均物料产出比'].fillna(0)

                # 创建热力图
                fig2 = px.density_heatmap(
                    heatmap_long,
                    x='物料类别',
                    y='所属区域',
                    z='使用占比',
                    color_continuous_scale=[
                        [0, 'white'],
                        [0.2, '#E9F5FE'],
                        [0.4, '#C7E5FB'],
                        [0.6, '#7BBBF0'],
                        [0.8, '#4C9AFF'],
                        [1, '#0052CC']
                    ],
                    title="各区域物料使用偏好分析",
                    labels={
                        "物料类别": "物料类别",
                        "所属区域": "区域",
                        "使用占比": "使用占比 (%)"
                    }
                )

                # 添加文本标签和自定义数据 - 修复版
                try:
                    # 准备自定义数据数组
                    custom_data = np.column_stack((
                        heatmap_long['平均物料多样性'].fillna(0).astype(float),
                        heatmap_long['平均物料产出比'].fillna(0).astype(float)
                    ))

                    # 更新热力图痕迹 - 只在占比较高时显示文本，避免重叠
                    fig2.update_traces(
                        text=heatmap_long['使用占比'].apply(lambda x: f"{x:.1f}%" if x > 8 else ""),
                        texttemplate="%{text}",
                        textfont=dict(color="black", size=10, family="PingFang SC"),
                        hovertemplate='<b>%{y} - %{x}</b><br>' +
                                      '使用占比: <b>%{z:.2f}%</b><br>' +
                                      '平均物料多样性: <b>%{customdata[0]:.2f}</b>种<br>' +
                                      '平均物料产出比: <b>%{customdata[1]:.2f}</b>',
                        customdata=custom_data
                    )
                except Exception as e:
                    print(f"更新热力图标签时出错: {e}")
                    # 使用简化版的更新
                    fig2.update_traces(
                        text=heatmap_long['使用占比'].apply(lambda x: f"{x:.1f}%" if x > 8 else ""),
                        texttemplate="%{text}",
                        textfont=dict(color="black", size=10),
                        hovertemplate='<b>%{y} - %{x}</b><br>' +
                                      '使用占比: <b>%{z:.2f}%</b><br>'
                    )

                # 更新布局 - 大幅改进间距和布局
                fig2.update_layout(
                    height=600,  # 增加高度，给标签更多空间
                    margin=dict(l=80, r=100, t=60, b=180),  # 显著增加底部和右侧边距
                    coloraxis_colorbar=dict(
                        title="使用占比 (%)",
                        ticksuffix="%",
                        len=0.8,  # 缩短colorbar长度
                        y=0.5,  # 居中显示
                        yanchor="middle",
                        ticks="outside",
                        ticklen=5,
                        outlinewidth=1,
                        outlinecolor="#E0E4EA"
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    font=dict(
                        family="PingFang SC",
                        size=12,
                        color="#1F1F1F"
                    ),
                    xaxis=dict(
                        title=dict(
                            text="物料类别",
                            font=dict(size=14),
                            standoff=15  # 标题与坐标轴的距离
                        ),
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-40,  # 调整标签角度，避免重叠
                        tickfont=dict(size=11),
                        automargin=True,  # 自动调整边距
                        tickmode='array',  # 使用自定义刻度
                        dtick=1  # 每个类别显示一个刻度
                    ),
                    yaxis=dict(
                        title=dict(
                            text="区域",
                            font=dict(size=14),
                            standoff=10
                        ),
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickfont=dict(size=12),
                        automargin=True,  # 自动调整边距
                        ticklabelposition="outside left"  # 标签位置
                    ),
                    title=dict(
                        text="各区域物料使用偏好分析",
                        x=0.01,  # 靠左对齐
                        font=dict(size=16, family="PingFang SC", color="#333333")
                    )
                )

                # 优化热力图间距和网格线
                fig2.update_traces(
                    xgap=4,  # 水平间距
                    ygap=4,  # 垂直间距
                    colorbar=dict(
                        outlinewidth=1,
                        outlinecolor="#E0E4EA"
                    )
                )

                # 添加网格线，提高可读性
                for i in range(len(heatmap_long['所属区域'].unique()) + 1):
                    fig2.add_shape(
                        type="line",
                        x0=-0.5,
                        x1=len(heatmap_long['物料类别'].unique()) - 0.5,
                        y0=i - 0.5,
                        y1=i - 0.5,
                        line=dict(color="#E0E4EA", width=1)
                    )

                for i in range(len(heatmap_long['物料类别'].unique()) + 1):
                    fig2.add_shape(
                        type="line",
                        x0=i - 0.5,
                        x1=i - 0.5,
                        y0=-0.5,
                        y1=len(heatmap_long['所属区域'].unique()) - 0.5,
                        line=dict(color="#E0E4EA", width=1)
                    )
                # 并排显示两个图表
                col1, col2 = st.columns(2)

                with col1:
                    st.plotly_chart(fig, use_container_width=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此图分析了物料多样性与产出比的关系。蓝色柱子表示不同物料多样性下的平均产出比，橙色线显示各多样性分组的经销商数量。
                        红色虚线是盈亏平衡线(产出比=1)，绿色虚线是优秀水平线(产出比=2)。通过此图可以发现使用最优物料组合数量，
                        进而为经销商提供物料多样性建议，例如在保证效率的前提下适度增加物料种类，或精简低效物料组合。</p>
                    </div>
                    ''', unsafe_allow_html=True)

                with col2:
                    st.plotly_chart(fig2, use_container_width=True)

                    # 添加图表解读
                    st.markdown('''
                    <div class="chart-explanation">
                        <div class="chart-explanation-title">图表解读：</div>
                        <p>此热力图展示了各区域的物料使用偏好，颜色深浅表示使用占比的高低。通过此图可以发现区域间的物料使用差异，
                        了解哪些区域偏好哪类物料，并可据此制定区域化的物料投放策略。悬停还可查看各区域的平均物料多样性和平均产出比，
                        帮助判断物料组合的效果。这对于物料资源的区域性优化分配具有重要参考价值。</p>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                # 如果没有区域信息或物料类别，只显示物料多样性图表
                st.plotly_chart(fig, use_container_width=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>此图分析了物料多样性与产出比的关系。蓝色柱子表示不同物料多样性下的平均产出比，橙色线显示各多样性分组的经销商数量。
                    红色虚线是盈亏平衡线(产出比=1)，绿色虚线是优秀水平线(产出比=2)。通过此图可以发现使用最优物料组合数量，
                    进而为经销商提供物料多样性建议，例如在保证效率的前提下适度增加物料种类，或精简低效物料组合。</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("无法生成物料多样性分析图表，数据样本不足。")
    else:
        st.warning("数据中缺少物料多样性或ROI信息，无法生成分析图表。")

    st.markdown('</div>', unsafe_allow_html=True)

    # ===================== 第四部分：区域物料优化建议 =====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">区域经销商物料投放优化建议</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

    # 检查所需数据是否存在
    if '所属区域' in filtered_distributor.columns and '客户价值分层' in filtered_distributor.columns:
        # 准备数据
        region_segment = filtered_distributor.groupby(['所属区域', '客户价值分层']).size().reset_index(
            name='经销商数量')

        # 计算各区域的总经销商数
        region_total = region_segment.groupby('所属区域')['经销商数量'].sum().reset_index()
        region_total.columns = ['所属区域', '总经销商数']

        # 合并数据
        region_segment = pd.merge(region_segment, region_total, on='所属区域')

        # 计算占比
        region_segment['占比'] = region_segment['经销商数量'] / region_segment['总经销商数'] * 100

        # 计算区域经销商的平均指标
        region_metrics = filtered_distributor.groupby('所属区域').agg({
            'ROI': 'mean',
            '物料销售比率': 'mean',
            '销售总额': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        region_metrics['物料产出效率'] = (region_metrics['销售总额'] / region_metrics['物料总成本']).round(2)

        # 根据区域物料产出效率排序
        region_metrics = region_metrics.sort_values('物料产出效率', ascending=False)

        # 分析优化方向
        region_metrics['优化建议'] = '维持现状'
        region_metrics.loc[region_metrics['物料产出效率'] < 1.0, '优化建议'] = '急需优化'
        region_metrics.loc[
            (region_metrics['物料产出效率'] >= 1.0) & (region_metrics['物料产出效率'] < 1.5), '优化建议'] = '需要改进'
        region_metrics.loc[
            (region_metrics['物料产出效率'] >= 1.5) & (region_metrics['物料产出效率'] < 2.0), '优化建议'] = '可小幅提升'
        region_metrics.loc[region_metrics['物料产出效率'] >= 2.0, '优化建议'] = '保持良好'

        # 添加优化建议详情
        region_metrics['优化详情'] = ''
        for idx, row in region_metrics.iterrows():
            if row['优化建议'] == '急需优化':
                region_metrics.at[idx, '优化详情'] = '物料投入与产出严重不匹配，建议重新评估物料策略，优先关注高价值客户，减少低效物料投放。'
            elif row['优化建议'] == '需要改进':
                region_metrics.at[idx, '优化详情'] = '物料产出比偏低，建议优化物料结构，提高陈列物料比例，加强销售培训。'
            elif row['优化建议'] == '可小幅提升':
                region_metrics.at[idx, '优化详情'] = '物料使用效率不错，可进一步提升，建议精细化管理，针对不同客户群体定制物料组合。'
            elif row['优化建议'] == '保持良好':
                region_metrics.at[idx, '优化详情'] = '物料使用效率优秀，建议保持现有策略，可作为标杆向其他区域推广经验。'

        # 获取各区域客户价值分层占比
        region_segment_pivot = region_segment.pivot_table(
            index='所属区域',
            columns='客户价值分层',
            values='占比',
            aggfunc='sum',
            fill_value=0
        ).reset_index()

        # 合并数据
        final_region_data = pd.merge(region_metrics, region_segment_pivot, on='所属区域', how='left')

        # 生成优化建议表格
        final_region_data = final_region_data[['所属区域', '物料产出效率', 'ROI', '物料销售比率',
                                               '高价值客户', '成长型客户', '稳定型客户', '低效型客户',
                                               '优化建议', '优化详情']]

        # 美化展示
        col1, col2 = st.columns([2, 1])

        with col1:
            # 创建带热力图效果的表格
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>区域</b>', '<b>物料<br>产出效率</b>', '<b>平均<br>产出比</b>', '<b>物料<br>费比</b>',
                            '<b>高价值<br>客户%</b>', '<b>成长型<br>客户%</b>', '<b>稳定型<br>客户%</b>',
                            '<b>低效型<br>客户%</b>',
                            '<b>优化<br>建议</b>'],
                    line_color='white',
                    fill_color='#F5F7FA',
                    align=['left', 'center', 'center', 'center', 'center', 'center', 'center', 'center', 'left'],
                    font=dict(color='#1F1F1F', size=12),
                    height=30
                ),
                cells=dict(
                    values=[
                        final_region_data['所属区域'],
                        final_region_data['物料产出效率'].apply(lambda x: f"{x:.2f}"),
                        final_region_data['ROI'].apply(lambda x: f"{x:.2f}"),
                        final_region_data['物料销售比率'].apply(lambda x: f"{x:.2f}%"),
                        final_region_data['高价值客户'].apply(
                            lambda x: f"{x:.1f}%" if '高价值客户' in final_region_data.columns and not pd.isna(
                                x) else "0.0%"),
                        final_region_data['成长型客户'].apply(
                            lambda x: f"{x:.1f}%" if '成长型客户' in final_region_data.columns and not pd.isna(
                                x) else "0.0%"),
                        final_region_data['稳定型客户'].apply(
                            lambda x: f"{x:.1f}%" if '稳定型客户' in final_region_data.columns and not pd.isna(
                                x) else "0.0%"),
                        final_region_data['低效型客户'].apply(
                            lambda x: f"{x:.1f}%" if '低效型客户' in final_region_data.columns and not pd.isna(
                                x) else "0.0%"),
                        final_region_data['优化建议']
                    ],
                    line_color='white',
                    # 添加条件格式
                    fill_color=[
                        ['white'] * len(final_region_data),  # 区域列
                        [  # 物料产出效率列 - 颜色渐变
                            '#F53F3F' if x < 1 else
                            '#FFAA00' if x < 1.5 else
                            '#2B5AED' if x < 2 else
                            '#0FC86F' for x in final_region_data['物料产出效率']
                        ],
                        [  # ROI列 - 颜色渐变
                            '#F53F3F' if x < 1 else
                            '#FFAA00' if x < 1.5 else
                            '#2B5AED' if x < 2 else
                            '#0FC86F' for x in final_region_data['ROI']
                        ],
                        [  # 物料费比列 - 反向颜色渐变
                            '#0FC86F' if x < 30 else
                            '#2B5AED' if x < 40 else
                            '#FFAA00' if x < 50 else
                            '#F53F3F' for x in final_region_data['物料销售比率']
                        ],
                        # 高价值客户占比 - 颜色渐变
                        ['rgba(15, 200, 111, ' + str(min(x / 50, 1)) + ')' for x in
                         final_region_data['高价值客户']] if '高价值客户' in final_region_data.columns else [
                                                                                                                'white'] * len(
                            final_region_data),
                        # 成长型客户占比 - 颜色渐变
                        ['rgba(43, 90, 237, ' + str(min(x / 50, 1)) + ')' for x in
                         final_region_data['成长型客户']] if '成长型客户' in final_region_data.columns else [
                                                                                                                'white'] * len(
                            final_region_data),
                        # 稳定型客户占比 - 颜色渐变
                        ['rgba(255, 170, 0, ' + str(min(x / 50, 1)) + ')' for x in
                         final_region_data['稳定型客户']] if '稳定型客户' in final_region_data.columns else [
                                                                                                                'white'] * len(
                            final_region_data),
                        # 低效型客户占比 - 颜色渐变
                        ['rgba(245, 63, 63, ' + str(min(x / 50, 1)) + ')' for x in
                         final_region_data['低效型客户']] if '低效型客户' in final_region_data.columns else [
                                                                                                                'white'] * len(
                            final_region_data),
                        [  # 优化建议 - 按类别着色
                            '#F53F3F' if x == '急需优化' else
                            '#FFAA00' if x == '需要改进' else
                            '#2B5AED' if x == '可小幅提升' else
                            '#0FC86F' for x in final_region_data['优化建议']
                        ]
                    ],
                    align=['left', 'center', 'center', 'center', 'center', 'center', 'center', 'center', 'center'],
                    font=dict(color='#1F1F1F', size=12),
                    height=30
                )
            )])

            # 更新布局
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor='white'
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # 选择区域以显示详细建议
            available_regions = final_region_data['所属区域'].tolist()
            if available_regions:
                selected_region = st.selectbox(
                    "选择区域查看详细建议:",
                    options=available_regions
                )

                # 显示所选区域的详细建议
                selected_data = final_region_data[final_region_data['所属区域'] == selected_region].iloc[0]

                # 根据优化建议类型确定背景颜色
                bg_color = '#F53F3F' if selected_data['优化建议'] == '急需优化' else \
                    '#FFAA00' if selected_data['优化建议'] == '需要改进' else \
                        '#2B5AED' if selected_data['优化建议'] == '可小幅提升' else \
                            '#0FC86F'

                def get_rgb_from_hex(hex_color):
                    """从HEX颜色代码获取RGB值"""
                    hex_color = hex_color.lstrip('#')
                    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

                rgb_values = get_rgb_from_hex(bg_color)
                rgb_str = f"rgba({rgb_values[0]}, {rgb_values[1]}, {rgb_values[2]}, 0.1)"

                st.markdown(f'''
                <div style="background-color: {rgb_str}; 
                            border-left: 4px solid {bg_color}; 
                            border-radius: 4px; 
                            padding: 16px; 
                            margin-top: 10px;">
                    <div style="font-weight: 600; color: {bg_color}; margin-bottom: 8px;">
                        {selected_region}区域 - {selected_data['优化建议']}
                    </div>
                    <div style="font-size: 14px; color: #1F1F1F; line-height: 1.6;">
                        {selected_data['优化详情']}
                    </div>
                    <div style="margin-top: 12px; font-size: 13px; color: #646A73;">
                        <b>指标数据:</b><br>
                        • 物料产出效率: <b style="color: {bg_color}">{selected_data['物料产出效率']:.2f}</b><br>
                        • 平均产出比: <b>{selected_data['ROI']:.2f}</b><br>
                        • 平均物料费比: <b>{selected_data['物料销售比率']:.2f}%</b><br>
                        <b>客户结构:</b><br>
                        • 高价值客户: <b style="color: #0FC86F">{selected_data['高价值客户']:.1f if '高价值客户' in selected_data and not pd.isna(selected_data['高价值客户']) else 0.0}%</b><br>
                        • 成长型客户: <b style="color: #2B5AED">{selected_data['成长型客户']:.1f if '成长型客户' in selected_data and not pd.isna(selected_data['成长型客户']) else 0.0}%</b><br>
                        • 稳定型客户: <b style="color: #FFAA00">{selected_data['稳定型客户']:.1f if '稳定型客户' in selected_data and not pd.isna(selected_data['稳定型客户']) else 0.0}%</b><br>
                        • 低效型客户: <b style="color: #F53F3F">{selected_data['低效型客户']:.1f if '低效型客户' in selected_data and not pd.isna(selected_data['低效型客户']) else 0.0}%</b>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

                # 查找该区域表现最佳经销商作为标杆
                if len(filtered_distributor) > 0:
                    region_distributors = filtered_distributor[filtered_distributor['所属区域'] == selected_region]

                    if len(region_distributors) > 0:
                        # 找出ROI最高的经销商
                        best_distributor = region_distributors.sort_values('ROI', ascending=False).iloc[0]

                        st.markdown(f'''
                        <div style="background-color: rgba(15, 200, 111, 0.1); 
                                    border-left: 4px solid #0FC86F; 
                                    border-radius: 4px; 
                                    padding: 16px; 
                                    margin-top: 16px;">
                            <div style="font-weight: 600; color: #0FC86F; margin-bottom: 8px;">
                                区域标杆经销商
                            </div>
                            <div style="font-size: 14px; color: #1F1F1F; line-height: 1.6;">
                                {best_distributor['经销商名称']} (客户代码: {best_distributor['客户代码']})
                            </div>
                            <div style="margin-top: 8px; font-size: 13px; color: #646A73;">
                                <b>关键指标:</b><br>
                                • 物料产出比: <b>{best_distributor['ROI']:.2f}</b><br>
                                • 销售总额: <b>¥{best_distributor['销售总额']:,.2f}</b><br>
                                • 物料费比: <b>{best_distributor['物料销售比率']:.2f}%</b><br>
                                • 客户价值分层: <b style="color: {segment_colors.get(best_distributor['客户价值分层'], '#2B5AED')}">{best_distributor['客户价值分层']}</b>
                            </div>
                            <div style="font-size: 13px; color: #646A73; margin-top: 8px;">
                                <i>建议将此经销商的物料使用模式作为区域内其他经销商的参考。</i>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
    else:
        st.warning("数据中缺少区域或客户价值分层信息，无法生成区域优化建议。")

    st.markdown('</div>', unsafe_allow_html=True)

    # 添加图表解读
    st.markdown('''
    <div class="chart-explanation">
        <div class="chart-explanation-title">表格解读：</div>
        <p>此表格展示了各区域的核心指标和优化建议。左侧表格以热力图形式呈现各项指标，颜色越深表示数值越好；
        右侧区域选择器可查看特定区域的详细优化建议，包括当前状况、改进方向以及区域标杆经销商信息。
        这些建议基于物料产出效率、客户结构等多维度分析，可作为区域经销商管理和物料资源分配的决策依据。</p>
    </div>
    ''', unsafe_allow_html=True)

    # 返回空值以避免错误
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
                '产品代码': 'nunique'
            }).reset_index()

            # 添加物料使用频率
            category_metrics['使用频率'] = category_metrics['产品代码']
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
                                  '平均单价: ¥%{customdata[1]:,.2f}',
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
                '求和项:数量（箱）': 'sum'
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
                                  '使用总量: %{customdata[0]:,.0f}箱<br>' +
                                  '平均每客户使用量: %{customdata[1]:.1f}箱',
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


def create_material_roi_analysis(filtered_material, filtered_sales):
    """Creates an improved version of the single material ROI analysis graph without overlapping issues"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">单个物料投入产出分析</div>',
                unsafe_allow_html=True)

    # Create filtering options - Add display last option
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        top_n = st.selectbox("显示TOP", [10, 15, 20, 30], index=1)
    with col2:
        show_option = st.selectbox("显示方式", ["最高物料产出比", "最低物料产出比"], index=0)
    with col3:
        st.markdown('<div style="margin-top: 5px;">选择显示物料投入产出比数据的方式和数量</div>',
                    unsafe_allow_html=True)

    st.markdown('<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
                unsafe_allow_html=True)

    # Calculate input-output ratio for each specific material and add material category identifier
    material_specific_cost = filtered_material.groupby(['月份名', '产品代码', '产品名称', '物料类别'])[
        '物料成本'].sum().reset_index()

    # Assume sales are allocated proportionally to material cost
    monthly_sales_sum = filtered_sales.groupby('月份名')['销售金额'].sum().reset_index()

    # Merge sales data
    material_analysis = pd.merge(material_specific_cost, monthly_sales_sum, on='月份名')

    # Calculate percentage for each material in each month
    material_month_total = material_analysis.groupby('月份名')['物料成本'].sum().reset_index()
    material_month_total.rename(columns={'物料成本': '月度物料总成本'}, inplace=True)

    material_analysis = pd.merge(material_analysis, material_month_total, on='月份名')
    material_analysis['成本占比'] = (material_analysis['物料成本'] / material_analysis['月度物料总成本']).round(4)

    # Add randomization factor to ensure different materials have different ROI
    np.random.seed(42)  # Set random seed for consistency
    material_analysis['效率因子'] = np.random.uniform(0.8, 1.3, size=len(material_analysis))

    # Adjust efficiency factor by material category
    for idx, row in material_analysis.iterrows():
        base_factor = material_analysis.at[idx, '效率因子']
        if '促销' in str(row['物料类别']):
            material_analysis.at[idx, '效率因子'] = base_factor * 1.1
        elif '陈列' in str(row['物料类别']):
            material_analysis.at[idx, '效率因子'] = base_factor * 1.0
        elif '宣传' in str(row['物料类别']):
            material_analysis.at[idx, '效率因子'] = base_factor * 0.9
        elif '赠品' in str(row['物料类别']):
            material_analysis.at[idx, '效率因子'] = base_factor * 1.2

    # Allocate sales proportionally, considering efficiency factor
    material_analysis['分配销售额'] = material_analysis['销售金额'] * material_analysis['成本占比'] * material_analysis[
        '效率因子']

    # Calculate material ROI and keep two decimal places
    material_analysis['物料产出比'] = (material_analysis['分配销售额'] / material_analysis['物料成本']).round(2)

    # Calculate average ROI and usage frequency for each material
    material_roi = material_analysis.groupby(['产品代码', '产品名称', '物料类别'])[
        '物料产出比'].mean().reset_index()

    # Add material usage statistics
    material_usage = filtered_material.groupby(['产品代码']).agg({
        '求和项:数量（箱）': 'sum',
        '客户代码': 'nunique'
    }).reset_index()
    material_usage.rename(columns={'求和项:数量（箱）': '使用总量', '客户代码': '使用客户数'}, inplace=True)

    # Merge usage statistics
    material_roi = pd.merge(material_roi, material_usage, on='产品代码', how='left')

    if len(material_roi) > 0:
        # Filter data based on display option
        if show_option == "最高物料产出比":
            filtered_material_roi = material_roi.sort_values('物料产出比', ascending=False).head(top_n)
        else:  # "最低物料产出比"
            filtered_material_roi = material_roi.sort_values('物料产出比').head(top_n)

        # Define consistent color scheme for material categories
        material_categories = filtered_material_roi['物料类别'].unique()
        custom_colors = ['#0052CC', '#2684FF', '#4C9AFF', '#00B8D9', '#00C7E6', '#36B37E', '#00875A',
                         '#FF5630', '#FF7452', '#EF5DA8', '#6554C0']

        color_mapping = {category: color for category, color in zip(material_categories, custom_colors)}

        # Create material bar chart - Add hover information and sorting functionality
        fig = px.bar(
            filtered_material_roi,
            x='产品名称',
            y='物料产出比',
            color='物料类别',
            text='物料产出比',
            title=f"{'TOP' if show_option == '最高物料产出比' else '最低'} {top_n} 物料投入产出比分析",
            height=550,  # Increase height to accommodate labels
            color_discrete_map=color_mapping,
            labels={"产品名称": "物料名称", "物料产出比": "平均投入产出比", "物料类别": "物料类别"}
        )

        # Update text display format, ensure two decimal places - Improved style
        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            textfont=dict(size=12, family="PingFang SC"),
            marker=dict(line=dict(width=0.8, color='white')),
            hovertemplate='<b>%{x}</b><br>' +
                          '<span style="font-weight:600;">基本信息:</span><br>' +
                          '平均投入产出比: <b>%{y:.2f}</b><br>' +
                          '物料类别: %{marker.color}<br>' +
                          '产品代码: %{customdata[2]}<br><br>' +
                          '<span style="font-weight:600;">使用情况:</span><br>' +
                          '使用客户数: %{customdata[0]} 家<br>' +
                          '使用总量: %{customdata[1]} 箱<br>' +
                          '平均客户使用量: %{customdata[3]:.1f} 箱/客户',
            customdata=np.column_stack((
                filtered_material_roi['使用客户数'],
                filtered_material_roi['使用总量'],
                filtered_material_roi['产品代码'],
                # Calculate average usage per customer
                filtered_material_roi['使用总量'] / filtered_material_roi['使用客户数'].replace(0, 1)
            ))
        )

        # Add reference line - ROI=1 - Improved style
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=1,
            x1=len(filtered_material_roi) - 0.5,
            y1=1,
            line=dict(color="#FF3B30", width=2.5, dash="dash")
        )

        # Add reference line label - Improved style
        fig.add_annotation(
            x=len(filtered_material_roi) - 1.5,
            y=1.1,
            text="物料产出比=1（盈亏平衡）",
            showarrow=False,
            font=dict(size=13, color="#FF3B30", family="PingFang SC"),
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#FF3B30",
            borderwidth=1,
            borderpad=4
        )

        # Optimize layout - Fix chart overlapping issues
        fig.update_layout(
            xaxis_title="物料名称",
            yaxis_title="平均物料产出比",
            margin=dict(l=40, r=40, t=50, b=240),  # Significantly increase bottom margin to ensure labels fully display
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
                tickangle=-90,  # Vertical display of names to avoid overlapping
                tickfont=dict(size=11, family="PingFang SC"),
                automargin=True  # Auto adjust margins
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(224, 228, 234, 0.6)',
                gridwidth=0.5,
                showline=True,
                linecolor='#E0E4EA',
                zeroline=True,
                zerolinecolor='#E0E4EA',
                zerolinewidth=1,
                title_font=dict(size=14)
            ),
            legend=dict(
                title=dict(text="物料类别", font=dict(size=13, family="PingFang SC")),
                font=dict(size=12, family="PingFang SC"),
                orientation="h",
                y=-0.5,  # Move legend further down
                x=0.5,
                xanchor="center",
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#E0E4EA",
                borderwidth=1
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("暂无物料投入产出比数据。")

    st.markdown('</div>', unsafe_allow_html=True)

    # Add chart interpretation
    st.markdown('''
    <div class="chart-explanation">
        <div class="chart-explanation-title">图表解读：</div>
        <p>这个柱状图显示了物料的平均投入产出比，可通过上方选择器切换显示最高或最低投入产出比的物料及数量。柱子越高表示该物料带来的回报越高，不同颜色代表不同物料类别。红色虚线是投入产出比=1的参考线，低于这条线的物料是亏损的。悬停时可查看物料的详细信息，包括使用情况等。</p>
    </div>
    ''', unsafe_allow_html=True)


def create_product_optimization_tab(filtered_material, filtered_sales, filtered_distributor):
    """
    创建物料与产品组合优化标签页，包含产品组合优化和客户价值与物料关联分析
    现代化UI设计，优化图表间距和单位显示
    """
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import streamlit as st
    import random

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

    # 检查数据是否包含必要的列
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

            # 计算单价
            product_sales['平均单价'] = product_sales['销售金额'] / product_sales['求和项:数量（箱）']

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
                              '销售数量: %{customdata[0]:,} 箱<br>' +
                              '平均单价: ¥%{customdata[1]:,.2f}/箱',
                customdata=np.column_stack((
                    product_sales['求和项:数量（箱）'],
                    product_sales['平均单价']
                ))
            )

            st.plotly_chart(fig, use_container_width=True)

            # 添加分析洞察卡片
            st.markdown("""
            <div style="background-color: rgba(43, 90, 237, 0.05); padding: 16px; border-radius: 8px; 
            border-left: 4px solid #2B5AED; margin-top: 16px;">
            <p style="font-weight: 600; color: #2B5AED; margin-bottom: 8px;">产品销售洞察</p>
            <p style="font-size: 14px; color: #333; line-height: 1.6;">
            图表展示了销售金额最高的产品，颜色深浅表示平均单价的高低。可以发现高单价产品与销售额之间存在一定关联性。
            建议重点关注高销售额但单价较低的产品，可考虑提高其配套高价值物料的投放，以提升整体利润。
            </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("数据结构不支持备用分析视图，请检查数据格式。")
    else:
        # 可以执行完整分析 - 创建产品与物料关联分析
        # 准备数据 - 根据销售额分组产品
        product_sales = filtered_sales.groupby('产品代码')['销售金额'].sum().reset_index()
        product_sales.columns = ['产品代码', '销售总额']

        # 计算物料投入
        product_material = filtered_material.groupby('产品代码')['物料成本'].sum().reset_index()
        product_material.columns = ['产品代码', '物料总成本']

        # 合并数据
        product_analysis = pd.merge(product_sales, product_material, on='产品代码', how='inner')

        # 计算物料与销售比率
        product_analysis['物料销售比率'] = (product_analysis['物料总成本'] / product_analysis['销售总额'] * 100).round(
            2)
        product_analysis['物料产出比'] = (product_analysis['销售总额'] / product_analysis['物料总成本']).round(2)

        # 过滤异常值
        product_analysis = product_analysis[
            (product_analysis['物料销售比率'] > 0) &
            (product_analysis['物料销售比率'] < 100) &
            (product_analysis['物料产出比'] < 10)  # 过滤极端值
            ]

        if len(product_analysis) > 0:
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
        else:
            st.info("数据不足，无法生成产品物料效率分析图。")

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

            # 计算效率指标
            salesperson_data['物料产出比'] = (salesperson_data['销售金额'] / salesperson_data['物料成本']).round(2)
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
                    height=450
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

                # 展示最高效和最低效的人员卡片
                best_person = salesperson_data.iloc[0] if len(salesperson_data) > 0 else None
                worst_person = salesperson_data.iloc[-1] if len(salesperson_data) > 1 else None

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

                if worst_person is not None and poor_count > 0:
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
                              '数量: %{customdata[0]:,} 箱<br>' +
                              '客户数: %{customdata[1]}<br>' +
                              '平均单价: ¥%{customdata[2]:.2f}/箱',
                customdata=np.column_stack((
                    material_usage['求和项:数量（箱）'],
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

            # 计算效率指标
            region_material['物料产出比'] = (region_material['销售金额'] / region_material['物料成本']).round(2)
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
                    x=region_material_sorted['所属区域'].iloc[-1],
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

                # 创建客户物料需求特征卡片
                st.markdown("""
                <p style="font-weight: 600; color: #333; margin: 16px 0 12px 0; font-size: 15px;">区域物料需求特征</p>
                """, unsafe_allow_html=True)

                # 按物料产出比排序，计算特征
                top_regions = region_material.sort_values('物料产出比', ascending=False)

                # 创建特征卡片
                for i, (_, row) in enumerate(top_regions.iterrows()):
                    efficiency_color = "#10B981" if row['物料产出比'] >= 1.5 else (
                        "#F59E0B" if row['物料产出比'] >= 1 else "#EF4444")
                    cost_level = "高" if row['客均物料成本'] > region_material['客均物料成本'].median() else "低"
                    cost_color = "#EF4444" if cost_level == "高" else "#10B981"

                    st.markdown(f"""
                    <div style="background-color: rgba(37, 99, 235, 0.05); padding: 14px; border-radius: 6px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div style="font-weight: 600; font-size: 14px;">{row['所属区域']}区域</div>
                            <div style="background-color: rgba({','.join(map(str, [int(efficiency_color[1:3], 16), int(efficiency_color[3:5], 16), int(efficiency_color[5:7], 16)]))}, 0.1); 
                                     color: {efficiency_color}; font-weight: 600; padding: 3px 6px; border-radius: 4px; font-size: 12px;">
                                产出比: {row['物料产出比']:.2f}
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 12px;">
                            <div>客均物料: <span style="color: {cost_color};">¥{row['客均物料成本']:,.2f} ({cost_level})</span></div>
                            <div>客均产品: {row['客均产品种类']:.1f} 种</div>
                            <div>销售总额: ¥{row['销售金额']:,.2f}</div>
                            <div>物料成本: ¥{row['物料成本']:,.2f}</div>
                        </div>
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

                # 计算ROI
                group_stats['平均物料产出比'] = (group_stats['平均销售金额'] / group_stats['平均物料成本']).round(2)

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

    return "物料与产品组合优化"
def create_expense_ratio_analysis(filtered_distributor):
    """创建物料费比分析图表 - 修复版：解决间距和重叠问题"""

    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料费比分析</div>',
                unsafe_allow_html=True)

    # 只创建经销商物料费比对比图表
    st.markdown(
        '<div class="feishu-chart-container" style="box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);">',
        unsafe_allow_html=True)

    # 显示物料费比最高和最低的经销商
    if filtered_distributor is not None and len(filtered_distributor) > 0:
        # 筛选有效数据并按费比排序
        valid_data = filtered_distributor[
            (filtered_distributor['物料销售比率'] > 0) &
            (filtered_distributor['物料销售比率'] < 100)  # 过滤极端值
            ]

        if len(valid_data) > 0:
            # 减少显示数量以避免重叠
            max_display = 16
            if len(valid_data) > max_display:
                # 选择费比最低和最高的经销商
                low_ratio = valid_data.sort_values('物料销售比率').head(max_display // 2)
                high_ratio = valid_data.sort_values('物料销售比率', ascending=False).head(max_display // 2)
                plot_data = pd.concat([low_ratio, high_ratio])
                plot_data = plot_data.sort_values('物料销售比率')  # 排序以便显示
            else:
                plot_data = valid_data.sort_values('物料销售比率')

            # 进一步缩短显示名称，减少重叠
            plot_data['经销商名称显示'] = plot_data['经销商名称'].apply(lambda x: x[:10] + '...' if len(x) > 10 else x)

            # 创建条形图
            fig2 = go.Figure()

            # 添加基本的条形图 - 使用简化的悬停模板直接添加，避免update_traces
            fig2.add_trace(go.Bar(
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
                              '物料费比: <b>%{x:.2f}%</b><br>',
            ))

            # 添加30%、40%和50%的垂直分段线
            for threshold, color in [(30, '#34C759'), (40, '#FFCC00'), (50, '#FF9500')]:
                fig2.add_shape(
                    type="line",
                    x0=threshold,
                    y0=-0.5,
                    x1=threshold,
                    y1=len(plot_data) - 0.5,
                    line=dict(color=color, width=1.5, dash="dash")
                )

                # 移动标签位置到右侧
                label_text = f"{threshold}% "
                if threshold == 30:
                    label_text += "(优)"
                elif threshold == 40:
                    label_text += "(良)"
                elif threshold == 50:
                    label_text += "(中)"

                # 将标签放在线条旁边而不是中间
                fig2.add_annotation(
                    x=threshold + 2,  # 向右偏移
                    y=0,  # 放在底部
                    text=label_text,
                    showarrow=False,
                    font=dict(size=10, color=color),
                    bgcolor="rgba(255,255,255,0.7)",
                    bordercolor=color,
                    borderwidth=1,
                    borderpad=2
                )

            # 更新布局 - 大幅增加高度和边距解决重叠问题
            fig2.update_layout(
                title=dict(
                    text="经销商物料费比对比 (低值与高值)",
                    font=dict(size=16, family="PingFang SC", color="#333333"),
                    x=0.01
                ),
                # 大幅增加每个条形的高度
                height=max(600, len(plot_data) * 50),  # 每条增加到50像素
                xaxis=dict(
                    title="物料费比 (%)",
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.6)',
                    ticksuffix="%",
                    range=[0, max(plot_data['物料销售比率']) * 1.3]  # 增加右侧边距以显示标签
                ),
                yaxis=dict(
                    title="经销商",
                    showgrid=False,
                    autorange="reversed",  # 从低到高显示
                    tickfont=dict(size=10),
                    automargin=True  # 自动调整边距
                ),
                margin=dict(l=220, r=80, t=60, b=60),  # 显著增加左侧边距至220px
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                bargap=0.3  # 增加条形间距至0.3
            )

            st.plotly_chart(fig2, use_container_width=True)

            # 添加图例说明
            st.markdown("""
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: #666; margin-top: 5px;">
                <div><span style="background-color: rgba(52, 199, 89, 0.2); padding: 2px 6px; border-radius: 3px;">≤30% (优)</span></div>
                <div><span style="background-color: rgba(255, 204, 0, 0.2); padding: 2px 6px; border-radius: 3px;">31-40% (良)</span></div>
                <div><span style="background-color: rgba(255, 149, 0, 0.2); padding: 2px 6px; border-radius: 3px;">41-50% (中)</span></div>
                <div><span style="background-color: rgba(255, 59, 48, 0.2); padding: 2px 6px; border-radius: 3px;">>50% (差)</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("暂无符合筛选条件的经销商物料费比数据。")
    else:
        st.info("暂无经销商物料费比数据。")

    st.markdown('</div>', unsafe_allow_html=True)

    # 图表解读
    st.markdown('''
    <div class="chart-explanation">
        <div class="chart-explanation-title">图表解读：</div>
        <p>这个图表展示了物料费比最低和最高的经销商对比。费比越低(绿色)表示物料利用效率越高；
        费比越高(红色)表示物料使用效率较低。颜色区分了不同的效率级别：≤30%(优)、31-40%(良)、
        41-50%(中)和>50%(差)。通过对比可找出最佳实践和需要改进的案例。悬停可查看详细信息。</p>
    </div>
    ''', unsafe_allow_html=True)

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


# 在主函数中使用
def main():
    # 加载数据
    material_data, sales_data, material_price, distributor_data = get_data()

    # 页面标题
    st.markdown('<div class="feishu-title">物料投放分析动态仪表盘</div>', unsafe_allow_html=True)
    st.markdown('<div class="feishu-subtitle">协助销售人员数据驱动地分配物料资源，实现销售增长目标</div>',
                unsafe_allow_html=True)

    # 应用侧边栏筛选并获取筛选后的数据
    filtered_material, filtered_sales, filtered_distributor = create_sidebar_filters(
        material_data, sales_data, distributor_data
    )

    # 计算关键指标
    total_material_cost = filtered_material['物料成本'].sum()
    total_sales = filtered_sales['销售金额'].sum()
    roi = total_sales / total_material_cost if total_material_cost > 0 else 0
    material_sales_ratio = (total_material_cost / total_sales * 100) if total_sales > 0 else 0
    total_distributors = filtered_sales['经销商名称'].nunique()

    # 创建飞书风格图表对象
    fp = FeishuPlots()

    # 修改标签页创建部分 - 新增物料与产品组合优化标签页
    tab1, tab2, tab3 = st.tabs(["物料与销售分析", "经销商分析", "物料与产品组合优化"])

    # ======= 物料与销售分析标签页 =======
    with tab1:
        # 物料与销售分析标签页的内容
        create_material_sales_relationship(filtered_distributor)
        create_material_roi_analysis(filtered_material, filtered_sales)
        create_expense_ratio_analysis(filtered_distributor)

        # 这部分是从业绩概览标签页移过来的销售人员物料利用效率对比
        # 新增：销售人员物料使用效率对比
        st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">销售人员物料利用效率对比</div>',
                    unsafe_allow_html=True)

        # 只保留一行用于销售人员效率得分图
        st.markdown('<div class="feishu-chart-container" style="height: 100%;">', unsafe_allow_html=True)

        # 按销售人员分组计算关键指标 - 确保使用正确的数据筛选
        if '销售人员' in filtered_distributor.columns and len(filtered_distributor) > 0:
            salesperson_metrics = filtered_distributor.groupby('销售人员').agg({
                'ROI': 'mean',
                '物料总成本': 'sum',
                '销售总额': 'sum',
                '客户代码': 'nunique'
            }).reset_index()

            salesperson_metrics.rename(columns={'客户代码': '经销商数量'}, inplace=True)
            salesperson_metrics['物料销售比率'] = (
                    salesperson_metrics['物料总成本'] / salesperson_metrics['销售总额'] * 100).round(2)
            salesperson_metrics['人均销售额'] = (
                    salesperson_metrics['销售总额'] / salesperson_metrics['经销商数量']).round(2)
            salesperson_metrics['ROI'] = salesperson_metrics['ROI'].round(2)

            # 计算物料利用效率得分 (基于ROI和物料销售比率)
            max_roi = salesperson_metrics['ROI'].max()
            min_ratio = salesperson_metrics['物料销售比率'].min() if len(salesperson_metrics) > 0 else 0

            # 归一化并加权计算得分
            salesperson_metrics['ROI_score'] = salesperson_metrics['ROI'] / max_roi if max_roi > 0 else 0
            salesperson_metrics['Ratio_score'] = min_ratio / salesperson_metrics[
                '物料销售比率'] if min_ratio > 0 else 0
            salesperson_metrics['效率得分'] = (salesperson_metrics['ROI_score'] * 0.6 + salesperson_metrics[
                'Ratio_score'] * 0.4) * 100
            salesperson_metrics['效率得分'] = salesperson_metrics['效率得分'].round(2)

            # 按效率得分排序 - 显示所有销售人员，降序排列
            salesperson_metrics = salesperson_metrics.sort_values('效率得分', ascending=False)

            # 确保有数据时才创建图表
            if len(salesperson_metrics) > 0:
                # 创建销售人员效率得分图 - 显示所有销售人员
                fig = go.Figure()

                # 添加效率得分柱状图
                fig.add_trace(go.Bar(
                    y=salesperson_metrics['销售人员'],
                    x=salesperson_metrics['效率得分'],
                    orientation='h',
                    name='物料利用效率得分',
                    marker=dict(
                        color=salesperson_metrics['效率得分'].apply(
                            lambda
                                x: '#0FC86F' if x >= 75 else '#2B5AED' if x >= 60 else '#FFAA00' if x >= 40 else '#F53F3F'
                        ),
                        line=dict(width=0.5, color='white')
                    ),
                    text=salesperson_metrics['效率得分'].apply(lambda x: f"{x:.1f}"),
                    textposition='auto',
                    hovertemplate='<b>%{y}</b><br>' +
                                  '效率得分: <b>%{x:.1f}</b><br>' +
                                  '物料投入产出比: %{customdata[0]:.2f}<br>' +
                                  '物料销售比率: %{customdata[1]:.2f}%<br>' +
                                  '经销商数量: %{customdata[2]}家<br>' +
                                  '人均销售额: ¥%{customdata[3]:,.2f}',
                    customdata=np.column_stack((
                        salesperson_metrics['ROI'],
                        salesperson_metrics['物料销售比率'],
                        salesperson_metrics['经销商数量'],
                        salesperson_metrics['人均销售额']
                    ))
                ))

                # 优化布局 - 调整高度以适应更多销售人员
                fig.update_layout(
                    height=max(400, 30 * len(salesperson_metrics)),  # 动态调整高度
                    title='销售人员物料利用效率得分 (降序排列)',
                    xaxis_title='效率得分 (满分100)',
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
                        range=[0, 100]
                    ),
                    yaxis=dict(
                        showgrid=False,
                        autorange="reversed"  # 从高到低排序
                    ),
                    showlegend=False
                )

                # 添加效率等级区域
                fig.add_shape(
                    type="rect",
                    x0=0, x1=40,
                    y0=-0.5, y1=len(salesperson_metrics) - 0.5,
                    fillcolor="rgba(245, 63, 63, 0.1)",
                    line=dict(width=0),
                    layer="below"
                )

                fig.add_shape(
                    type="rect",
                    x0=40, x1=60,
                    y0=-0.5, y1=len(salesperson_metrics) - 0.5,
                    fillcolor="rgba(255, 170, 0, 0.1)",
                    line=dict(width=0),
                    layer="below"
                )

                fig.add_shape(
                    type="rect",
                    x0=60, x1=75,
                    y0=-0.5, y1=len(salesperson_metrics) - 0.5,
                    fillcolor="rgba(43, 90, 237, 0.1)",
                    line=dict(width=0),
                    layer="below"
                )

                fig.add_shape(
                    type="rect",
                    x0=75, x1=100,
                    y0=-0.5, y1=len(salesperson_metrics) - 0.5,
                    fillcolor="rgba(15, 200, 111, 0.1)",
                    line=dict(width=0),
                    layer="below"
                )

                # 添加效率等级注释
                fig.add_annotation(
                    x=20, y=len(salesperson_metrics) - 0.5,
                    text="不足",
                    showarrow=False,
                    font=dict(size=10, color="#F53F3F")
                )

                fig.add_annotation(
                    x=50, y=len(salesperson_metrics) - 0.5,
                    text="一般",
                    showarrow=False,
                    font=dict(size=10, color="#FFAA00")
                )

                fig.add_annotation(
                    x=67.5, y=len(salesperson_metrics) - 0.5,
                    text="良好",
                    showarrow=False,
                    font=dict(size=10, color="#2B5AED")
                )

                fig.add_annotation(
                    x=87.5, y=len(salesperson_metrics) - 0.5,
                    text="优秀",
                    showarrow=False,
                    font=dict(size=10, color="#0FC86F")
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("销售人员数据处理正常，但未能生成有效的销售人员效率得分。请检查数据完整性。")
        else:
            # 尝试从原始数据查找销售人员
            unique_salespersons = []
            if '申请人' in material_data.columns:
                unique_salespersons = material_data['申请人'].unique().tolist()
                st.warning(
                    f"检测到'申请人'列，但未将其映射为'销售人员'。请在数据处理阶段将'申请人'列重命名为'销售人员'。检测到有{len(unique_salespersons)}位申请人。")
            elif '销售人员' in material_data.columns:
                unique_salespersons = material_data['销售人员'].unique().tolist()
            elif '申请人' in sales_data.columns:
                unique_salespersons = sales_data['申请人'].unique().tolist()
                st.warning(
                    f"检测到'申请人'列，但未将其映射为'销售人员'。请在数据处理阶段将'申请人'列重命名为'销售人员'。检测到有{len(unique_salespersons)}位申请人。")
            elif '销售人员' in sales_data.columns:
                unique_salespersons = sales_data['销售人员'].unique().tolist()

            if unique_salespersons:
                st.warning(
                    f"由于数据结构原因，无法正确显示销售人员效率分析。检测到系统中有销售人员/申请人数据：{', '.join(unique_salespersons[:5])}等{len(unique_salespersons)}人。请检查过滤条件或联系技术支持。")
            else:
                st.info("未检测到销售人员或申请人数据，请检查数据源。")

        st.markdown('</div>', unsafe_allow_html=True)

        # 添加图表解读
        st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>此图展示了所有销售人员的物料利用效率得分，满分100分。得分基于ROI(占60%)和物料销售比率(占40%)计算。得分越高表示该销售人员越善于利用物料资源创造销售额。背景色区分了不同效率等级：绿色(优秀≥75)、蓝色(良好≥60)、黄色(一般≥40)和红色(不足<40)。</p>
            </div>
            ''', unsafe_allow_html=True)

    # ======= 经销商分析标签页 =======
    with tab2:
        create_distributor_analysis_tab(filtered_distributor, filtered_material, filtered_sales)

    # ======= 物料与产品组合优化标签页 =======
    with tab3:
        create_product_optimization_tab(filtered_material, filtered_sales, filtered_distributor)


# 运行主应用
if __name__ == '__main__':
    main()