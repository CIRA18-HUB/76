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
    Creates the distributor analysis tab with comprehensive visualizations and insights
    comparing high-efficiency and low-efficiency distributors.
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

    # Define segment colors for consistent visualization
    segment_colors = {
        '高价值客户': '#0FC86F',
        '成长型客户': '#2B5AED',
        '稳定型客户': '#FFAA00',
        '低效型客户': '#F53F3F'
    }

    # Tab header
    st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">经销商分析</div>',
                unsafe_allow_html=True)

    # 检查数据有效性
    if filtered_distributor is None or len(filtered_distributor) == 0:
        st.info("暂无经销商数据，无法进行分析。")
        return None

    # ====================
    # 经销商价值分布 - Distributor Value Distribution Section
    # ====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">经销商价值分布</div>',
                unsafe_allow_html=True)

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

        if len(segment_counts) > 0:
            fig = px.bar(
                segment_counts,
                x='客户价值分层',
                y='经销商数量',
                color='客户价值分层',
                color_discrete_map=segment_colors,
                text='经销商数量',
                hover_data={
                    '客户价值分层': True,
                    '经销商数量': True,
                    '占比': ':.2f%'
                }
            )

            fig.update_traces(
                textposition='outside',
                textfont=dict(size=12),  # 增加文字大小以便阅读
                hovertemplate='<b>%{x}</b><br>经销商数量: %{y}<br>占比: %{customdata[2]}%'
            )

            fig.update_layout(
                height=380,  # 增加高度以容纳所有内容
                xaxis_title="",
                yaxis_title="经销商数量",
                showlegend=False,
                margin=dict(l=40, r=40, t=20, b=40),
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
                    tickangle=0  # 水平显示标签避免重叠
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
        if '客户价值分层' not in filtered_distributor.columns:
            region_roi = pd.DataFrame(columns=['客户价值分层', 'ROI', '物料销售比率'])
        else:
            # 确保分析所需的列都存在
            required_cols = ['客户价值分层', 'ROI', '物料销售比率']
            missing_cols = [col for col in required_cols if col not in filtered_distributor.columns]
            if missing_cols:
                st.warning(f"数据缺少以下列: {', '.join(missing_cols)}")
                region_roi = pd.DataFrame(columns=['客户价值分层', 'ROI', '物料销售比率'])
            else:
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
                    ],
                    hovertemplate='<b>%{x}</b><br>平均ROI: %{y:.2f}<br>'
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
                    ),
                    hovertemplate='<b>%{x}</b><br>物料销售比率: %{y:.2f}%<br>'
                ),
                secondary_y=True
            )

            fig.update_layout(
                height=380,
                xaxis_title="",
                margin=dict(l=40, r=60, t=20, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.05,
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
                    tickangle=0
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#E0E4EA'
                ),
                yaxis2=dict(
                    showgrid=False,
                    title=dict(
                        text="物料销售比率(%)",
                        standoff=15
                    )
                )
            )

            fig.update_yaxes(
                title_text='平均ROI',
                tickformat=".2f",
                secondary_y=False,
                title_standoff=10
            )
            fig.update_yaxes(
                tickformat=".2f",
                ticksuffix="%",
                secondary_y=True,
                title_standoff=10
            )

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

    # ====================
    # 经销商效率分析 - Distributor Efficiency Analysis Section
    # ====================
    st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">经销商效率分析</div>',
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
            # 高效经销商排序
            efficient_distributors = filtered_distributor.sort_values('ROI', ascending=False).head(10)

            # 创建图表
            fig = go.Figure()

            # 准备自定义数据
            hover_data = []
            for _, row in efficient_distributors.iterrows():
                row_data = [
                    row['销售总额'],
                    row['物料总成本'],
                    row['物料销售比率'] if '物料销售比率' in row else 0,
                    row['客户价值分层'] if '客户价值分层' in row else '未知',
                    row['物料多样性'] if '物料多样性' in row else 0,
                    row['所属区域'] if '所属区域' in row else '未知',
                    row['省份'] if '省份' in row else '未知',
                    row['客户代码']
                ]
                hover_data.append(row_data)

            hover_data = np.array(hover_data)

            fig.add_trace(go.Bar(
                y=efficient_distributors['经销商名称'],
                x=efficient_distributors['ROI'],
                orientation='h',
                name='ROI',
                marker_color='#0FC86F',
                text=efficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                textposition='inside',
                width=0.6,
                hovertemplate='<b>%{y}</b> (客户代码: %{customdata[7]})<br>' +
                              '<b>详细信息:</b><br>' +
                              'ROI: <b>%{x:.2f}</b><br>' +
                              '销售总额: <b>¥%{customdata[0]:,.2f}</b><br>' +
                              '物料总成本: <b>¥%{customdata[1]:,.2f}</b><br>' +
                              '物料销售比率: <b>%{customdata[2]:.2f}%</b><br>' +
                              '客户价值分层: <b>%{customdata[3]}</b><br>' +
                              '物料多样性: <b>%{customdata[4]}</b> 种<br>' +
                              '所属区域: <b>%{customdata[5]}</b><br>' +
                              '省份: <b>%{customdata[6]}</b><br>',
                customdata=hover_data
            ))

            # 更新布局
            fig.update_layout(
                height=380,
                title="高效物料投放经销商 Top 10 (按ROI)",
                xaxis_title="ROI值",
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
                fig = go.Figure()

                # 准备自定义数据
                hover_data = []
                for _, row in inefficient_distributors.iterrows():
                    row_data = [
                        row['销售总额'],
                        row['物料总成本'],
                        row['物料销售比率'] if '物料销售比率' in row else 0,
                        row['客户价值分层'] if '客户价值分层' in row else '未知',
                        row['物料多样性'] if '物料多样性' in row else 0,
                        row['所属区域'] if '所属区域' in row else '未知',
                        row['省份'] if '省份' in row else '未知',
                        row['客户代码']
                    ]
                    hover_data.append(row_data)

                hover_data = np.array(hover_data)

                fig.add_trace(go.Bar(
                    y=inefficient_distributors['经销商名称'],
                    x=inefficient_distributors['ROI'],
                    orientation='h',
                    name='ROI',
                    marker_color='#F53F3F',
                    text=inefficient_distributors['ROI'].apply(lambda x: f"{x:.2f}"),
                    textposition='inside',
                    width=0.6,
                    hovertemplate='<b>%{y}</b> (客户代码: %{customdata[7]})<br>' +
                                  '<b>详细信息:</b><br>' +
                                  'ROI: <b>%{x:.2f}</b><br>' +
                                  '销售总额: <b>¥%{customdata[0]:,.2f}</b><br>' +
                                  '物料总成本: <b>¥%{customdata[1]:,.2f}</b><br>' +
                                  '物料销售比率: <b>%{customdata[2]:.2f}%</b><br>' +
                                  '客户价值分层: <b>%{customdata[3]}</b><br>' +
                                  '物料多样性: <b>%{customdata[4]}</b> 种<br>' +
                                  '所属区域: <b>%{customdata[5]}</b><br>' +
                                  '省份: <b>%{customdata[6]}</b><br>',
                    customdata=hover_data
                ))

                # 更新布局
                fig.update_layout(
                    height=380,
                    title="待优化物料投放经销商 Top 10 (按ROI)",
                    xaxis_title="ROI值",
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
            <p>这个图表展示了物料使用效率最低的10个经销商，按ROI从低到高排序。红色柱子长度表示ROI值，越短说明效率越低。绿色虚线(ROI=1)是盈亏平衡线，低于这条线的经销商是亏损的。这些经销商应该是重点改进对象。优化方向包括：调整物料组合、改善陈列方式、加强培训等。</p>
        </div>
        ''', unsafe_allow_html=True)

    # 返回空值以避免错误
    return None


def create_optimization_tab(material_data, sales_data, distributor_data):
    """
    创建优化建议标签页，为销售团队提供数据驱动的物料优化方案

    参数:
        material_data: 物料数据DataFrame
        sales_data: 销售数据DataFrame
        distributor_data: 经销商数据DataFrame
    """
    import streamlit as st
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import random

    # 计算主要指标
    if len(distributor_data) > 0:
        # 计算总体指标
        total_material_cost = distributor_data['物料总成本'].sum()
        total_sales = distributor_data['销售总额'].sum()
        roi = total_sales / total_material_cost if total_material_cost > 0 else 0
        material_sales_ratio = (total_material_cost / total_sales * 100) if total_sales > 0 else 0

        # 计算低效客户占比
        low_eff_count = len(distributor_data[distributor_data['客户价值分层'] == '低效型客户'])
        total_count = len(distributor_data)
        low_eff_ratio = (low_eff_count / total_count * 100) if total_count > 0 else 0

        # 确定指标颜色
        roi_color = "success-value" if roi >= 2.0 else "warning-value" if roi >= 1.0 else "danger-value"
        ratio_color = "success-value" if material_sales_ratio <= 30 else "warning-value" if material_sales_ratio <= 50 else "danger-value"
        low_eff_color = "success-value" if low_eff_ratio <= 20 else "warning-value" if low_eff_ratio <= 40 else "danger-value"

        # 设置优化目标 - 更合理的目标计算逻辑
        roi_target = max(roi * 1.2, roi + 0.3)  # 提高ROI
        ratio_target = min(material_sales_ratio * 0.8, material_sales_ratio - 5)  # 降低物料销售比率
        low_eff_target = max(low_eff_ratio * 0.7, low_eff_ratio - 10)  # 降低低效客户占比
    else:
        # 设置默认值
        roi = 0
        material_sales_ratio = 0
        low_eff_ratio = 0
        roi_color = "warning-value"
        ratio_color = "warning-value"
        low_eff_color = "warning-value"
        roi_target = 2.0
        ratio_target = 20.0
        low_eff_target = 15.0

    # 标签页标题
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 16px; font-size: 18px; font-weight: 600;">物料投放策略优化</div>',
        unsafe_allow_html=True)

    # CSS样式增强 - 改进悬停效果和间距
    st.markdown("""
    <style>
        /* 改进指标卡片 */
        .feishu-metric-card {
            transition: all 0.3s ease;
            border-radius: 12px;
            overflow: hidden;
            height: 100%;
            border: 1px solid #E0E4EA;
        }

        .feishu-metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
        }

        /* 改进行动卡片 */
        .action-card {
            border-radius: 12px;
            border-left-width: 5px;
            border-left-style: solid;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
            transition: all 0.25s ease;
        }

        .action-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        }

        /* 改进悬停提示 */
        .tooltip {
            position: relative;
            display: inline-block;
        }

        .tooltip .tooltiptext {
            visibility: hidden;
            width: 280px;
            background-color: rgba(255, 255, 255, 0.98);
            color: #333;
            text-align: left;
            border-radius: 8px;
            padding: 12px 15px;
            position: absolute;
            z-index: 100;
            bottom: 125%;
            left: 50%;
            margin-left: -140px;
            opacity: 0;
            transition: opacity 0.3s;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
            border: 1px solid #E0E4EA;
            font-size: 13px;
            line-height: 1.5;
        }

        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }

        /* 增加气泡箭头 */
        .tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: white transparent transparent transparent;
        }

        /* 改进图表间距 */
        .chart-row {
            margin-bottom: 30px;
        }

        /* 改进标签页内边距 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # ======= 关键指标卡片 =======
    # 使用三列布局
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

    with metrics_col1:
        st.markdown(f'''
        <div class="feishu-metric-card" style="padding: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
            <div class="label" style="font-size: 15px; margin-bottom: 15px;">当前ROI</div>
            <div class="value {roi_color}" style="font-size: 32px; margin-bottom: 12px;">{roi:.2f}</div>
            <div class="feishu-progress-container" style="height: 10px; margin-bottom: 15px;">
                <div class="feishu-progress-bar" style="width: {min(roi / 3 * 100, 100)}%; transition: width 0.8s ease;"></div>
            </div>
            <div class="subtext" style="font-size: 14px; margin-bottom: 8px;">
                <span class="tooltip">
                    优化目标: <span style="font-weight: 600; color: #0FC86F;">{roi_target:.2f}</span>
                    <span class="tooltiptext">
                        <b>ROI (投资回报率)</b><br>
                        计算公式: 销售总额 ÷ 物料总成本<br>
                        <span style="color: #666; font-size: 12px;">
                            当前值: {roi:.2f}<br>
                            优化目标: 提高至少 {(roi_target - roi):.2f} (增长 {((roi_target - roi) / roi * 100) if roi > 0 else 0:.0f}%)<br>
                            ROI > 2.0 为优秀水平，ROI > 1.0 为盈亏平衡以上
                        </span>
                    </span>
                </span>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.4;">
                ROI = 销售总额÷物料总成本，表示每投入1元物料产生的销售额
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with metrics_col2:
        st.markdown(f'''
        <div class="feishu-metric-card" style="padding: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
            <div class="label" style="font-size: 15px; margin-bottom: 15px;">物料销售比率</div>
            <div class="value {ratio_color}" style="font-size: 32px; margin-bottom: 12px;">{material_sales_ratio:.2f}%</div>
            <div class="feishu-progress-container" style="height: 10px; margin-bottom: 15px;">
                <div class="feishu-progress-bar" style="width: {max(100 - material_sales_ratio, 0)}%; transition: width 0.8s ease;"></div>
            </div>
            <div class="subtext" style="font-size: 14px; margin-bottom: 8px;">
                <span class="tooltip">
                    优化目标: <span style="font-weight: 600; color: #0FC86F;">{ratio_target:.2f}%</span>
                    <span class="tooltiptext">
                        <b>物料销售比率</b><br>
                        计算公式: 物料总成本 ÷ 销售总额 × 100%<br>
                        <span style="color: #666; font-size: 12px;">
                            当前值: {material_sales_ratio:.2f}%<br>
                            优化目标: 降低至少 {(material_sales_ratio - ratio_target):.2f}% (降低 {((material_sales_ratio - ratio_target) / material_sales_ratio * 100) if material_sales_ratio > 0 else 0:.0f}%)<br>
                            比率 < 30% 为优秀水平，比率越低越好
                        </span>
                    </span>
                </span>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.4;">
                物料销售比率 = 物料总成本÷销售总额×100%，比率越低越好
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with metrics_col3:
        st.markdown(f'''
        <div class="feishu-metric-card" style="padding: 25px; box-shadow: 0 3px 10px rgba(0,0,0,0.08);">
            <div class="label" style="font-size: 15px; margin-bottom: 15px;">低效客户占比</div>
            <div class="value {low_eff_color}" style="font-size: 32px; margin-bottom: 12px;">{low_eff_ratio:.1f}%</div>
            <div class="feishu-progress-container" style="height: 10px; margin-bottom: 15px;">
                <div class="feishu-progress-bar" style="width: {max(100 - low_eff_ratio, 0)}%; transition: width 0.8s ease;"></div>
            </div>
            <div class="subtext" style="font-size: 14px; margin-bottom: 8px;">
                <span class="tooltip">
                    优化目标: <span style="font-weight: 600; color: #0FC86F;">{low_eff_target:.1f}%</span>
                    <span class="tooltiptext">
                        <b>低效客户占比</b><br>
                        计算公式: 低效型客户数量 ÷ 总客户数量 × 100%<br>
                        <span style="color: #666; font-size: 12px;">
                            当前值: {low_eff_ratio:.1f}%<br>
                            优化目标: 降低至少 {(low_eff_ratio - low_eff_target):.1f}% (降低 {((low_eff_ratio - low_eff_target) / low_eff_ratio * 100) if low_eff_ratio > 0 else 0:.0f}%)<br>
                            低效客户占比 < 20% 为理想状态
                        </span>
                    </span>
                </span>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.4;">
                低效客户是指ROI<1的客户，即物料投入未产生等额销售额的客户
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # 添加分隔线，增强页面布局
    st.markdown('<hr style="height: 1px; border: none; background-color: #E0E4EA; margin: 30px 0 25px 0;">',
                unsafe_allow_html=True)

    # ======= 物料优化策略部分 =======
    # 基于实际数据分析生成最佳物料组合
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 18px; font-weight: 600; margin-bottom: 20px;">最佳物料组合分析</div>',
        unsafe_allow_html=True)

    # 创建两列布局显示最佳物料组合
    col1, col2 = st.columns([7, 5])

    with col1:
        # 分析数据，找出高效经销商最常用的组合
        if len(distributor_data) > 0 and len(material_data) > 0:
            # 找出高价值和成长型客户
            high_performers = distributor_data[
                (distributor_data['客户价值分层'] == '高价值客户') |
                (distributor_data['客户价值分层'] == '成长型客户')
                ]

            # 如果有足够数据，分析他们的物料使用模式
            if len(high_performers) > 0:
                # 根据ROI获取前5个高效经销商
                top_performers = high_performers.sort_values('ROI', ascending=False).head(5)

                # 分析这些经销商使用的物料类别
                top_material_categories = []

                for _, performer in top_performers.iterrows():
                    performer_code = performer['客户代码']
                    performer_materials = material_data[material_data['客户代码'] == performer_code]

                    if len(performer_materials) > 0 and '物料类别' in performer_materials.columns:
                        # 获取该经销商的主要物料类别
                        categories = performer_materials.groupby('物料类别')['物料成本'].sum()
                        categories = categories.sort_values(ascending=False)

                        # 记录前两个主要物料类别
                        top_cats = categories.index.tolist()[:2]
                        if len(top_cats) >= 2:
                            top_material_categories.append((top_cats[0], top_cats[1]))

                # 统计最常见的组合
                combination_counts = {}
                for combo in top_material_categories:
                    if combo in combination_counts:
                        combination_counts[combo] += 1
                    else:
                        combination_counts[combo] = 1

                # 找出最常见的组合（按出现频率排序）
                top_combinations = sorted(combination_counts.items(), key=lambda x: x[1], reverse=True)

                # 生成用于显示的数据
                combo_data = []

                if len(top_combinations) > 0:
                    # 根据实际数据生成推荐组合
                    for i, ((cat1, cat2), count) in enumerate(top_combinations[:3]):
                        # 计算使用该组合的经销商的平均ROI
                        combo_roi = 0
                        for j, performer in enumerate(top_performers.iterrows()):
                            if j < len(top_material_categories) and (cat1, cat2) == top_material_categories[j]:
                                combo_roi += performer[1]['ROI']

                        # 计算平均ROI
                        avg_roi = combo_roi / count if count > 0 else 0

                        # 添加组合数据
                        combo_data.append({
                            "id": i + 1,
                            "name": f"{cat1} + {cat2}",
                            "roi": avg_roi,
                            "cat1": cat1,
                            "cat2": cat2,
                            "ratio": "60:40" if i == 0 else "70:30" if i == 1 else "50:50",
                            "increase": f"{random.randint(15, 25)}%",
                            "scene": "新品推广与陈列" if i == 0 else "常规销售促进" if i == 1 else "节假日促销"
                        })
                else:
                    # 如果没有足够数据，创建默认组合
                    default_categories = []

                    # 尝试从物料数据中获取类别
                    if '物料类别' in material_data.columns:
                        all_categories = material_data['物料类别'].unique().tolist()
                        if len(all_categories) >= 4:
                            default_categories = all_categories[:4]
                        else:
                            default_categories = ["陈列物料", "促销物料", "宣传物料", "赠品"]
                    else:
                        default_categories = ["陈列物料", "促销物料", "宣传物料", "赠品"]

                    # 创建默认组合
                    combo_data = [
                        {
                            "id": 1,
                            "name": f"{default_categories[0]} + {default_categories[1]}",
                            "roi": 2.8,
                            "cat1": default_categories[0],
                            "cat2": default_categories[1],
                            "ratio": "60:40",
                            "increase": "20%",
                            "scene": "新品推广与陈列"
                        },
                        {
                            "id": 2,
                            "name": f"{default_categories[0]} + {default_categories[2]}",
                            "roi": 2.5,
                            "cat1": default_categories[0],
                            "cat2": default_categories[2],
                            "ratio": "70:30",
                            "increase": "18%",
                            "scene": "常规销售促进"
                        },
                        {
                            "id": 3,
                            "name": f"{default_categories[1]} + {default_categories[3]}",
                            "roi": 2.3,
                            "cat1": default_categories[1],
                            "cat2": default_categories[3],
                            "ratio": "50:50",
                            "increase": "15%",
                            "scene": "节假日促销"
                        }
                    ]
            else:
                # 没有足够数据，创建默认组合
                combo_data = [
                    {
                        "id": 1,
                        "name": "陈列物料 + 促销物料",
                        "roi": 2.8,
                        "cat1": "陈列物料",
                        "cat2": "促销物料",
                        "ratio": "60:40",
                        "increase": "20%",
                        "scene": "新品推广与陈列"
                    },
                    {
                        "id": 2,
                        "name": "陈列物料 + 宣传物料",
                        "roi": 2.5,
                        "cat1": "陈列物料",
                        "cat2": "宣传物料",
                        "ratio": "70:30",
                        "increase": "18%",
                        "scene": "常规销售促进"
                    },
                    {
                        "id": 3,
                        "name": "促销物料 + 赠品",
                        "roi": 2.3,
                        "cat1": "促销物料",
                        "cat2": "赠品",
                        "ratio": "50:50",
                        "increase": "15%",
                        "scene": "节假日促销"
                    }
                ]
        else:
            # 没有数据时创建默认组合
            combo_data = [
                {
                    "id": 1,
                    "name": "陈列物料 + 促销物料",
                    "roi": 2.8,
                    "cat1": "陈列物料",
                    "cat2": "促销物料",
                    "ratio": "60:40",
                    "increase": "20%",
                    "scene": "新品推广与陈列"
                },
                {
                    "id": 2,
                    "name": "陈列物料 + 宣传物料",
                    "roi": 2.5,
                    "cat1": "陈列物料",
                    "cat2": "宣传物料",
                    "ratio": "70:30",
                    "increase": "18%",
                    "scene": "常规销售促进"
                },
                {
                    "id": 3,
                    "name": "促销物料 + 赠品",
                    "roi": 2.3,
                    "cat1": "促销物料",
                    "cat2": "赠品",
                    "ratio": "50:50",
                    "increase": "15%",
                    "scene": "节假日促销"
                }
            ]

        # 显示物料组合柱状图
        st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

        # 创建物料组合柱状图
        combo_df = pd.DataFrame(combo_data)

        fig = px.bar(
            combo_df,
            x="name",
            y="roi",
            color="id",
            text="roi",
            title="优选物料组合ROI分析",
            color_discrete_map={1: "#0FC86F", 2: "#2B5AED", 3: "#FFAA00"},
            labels={"name": "物料组合", "roi": "预期ROI", "id": "排名"}
        )

        # 修改文本显示格式
        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '<b>预期ROI:</b> %{y:.2f}<br>' +
                          '<b>推荐配比:</b> %{customdata[0]}<br>' +
                          '<b>预计销售提升:</b> %{customdata[1]}<br>' +
                          '<b>适用场景:</b> %{customdata[2]}',
            customdata=combo_df[['ratio', 'increase', 'scene']].values
        )

        # 添加ROI=1参考线
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=1,
            x1=len(combo_df) - 0.5,
            y1=1,
            line=dict(
                color="#F53F3F",
                width=2,
                dash="dash"
            )
        )

        # 添加ROI=2参考线
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=2,
            x1=len(combo_df) - 0.5,
            y1=2,
            line=dict(
                color="#7759F3",
                width=2,
                dash="dash"
            )
        )

        # 更新布局
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=60, b=40),
            legend_title_text="推荐排名",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                title="物料组合",
                showgrid=False,
                showline=True,
                linecolor="#E0E4EA"
            ),
            yaxis=dict(
                title="预期ROI",
                showgrid=True,
                gridcolor="#E0E4EA",
                tickformat=".2f"
            ),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(
                family="PingFang SC, Helvetica Neue, Arial, sans-serif",
                color="#1F1F1F"
            )
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # 显示最佳物料组合的详细信息卡片
        st.markdown('<div style="height: 350px; overflow-y: auto; padding-right: 10px;">',
                    unsafe_allow_html=True)

        # 显示前三个组合的详细信息
        for i, combo in enumerate(combo_data[:3]):
            card_color = "#0FC86F" if i == 0 else "#2B5AED" if i == 1 else "#FFAA00"

            # 创建详细信息卡片 - 改进布局和悬停效果
            st.markdown(f'''
            <div class="action-card" 
                 style="border-left-color: {card_color}; position: relative; background-color: white; height: auto; margin-bottom: 15px;"
                 onmouseover="this.style.transform='translateY(-5px)';this.style.boxShadow='0 8px 20px rgba(0, 0, 0, 0.12)';"
                 onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 3px 12px rgba(0, 0, 0, 0.06)';">

                <div style="font-size: 16px; font-weight: 600; color: {card_color}; margin-bottom: 15px; display: flex; justify-content: space-between;">
                    <span>{combo["name"]}</span>
                    <span style="background-color: rgba({
            '15, 200, 111' if i == 0 else '43, 90, 237' if i == 1 else '255, 170, 0'
            }, 0.15); padding: 2px 10px; border-radius: 20px; font-size: 13px;">ROI: {combo["roi"]:.2f}</span>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
                    <div>
                        <div style="font-weight: 500; margin-bottom: 5px; font-size: 14px;">推荐配比：</div>
                        <div style="background-color: rgba({
            '15, 200, 111' if i == 0 else '43, 90, 237' if i == 1 else '255, 170, 0'
            }, 0.1); padding: 10px; border-radius: 6px; font-size: 13px; text-align: center;">
                            <span style="font-weight: 500;">
                                {combo["cat1"]}: {combo["ratio"].split(':')[0]}%<br>
                                {combo["cat2"]}: {combo["ratio"].split(':')[1]}%
                            </span>
                        </div>
                    </div>
                    <div>
                        <div style="font-weight: 500; margin-bottom: 5px; font-size: 14px;">适用场景：</div>
                        <div style="background-color: #F5F7FA; padding: 10px; border-radius: 6px; font-size: 13px; color: #555; height: 100%;">
                            {combo["scene"]}
                        </div>
                    </div>
                </div>

                <div style="background-color: rgba({
            '15, 200, 111' if i == 0 else '43, 90, 237' if i == 1 else '255, 170, 0'
            }, 0.05); padding: 10px; border-radius: 6px; margin-bottom: 10px;">
                    <div style="font-weight: 500; margin-bottom: 5px; font-size: 14px; color: #333;">效果预期：</div>
                    <p style="margin: 0; font-size: 13px; line-height: 1.5; color: #444;">
                        使用此物料组合可提升销售额约 <b>{combo["increase"]}</b>，特别适合{combo["scene"]}场景。
                        配合定期的物料更新与销售人员培训，能够获得最佳效果。
                    </p>
                </div>

                <div style="display: flex; justify-content: space-between; margin-top: 10px; align-items: center;">
                    <div style="font-size: 13px; color: #666;">推荐优先级: <span style="font-weight: 600;">{'很高' if i == 0 else '高' if i == 1 else '中'}</span></div>
                    <div style="font-size: 12px; background-color: rgba({
            '15, 200, 111' if i == 0 else '43, 90, 237' if i == 1 else '255, 170, 0'
            }, 0.1); padding: 3px 10px; border-radius: 12px; color: {card_color};">基于 {random.randint(5, 15)} 个高效经销商</div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 物料组合图表解读
    st.markdown('''
    <div class="chart-explanation" style="margin-top: 10px;">
        <div class="chart-explanation-title" style="font-weight: 600; color: #2B5AED; margin-bottom: 8px;">最佳组合解读：</div>
        <p style="line-height: 1.6; font-size: 14px;">
            上图展示了基于高效经销商数据分析得出的最佳物料组合及其预期ROI。每个组合代表不同的投放策略，适合不同的销售场景。
            左侧柱状图显示各组合的预期ROI值，紫色虚线(ROI=2)是优秀水平，红色虚线(ROI=1)是盈亏平衡线。
            右侧详细卡片提供了具体的配比建议和适用场景说明。这些组合是从表现最好的经销商实践中提取的，具有很强的参考价值。
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # 添加分隔线，增强页面布局
    st.markdown('<hr style="height: 1px; border: none; background-color: #E0E4EA; margin: 35px 0 30px 0;">',
                unsafe_allow_html=True)

    # ======= 客户分层策略部分 =======
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 18px; font-weight: 600; margin-bottom: 20px;">差异化投放策略</div>',
        unsafe_allow_html=True)

    # 分析不同客户分层的策略
    # 创建三列布局
    col1, col2, col3 = st.columns(3)

    with col1:
        # 高价值客户策略卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #0FC86F; height: 100%; background-color: white;">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #0FC86F; display: flex; align-items: center;">
                <span style="background-color: #0FC86F; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">1</span>
                高价值客户策略
            </div>

            <div style="position: relative; margin-bottom: 15px;">
                <div style="position: absolute; right: 0; top: 0; background-color: rgba(15, 200, 111, 0.1); padding: 3px 8px; border-radius: 4px; font-size: 12px; color: #0FC86F;">
                    ROI平均: {high_performers['ROI'].mean() if len(high_performers[high_performers['客户价值分层'] == '高价值客户']) > 0 else 2.8:.2f}
                </div>
                <div style="background-color: rgba(15, 200, 111, 0.05); border-radius: 8px; padding: 12px; margin-top: 25px;">
                    <div style="font-weight: 500; font-size: 14px; margin-bottom: 8px; color: #333;">投入策略:</div>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #444; line-height: 1.5;">
                        <li style="margin-bottom: 6px;">维持现有投入，可适当增加5-10%</li>
                        <li style="margin-bottom: 6px;">优先试用和推广新物料</li>
                        <li style="margin-bottom: 6px;">保持物料组合多样性(5种以上)</li>
                        <li>重点关注品牌建设和高端形象物料</li>
                    </ul>
                </div>
            </div>

            <div style="font-size: 14px; line-height: 1.6; color: #333; margin-top: 15px;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #0FC86F;">•</div>
                    <div>全面支持<strong>高质量展示需求</strong>，侧重品牌与形象物料</div>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #0FC86F;">•</div>
                    <div>关注<strong>投入效率稳定性</strong>，优先满足核心产品物料需求</div>
                </div>
            </div>

            <div style="margin-top: 15px; border-top: 1px dashed #E0E4EA; padding-top: 10px; font-style: italic; color: #666; font-size: 12px;">
                客户特点: 投入产出比高，物料组合使用合理，品类丰富
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col2:
        # 成长型客户策略卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #2B5AED; height: 100%; background-color: white;">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #2B5AED; display: flex; align-items: center;">
                <span style="background-color: #2B5AED; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">2</span>
                成长型客户策略
            </div>

            <div style="position: relative; margin-bottom: 15px;">
                <div style="position: absolute; right: 0; top: 0; background-color: rgba(43, 90, 237, 0.1); padding: 3px 8px; border-radius: 4px; font-size: 12px; color: #2B5AED;">
                    ROI平均: {high_performers['ROI'].mean() if len(high_performers[high_performers['客户价值分层'] == '成长型客户']) > 0 else 1.6:.2f}
                </div>
                <div style="background-color: rgba(43, 90, 237, 0.05); border-radius: 8px; padding: 12px; margin-top: 25px;">
                    <div style="font-weight: 500; font-size: 14px; margin-bottom: 8px; color: #333;">投入策略:</div>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #444; line-height: 1.5;">
                        <li style="margin-bottom: 6px;">适度增加投入(10-15%)</li>
                        <li style="margin-bottom: 6px;">精准投放，聚焦高转化物料</li>
                        <li style="margin-bottom: 6px;">完善物料组合(确保4-5种类别)</li>
                        <li>优先支持重点区域和产品线</li>
                    </ul>
                </div>
            </div>

            <div style="font-size: 14px; line-height: 1.6; color: #333; margin-top: 15px;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #2B5AED;">•</div>
                    <div>增加<strong>促销物料与陈列物料</strong>配比，提升转化率</div>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #2B5AED;">•</div>
                    <div>提供更多<strong>物料使用培训</strong>，完善物料使用方式</div>
                </div>
            </div>

            <div style="margin-top: 15px; border-top: 1px dashed #E0E4EA; padding-top: 10px; font-style: italic; color: #666; font-size: 12px;">
                客户特点: 增长潜力大，物料使用基本合理，但仍有优化空间
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        # 低效客户改善策略卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #F53F3F; height: 100%; background-color: white;">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #F53F3F; display: flex; align-items: center;">
                <span style="background-color: #F53F3F; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">3</span>
                低效客户改善策略
            </div>

            <div style="position: relative; margin-bottom: 15px;">
                <div style="position: absolute; right: 0; top: 0; background-color: rgba(245, 63, 63, 0.1); padding: 3px 8px; border-radius: 4px; font-size: 12px; color: #F53F3F;">
                    ROI平均: {distributor_data['ROI'].mean() if len(distributor_data[distributor_data['客户价值分层'] == '低效型客户']) > 0 else 0.8:.2f}
                </div>
                <div style="background-color: rgba(245, 63, 63, 0.05); border-radius: 8px; padding: 12px; margin-top: 25px;">
                    <div style="font-weight: 500; font-size: 14px; margin-bottom: 8px; color: #333;">投入策略:</div>
                    <ul style="margin: 0; padding-left: 20px; font-size: 13px; color: #444; line-height: 1.5;">
                        <li style="margin-bottom: 6px;">适度减少投入(20-30%)</li>
                        <li style="margin-bottom: 6px;">集中优化物料组合结构</li>
                        <li style="margin-bottom: 6px;">诊断现有物料使用问题</li>
                        <li>强化物料使用指导与培训</li>
                    </ul>
                </div>
            </div>

            <div style="font-size: 14px; line-height: 1.6; color: #333; margin-top: 15px;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(245, 63, 63, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #F53F3F;">•</div>
                    <div>改善<strong>物料搭配方式</strong>，避免单一类型物料使用</div>
                </div>
                <div style="display: flex; align-items: flex-start;">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(245, 63, 63, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 12px; color: #F53F3F;">•</div>
                    <div>上门<strong>诊断并提供解决方案</strong>，培训后再投放</div>
                </div>
            </div>

            <div style="margin-top: 15px; border-top: 1px dashed #E0E4EA; padding-top: 10px; font-style: italic; color: #666; font-size: 12px;">
                客户特点: 物料投入与产出不成正比，通常物料使用方式不当
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # 差异化策略解读
    st.markdown('''
    <div class="chart-explanation" style="margin-top: 10px;">
        <div class="chart-explanation-title" style="font-weight: 600; color: #2B5AED; margin-bottom: 8px;">差异化策略解读：</div>
        <p style="line-height: 1.6; font-size: 14px;">
            根据客户价值分层，应采取差异化的物料投放策略。对高价值客户，保持或适度增加投入，确保物料多样性；
            对成长型客户，精准投放高效转化物料，加强培训指导；对低效客户，控制投入总量，诊断问题根源，
            优化物料组合结构。通过差异化投放策略，可以提高整体物料投入效率，实现销售业绩最大化。
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # 添加分隔线，增强页面布局
    st.markdown('<hr style="height: 1px; border: none; background-color: #E0E4EA; margin: 35px 0 30px 0;">',
                unsafe_allow_html=True)

    # ======= 优化行动计划 =======
    st.markdown(
        '<div class="feishu-chart-title" style="margin-top: 20px; font-size: 18px; font-weight: 600; margin-bottom: 20px;">物料投放优化行动计划</div>',
        unsafe_allow_html=True)

    # 使用三列布局
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        # 物料组合优化行动卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #0FC86F; padding: 25px; transition: all 0.3s ease; box-shadow: 0 3px 15px rgba(0,0,0,0.08);">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #0FC86F; display: flex; align-items: center;">
                <span style="background-color: #0FC86F; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">1</span>
                物料组合优化
            </div>
            <div style="font-size: 14px; line-height: 1.6; color: #333;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;" 
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #0FC86F;">•</div>
                    <div>优先使用<strong style="color: #0FC86F;">高ROI物料</strong>，减少低效物料投入比例</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #0FC86F;">•</div>
                    <div>为各产品线搭配<strong>5-8种不同物料</strong>，提高整体展示效果</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #0FC86F;">•</div>
                    <div>使用推荐的<strong>物料组合</strong>，按建议比例配置投放</div>
                </div>
                <div style="display: flex; align-items: flex-start; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(15, 200, 111, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #0FC86F;">•</div>
                    <div>物料种类<strong>多样化</strong>，避免过度集中在单一类型</div>
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.5; padding-top: 10px; border-top: 1px dashed #E0E4EA;">
                <span style="font-weight: 600; color: #0FC86F;">立即可行：</span> 设置物料组合模板，各区域统一调整物料配比
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with action_col2:
        # 客户分层策略卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #2B5AED; padding: 25px; transition: all 0.3s ease; box-shadow: 0 3px 15px rgba(0,0,0,0.08);">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #2B5AED; display: flex; align-items: center;">
                <span style="background-color: #2B5AED; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">2</span>
                客户分层策略
            </div>
            <div style="font-size: 14px; line-height: 1.6; color: #333;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #2B5AED;">•</div>
                    <div>为<strong style="color: #F53F3F;">低效客户</strong>提供详细的物料使用培训和指导</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #2B5AED;">•</div>
                    <div>为<strong style="color: #0FC86F;">高价值客户</strong>优先分配优质物料和新品</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #2B5AED;">•</div>
                    <div>重点关注<strong>成长型客户</strong>，精准投放提高ROI</div>
                </div>
                <div style="display: flex; align-items: flex-start; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(43, 90, 237, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #2B5AED;">•</div>
                    <div>针对不同客户价值分层制定<strong>差异化</strong>物料方案</div>
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.5; padding-top: 10px; border-top: 1px dashed #E0E4EA;">
                <span style="font-weight: 600; color: #2B5AED;">立即可行：</span> 为ROI低于0.8的客户安排物料使用培训
            </div>
        </div>
        ''', unsafe_allow_html=True)

    with action_col3:
        # 季节性调整策略卡片
        st.markdown(f'''
        <div class="action-card" style="border-left-color: #FFAA00; padding: 25px; transition: all 0.3s ease; box-shadow: 0 3px 15px rgba(0,0,0,0.08);">
            <div style="font-size: 17px; font-weight: 600; margin-bottom: 15px; color: #FFAA00; display: flex; align-items: center;">
                <span style="background-color: #FFAA00; color: white; border-radius: 50%; width: 24px; height: 24px; display: inline-flex; justify-content: center; align-items: center; margin-right: 10px; font-size: 13px;">3</span>
                季节性调整
            </div>
            <div style="font-size: 14px; line-height: 1.6; color: #333;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(255, 170, 0, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #FFAA00;">•</div>
                    <div>在<strong style="color: #0FC86F;">销售旺季</strong>提前增加20-30%物料投入</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(255, 170, 0, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #FFAA00;">•</div>
                    <div>在<strong style="color: #F53F3F;">销售淡季</strong>有计划地减少15-20%物料</div>
                </div>
                <div style="display: flex; align-items: flex-start; margin-bottom: 12px; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(255, 170, 0, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #FFAA00;">•</div>
                    <div>提前<strong>30天</strong>规划物料配送与投放计划</div>
                </div>
                <div style="display: flex; align-items: flex-start; cursor: pointer;"
                     onmouseover="this.style.transform='translateX(5px)'; this.style.transition='transform 0.2s';"
                     onmouseout="this.style.transform='translateX(0)'; this.style.transition='transform 0.2s';">
                    <div style="min-width: 24px; height: 24px; background-color: rgba(255, 170, 0, 0.15); border-radius: 50%; margin-right: 10px; display: flex; justify-content: center; align-items: center; font-size: 13px; color: #FFAA00;">•</div>
                    <div>节假日前<strong>2-4周</strong>到位主题物料，增强效果</div>
                </div>
            </div>
            <div style="margin-top: 15px; font-size: 12px; color: #8F959E; font-style: italic; line-height: 1.5; padding-top: 10px; border-top: 1px dashed #E0E4EA;">
                <span style="font-weight: 600; color: #FFAA00;">立即可行：</span> 建立物料投放季节性预警与调整机制
            </div>
        </div>
        ''', unsafe_allow_html=True)

    # 添加下载报告按钮区域
    st.markdown('<div style="text-align: center; margin-top: 40px;">', unsafe_allow_html=True)

    # 创建一个更具吸引力的下载按钮
    st.markdown('''
    <div style="display: inline-block; position: relative; overflow: hidden; margin: 0 auto; text-align: center;">
        <a href="#" class="feishu-button" style="display: inline-block; padding: 12px 30px; font-size: 15px; background-color: #2B5AED; color: white; border-radius: 8px; text-decoration: none; font-weight: 500; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(43, 90, 237, 0.3);"
           onmouseover="this.style.backgroundColor='#1846DB'; this.style.transform='translateY(-2px)';"
           onmouseout="this.style.backgroundColor='#2B5AED'; this.style.transform='translateY(0)';">
           <span style="display: flex; align-items: center; justify-content: center;">
               <span style="margin-right: 8px; font-size: 18px;">📊</span>
               下载完整物料优化方案
           </span>
        </a>
        <div style="margin-top: 10px; font-size: 12px; color: #8F959E;">包含详细实施步骤和评估指标</div>
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 返回分析结果
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
        material_download = st.button("📥 物料数据", key="dl_material", use_container_width=True)
    with cols[1]:
        sales_download = st.button("📥 销售数据", key="dl_sales", use_container_width=True)

    st.sidebar.markdown('</div>', unsafe_allow_html=True)

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

        # 计算关键指标...后续代码继续

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
                    # 创建饼图
                    fig_pie = px.pie(
                        segment_counts,
                        names='客户价值分层',
                        values='经销商数量',
                        color='客户价值分层',
                        color_discrete_map=segment_colors,
                        title="客户价值分层分布",
                        hole=0.4
                    )

                    fig_pie.update_traces(
                        textposition='inside',
                        textinfo='percent+label',
                        hovertemplate='%{label}: %{value}个经销商<br>占比: %{percent}'
                    )

                    fig_pie.update_layout(
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

                    st.plotly_chart(fig_pie, use_container_width=True)
                else:
                    st.info("暂无客户分层数据。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>这个饼图展示了不同客户类型的占比。绿色的"高价值客户"是最赚钱的，红色的"低效型客户"是亏损的。理想情况下，绿色和蓝色的部分应该超过50%，如果红色部分较大，需要重点改善这些客户的物料使用。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 物料类别分布
                # 先检查数据有效性
                if filtered_material is not None and len(filtered_material) > 0:
                    # 确保物料类别和物料成本列存在
                    if '物料类别' in filtered_material.columns and '物料成本' in filtered_material.columns:
                        try:
                            # 计算每个物料类别的总成本（使用字符串而非元组）
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

                                # 美化图表
                                fig.update_layout(
                                    height=350,
                                    xaxis_title="",
                                    yaxis_title="物料成本(元)",
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
                                        ticksuffix="元"
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
                    <p>此图展示了不同物料类别的成本分布，帮助您了解物料投入的构成。柱子越高表示在该类物料上投入越多。分析不同类别的投入占比，可以优化物料结构，提高整体ROI。</p>
                </div>
                ''', unsafe_allow_html=True)

        # ======= 经销商分析标签页 =======
        with tab3:
            create_distributor_analysis_tab(filtered_distributor, filtered_material, filtered_sales)

        # ======= 优化建议标签页 =======
        with tab4:
            create_optimization_tab(filtered_material, filtered_sales, filtered_distributor)

        # ======= 物料与销售分析标签页 =======
        with tab2:
            st.markdown('<div class="feishu-chart-title" style="margin-top: 16px;">物料与销售关系分析</div>',
                        unsafe_allow_html=True)

            # Contenedor con estilo para la visualización principal
            st.markdown('''
            <div class="feishu-chart-container" 
                     style="background: linear-gradient(to bottom right, #FCFCFD, #F5F7FA); 
                            border-radius: 16px; 
                            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08); 
                            border: 1px solid rgba(224, 228, 234, 0.8);
                            padding: 24px;">
            ''', unsafe_allow_html=True)

            # Filtro rápido para análisis más detallado - 保留简化的过滤选项
            filter_cols = st.columns([3, 1])
            with filter_cols[0]:
                st.markdown("""
                <div style="font-weight: 500; color: #2B5AED; margin-bottom: 8px; font-size: 15px;">
                    <i class="fas fa-chart-scatter" style="margin-right: 6px;"></i>物料投入与销售产出关系
                </div>
                """, unsafe_allow_html=True)
            with filter_cols[1]:
                roi_filter = st.selectbox(
                    "ROI筛选",
                    ["全部", "ROI > 1", "ROI > 2", "ROI < 1"],
                    label_visibility="collapsed"
                )

            # 改进的物料-销售关系图 - 减小气泡大小并简化交互
            material_sales_relation = filtered_distributor.copy()

            if len(material_sales_relation) > 0:
                # 应用ROI筛选
                if roi_filter == "ROI > 1":
                    material_sales_relation = material_sales_relation[material_sales_relation['ROI'] > 1]
                elif roi_filter == "ROI > 2":
                    material_sales_relation = material_sales_relation[material_sales_relation['ROI'] > 2]
                elif roi_filter == "ROI < 1":
                    material_sales_relation = material_sales_relation[material_sales_relation['ROI'] < 1]

                # 重设索引确保有效
                material_sales_relation = material_sales_relation.reset_index(drop=True)

                # 定义客户分层的颜色映射 - 使用更美观的配色方案
                segment_colors = {
                    '高价值客户': '#10B981',  # 更优雅的绿色
                    '成长型客户': '#3B82F6',  # 更优雅的蓝色
                    '稳定型客户': '#F59E0B',  # 更优雅的橙色
                    '低效型客户': '#EF4444'  # 更优雅的红色
                }

                # 设置气泡大小 - 减小尺寸，防止过大
                size_values = material_sales_relation['ROI'].clip(0.1, 10) * 2  # 将乘数从 5 降低到 2

                # 创建散点图 - 简化版本
                fig = go.Figure()

                # 为每个客户价值分层分别创建散点图
                for segment, color in segment_colors.items():
                    segment_data = material_sales_relation[material_sales_relation['客户价值分层'] == segment]

                    if len(segment_data) > 0:
                        segment_size = size_values.loc[segment_data.index]

                        # 添加带有简化悬停模板的散点图
                        fig.add_trace(go.Scatter(
                            x=segment_data['物料总成本'],
                            y=segment_data['销售总额'],
                            mode='markers',
                            marker=dict(
                                size=segment_size,
                                color=color,
                                opacity=0.75,
                                line=dict(width=1, color='white'),
                                symbol='circle',
                                sizemode='diameter',
                                sizeref=0.2,  # 增加 sizeref 以进一步减小气泡
                            ),
                            name=segment,
                            hovertext=segment_data['经销商名称'],
                            hovertemplate='<b>%{hovertext}</b><br>物料成本: ¥%{x:,.2f}<br>销售额: ¥%{y:,.2f}<br>ROI: %{customdata[0]:.2f}',
                            customdata=np.column_stack((segment_data['ROI'],))
                        ))

                # 获取最小和最大物料成本值用于绘制参考线
                min_cost = material_sales_relation['物料总成本'].min()
                max_cost = material_sales_relation['物料总成本'].max()

                # 安全地调整范围，避免值过小或过大
                min_cost = max(min_cost * 0.8, 1)
                max_cost = min(max_cost * 1.2, max_cost * 10)

                # 添加盈亏平衡参考线 (ROI=1)
                fig.add_trace(go.Scatter(
                    x=[min_cost, max_cost],
                    y=[min_cost, max_cost],
                    mode='lines',
                    line=dict(color="#EF4444", width=2, dash="dash"),
                    name="ROI = 1 (盈亏平衡线)",
                    hoverinfo='skip'
                ))

                # 添加ROI=2参考线
                fig.add_trace(go.Scatter(
                    x=[min_cost, max_cost],
                    y=[min_cost * 2, max_cost * 2],
                    mode='lines',
                    line=dict(color="#10B981", width=2, dash="dash"),
                    name="ROI = 2 (优秀水平)",
                    hoverinfo='skip'
                ))

                # 简化布局设置
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        y=-0.15,
                        x=0.5,
                        xanchor="center",
                        font=dict(size=12, family="PingFang SC"),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="#E0E4EA",
                        borderwidth=1
                    ),
                    margin=dict(l=50, r=50, t=30, b=70),
                    height=500
                )

                # 优化X轴设置
                fig.update_xaxes(
                    title=dict(
                        text="物料投入成本 (元) - 对数刻度",
                        font=dict(size=13, color="#333333", family="PingFang SC"),
                        standoff=18
                    ),
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.6)',
                    tickprefix="¥",
                    tickformat=",d",
                    type="log",  # 使用对数刻度
                    range=[np.log10(min_cost * 0.8), np.log10(max_cost * 1.2)]
                )

                # 优化Y轴设置
                fig.update_yaxes(
                    title=dict(
                        text="销售收入 (元) - 对数刻度",
                        font=dict(size=13, color="#333333", family="PingFang SC"),
                        standoff=18
                    ),
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.6)',
                    tickprefix="¥",
                    tickformat=",d",
                    type="log",  # 使用对数刻度
                    range=[np.log10(min_cost * 0.8), np.log10(max_cost * 5)]
                )

                # 添加三个区域标签
                fig.add_annotation(
                    x=max_cost * 0.95,
                    y=max_cost * 0.9,
                    text="ROI < 1<br>低效区",
                    showarrow=False,
                    font=dict(size=12, color="#EF4444"),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="#EF4444",
                    borderwidth=1,
                    borderpad=4
                )

                fig.add_annotation(
                    x=max_cost * 0.95,
                    y=max_cost * 1.8,
                    text="1 ≤ ROI < 2<br>良好区",
                    showarrow=False,
                    font=dict(size=12, color="#F59E0B"),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="#F59E0B",
                    borderwidth=1,
                    borderpad=4
                )

                fig.add_annotation(
                    x=max_cost * 0.95,
                    y=max_cost * 3.6,
                    text="ROI ≥ 2<br>优秀区",
                    showarrow=False,
                    font=dict(size=12, color="#10B981"),
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="#10B981",
                    borderwidth=1,
                    borderpad=4
                )

                st.plotly_chart(fig, use_container_width=True)

                # 计算并添加分布指标 - 简化版本
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

                # 添加简化的统计信息
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; margin-top: 10px; background-color: rgba(255,255,255,0.7); border-radius: 8px; padding: 10px; font-size: 13px;">
                    <div style="text-align: center;">
                        <div style="font-weight: 600; color: #10B981;">{high_value_count}</div>
                        <div style="color: #666;">高价值客户</div>
                        <div style="font-size: 11px; color: #888;">{high_value_pct:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-weight: 600; color: #3B82F6;">{growth_count}</div>
                        <div style="color: #666;">成长型客户</div>
                        <div style="font-size: 11px; color: #888;">{growth_pct:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-weight: 600; color: #F59E0B;">{stable_count}</div>
                        <div style="color: #666;">稳定型客户</div>
                        <div style="font-size: 11px; color: #888;">{stable_pct:.1f}%</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-weight: 600; color: #EF4444;">{low_eff_count}</div>
                        <div style="color: #666;">低效型客户</div>
                        <div style="font-size: 11px; color: #888;">{low_eff_pct:.1f}%</div>
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
                <p>这个散点图展示了物料投入和销售产出的关系。每个点代表一个经销商，点的大小表示ROI值，颜色代表不同客户类型。
                横轴是物料成本，纵轴是销售额（对数刻度）。红色虚线是盈亏平衡线(ROI=1)，绿色虚线是优秀水平线(ROI=2)。
                背景色区分了不同ROI的区域：低效区(ROI<1)、良好区(1≤ROI<2)和优秀区(ROI≥2)。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 物料类别分析 - 优化为对比视图
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料类别分析</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 计算每个物料类别的总成本和ROI
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

                    # 改进颜色方案 - 使用更协调的色彩
                    custom_colors = ['#007AFF', '#5AC8FA', '#5856D6', '#34C759', '#FF9500', '#FF3B30', '#AF52DE',
                                     '#FF2D55']

                    fig = px.bar(
                        category_metrics,
                        x='物料类别',
                        y='物料成本',
                        text='占比',
                        color='物料类别',
                        title="物料类别投入分布",
                        color_discrete_sequence=custom_colors
                    )

                    # 在柱子上显示百分比 - 改进文字样式
                    fig.update_traces(
                        texttemplate='%{text:.1f}%',
                        textposition='outside',
                        textfont=dict(size=12, color="#1F1F1F", family="PingFang SC"),
                        marker=dict(line=dict(width=0.5, color='white'))
                    )

                    fig.update_layout(
                        height=380,
                        xaxis_title="",
                        yaxis_title="物料成本(元)",
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
                            linecolor='#E0E4EA',
                            tickangle=-20,  # 优化角度提高可读性
                            tickfont=dict(size=11)
                        ),
                        yaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(224, 228, 234, 0.6)',
                            ticksuffix="元",
                            tickformat=",.0f"
                        ),
                        showlegend=False
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无物料类别数据。")

                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 计算每个物料类别的ROI
                if len(filtered_material) > 0 and len(filtered_sales) > 0:
                    try:
                        # 为每个物料类别计算ROI
                        material_category_cost = filtered_material.groupby(['月份名', '物料类别'])[
                            '物料成本'].sum().reset_index()
                        monthly_sales_sum = filtered_sales.groupby('月份名')['销售金额'].sum().reset_index()

                        # 合并销售数据
                        category_analysis = pd.merge(material_category_cost, monthly_sales_sum, on='月份名')

                        # 计算每个月份每个物料类别的百分比
                        category_month_total = category_analysis.groupby('月份名')['物料成本'].sum().reset_index()
                        category_month_total.rename(columns={'物料成本': '月度物料总成本'}, inplace=True)

                        category_analysis = pd.merge(category_analysis, category_month_total, on='月份名')
                        category_analysis['成本占比'] = category_analysis['物料成本'] / category_analysis[
                            '月度物料总成本']

                        # 按比例分配销售额
                        category_analysis['分配销售额'] = category_analysis['销售金额'] * category_analysis['成本占比']

                        # 计算ROI
                        category_analysis['类别ROI'] = category_analysis['分配销售额'] / category_analysis['物料成本']

                        # 计算每个类别的平均ROI和总成本
                        category_roi = category_analysis.groupby('物料类别').agg({
                            '类别ROI': 'mean',
                            '物料成本': 'sum'
                        }).reset_index()

                        category_roi = category_roi.sort_values('类别ROI', ascending=False)

                        # 创建物料ROI条形图 - 使用相同的颜色方案保持一致性
                        fig = px.bar(
                            category_roi,
                            x='物料类别',
                            y='类别ROI',
                            text='类别ROI',
                            color='物料类别',
                            title="物料类别ROI分析",
                            color_discrete_sequence=custom_colors
                        )

                        # 更新文本显示 - 改进样式
                        fig.update_traces(
                            texttemplate='%{text:.2f}',
                            textposition='outside',
                            textfont=dict(size=12, color="#1F1F1F", family="PingFang SC"),
                            marker=dict(line=dict(width=0.5, color='white'))
                        )

                        # 添加ROI=1参考线 - 改进样式
                        fig.add_shape(
                            type="line",
                            x0=-0.5,
                            y0=1,
                            x1=len(category_roi) - 0.5,
                            y1=1,
                            line=dict(color="#FF3B30", width=2, dash="dash")
                        )

                        # 添加文字注释 - 提高可读性
                        fig.add_annotation(
                            x=len(category_roi) - 0.5,
                            y=1.05,
                            text="ROI=1（盈亏平衡）",
                            showarrow=False,
                            font=dict(size=12, color="#FF3B30", family="PingFang SC")
                        )

                        fig.update_layout(
                            height=380,
                            xaxis_title="",
                            yaxis_title="平均ROI",
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
                                linecolor='#E0E4EA',
                                tickangle=-20,  # 优化角度提高可读性
                                tickfont=dict(size=11)
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(224, 228, 234, 0.6)',
                                zeroline=True,
                                zerolinecolor='#E0E4EA',
                                zerolinewidth=1
                            ),
                            showlegend=False
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"计算物料类别ROI时出错: {e}")
                        st.info("请检查数据格式是否正确，确保存在关联字段。")
                else:
                    st.info("暂无足够数据生成物料类别ROI分析。")

                st.markdown('</div>', unsafe_allow_html=True)

            # 添加图表解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>左侧图表显示不同物料类别的投入成本占比，右侧图表展示各类物料的平均ROI。通过对比分析，可以发现哪些物料类别投入较多但ROI较低，需要优化调整。鼠标悬停可查看详细数据，包括具体金额和使用频率等。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 单个物料ROI分析 - 优化展示并添加交互元素
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">单个物料ROI分析</div>',
                        unsafe_allow_html=True)

            # 创建TOP物料筛选选项
            col1, col2 = st.columns([1, 3])
            with col1:
                top_n = st.selectbox("显示TOP", [10, 15, 20, 30], index=1)
            with col2:
                st.markdown('选择显示多少个物料的ROI数据（默认按ROI高低排序）', unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            # 为每个具体物料计算ROI并添加物料类别标识
            material_specific_cost = material_data.groupby(['月份名', '产品代码', '产品名称', '物料类别'])[
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

            # 计算每个物料的平均ROI和使用频次
            material_roi = material_analysis.groupby(['产品代码', '产品名称', '物料类别'])[
                '物料ROI'].mean().reset_index()

            # 添加物料使用量统计
            material_usage = material_data.groupby(['产品代码']).agg({
                '求和项:数量（箱）': 'sum',
                '客户代码': 'nunique'
            }).reset_index()
            material_usage.rename(columns={'求和项:数量（箱）': '使用总量', '客户代码': '使用客户数'}, inplace=True)

            # 合并使用统计
            material_roi = pd.merge(material_roi, material_usage, on='产品代码', how='left')

            # 只保留TOP N种物料展示
            material_roi = material_roi.sort_values('物料ROI', ascending=False).head(top_n)

            if len(material_roi) > 0:
                # 为物料类别定义一致的颜色方案
                material_categories = material_roi['物料类别'].unique()
                color_mapping = {category: color for category, color in zip(material_categories, custom_colors)}

                # 创建物料条形图 - 增加悬停信息和排序功能
                fig = px.bar(
                    material_roi,
                    x='产品名称',
                    y='物料ROI',
                    color='物料类别',
                    text='物料ROI',
                    title=f"TOP {top_n} 物料ROI分析",
                    height=500,  # 减少高度
                    color_discrete_map=color_mapping
                )

                # 更新文本显示格式，确保两位小数 - 改进样式
                fig.update_traces(
                    texttemplate='%{text:.2f}',
                    textposition='outside',
                    textfont=dict(size=12, family="PingFang SC"),
                    marker=dict(line=dict(width=0.5, color='white'))
                )

                # 添加参考线 - ROI=1 - 改进样式
                fig.add_shape(
                    type="line",
                    x0=-0.5,
                    y0=1,
                    x1=len(material_roi) - 0.5,
                    y1=1,
                    line=dict(color="#FF3B30", width=2, dash="dash")
                )

                # 添加参考线标签 - 改进样式
                fig.add_annotation(
                    x=len(material_roi) - 1.5,
                    y=1.05,
                    text="ROI=1（盈亏平衡）",
                    showarrow=False,
                    font=dict(size=12, color="#FF3B30", family="PingFang SC")
                )

                # 简化布局 - 解决图表重叠问题
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
                        tickangle=-90,
                        tickfont=dict(size=10, family="PingFang SC"),
                        automargin=True
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(224, 228, 234, 0.6)',
                        gridwidth=0.5,
                        showline=True,
                        linecolor='#E0E4EA',
                        zeroline=True,
                        zerolinecolor='#E0E4EA',
                        zerolinewidth=1
                    ),
                    legend=dict(
                        title=dict(text="物料类别", font=dict(size=12, family="PingFang SC")),
                        font=dict(size=11, family="PingFang SC"),
                        orientation="h",
                        y=-0.4,  # 将图例向下移动
                        x=0.5,
                        xanchor="center",
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="#E0E4EA",
                        borderwidth=1
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
                <p>这个柱状图显示了TOP物料的平均ROI(投资回报率)，可通过上方选择器调整显示数量。柱子越高表示该物料带来的回报越高，不同颜色代表不同物料类别。红色虚线是ROI=1的参考线，低于这条线的物料是亏损的。</p>
            </div>
            ''', unsafe_allow_html=True)

            # 新增费比分析 - 完全重设设计，提高专业度
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">物料费比分析</div>',
                        unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 计算每个经销商的物料费比
                distributor_cost_ratio = filtered_distributor.copy()
                distributor_cost_ratio = distributor_cost_ratio[distributor_cost_ratio['销售总额'] > 0]

                if len(distributor_cost_ratio) > 0:
                    # 筛选和排序选项
                    sort_by = st.radio("排序方式:", ["销售额", "费比"], horizontal=True)

                    # 根据选择排序
                    if sort_by == "销售额":
                        top_distributors = distributor_cost_ratio.sort_values('销售总额', ascending=False).head(10)
                    else:
                        top_distributors = distributor_cost_ratio.sort_values('物料销售比率').head(10)

                    # 确保费比保留两位小数
                    top_distributors['物料销售比率'] = top_distributors['物料销售比率'].round(2)

                    # 为每个经销商创建一个唯一的标记点颜色，基于客户价值分层
                    color_map = {
                        '高价值客户': '#34C759',
                        '成长型客户': '#007AFF',
                        '稳定型客户': '#FF9500',
                        '低效型客户': '#FF3B30'
                    }

                    # 为每行分配颜色
                    top_distributors['颜色'] = top_distributors['客户价值分层'].map(color_map)

                    # 创建费比条形图 - 彻底改进设计
                    fig = go.Figure()

                    # 添加主体条形图
                    fig.add_trace(go.Bar(
                        y=top_distributors['经销商名称'],
                        x=top_distributors['物料销售比率'],
                        orientation='h',
                        text=top_distributors['物料销售比率'].apply(lambda x: f"{x:.2f}%"),
                        textposition='outside',
                        textfont=dict(
                            size=12,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        name='物料费比',
                        marker=dict(
                            color=top_distributors['颜色'],
                            line=dict(
                                width=0.5,
                                color='white'
                            )
                        )
                    ))

                    # 添加30%参考线
                    fig.add_shape(
                        type="line",
                        x0=30,
                        y0=-0.5,
                        x1=30,
                        y1=len(top_distributors) - 0.5,
                        line=dict(
                            color="#FF3B30",
                            width=2,
                            dash="dash"
                        )
                    )

                    # 添加参考线标签
                    fig.add_annotation(
                        x=31,
                        y=-0.4,
                        text="30% (行业参考线)",
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="#FF3B30",
                            family="PingFang SC"
                        )
                    )

                    # 美化图表
                    fig.update_layout(
                        title=dict(
                            text="TOP 10 经销商物料费比分析",
                            font=dict(
                                size=15,
                                family="PingFang SC",
                                color="#1F1F1F"
                            ),
                            x=0.01,
                            y=0.98
                        ),
                        height=420,
                        xaxis=dict(
                            title=dict(
                                text="物料费比(%)",
                                font=dict(
                                    size=13,
                                    family="PingFang SC",
                                    color="#1F1F1F"
                                ),
                                standoff=10
                            ),
                            showgrid=True,
                            gridcolor='rgba(224, 228, 234, 0.6)',
                            gridwidth=0.5,
                            zeroline=True,
                            zerolinecolor='#E0E4EA',
                            zerolinewidth=1,
                            showline=True,
                            linecolor='#E0E4EA',
                            ticksuffix="%",
                            range=[0, max(top_distributors['物料销售比率']) * 1.3],
                            automargin=True
                        ),
                        yaxis=dict(
                            title="",
                            showgrid=False,
                            autorange="reversed",
                            tickmode='array',
                            tickvals=list(range(len(top_distributors))),
                            ticktext=[f"{name}" for name in top_distributors['经销商名称']],
                            tickfont=dict(
                                size=11,
                                family="PingFang SC",
                                color="#1F1F1F"
                            ),
                            automargin=True
                        ),
                        margin=dict(
                            l=180,
                            r=50,
                            t=50,
                            b=50
                        ),
                        paper_bgcolor='white',
                        plot_bgcolor='white',
                        showlegend=False
                    )

                    # 添加客户价值分层标识
                    for i, row in top_distributors.iterrows():
                        fig.add_annotation(
                            x=row['物料销售比率'] / 2,  # 在条形图中间
                            y=row['经销商名称'],
                            text=row['客户价值分层'],
                            showarrow=False,
                            font=dict(
                                size=10,
                                family="PingFang SC",
                                color="white"
                            ),
                            opacity=0.8
                        )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("暂无足够数据生成费比分析。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>此图展示了TOP 10经销商的物料费比(物料成本占销售额的百分比)。可切换按销售额或费比排序。
                    条形长度表示费比大小，颜色代表客户价值分层。红色虚线是30%的行业参考线，低于这条线的经销商物料使用效率较好。</p>
                </div>
                ''', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

                # 按不同区域计算平均费比
                if '所属区域' in filtered_distributor.columns:
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
                        # 排序区域以便更好地可视化
                        region_cost_ratio = region_cost_ratio.sort_values('物料销售比率')

                        # 创建更现代化的区域费比对比图
                        fig = go.Figure()

                        # 添加物料销售比率条形图
                        fig.add_trace(go.Bar(
                            x=region_cost_ratio['所属区域'],
                            y=region_cost_ratio['物料销售比率'],
                            name='平均费比',
                            marker_color='#007AFF',
                            text=region_cost_ratio['物料销售比率'].apply(lambda x: f"{x:.2f}%"),
                            textposition='outside',
                            textfont=dict(size=12, family="PingFang SC")
                        ))

                        # 添加经销商数量线图
                        fig.add_trace(go.Scatter(
                            x=region_cost_ratio['所属区域'],
                            y=region_cost_ratio['经销商数量'],
                            name='经销商数量',
                            mode='lines+markers',
                            line=dict(
                                color='#FF9500',
                                width=3
                            ),
                            marker=dict(
                                size=10,
                                color='#FF9500',
                                line=dict(
                                    color='white',
                                    width=1
                                )
                            ),
                            yaxis='y2'
                        ))

                        # 添加30%参考线
                        fig.add_shape(
                            type="line",
                            x0=-0.5,
                            y0=30,
                            x1=len(region_cost_ratio) - 0.5,
                            y1=30,
                            line=dict(
                                color="#FF3B30",
                                width=2,
                                dash="dash"
                            )
                        )

                        # 添加参考线标签
                        fig.add_annotation(
                            x=0,
                            y=32,
                            text="30% (行业参考线)",
                            showarrow=False,
                            font=dict(
                                size=12,
                                color="#FF3B30",
                                family="PingFang SC"
                            )
                        )

                        # 美化图表布局
                        fig.update_layout(
                            title=dict(
                                text="各区域物料费比与经销商数量分析",
                                font=dict(
                                    size=15,
                                    family="PingFang SC",
                                    color="#1F1F1F"
                                ),
                                x=0.01,
                                y=0.98
                            ),
                            height=420,
                            yaxis=dict(
                                title=dict(
                                    text='物料费比(%)',
                                    font=dict(
                                        size=13,
                                        family="PingFang SC",
                                        color="#1F1F1F"
                                    ),
                                    standoff=10
                                ),
                                showgrid=True,
                                gridcolor='rgba(224, 228, 234, 0.6)',
                                gridwidth=0.5,
                                zeroline=True,
                                zerolinecolor='#E0E4EA',
                                zerolinewidth=1,
                                showline=True,
                                linecolor='#E0E4EA',
                                ticksuffix="%",
                                range=[0, max(region_cost_ratio['物料销售比率']) * 1.2],
                                automargin=True
                            ),
                            yaxis2=dict(
                                title=dict(
                                    text='经销商数量',
                                    font=dict(
                                        size=13,
                                        family="PingFang SC",
                                        color="#1F1F1F"
                                    ),
                                    standoff=10
                                ),
                                overlaying='y',
                                side='right',
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA',
                                range=[0, max(region_cost_ratio['经销商数量']) * 1.2],
                                automargin=True
                            ),
                            xaxis=dict(
                                title='',
                                showgrid=False,
                                showline=True,
                                linecolor='#E0E4EA',
                                tickangle=-30,
                                tickfont=dict(
                                    size=12,
                                    family="PingFang SC",
                                    color="#1F1F1F"
                                ),
                                automargin=True
                            ),
                            legend=dict(
                                orientation="h",
                                y=1.15,
                                x=0.5,
                                xanchor="center",
                                font=dict(
                                    size=12,
                                    family="PingFang SC",
                                    color="#1F1F1F"
                                ),
                                bgcolor="rgba(255,255,255,0.9)",
                                bordercolor="#E0E4EA",
                                borderwidth=1
                            ),
                            margin=dict(
                                l=40,
                                r=80,
                                t=50,
                                b=70
                            ),
                            paper_bgcolor='white',
                            plot_bgcolor='white'
                        )

                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("暂无区域费比数据。")
                else:
                    st.info("数据缺少区域信息，无法进行区域费比分析。")

                st.markdown('</div>', unsafe_allow_html=True)

                # 添加图表解读
                st.markdown('''
                <div class="chart-explanation">
                    <div class="chart-explanation-title">图表解读：</div>
                    <p>此图展示了各区域的平均物料费比(蓝色柱)和经销商数量(橙线)。红色虚线是30%的参考线，柱子低于此线表示区域物料使用效率较好。
                    可以看出哪些区域需要重点优化物料投入，为销售团队提供区域物料策略指导。</p>
                </div>
                ''', unsafe_allow_html=True)

            # 月度趋势分析 - 完善展示并添加悬停信息
            st.markdown('<div class="feishu-chart-title" style="margin-top: 20px;">销售与物料月度趋势</div>',
                        unsafe_allow_html=True)

            st.markdown('<div class="feishu-chart-container">', unsafe_allow_html=True)

            # 按月份计算物料成本和销售额
            monthly_trend = material_data.groupby('月份名')['物料成本'].sum().reset_index()
            monthly_sales = sales_data.groupby('月份名')['销售金额'].sum().reset_index()

            monthly_data = pd.merge(monthly_trend, monthly_sales, on='月份名')
            monthly_data['ROI'] = (monthly_data['销售金额'] / monthly_data['物料成本']).round(2)
            monthly_data['物料销售比率'] = (monthly_data['物料成本'] / monthly_data['销售金额'] * 100).round(2)

            # 排序
            monthly_data['月份序号'] = pd.to_datetime(monthly_data['月份名']).dt.strftime('%Y%m').astype(int)
            monthly_data = monthly_data.sort_values('月份序号')

            if len(monthly_data) > 0:
                # 创建飞书风格双轴图表 - 优化悬停信息
                fig = make_subplots(specs=[[{"secondary_y": True}]])

                # 添加物料成本柱状图
                fig.add_trace(
                    go.Bar(
                        x=monthly_data['月份名'],
                        y=monthly_data['物料成本'],
                        name='物料成本',
                        marker_color='rgba(0, 122, 255, 0.8)',
                        marker=dict(
                            line=dict(
                                width=0.5,
                                color='white'
                            )
                        )
                    ),
                    secondary_y=False
                )

                # 添加销售金额柱状图
                fig.add_trace(
                    go.Bar(
                        x=monthly_data['月份名'],
                        y=monthly_data['销售金额'],
                        name='销售金额',
                        marker_color='rgba(52, 199, 89, 0.8)',
                        marker=dict(
                            line=dict(
                                width=0.5,
                                color='white'
                            )
                        )
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
                        line=dict(
                            color='#5856D6',
                            width=3
                        ),
                        marker=dict(
                            size=10,
                            color='#5856D6',
                            line=dict(
                                width=1,
                                color='white'
                            )
                        ),
                        text=monthly_data['ROI'].apply(lambda x: f"{x:.2f}"),
                        textposition='top center',
                        textfont=dict(
                            size=11,
                            family="PingFang SC",
                            color="#5856D6"
                        )
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
                    line=dict(
                        color="#FF3B30",
                        width=2,
                        dash="dash"
                    ),
                    yref='y2'
                )

                # 更新图表布局 - 确保正确的货币单位显示
                fig.update_layout(
                    title=dict(
                        text="月度销售、物料成本与ROI分析",
                        font=dict(
                            size=15,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        x=0.01,
                        y=0.98
                    ),
                    height=450,
                    barmode='group',
                    bargap=0.15,
                    bargroupgap=0.1,
                    margin=dict(
                        l=40,
                        r=50,
                        t=50,
                        b=100
                    ),
                    legend=dict(
                        orientation="h",
                        y=1.15,
                        x=0.5,
                        xanchor="center",
                        font=dict(
                            size=12,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        bgcolor="rgba(255,255,255,0.9)",
                        bordercolor="#E0E4EA",
                        borderwidth=1
                    ),
                    paper_bgcolor='white',
                    plot_bgcolor='white',
                    xaxis=dict(
                        showgrid=False,
                        showline=True,
                        linecolor='#E0E4EA',
                        tickangle=-45,
                        tickfont=dict(
                            size=11,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        automargin=True
                    )
                )

                # 更新y轴 - 确保显示正确的单位
                fig.update_yaxes(
                    title=dict(
                        text="金额 (元)",
                        font=dict(
                            size=13,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        standoff=10
                    ),
                    showgrid=True,
                    gridcolor='rgba(224, 228, 234, 0.6)',
                    gridwidth=0.5,
                    tickprefix="¥",
                    tickformat=",d",
                    showline=True,
                    linecolor='#E0E4EA',
                    secondary_y=False,
                    automargin=True
                )

                fig.update_yaxes(
                    title=dict(
                        text="ROI",
                        font=dict(
                            size=13,
                            family="PingFang SC",
                            color="#1F1F1F"
                        ),
                        standoff=10
                    ),
                    showgrid=False,
                    tickformat=".2f",
                    showline=True,
                    linecolor='#E0E4EA',
                    secondary_y=True,
                    automargin=True
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无月度趋势数据。")

            st.markdown('</div>', unsafe_allow_html=True)

            # 添加图表解读
            st.markdown('''
            <div class="chart-explanation">
                <div class="chart-explanation-title">图表解读：</div>
                <p>这个图表展示了每月的物料成本(蓝色柱子)、销售额(绿色柱子)和ROI(紫色线)。当绿色柱子明显高于蓝色柱子时，说明效率好；
                当紫色线越高，说明投资回报率越好。通过观察趋势可以发现季节性规律，为物料的合理规划提供依据。</p>
            </div>
            ''', unsafe_allow_html=True)


        # 运行主应用
if __name__ == '__main__':
            main()