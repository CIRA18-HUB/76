import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import calendar
import warnings
from scipy import stats
from datetime import datetime, timedelta
import json

# 设置页面配置 - 必须是第一个st命令
st.set_page_config(
    page_title="口力营销物料与销售分析仪表盘",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

warnings.filterwarnings('ignore')

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
    """
    加载数据文件并进行预处理

    返回:
    - df_material: 物料数据DataFrame
    - df_sales: 销售数据DataFrame
    - df_material_price: 物料单价DataFrame
    """
    import os
    import logging

    # 配置日志
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('物料分析')

    try:
        # 尝试加载真实数据
        material_file = "2025物料源数据.xlsx"
        sales_file = "25物料源销售数据.xlsx"
        price_file = "物料单价.xlsx"

        # 首先检查文件是否存在
        missing_files = []
        for file_path in [material_file, sales_file, price_file]:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        if missing_files:
            raise FileNotFoundError(f"找不到以下文件: {', '.join(missing_files)}")

        # 加载Excel文件
        logger.info("开始加载Excel文件...")
        try:
            import openpyxl
            df_material = pd.read_excel(material_file)
            df_sales = pd.read_excel(sales_file)
            df_material_price = pd.read_excel(price_file)
            logger.info("Excel文件加载成功")
        except ImportError:
            st.error("缺少openpyxl库，无法读取Excel文件。请运行: pip install openpyxl")
            raise
        except Exception as e:
            logger.error(f"读取Excel文件时出错: {str(e)}")
            raise

        # 确保物料单价表的列名正确
        logger.info("开始处理物料单价表...")
        if '物料代码' in df_material_price.columns:
            if '单价（元）' in df_material_price.columns:
                # 列名已正确
                logger.info("物料单价表列名正确")
                pass
            elif any(col for col in df_material_price.columns if '单价' in col or '价格' in col):
                # 找到可能的单价列
                price_col = next(col for col in df_material_price.columns if '单价' in col or '价格' in col)
                logger.info(f"找到可能的单价列: {price_col}, 重命名为'单价（元）'")
                df_material_price = df_material_price[['物料代码', price_col]]
                df_material_price.columns = ['物料代码', '单价（元）']
            elif len(df_material_price.columns) >= 4:
                # 根据数据样例进行调整
                logger.info(f"使用位置索引确定物料单价列")
                df_material_price = df_material_price[['物料代码', df_material_price.columns[3]]]
                df_material_price.columns = ['物料代码', '单价（元）']
            else:
                raise ValueError("物料单价表格式不正确，无法识别单价列")
        else:
            # 尝试使用位置索引
            if len(df_material_price.columns) >= 4:
                logger.info("物料代码列不存在，使用位置索引重命名列")
                df_material_price.columns = ['物料类别', '物料代码', '物料类别_2', '单价（元）']
                df_material_price = df_material_price[['物料代码', '单价（元）']]
            else:
                raise ValueError("物料单价表格式不正确，无法识别物料代码列")

        # 验证必要的列是否存在
        logger.info("验证数据列...")
        required_material_cols = ['发运月份', '所属区域', '省份', '城市', '经销商名称', '客户代码', '物料代码',
                                  '物料名称', '物料数量', '申请人']
        required_sales_cols = ['发运月份', '所属区域', '省份', '城市', '经销商名称', '客户代码', '产品代码', '产品名称',
                               '求和项:数量（箱）', '求和项:单价（箱）', '申请人']

        missing_material_cols = [col for col in required_material_cols if col not in df_material.columns]
        missing_sales_cols = [col for col in required_sales_cols if col not in df_sales.columns]

        if missing_material_cols:
            raise ValueError(f"物料数据缺少必要列: {', '.join(missing_material_cols)}")
        if missing_sales_cols:
            raise ValueError(f"销售数据缺少必要列: {', '.join(missing_sales_cols)}")

        st.success("成功加载真实数据文件")
        logger.info("真实数据文件加载和验证成功")

    except Exception as e:
        logger.error(f"加载真实数据文件时出错: {str(e)}")
        st.warning(f"无法加载Excel文件: {e}，创建模拟数据用于演示...")

        # 如果是缺少openpyxl库的错误，添加更具体的提示
        if "openpyxl" in str(e).lower():
            st.info("提示：需要安装openpyxl库才能读取Excel文件，请运行：pip install openpyxl")

        # 创建模拟数据
        logger.info("开始创建模拟数据...")

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
        logger.info("模拟数据创建成功")

    # 清理和标准化数据
    logger.info("开始清理和标准化数据...")

    # 确保日期格式一致
    df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
    df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])

    # 确保所有文本列的数据类型一致 - 修复类型错误
    try:
        text_columns = {
            'df_material': ['所属区域', '省份', '城市', '经销商名称', '客户代码', '物料代码', '物料名称', '申请人'],
            'df_sales': ['所属区域', '省份', '城市', '经销商名称', '客户代码', '产品代码', '产品名称', '申请人']
        }

        for col in text_columns['df_material']:
            if col in df_material.columns:
                df_material[col] = df_material[col].astype(str)

        for col in text_columns['df_sales']:
            if col in df_sales.columns:
                df_sales[col] = df_sales[col].astype(str)

        logger.info("文本列类型转换成功")
    except Exception as e:
        logger.error(f"文本列类型转换错误: {str(e)}")
        st.warning(f"数据类型转换警告: {e}")

    # 处理物料单价数据，创建查找字典
    logger.info("处理物料单价数据...")
    try:
        material_price_dict = dict(zip(df_material_price['物料代码'], df_material_price['单价（元）']))

        # 将物料单价添加到物料数据中
        df_material['物料单价'] = df_material['物料代码'].map(material_price_dict)

        # 处理可能的NaN值
        df_material['物料单价'].fillna(0, inplace=True)

        # 计算物料总成本
        df_material['物料总成本'] = df_material['物料数量'] * df_material['物料单价']
        logger.info("物料总成本计算成功")
    except Exception as e:
        logger.error(f"物料单价处理错误: {str(e)}")
        st.warning(f"物料单价处理警告: {e}")
        # 确保有一个默认值以免后续计算出错
        if '物料总成本' not in df_material.columns:
            df_material['物料总成本'] = 0

    # 计算销售总额
    logger.info("计算销售总额...")
    try:
        if '求和项:数量（箱）' in df_sales.columns and '求和项:单价（箱）' in df_sales.columns:
            df_sales['销售总额'] = df_sales['求和项:数量（箱）'] * df_sales['求和项:单价（箱）']
            logger.info("销售总额计算成功")
        else:
            raise ValueError("销售数据缺少必要的数量或单价列")
    except Exception as e:
        logger.error(f"销售总额计算错误: {str(e)}")
        st.warning(f"销售总额计算警告: {e}")
        # 确保有一个默认值以免后续计算出错
        if '销售总额' not in df_sales.columns:
            df_sales['销售总额'] = 0

    logger.info("数据加载和预处理完成")
    return df_material, df_sales, df_material_price


def configure_bar_chart(fig, title, height=500, orientation='v', **kwargs):
    """
    配置条形图特定样式
    (修改版：优化条形图样式，防止重叠)
    """
    # 首先应用通用配置
    fig = configure_plotly_chart(fig, title, height, **kwargs)

    # 添加条形图特定配置
    if orientation == 'v':
        fig.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=1, color='white')),
            width=0.7,  # 控制条形宽度以防止重叠
            error_y=dict(thickness=1, width=4),  # 如果有误差条，设置其样式
        )
    else:  # 水平条形图
        fig.update_traces(
            textposition='outside',
            marker=dict(line=dict(width=1, color='white')),
            width=0.7,  # 控制条形宽度以防止重叠
            error_x=dict(thickness=1, width=4),  # 如果有误差条，设置其样式
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed")  # 确保Y轴排序从上到下
        )

    # 增加条形图间的间距
    fig.update_layout(
        bargap=0.2,  # 组间距
        bargroupgap=0.1  # 组内间距
    )

    return fig


def configure_scatter_chart(fig, title, height=600, **kwargs):
    """
    配置散点图特定样式

    参数:
    - fig: Plotly图表对象
    - title: 图表标题
    - height: 图表高度
    - **kwargs: 其他参数

    返回:
    - 配置后的Plotly图表对象
    """
    # 首先应用通用配置
    fig = configure_plotly_chart(fig, title, height, **kwargs)

    # 添加散点图特定配置
    fig.update_traces(
        marker=dict(line=dict(width=1, color='white')),
        opacity=0.85
    )

    fig.update_layout(
        dragmode='zoom',  # 启用区域缩放
        hovermode='closest'  # 悬停模式设置为最近点
    )

    return fig


def configure_line_chart(fig, title, height=500, **kwargs):
    """
    配置折线图特定样式

    参数:
    - fig: Plotly图表对象
    - title: 图表标题
    - height: 图表高度
    - **kwargs: 其他参数

    返回:
    - 配置后的Plotly图表对象
    """
    # 首先应用通用配置
    fig = configure_plotly_chart(fig, title, height, **kwargs)

    # 添加折线图特定配置
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=2),
        marker=dict(size=6, line=dict(width=1, color='white'))
    )

    return fig


def configure_heatmap(fig, title, height=600, **kwargs):
    """
    配置热力图特定样式
    (修改版：优化热力图样式，防止标签重叠)
    """
    # 首先应用通用配置
    fig = configure_plotly_chart(fig, title, height, **kwargs)

    # 添加热力图特定配置
    fig.update_layout(
        xaxis=dict(
            tickangle=-45,
            side='bottom',
            automargin=True,  # 自动调整边距以适应标签
            tickfont=dict(size=10)  # 减小标签字体大小，防止重叠
        ),
        yaxis=dict(
            automargin=True,  # 自动调整边距以适应标签
            tickfont=dict(size=10)  # 减小标签字体大小，防止重叠
        ),
        coloraxis_colorbar=dict(
            len=0.8,
            thickness=15,
            outlinewidth=1,
            outlinecolor='#EEEEEE',
            title_font=dict(size=12),
            tickfont=dict(size=10)
        )
    )

    return fig


def convert_table_to_chart(df, value_column, label_column, color_column=None, title="数据可视化"):
    """
    将表格数据转换为图表

    参数:
    - df: 数据DataFrame
    - value_column: 数值列名
    - label_column: 标签列名
    - color_column: 颜色列名(可选)
    - title: 图表标题

    返回:
    - Plotly图表对象
    """
    # 根据数据类型和数量选择合适的图表类型
    n_rows = len(df)

    if n_rows <= 20:  # 数据量适中，使用条形图
        if color_column:
            fig = px.bar(
                df.sort_values(value_column, ascending=False),
                x=label_column,
                y=value_column,
                color=color_column,
                title=title,
                text=value_column,
                height=max(400, min(n_rows * 30, 700))  # 根据数据量自适应高度
            )
        else:
            fig = px.bar(
                df.sort_values(value_column, ascending=False),
                x=label_column,
                y=value_column,
                title=title,
                text=value_column,
                height=max(400, min(n_rows * 30, 700))
            )

        # 调整文本格式
        if df[value_column].dtype in [float, np.float64, np.float32]:
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        else:
            fig.update_traces(texttemplate='%{text}', textposition='outside')

    elif n_rows <= 50:  # 数据量较大，使用水平条形图
        if color_column:
            fig = px.bar(
                df.sort_values(value_column, ascending=True).tail(20),  # 只取前20条
                y=label_column,
                x=value_column,
                color=color_column,
                title=f"{title} (Top 20)",
                text=value_column,
                orientation='h',
                height=600
            )
        else:
            fig = px.bar(
                df.sort_values(value_column, ascending=True).tail(20),
                y=label_column,
                x=value_column,
                title=f"{title} (Top 20)",
                text=value_column,
                orientation='h',
                height=600
            )

        # 调整文本格式
        if df[value_column].dtype in [float, np.float64, np.float32]:
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        else:
            fig.update_traces(texttemplate='%{text}', textposition='outside')

    else:  # 数据量过大，使用散点图或热力图
        if color_column:
            fig = px.scatter(
                df.sort_values(value_column, ascending=False).head(50),
                x=label_column,
                y=value_column,
                color=color_column,
                title=f"{title} (Top 50)",
                size=value_column,
                hover_name=label_column,
                height=500
            )
        else:
            # 创建热力图
            values = df[value_column].values
            # 将值归一化到0-1范围
            norm_values = (values - values.min()) / (values.max() - values.min() + 1e-10)

            # 创建热力图数据
            heat_data = pd.DataFrame({
                'value': values,
                'label': df[label_column].values,
                'normalized': norm_values
            }).sort_values('value', ascending=False).head(50)

            fig = px.imshow(
                np.array([heat_data['normalized'].values]),
                x=heat_data['label'].values,
                color_continuous_scale='Blues',
                title=f"{title} (Top 50)",
                labels={'x': label_column, 'color': value_column},
                height=300
            )

            # 添加数值标签
            for i, label in enumerate(heat_data['label']):
                value = heat_data['value'].iloc[i]
                if isinstance(value, (int, float)):
                    if value >= 1000:
                        text = f"{value:,.0f}"
                    elif value >= 1:
                        text = f"{value:.2f}"
                    else:
                        text = f"{value:.4f}"
                else:
                    text = str(value)

                fig.add_annotation(
                    x=i,
                    y=0,
                    text=text,
                    showarrow=False,
                    font=dict(color="white" if heat_data['normalized'].iloc[i] > 0.5 else "black")
                )

    # 配置图表
    return configure_plotly_chart(fig, title)


def add_chart_spacing():
    """
    添加图表之间的间距
    """
    st.markdown("<div style='margin-top: 40px; margin-bottom: 40px;'></div>", unsafe_allow_html=True)


def create_chart_wrapper(title=""):
    """
    创建统一的图表包装器，确保布局一致

    参数:
    - title: 节标题(可选)
    """
    if title:
        st.markdown(
            f"<h3 style='margin-top: 40px; margin-bottom: 20px; color: #1f3867; font-size: 1.5rem;'>{title}</h3>",
            unsafe_allow_html=True)

    # 开始图表容器
    st.markdown("""
    <div style="background-color: white; border-radius: 10px; padding: 20px; 
    box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid #f0f2f5;">
    """, unsafe_allow_html=True)

    return st.container()


def render_customer_cards(customers_data, num_cols=3):
    """
    渲染客户卡片，替代表格显示

    参数:
    - customers_data: 客户数据DataFrame
    - num_cols: 每行显示的卡片数量
    """
    if customers_data.empty:
        st.warning("没有符合条件的客户数据")
        return

    # 准备数据
    customers = customers_data.to_dict('records')

    # 创建行
    rows = [customers[i:i + num_cols] for i in range(0, len(customers), num_cols)]

    for row in rows:
        cols = st.columns(num_cols)

        for i, customer in enumerate(row):
            if i < len(cols):
                # 计算ROI
                roi = customer.get('销售总额', 0) / customer.get('物料总成本', 1) if customer.get('物料总成本',
                                                                                                  0) > 0 else 0

                # 设置颜色（基于费比或ROI）
                if 'fees_ratio' in customer:
                    fee_ratio = customer['费比']
                    color = "#48BB78" if fee_ratio < 3 else "#ECC94B" if fee_ratio < 5 else "#F56565"
                else:
                    color = "#48BB78" if roi > 3 else "#ECC94B" if roi > 1 else "#F56565"

                # 渲染客户卡片
                with cols[i]:
                    st.markdown(f"""
                    <div style="background-color: white; border-radius: 10px; padding: 15px; 
                         box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; 
                         border-left: 5px solid {color};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <h4 style="margin: 0; font-size: 1.1rem;">{customer.get('经销商名称', 'N/A')}</h4>
                            <span style="background-color: {color}; color: white; padding: 3px 10px; 
                                  border-radius: 20px; font-size: 0.8rem;">
                                #{int(customer.get('价值排名', 0)) if '价值排名' in customer else ''}
                            </span>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px;">
                            <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #718096;">客户价值</div>
                                <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">
                                    ￥{customer.get('客户价值', 0):,.0f}
                                </div>
                            </div>
                            <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #718096;">销售总额</div>
                                <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">
                                    ￥{customer.get('销售总额', 0):,.0f}
                                </div>
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                            <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #718096;">ROI</div>
                                <div style="font-size: 1.1rem; font-weight: bold; color: {color};">
                                    {roi:.2f}
                                </div>
                            </div>
                            <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #718096;">费比</div>
                                <div style="font-size: 1.1rem; font-weight: bold; color: {color};">
                                    {customer.get('费比', 0):.2f}%
                                </div>
                            </div>
                            <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                <div style="font-size: 0.8rem; color: #718096;">物料成本</div>
                                <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">
                                    ￥{customer.get('物料总成本', 0):,.0f}
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# 添加自定义CSS样式
def add_custom_css():
    """
    添加自定义CSS样式，优化UI视觉效果
    """
    st.markdown("""
    <style>
        /* 主题颜色 */
        :root {
            --primary-color: #1f3867;
            --secondary-color: #5e72e4;
            --success-color: #2dce89;
            --info-color: #11cdef;
            --warning-color: #fb6340;
            --danger-color: #f5365c;
            --light-color: #f8f9fe;
            --dark-color: #172b4d;
        }

        /* 全局样式 */
        body {
            font-family: 'Source Sans Pro', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background-color: #f8f9fe;
        }

        /* 主标题 */
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: var(--primary-color);
            text-align: center;
            margin: 1.5rem 0;
            padding-bottom: 1.2rem;
            border-bottom: 3px solid #eee;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.05);
        }

        /* 区域标题 */
        .section-header {
            font-size: 1.8rem;
            font-weight: 600;
            color: var(--primary-color);
            margin: 2.5rem 0 1.5rem 0;
            padding-bottom: 0.8rem;
            border-bottom: 2px solid #eee;
        }

        /* 图表容器 - 更新 */
        .chart-container {
            background-color: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin: 30px 0 50px 0 !important;  /* 增加间距 */
            border: 1px solid #f0f2f5;
            overflow: hidden;
        }

        /* 图表包装器 - 改进 */
        .chart-wrapper {
            padding: 30px !important;
            background-color: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin: 40px 0 !important;  /* 增加图表间垂直间距 */
            border: 1px solid #f5f7fa;
        }

        /* 标签页样式优化 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2px;
            border-radius: 10px;
            background-color: #f8f9fe;
            padding: 8px;
            margin-bottom: 15px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: white;
            border-radius: 8px;
            gap: 2px;
            padding: 10px 16px;
            margin: 0 4px;  /* 增加标签间距 */
            font-weight: 500;
            transition: all 0.2s ease;
            border: 1px solid transparent;
        }

        .stTabs [aria-selected="true"] {
            background-color: #f0f7ff;
            border-bottom: 2px solid var(--primary-color);
            font-weight: 600;
            color: var(--primary-color);
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        /* 每个选项卡内容之间的间距 */
        .stTabs [role="tabpanel"] {
            padding: 20px 0;
        }

        /* 图表之间的间距 */
        .element-container {
            margin-bottom: 30px;
        }

        /* 改进边距和间距 */
        .stPlotlyChart {
            margin-bottom: 30px;
        }

        /* 更新提示卡片样式 */
        .alert-green, .alert-success {
            padding: 1.2rem;
            border-radius: 10px;
            background-color: rgba(45, 206, 137, 0.1);
            border-left: 0.5rem solid var(--success-color);
            margin: 1.8rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .alert-orange, .alert-warning {
            padding: 1.2rem;
            border-radius: 10px;
            background-color: rgba(251, 99, 64, 0.1);
            border-left: 0.5rem solid var(--warning-color);
            margin: 1.8rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        .alert-red, .alert-danger {
            padding: 1.2rem;
            border-radius: 10px;
            background-color: rgba(245, 54, 92, 0.1);
            border-left: 0.5rem solid var(--danger-color);
            margin: 1.8rem 0;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }

        /* 侧边栏优化 */
        .css-1lcbmhc.e1fqkh3o0 {
            padding: 2rem 1rem;
        }

        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb {
            background: #c1c9d6;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #a3afc2;
        }
    </style>
    """, unsafe_allow_html=True)


def configure_plotly_chart(fig, title, height=600, showlegend=True, legend_orientation="h"):
    """
    设置统一的Plotly图表样式 - 优化版
    (修改版：解决数据重叠问题，优化标签UI)
    """
    fig.update_layout(
        title={
            'text': title,
            'y': 0.97,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 22, 'color': '#1f3867',
                     'family': 'Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif'}
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'color': '#444444', 'family': 'Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif'},
        margin=dict(l=80, r=80, t=100, b=80),  # 增加边距，防止标签被截断
        height=height,
        showlegend=showlegend,
        legend=dict(
            orientation=legend_orientation,
            yanchor="bottom" if legend_orientation == "h" else "top",
            y=1.05 if legend_orientation == "h" else 1,  # 增加图例位置，防止与图表重叠
            xanchor="right" if legend_orientation == "h" else "left",
            x=1 if legend_orientation == "h" else 1.05,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#e2e8f0',
            borderwidth=1,
            font=dict(size=12),
            # 添加图例项目之间的间距
            itemsizing='constant',
            itemwidth=30
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#f4f4f4',
            zeroline=False,
            showline=True,
            linecolor='#e2e8f0',
            linewidth=1,
            tickfont=dict(size=12),
            # 防止x轴标签重叠
            tickangle=-45,
            automargin=True,  # 自动调整边距以适应标签
            tickmode='auto',
            nticks=20  # 限制x轴标签数量
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#f4f4f4',
            zeroline=False,
            showline=True,
            linecolor='#e2e8f0',
            linewidth=1,
            tickfont=dict(size=12),
            automargin=True  # 自动调整边距以适应标签
        ),
        hoverlabel=dict(
            bgcolor='rgba(255,255,255,0.95)',
            font_size=14,
            font_family='Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif',
            bordercolor='#e2e8f0'
        ),
        hovermode='closest',
        modebar=dict(
            bgcolor='rgba(255,255,255,0.9)',
            color='#1f3867',
            activecolor='#5e72e4'
        ),
        # 添加图表间距和布局调整
        autosize=True,
        template='plotly_white',  # 使用现代简洁的模板
        separators=',.',  # 千位分隔符
        dragmode='zoom',  # 默认缩放模式
        clickmode='event+select',  # 点击交互模式
        # 防止数据点重叠的设置
        barmode='group',  # 分组条形图
        boxmode='group',  # 分组箱形图
    )

    # 处理标签重叠问题
    if hasattr(fig, 'data') and len(fig.data) > 0:
        # 判断是否为条形图
        is_bar_chart = any(trace.type == 'bar' for trace in fig.data)
        if is_bar_chart:
            # 条形图文本位置调整
            for trace in fig.data:
                if trace.type == 'bar':
                    # 调整文本位置，减少重叠
                    if hasattr(trace, 'textposition') and trace.textposition == 'outside':
                        if trace.orientation == 'h':  # 水平条形图
                            fig.update_traces(textposition='outside', selector=dict(type='bar'))
                        else:  # 垂直条形图
                            fig.update_traces(textposition='outside', selector=dict(type='bar'))

                    # 添加条形图之间的间距
                    fig.update_layout(bargap=0.2, bargroupgap=0.1)

        # 判断是否为散点图
        is_scatter = any(trace.type == 'scatter' for trace in fig.data)
        if is_scatter:
            # 散点图防止重叠
            for trace in fig.data:
                if trace.type == 'scatter':
                    # 如果有文本标签，调整位置
                    if hasattr(trace, 'textposition'):
                        positions = ['top center', 'bottom center', 'middle left', 'middle right']
                        index = fig.data.index(trace) % len(positions)
                        trace.textposition = positions[index]  # 交替使用不同的文本位置

    # 确保金额显示带有'￥'前缀
    for i in range(len(fig.data)):
        if hasattr(fig.data[i], 'hovertemplate'):
            hover_text = fig.data[i].hovertemplate

            # 检查是否包含销售额、成本、价值等金额相关字段
            is_money_field = any(term in fig.data[i].name.lower() for term in
                                 ['销售', '成本', '价值', '额', 'sales', 'cost', 'value'])

            if is_money_field:
                # 对y轴值添加￥符号（如果尚未添加）
                if '%{y:,' in hover_text and '￥%{y:,' not in hover_text:
                    hover_text = hover_text.replace('%{y:,', '￥%{y:,')

                # 对自定义数据添加￥符号
                if '%{customdata[' in hover_text:
                    for j in range(10):  # 检查最多10个自定义数据字段
                        if f'%{{customdata[{j}]:,' in hover_text and f'￥%{{customdata[{j}]:,' not in hover_text:
                            hover_text = hover_text.replace(f'%{{customdata[{j}]:,', f'￥%{{customdata[{j}]:,')

            fig.data[i].hovertemplate = hover_text

    return fig
def create_region_sales_chart(region_sales):
    """
    创建区域销售表现图表

    参数:
    - region_sales: 按区域汇总的销售数据

    返回:
    - Plotly图表对象
    """
    # 创建区域销售表现图表
    fig_region_sales = px.bar(
        region_sales.sort_values('销售总额', ascending=False),
        x='所属区域',
        y='销售总额',
        labels={'销售总额': '销售总额 (元)', '所属区域': '区域'},
        color='所属区域',
        text='销售总额',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )

    # 更新柱状图样式
    fig_region_sales.update_traces(
        texttemplate='￥%{text:,.0f}',
        textposition='outside',
        hovertemplate='<b>%{x}区域</b><br>' +
                      '销售总额: <b>￥%{y:,.0f}</b><br>' +
                      '<extra></extra>',
        marker=dict(
            line=dict(width=1, color='white'),
            opacity=0.9
        )
    )

    # 配置图表布局
    fig_region_sales = configure_plotly_chart(
        fig_region_sales,
        title="各区域销售总额",
        height=500
    )

    # 调整x轴
    fig_region_sales.update_layout(
        xaxis=dict(
            title=dict(text="区域", font=dict(size=14)),
            tickfont=dict(size=13),
            categoryorder='total descending'
        ),
        yaxis=dict(
            title=dict(text="销售总额 (元)", font=dict(size=14)),
            tickprefix="￥",
            tickformat=",",
            tickfont=dict(size=13)
        )
    )

    return fig_region_sales


def create_material_product_heatmap(pivot_data, material_product_sales):
    """
    创建物料-产品关联热力图 - 增强版

    参数:
    - pivot_data: 物料-产品销售数据透视表
    - material_product_sales: 物料-产品销售原始数据

    返回:
    - Plotly热力图对象, 是否成功创建的标志
    """
    try:
        # 检查数据完整性
        if pivot_data is None or material_product_sales is None:
            return None, False

        if pivot_data.empty or material_product_sales.empty:
            return None, False

        # 检查数据是否足够生成有意义的热力图
        if len(material_product_sales['物料名称'].unique()) < 2 or len(material_product_sales['产品名称'].unique()) < 2:
            return None, False

        # 获取前8种物料和前8种产品
        try:
            top_materials = material_product_sales.groupby('物料名称')['销售总额'].sum().nlargest(8).index
            top_products = material_product_sales.groupby('产品名称')['销售总额'].sum().nlargest(8).index
        except Exception as e:
            print(f"获取前8种物料和产品时出错: {e}")
            return None, False

        # 确保有足够的数据
        if len(top_materials) == 0 or len(top_products) == 0:
            return None, False

        # 筛选数据
        filtered_pivot = pivot_data.loc[pivot_data.index.isin(top_materials), pivot_data.columns.isin(top_products)]

        if filtered_pivot.empty:
            return None, False

        # 创建热力图
        fig_material_product_heatmap = px.imshow(
            filtered_pivot,
            labels=dict(x="产品名称", y="物料名称", color="销售额 (元)"),
            x=filtered_pivot.columns,
            y=filtered_pivot.index,
            color_continuous_scale='Blues',  # 使用更醒目的颜色方案
            text_auto='.2s',
            aspect="auto"
        )

        # 增强悬停信息
        fig_material_product_heatmap.update_traces(
            hovertemplate='<b>物料:</b> %{y}<br>' +
                          '<b>产品:</b> %{x}<br>' +
                          '<b>销售额:</b> ￥%{z:,.0f}<br>' +
                          '<b>点击查看详情</b><extra></extra>',
            showscale=True
        )

        # 配置图表布局
        fig_material_product_heatmap = configure_plotly_chart(
            fig_material_product_heatmap,
            title="物料-产品关联销售热力图",
            height=650
        )

        # 特定的热力图样式调整
        fig_material_product_heatmap.update_layout(
            margin=dict(l=60, r=60, t=80, b=60),  # 增加边距避免标签截断
            xaxis=dict(
                title=dict(text='产品名称', font=dict(size=14)),
                tickangle=-45,
                side='bottom',
                tickfont=dict(size=11)  # 调小字体避免重叠
            ),
            yaxis=dict(
                title=dict(text='物料名称', font=dict(size=14)),
                tickangle=0,
                tickfont=dict(size=11)  # 调小字体避免重叠
            ),
            coloraxis_colorbar=dict(
                title="销售额 (元)",  # 修改这里，移除titleside属性
                tickprefix="￥",
                ticks="outside",
                len=0.8,
                thickness=15,
                outlinewidth=1,
                outlinecolor='#EEEEEE',
                tickfont=dict(size=11)
            )
        )

        # 添加标注解释热力图
        fig_material_product_heatmap.add_annotation(
            text="颜色越深表示销售额越高",
            showarrow=False,
            x=1.05,
            y=0.5,
            xref="paper",
            yref="paper",
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="#11cdef",
            borderwidth=1,
            borderpad=4,
            align="left"
        )

        return fig_material_product_heatmap, True

    except Exception as e:
        # 记录详细错误信息
        import traceback
        error_details = traceback.format_exc()
        print(f"创建物料-产品热力图时出错: {e}\n{error_details}")
        return None, False


def chart_error_handler(func):
    """
    图表生成函数的错误处理装饰器

    参数:
    - func: 要装饰的图表生成函数

    返回:
    - 装饰后的函数
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"生成图表'{func.__name__}'时出错: {e}\n{error_details}")

            # 创建一个带有错误信息的空白图表
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_annotation(
                text=f"生成图表时出错: {str(e)}<br>请检查数据或筛选条件",
                showarrow=False,
                font=dict(size=14, color="#FF0000"),
                align="center",
                xref="paper", yref="paper",
                x=0.5, y=0.5
            )
            fig.update_layout(
                height=400,
                plot_bgcolor="#f9f9f9",
                paper_bgcolor="#f9f9f9"
            )
            return fig

    return wrapper


def create_kpi_card_html(title, value, description, color, percentage=None, prefix="￥", is_percentage=False):
    """
    创建单个KPI卡片的HTML

    参数:
    - title: 卡片标题
    - value: 卡片数值
    - description: 卡片描述
    - color: 进度条颜色代码
    - percentage: 进度条百分比（可选）
    - prefix: 数值前缀（可选）
    - is_percentage: 是否为百分比值（可选）

    返回:
    - 格式化的HTML字符串
    """
    # 格式化数值
    if is_percentage:
        formatted_value = f"{value:.2f}%"
        display_prefix = ""
    else:
        formatted_value = f"{value:,.0f}"
        display_prefix = prefix

    # 设置进度条百分比
    progress_percentage = percentage if percentage is not None else 100

    # 分段构建HTML以确保安全性
    html = "<div class='metric-card'>"
    html += f"<p class='card-header'>{title}</p>"
    html += f"<p class='card-value'>{display_prefix}{formatted_value}</p>"
    html += "<div class='progress-bar'>"
    html += f"<div class='progress-value' style='width: {progress_percentage}%; background-color: {color};'></div>"
    html += "</div>"
    html += f"<p style='font-size: 0.9rem; color: #6c757d; margin-top: 10px;'>{description}</p>"
    html += "</div>"

    return html


def display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness):
    """
    显示关键绩效指标(KPI)卡片 - 优化版本

    参数:
    - total_material_cost: 总物料成本
    - total_sales: 总销售额
    - overall_cost_sales_ratio: 总体费比
    - avg_material_effectiveness: 平均物料效益
    """
    st.markdown("<h3 class='section-header'>关键绩效指标</h3>", unsafe_allow_html=True)

    # 创建四个并排的列
    kpi_cols = st.columns(4)

    # 为费比设置颜色
    fee_ratio_color = "#f5365c" if overall_cost_sales_ratio > 5 else "#fb6340" if overall_cost_sales_ratio > 3 else "#2dce89"
    fee_ratio_percentage = min(overall_cost_sales_ratio * 10, 100)

    # 第一列：总物料成本
    with kpi_cols[0]:
        st.markdown(
            create_kpi_card_html(
                "总物料成本",
                total_material_cost,
                "总投入物料资金",
                "#1f3867"
            ),
            unsafe_allow_html=True
        )

    # 第二列：总销售额
    with kpi_cols[1]:
        st.markdown(
            create_kpi_card_html(
                "总销售额",
                total_sales,
                "总体销售收入",
                "#2dce89"
            ),
            unsafe_allow_html=True
        )

    # 第三列：总体费比
    with kpi_cols[2]:
        st.markdown(
            create_kpi_card_html(
                "总体费比",
                overall_cost_sales_ratio,
                "物料成本占销售额比例",
                fee_ratio_color,
                fee_ratio_percentage,
                "",
                True
            ),
            unsafe_allow_html=True
        )

    # 第四列：平均物料效益
    with kpi_cols[3]:
        st.markdown(
            create_kpi_card_html(
                "平均物料效益",
                avg_material_effectiveness,
                "每单位物料平均产生销售额",
                "#11cdef"
            ),
            unsafe_allow_html=True
        )


def create_chart_container(chart_figure, title, description, tips, insight_text=None):
    """
    创建带有标题、描述和解释的图表容器 - 现代化设计
    (修改版：说明放在图表下方，优化布局)
    """
    # 创建一个设置了更好边距的容器
    st.markdown("<div style='margin-bottom: 40px; padding: 5px;'>", unsafe_allow_html=True)

    # 显示图表
    st.plotly_chart(chart_figure, use_container_width=True, config={
        "displayModeBar": True,
        "responsive": True,
        "displaylogo": False,  # 隐藏Plotly logo
        "modeBarButtonsToRemove": ['lasso2d', 'select2d']  # 移除不必要的按钮
    })

    # 显示解释和提示（放在图表下方）
    st.markdown(f"""
    <div style="background-color: #f8f9fe; border-radius: 10px; padding: 20px; margin-top: 15px; border: 1px solid #e2e8f0; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
            <div>
                <h5 style="color: #1f3867; font-size: 1.1rem; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; display: flex; align-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                    图表说明
                </h5>
                <p style="font-size: 0.95rem; margin-bottom: 0; color: #4a5568; line-height: 1.6;">{description}</p>
            </div>

            <div>
                <h5 style="color: #1f3867; font-size: 1.1rem; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; display: flex; align-items: center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    使用提示
                </h5>
                <ul style="padding-left: 20px; margin-bottom: 0; list-style-type: '→ ';">
    """, unsafe_allow_html=True)

    for tip in tips:
        st.markdown(f"""
        <li style="font-size: 0.9rem; margin-bottom: 8px; color: #4a5568; line-height: 1.5;">{tip}</li>
        """, unsafe_allow_html=True)

    st.markdown("</ul></div></div>", unsafe_allow_html=True)

    if insight_text:
        st.markdown(f"""
        <div style="margin-top: 15px; background-color: rgba(45, 206, 137, 0.1); border-left: 4px solid #2dce89; padding: 15px; border-radius: 8px;">
            <h6 style="margin: 0 0 10px 0; font-size: 1rem; color: #276749; display: flex; align-items: center;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                    <line x1="9" y1="9" x2="9.01" y2="9"></line>
                    <line x1="15" y1="9" x2="15.01" y2="9"></line>
                </svg>
                数据洞察
            </h6>
            <p style="margin: 0; font-size: 0.95rem; color: #2d3748; line-height: 1.6;">{insight_text}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # 添加额外的间距，确保图表之间不会重叠
    st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)


def calculate_fee_ratio(cost, sales):
    """
    安全计算费比，增强版
    """
    try:
        # 检查输入是否为空
        if sales is None or cost is None:
            return 0

        # 处理标量值
        if isinstance(sales, (int, float)) and isinstance(cost, (int, float)):
            # 避免除零错误
            if sales == 0:
                return 0

            # 处理负值情况
            if sales < 0 or cost < 0:
                if sales < 0 and cost < 0:
                    # 如果都是负的，取绝对值计算
                    return (abs(cost) / abs(sales)) * 100
                else:
                    # 单项负值，可能是数据错误
                    return 0

            # 计算费比并限制异常值
            ratio = (cost / sales) * 100
            return min(ratio, 1000)  # 限制最大值为1000%

        # 处理Series或DataFrame
        elif isinstance(sales, pd.Series) or isinstance(sales, pd.DataFrame):
            # 复制数据以避免修改原始数据
            temp_sales = sales.copy()
            temp_cost = cost.copy()

            # 处理销售额中的0值和负值
            if (temp_sales <= 0).any().any() if isinstance(temp_sales, pd.DataFrame) else (temp_sales <= 0).any():
                # 将≤0的值替换为NaN
                temp_sales = temp_sales.mask(temp_sales <= 0, np.nan)

            # 处理成本中的负值
            if (temp_cost < 0).any().any() if isinstance(temp_cost, pd.DataFrame) else (temp_cost < 0).any():
                # 将<0的值替换为NaN
                temp_cost = temp_cost.mask(temp_cost < 0, np.nan)

            # 计算费比
            result = (temp_cost / temp_sales) * 100

            # 限制异常值
            result = result.clip(upper=1000)  # 最大1000%

            # 用0填充NaN值
            result = result.fillna(0)

            return result
        else:
            return 0

    except Exception as e:
        # 记录错误但不中断程序
        print(f"计算费比时出错: {e}")
        return 0


def render_time_trend_tab(filtered_material, filtered_sales):
    """
    渲染时间趋势分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>时间趋势分析</h2>", unsafe_allow_html=True)

    # 确保数据中有发运月份列并且格式正确
    if '发运月份' not in filtered_material.columns or '发运月份' not in filtered_sales.columns:
        st.error("数据中缺少'发运月份'列，无法生成时间趋势分析。")
        return

    try:
        # 按月份聚合物料和销售数据
        material_monthly = filtered_material.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        sales_monthly = filtered_sales.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        monthly_data = pd.merge(material_monthly, sales_monthly, on='发运月份', how='outer')
        monthly_data = monthly_data.sort_values('发运月份')

        # 计算费比
        monthly_data['费比'] = calculate_fee_ratio(monthly_data['物料总成本'], monthly_data['销售总额'])

        # 计算物料效率
        monthly_data['物料效率'] = monthly_data['销售总额'] / monthly_data['物料数量'].where(
            monthly_data['物料数量'] > 0, np.nan)

        # 计算移动平均 (3个月)
        monthly_data['销售额_3MA'] = monthly_data['销售总额'].rolling(window=3, min_periods=1).mean()
        monthly_data['物料成本_3MA'] = monthly_data['物料总成本'].rolling(window=3, min_periods=1).mean()
        monthly_data['费比_3MA'] = monthly_data['费比'].rolling(window=3, min_periods=1).mean()

        # 格式化日期显示
        monthly_data['月份'] = monthly_data['发运月份'].dt.strftime('%Y-%m')

        # 1. 销售额和物料成本趋势图
        st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)

        if not monthly_data.empty:
            # 创建趋势图
            fig_trend = make_subplots(specs=[[{"secondary_y": True}]])

            # 添加销售额线
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_data['月份'],
                    y=monthly_data['销售总额'],
                    mode='lines+markers',
                    name='销售总额',
                    line=dict(color='#5e72e4', width=3),
                    marker=dict(size=8, symbol='circle', color='#5e72e4', line=dict(width=1, color='white')),
                    hovertemplate='月份: %{x}<br>销售总额: ￥%{y:,.0f}<br><extra></extra>'
                ),
                secondary_y=False
            )

            # 添加销售额移动平均线
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_data['月份'],
                    y=monthly_data['销售额_3MA'],
                    mode='lines',
                    name='销售额 (3月移动平均)',
                    line=dict(color='#5e72e4', width=1.5, dash='dot'),
                    hovertemplate='月份: %{x}<br>销售额 (3MA): ￥%{y:,.0f}<br><extra></extra>'
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
                    line=dict(color='#fb6340', width=3),
                    marker=dict(size=8, symbol='diamond', color='#fb6340', line=dict(width=1, color='white')),
                    hovertemplate='月份: %{x}<br>物料成本: ￥%{y:,.0f}<br><extra></extra>'
                ),
                secondary_y=True
            )

            # 添加物料成本移动平均线
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_data['月份'],
                    y=monthly_data['物料成本_3MA'],
                    mode='lines',
                    name='物料成本 (3月移动平均)',
                    line=dict(color='#fb6340', width=1.5, dash='dot'),
                    hovertemplate='月份: %{x}<br>物料成本 (3MA): ￥%{y:,.0f}<br><extra></extra>'
                ),
                secondary_y=True
            )

            # 配置图表布局
            fig_trend.update_layout(
                title='销售额与物料成本月度趋势',
                title_font=dict(size=18, color='#1f3867',
                                family="Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif"),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif"),
                height=500,
                margin=dict(l=60, r=60, t=80, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#e2e8f0',
                    borderwidth=1
                ),
                hovermode='x unified'
            )

            # 设置y轴
            fig_trend.update_yaxes(
                title_text="销售总额 (元)",
                secondary_y=False,
                tickprefix="￥",
                tickformat=",",
                gridcolor='#f4f4f4'
            )

            fig_trend.update_yaxes(
                title_text="物料成本 (元)",
                secondary_y=True,
                tickprefix="￥",
                tickformat=",",
                gridcolor='#f4f4f4'
            )

            # 设置x轴
            fig_trend.update_xaxes(
                title_text="月份",
                tickangle=-45,
                gridcolor='#f4f4f4'
            )

            # 显示图表
            create_chart_container(
                chart_figure=fig_trend,
                title="销售额与物料成本月度趋势",
                description="该图表展示了销售额与物料成本的月度变化趋势。主Y轴（左侧）显示销售总额，次Y轴（右侧）显示物料成本。",
                tips=[
                    "实线表示实际值，虚线表示3个月移动平均值",
                    "移动鼠标可查看每个月的具体数值",
                    "通过移动平均线可以更容易观察整体趋势",
                    "销售额与物料成本的增减变化应保持一定的比例关系"
                ],
                insight_text="留意销售额和物料成本线的变化幅度，若物料成本增长但销售额没有相应增长，需检查物料使用效率。"
            )
        else:
            st.warning("没有足够的数据来生成月度趋势图表。")

        st.markdown("</div>", unsafe_allow_html=True)

        # 2. 费比趋势图
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        if not monthly_data.empty:
            # 创建费比趋势图
            fig_fee_ratio = go.Figure()

            # 添加费比柱状图
            fig_fee_ratio.add_trace(
                go.Bar(
                    x=monthly_data['月份'],
                    y=monthly_data['费比'],
                    name='费比',
                    marker_color='#11cdef',
                    hovertemplate='月份: %{x}<br>费比: %{y:.2f}%<br><extra></extra>'
                )
            )

            # 添加费比移动平均线
            fig_fee_ratio.add_trace(
                go.Scatter(
                    x=monthly_data['月份'],
                    y=monthly_data['费比_3MA'],
                    mode='lines+markers',
                    name='费比 (3月移动平均)',
                    line=dict(color='#f5365c', width=3),
                    marker=dict(size=8, symbol='circle', color='#f5365c', line=dict(width=1, color='white')),
                    hovertemplate='月份: %{x}<br>费比 (3MA): %{y:.2f}%<br><extra></extra>'
                )
            )

            # 添加参考线 - 平均费比
            avg_fee_ratio = monthly_data['费比'].mean()
            fig_fee_ratio.add_shape(
                type='line',
                x0=0,
                y0=avg_fee_ratio,
                x1=len(monthly_data['月份']) - 1,
                y1=avg_fee_ratio,
                line=dict(
                    color='#2dce89',
                    width=2,
                    dash='dash',
                ),
                xref='x',
                yref='y'
            )

            # 添加平均费比标签
            fig_fee_ratio.add_annotation(
                x=monthly_data['月份'].iloc[-1],
                y=avg_fee_ratio,
                text=f"平均费比: {avg_fee_ratio:.2f}%",
                showarrow=True,
                arrowhead=1,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor='#2dce89',
                ax=-50,
                ay=-30,
                font=dict(
                    size=12,
                    color='#2dce89'
                ),
                bgcolor='white',
                bordercolor='#2dce89',
                borderwidth=1,
                borderpad=4
            )

            # 配置图表布局
            fig_fee_ratio.update_layout(
                title='月度费比变化趋势',
                title_font=dict(size=18, color='#1f3867',
                                family="Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif"),
                plot_bgcolor='white',
                paper_bgcolor='white',
                font=dict(family="Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif"),
                height=500,
                margin=dict(l=60, r=60, t=80, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    bgcolor='rgba(255,255,255,0.9)',
                    bordercolor='#e2e8f0',
                    borderwidth=1
                ),
                hovermode='x'
            )

            # 设置y轴
            fig_fee_ratio.update_yaxes(
                title_text="费比 (%)",
                ticksuffix="%",
                gridcolor='#f4f4f4',
                zeroline=True,
                zerolinecolor='#e0e0e0',
                zerolinewidth=1
            )

            # 设置x轴
            fig_fee_ratio.update_xaxes(
                title_text="月份",
                tickangle=-45,
                gridcolor='#f4f4f4'
            )

            # 显示图表
            create_chart_container(
                chart_figure=fig_fee_ratio,
                title="月度费比变化趋势",
                description="该图表展示了每月费比的变化情况。柱状图表示实际费比，红线表示3个月移动平均，绿色虚线表示平均费比基准线。",
                tips=[
                    "费比 = (物料成本 ÷ 销售总额) × 100%",
                    "费比越低越好，表示物料使用效率越高",
                    "留意费比高于平均线的月份，分析原因",
                    "关注费比的整体趋势是上升还是下降"
                ],
                insight_text="费比的波动反映物料使用效率的变化，若连续3个月费比上升，应及时检查物料投放策略是否需要调整。"
            )
        else:
            st.warning("没有足够的数据来生成费比趋势图表。")

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"生成时间趋势分析时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
@chart_error_handler
def create_material_effectiveness_chart(effectiveness_data):
    """
    创建物料投放效果评估散点图

    参数:
    - effectiveness_data: 包含物料数量和销售额的数据框

    返回:
    - Plotly散点图对象, r值, 斜率
    """
    # 数据验证
    if effectiveness_data is None or effectiveness_data.empty:
        raise ValueError("无效的数据: 数据为空或不存在")

    required_cols = ['物料数量', '销售总额', '物料总成本', '物料效益', '经销商名称', '发运月份']
    missing_cols = [col for col in required_cols if col not in effectiveness_data.columns]

    if missing_cols:
        raise ValueError(f"数据缺少必要列: {', '.join(missing_cols)}")

    # 创建物料投放效果散点图
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
        opacity=0.85,
        size_max=50,
        range_color=[
            effectiveness_data['物料效益'].quantile(0.05),
            effectiveness_data['物料效益'].quantile(0.95)
        ]
    )

    # 增强悬停信息
    fig_material_effectiveness_chart.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>' +
                      '物料数量: <b>%{x:,}件</b><br>' +
                      '销售总额: <b>￥%{y:,.0f}</b><br>' +
                      '物料成本: <b>￥%{marker.size:,.0f}</b><br>' +
                      '物料效益: <b>￥%{marker.color:.2f}/件</b><br>' +
                      '月份: <b>%{customdata}</b>' +
                      '<extra></extra>',
        customdata=effectiveness_data['发运月份'].dt.strftime('%Y-%m').values,
        marker=dict(
            line=dict(width=1, color='white')
        )
    )

    # 计算线性回归趋势线
    try:
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

        # 添加趋势线
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

        # 添加相关性说明文本
        fig_material_effectiveness_chart.add_annotation(
            x=effectiveness_data['物料数量'].max() * 0.85,
            y=effectiveness_data['销售总额'].min() + (
                    effectiveness_data['销售总额'].max() - effectiveness_data['销售总额'].min()) * 0.1,
            text=f"相关系数: r² = {r_value ** 2:.2f}<br>每增加1件物料<br>平均增加 ￥{slope:.2f} 销售额",
            showarrow=True,
            arrowhead=1,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor='rgba(255, 99, 132, 0.8)',
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(255, 99, 132, 0.8)',
            borderwidth=1,
            borderpad=4,
            font=dict(size=12, color='#333333')
        )
    except Exception as e:
        print(f"计算线性回归时出错: {e}")
        # 不阻止函数继续执行，但设置默认值
        r_value = 0
        slope = 0

    # 配置图表布局
    fig_material_effectiveness_chart = configure_plotly_chart(
        fig_material_effectiveness_chart,
        title="物料投放量与销售额关系",
        height=700
    )

    # 增强图表可视化效果
    fig_material_effectiveness_chart.update_layout(
        xaxis=dict(
            title=dict(text='物料数量 (件)', font=dict(size=14)),
            tickformat=',d',
            zeroline=True,
            zerolinecolor='#e0e0e0',
            zerolinewidth=1
        ),
        yaxis=dict(
            title=dict(text='销售总额 (元)', font=dict(size=14)),
            tickprefix='￥',
            tickformat=',.0f',
            zeroline=True,
            zerolinecolor='#e0e0e0',
            zerolinewidth=1
        ),
        coloraxis_colorbar=dict(
            title="物料效益<br>(元/件)",
            tickprefix="￥",
            len=0.8
        )
    )

    return fig_material_effectiveness_chart, r_value, slope


def add_loading_state(message="数据处理中..."):
    """
    添加加载状态指示器

    参数:
    - message: 加载时显示的消息
    """
    with st.spinner(message):
        # 返回一个上下文管理器占位符
        return st.empty()


# 使用示例
# with add_loading_state("正在分析数据..."):
#     result = complex_calculation()
#     st.success("分析完成！")
def display_fee_ratio_anomalies(anomalies, overall_cost_sales_ratio):
    """
    显示费比异常警告卡片

    参数:
    - anomalies: 包含费比异常的数据框
    - overall_cost_sales_ratio: 总体费比
    """
    if len(anomalies) > 0:
        # 显示警告标题
        st.markdown(f"""
        <div style='background-color: rgba(245, 54, 92, 0.05); border-radius: 10px; border-left: 5px solid #f5365c; padding: 20px; margin-bottom: 20px;'>
            <h5 style='color: #f5365c; font-weight: 600; display: flex; align-items: center; margin-top: 0;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#f5365c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="8" x2="12" y2="12"></line>
                    <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
                费比异常警告 ({len(anomalies)}个)
            </h5>
        </div>
        """, unsafe_allow_html=True)

        # 使用列布局展示异常卡片
        anomaly_cols = st.columns(3)

        for i, (_, row) in enumerate(anomalies.iterrows()):
            # 计算异常程度
            anomaly_level = row['费比'] / overall_cost_sales_ratio

            # 根据异常程度设置不同颜色
            if anomaly_level > 2:
                card_color = "#FDE8E8"  # 严重异常 - 红色背景
                border_color = "#F56565"
                text_color = "#C53030"
            else:
                card_color = "#FEFCBF"  # 中等异常 - 黄色背景
                border_color = "#ECC94B"
                text_color = "#B7791F"

            with anomaly_cols[i % 3]:
                # 为每张卡片单独创建安全的HTML
                card_html = f"""
                <div style='border-radius: 10px; border: 1px solid {border_color}; padding: 15px; margin-bottom: 15px; background-color: {card_color};'>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                        <h6 style='margin: 0; color: {text_color};'>{row['经销商名称']}</h6>
                        <span style='font-size: 0.8rem; color: {text_color}; background-color: rgba(0,0,0,0.05); padding: 3px 8px; border-radius: 50px;'>
                            {anomaly_level:.1f}倍
                        </span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                        <span style='font-weight: 500;'>费比:</span>
                        <span style='font-weight: 600; color: {text_color};'>{row['费比']:.2f}%</span>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                        <span style='font-weight: 500;'>物料成本:</span>
                        <span>￥{row['物料总成本']:,.0f}</span>
                    </div>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='font-weight: 500;'>销售额:</span>
                        <span>￥{row['销售总额']:,.0f}</span>
                    </div>
                    <div style='height: 4px; background-color: rgba(0,0,0,0.05); border-radius: 2px; margin-top: 12px;'>
                        <div style='height: 100%; width: {min(anomaly_level / 3 * 100, 100)}%; background-color: {text_color}; border-radius: 2px;'></div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

        # 添加总结和建议
        st.markdown("""
        <div style='border-radius: 10px; border: 1px solid #63B3ED; padding: 20px; margin-top: 25px; background-color: rgba(66, 153, 225, 0.05);'>
            <h5 style='margin-top: 0; color: #3182CE; display: flex; align-items: center;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3182CE" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                费比异常分析总结
            </h5>
        """, unsafe_allow_html=True)

        st.markdown(
            f"<p>共发现<strong>{len(anomalies)}个</strong>费比异常经销商。平均费比为<strong>{overall_cost_sales_ratio:.2f}%</strong>，但这些经销商的费比远高于平均值。</p>",
            unsafe_allow_html=True)

        st.markdown("""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
                <div>
                    <h6 style='margin-top: 0; color: #3182CE;'>可能的原因:</h6>
                    <ul style='margin-top: 10px; padding-left: 20px;'>
                        <li>物料使用效率低，未转化为有效销售</li>
                        <li>销售策略不当，导致投入产出比不佳</li>
                        <li>物料分配不合理，未针对客户需求定制</li>
                        <li>销售人员未正确使用物料或未进行有效促销</li>
                    </ul>
                </div>

                <div>
                    <h6 style='margin-top: 0; color: #3182CE;'>建议行动:</h6>
                    <ul style='margin-top: 10px; padding-left: 20px;'>
                        <li>与这些经销商沟通，了解物料使用情况</li>
                        <li>提供针对性培训，提高物料使用效率</li>
                        <li>调整物料分配策略，减少费比异常高的经销商的物料投入</li>
                        <li>建立物料使用监控机制，定期评估效果</li>
                    </ul>
                </div>
            </div>

            <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #E2E8F0;'>
                <h6 style='margin-top: 0; color: #3182CE;'>优先处理建议:</h6>
                <p>根据异常程度和销售额，建议优先关注上述卡片中深红色背景的经销商，其费比超过平均水平2倍以上，改进空间最大。</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 返回正面信息卡片
        st.markdown(f"""
        <div style='border-radius: 10px; border: 1px solid #c3e6cb; padding: 20px; margin-bottom: 20px; background-color: rgba(72, 187, 120, 0.05);'>
            <h5 style='color: #276749; font-weight: 600; display: flex; align-items: center; margin-top: 0;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#276749" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px;">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
                良好费比控制
            </h5>
        """, unsafe_allow_html=True)

        st.markdown("<p>恭喜! 未发现费比异常值。所有经销商的费比都在平均值的1.5倍范围内，表明物料使用效率整体良好。</p>",
                    unsafe_allow_html=True)

        st.markdown(
            f"<p>当前平均费比为 <strong>{overall_cost_sales_ratio:.2f}%</strong>，继续保持这一水平将有利于提高整体投资回报率。</p>",
            unsafe_allow_html=True)

        st.markdown("""
            <div style='background-color: rgba(72, 187, 120, 0.1); border-radius: 8px; padding: 12px; margin-top: 15px;'>
                <h6 style='margin-top: 0; color: #276749;'>建议行动:</h6>
                <ul style='margin-top: 10px; margin-bottom: 0; padding-left: 20px;'>
                    <li>分享优秀经销商的物料使用经验</li>
                    <li>继续监控费比变化趋势，及时发现潜在问题</li>
                    <li>探索进一步优化物料投放策略的机会</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)


def add_chart_explanation(title, description, tips, insight_text=None):
    """
    添加标准化的图表解释框

    参数:
    - title: 解释框标题
    - description: 图表描述文本
    - tips: 使用提示列表
    - insight_text: 可选的数据洞察文本
    """
    # 开始HTML容器
    st.markdown("""
    <div class='explanation'>
        <h6>{0}</h6>
    """.format(title), unsafe_allow_html=True)

    # 添加描述
    st.markdown(f"<p>{description}</p>", unsafe_allow_html=True)

    # 添加提示开头
    st.markdown("<div><strong>使用提示:</strong><ul>", unsafe_allow_html=True)

    # 添加每个提示项
    for tip in tips:
        st.markdown(f"<li>{tip}</li>", unsafe_allow_html=True)

    # 关闭提示列表
    st.markdown("</ul></div>", unsafe_allow_html=True)

    # 添加洞察文本（如果有）
    if insight_text:
        st.markdown("""
        <div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e2e8f0;'>
            <strong>数据洞察:</strong>
        """, unsafe_allow_html=True)

        st.markdown(f"<p style='margin-bottom: 0;'>{insight_text}</p>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 关闭HTML容器
    st.markdown("</div>", unsafe_allow_html=True)


def display_optimal_material_allocation(material_roi, filtered_material, filtered_sales):
    """
    显示最优物料分配建议

    参数:
    - material_roi: 物料ROI数据
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    if not material_roi.empty:
        # 分析高效和低效物料
        high_roi_materials = material_roi.sort_values('ROI', ascending=False).head(5)
        low_roi_materials = material_roi.sort_values('ROI').head(5)

        # 计算整体ROI
        total_material_cost = filtered_material['物料总成本'].sum()
        total_sales = filtered_sales['销售总额'].sum()
        overall_roi = total_sales / total_material_cost if total_material_cost > 0 else 0

        # 显示物料投入现状分析卡片
        roi_color = "#48BB78" if overall_roi >= 5 else "#ECC94B" if overall_roi >= 3 else "#F56565"
        roi_width = min(int(overall_roi * 10), 100)

        st.markdown("""
        <div style='border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E2E8F0; padding: 20px; margin-bottom: 25px; background-color: white;'>
            <h5 style='margin-top: 0; font-weight: 600; color: #2D3748; display: flex; align-items: center;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 10px; color: #4299E1;">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
                物料投入现状分析
            </h5>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='display: flex; align-items: center; margin: 20px 0;'>
                <div style='min-width: 150px;'>
                    <span style='font-size: 0.9rem; color: #718096;'>当前整体ROI</span>
                    <div style='font-size: 2rem; font-weight: 700; color: #2D3748;'>{overall_roi:.2f}</div>
                </div>
                <div style='flex-grow: 1; margin-left: 20px;'>
                    <div style='height: 10px; background-color: #EDF2F7; border-radius: 5px; position: relative;'>
                        <div style='position: absolute; height: 100%; width: {roi_width}%; background-color: {roi_color}; border-radius: 5px;'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-top: 5px;'>
                        <span style='font-size: 0.8rem; color: #F56565;'>低效 (<3)</span>
                        <span style='font-size: 0.8rem; color: #ECC94B;'>中等 (3-5)</span>
                        <span style='font-size: 0.8rem; color: #48BB78;'>高效 (>5)</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style='display: flex; justify-content: space-between; margin: 15px 0; background-color: #F7FAFC; padding: 15px; border-radius: 8px;'>
                <div>
                    <span style='font-size: 0.85rem; color: #718096;'>总销售额</span>
                    <div style='font-size: 1.4rem; font-weight: 600; color: #48BB78;'>￥{total_sales:,.0f}</div>
                </div>
                <div style='text-align: center;'>
                    <span style='font-size: 0.85rem; color: #718096;'>投入产出比</span>
                    <div style='font-size: 1.4rem; font-weight: 600; color: #4299E1;'>1:{overall_roi:.2f}</div>
                </div>
                <div style='text-align: right;'>
                    <span style='font-size: 0.85rem; color: #718096;'>总物料成本</span>
                    <div style='font-size: 1.4rem; font-weight: 600; color: #F56565;'>￥{total_material_cost:,.0f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style='background-color: #FFFAF0; border-left: 4px solid #F6AD55; padding: 12px 15px; border-radius: 4px;'>
                <p style='margin: 0; font-size: 0.95rem;'>通过优化物料分配，预估可将整体ROI提高15-20%，直接提升销售业绩。建议分析下方高ROI与低ROI物料差异，调整投放策略。</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 使用列布局显示高ROI和低ROI物料
        roi_cols = st.columns(2)

        # 高ROI物料卡片
        with roi_cols[0]:
            st.markdown("""
            <h5 style='color: #276749; font-weight: 600; display: flex; align-items: center;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; color: #48BB78;">
                    <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                    <polyline points="17 6 23 6 23 12"></polyline>
                </svg>
                高ROI物料 (建议增加投放)
            </h5>
            """, unsafe_allow_html=True)

            for i, (_, row) in enumerate(high_roi_materials.iterrows()):
                roi_percentage = int(min(row['ROI'] / overall_roi * 100, 200))
                st.markdown(f"""
                <div style='border-radius: 8px; border-left: 4px solid #48BB78; padding: 12px; margin-bottom: 12px; background-color: rgba(72, 187, 120, 0.05);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h6 style='margin: 0; font-weight: 600;'>{row['物料名称']}</h6>
                        <span style='font-size: 0.85rem; background-color: rgba(72, 187, 120, 0.1); color: #276749; padding: 3px 8px; border-radius: 50px;'>
                            ROI: <strong>{row['ROI']:.2f}</strong>
                        </span>
                    </div>

                    <div style='margin: 12px 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>物料成本</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>￥{row['物料总成本']:,.0f}</div>
                        </div>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>销售额</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>￥{row['销售总额']:,.0f}</div>
                        </div>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>数量</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>{row['物料数量']:,}件</div>
                        </div>
                    </div>

                    <div style='margin-top: 10px;'>
                        <div style='font-size: 0.8rem; color: #718096; margin-bottom: 4px; display: flex; justify-content: space-between;'>
                            <span>平均ROI表现</span>
                            <span>+{roi_percentage - 100}%</span>
                        </div>
                        <div style='height: 8px; background-color: #E2E8F0; border-radius: 4px;'>
                            <div style='height: 100%; width: {roi_percentage}%; background-color: #48BB78; border-radius: 4px;'></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 低ROI物料卡片
        with roi_cols[1]:
            st.markdown("""
            <h5 style='color: #9B2C2C; font-weight: 600; display: flex; align-items: center;'>
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; color: #F56565;">
                    <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                    <polyline points="17 18 23 18 23 12"></polyline>
                </svg>
                低ROI物料 (建议减少或优化投放)
            </h5>
            """, unsafe_allow_html=True)

            for i, (_, row) in enumerate(low_roi_materials.iterrows()):
                roi_percentage = int(min(row['ROI'] / overall_roi * 100, 100))
                st.markdown(f"""
                <div style='border-radius: 8px; border-left: 4px solid #F56565; padding: 12px; margin-bottom: 12px; background-color: rgba(245, 101, 101, 0.05);'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <h6 style='margin: 0; font-weight: 600;'>{row['物料名称']}</h6>
                        <span style='font-size: 0.85rem; background-color: rgba(245, 101, 101, 0.1); color: #9B2C2C; padding: 3px 8px; border-radius: 50px;'>
                            ROI: <strong>{row['ROI']:.2f}</strong>
                        </span>
                    </div>

                    <div style='margin: 12px 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>物料成本</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>￥{row['物料总成本']:,.0f}</div>
                        </div>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>销售额</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>￥{row['销售总额']:,.0f}</div>
                        </div>
                        <div style='text-align: center; background-color: white; padding: 8px 5px; border-radius: 6px;'>
                            <div style='font-size: 0.8rem; color: #718096;'>数量</div>
                            <div style='font-size: 1rem; font-weight: 600; color: #4A5568;'>{row['物料数量']:,}件</div>
                        </div>
                    </div>

                    <div style='margin-top: 10px;'>
                        <div style='font-size: 0.8rem; color: #718096; margin-bottom: 4px; display: flex; justify-content: space-between;'>
                            <span>平均ROI表现</span>
                            <span>{roi_percentage - 100}%</span>
                        </div>
                        <div style='height: 8px; background-color: #E2E8F0; border-radius: 4px;'>
                            <div style='height: 100%; width: {roi_percentage}%; background-color: #F56565; border-radius: 4px;'></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 添加优化建议总结
        st.markdown("""
        <div style='border-radius: 10px; border: 1px solid #63B3ED; padding: 20px; margin-top: 25px; background-color: rgba(66, 153, 225, 0.05);'>
            <h5 style='margin-top: 0; color: #3182CE; font-weight: 600;'>物料投入优化策略</h5>

            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 15px;'>
                <div style='background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
                    <h6 style='color: #3182CE; margin-top: 0; font-weight: 600; display: flex; align-items: center;'>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; color: #3182CE;">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="16"></line>
                            <line x1="8" y1="12" x2="16" y2="12"></line>
                        </svg>
                        增加投入
                    </h6>
                    <ul style='padding-left: 20px; margin-bottom: 0;'>
                        <li>对高ROI物料增加15-20%的预算</li>
                        <li>优先考虑ROI超过平均值50%以上的物料</li>
                        <li>针对最畅销产品定制高效物料</li>
                        <li>与优秀经销商合作开发新物料</li>
                    </ul>
                </div>

                <div style='background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
                    <h6 style='color: #E53E3E; margin-top: 0; font-weight: 600; display: flex; align-items: center;'>
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; color: #E53E3E;">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="8" y1="12" x2="16" y2="12"></line>
                        </svg>
                        减少投入
                    </h6>
                    <ul style='padding-left: 20px; margin-bottom: 0;'>
                        <li>逐步减少低ROI物料的预算(10-15%)</li>
                        <li>检查ROI低于平均值40%以下的物料</li>
                        <li>优化或重新设计低效物料</li>
                        <li>停止投放长期表现不佳的物料</li>
                    </ul>
                </div>
            </div>

            <div style='margin-top: 20px; background-color: white; border-radius: 8px; padding: 15px; box-shadow: 0 2px 6px rgba(0,0,0,0.05);'>
                <h6 style='color: #38A169; margin-top: 0; font-weight: 600; display: flex; align-items: center;'>
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px; color: #38A169;">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    预期效果
                </h6>
                <p style='margin-bottom: 0.5rem;'>通过上述策略调整，预计可实现:</p>
                <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>
                    <div style='text-align: center; background-color: #F7FAFC; padding: 10px; border-radius: 6px;'>
                        <div style='font-size: 0.9rem; color: #718096;'>ROI提升</div>
                        <div style='font-size: 1.2rem; font-weight: 600; color: #38A169;'>+15-20%</div>
                    </div>
                    <div style='text-align: center; background-color: #F7FAFC; padding: 10px; border-radius: 6px;'>
                        <div style='font-size: 0.9rem; color: #718096;'>物料使用效率</div>
                        <div style='font-size: 1.2rem; font-weight: 600; color: #38A169;'>+25%</div>
                    </div>
                    <div style='text-align: center; background-color: #F7FAFC; padding: 10px; border-radius: 6px;'>
                        <div style='font-size: 0.9rem; color: #718096;'>费比改善</div>
                        <div style='font-size: 1.2rem; font-weight: 600; color: #38A169;'>-10%</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 数据不足时的提示
        st.warning("数据不足，无法生成最优物料分配建议。请尝试减少筛选条件或检查数据完整性。")


def create_region_cost_sales_analysis(region_cost_sales):
    """
    创建区域费比分析图表 - 优化版

    参数:
    - region_cost_sales: 包含区域销售额和物料成本的数据框

    返回:
    - Plotly气泡图对象
    """
    # 创建区域费比分析气泡图
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
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    # 增强悬停信息
    fig_region_cost_sales_analysis.update_traces(
        textposition='top center',
        hovertemplate='<b>%{text}区域</b><br>' +
                      '销售贡献: <b>%{x:.2f}%</b><br>' +
                      '费比: <b>%{y:.2f}%</b><br>' +
                      '物料成本: <b>￥%{customdata[0]:,.0f}</b><br>' +
                      '销售总额: <b>￥%{customdata[1]:,.0f}</b><br>' +
                      '<extra></extra>',
        customdata=region_cost_sales[['物料总成本', '销售总额']].values,
        marker=dict(
            opacity=0.85,
            line=dict(width=1, color='white')
        )
    )

    # 计算平均费比
    avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales['销售总额'].sum()) * 100 if \
        region_cost_sales['销售总额'].sum() > 0 else 0

    # 添加平均费比参考线
    fig_region_cost_sales_analysis.add_hline(
        y=avg_cost_sales_ratio,
        line_dash="dash",
        line_color="#ff5a36",
        line_width=2,
        annotation=dict(
            text=f"平均费比: {avg_cost_sales_ratio:.2f}%",
            font=dict(size=14, color="#ff5a36", family="Source Sans Pro, PingFang SC, Microsoft YaHei, sans-serif"),
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

    # 添加象限背景
    max_x = region_cost_sales['销售额百分比'].max() * 1.1 if not region_cost_sales.empty else 100
    max_y = max(region_cost_sales['费比'].max() * 1.1, avg_cost_sales_ratio * 2) if not region_cost_sales.empty else 100

    # 添加低费比区域背景色
    fig_region_cost_sales_analysis.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=max_x,
        y1=avg_cost_sales_ratio,
        fillcolor="rgba(45, 206, 137, 0.15)",
        line=dict(width=0),
        layer="below"
    )

    # 添加高费比区域背景色
    fig_region_cost_sales_analysis.add_shape(
        type="rect",
        x0=0,
        y0=avg_cost_sales_ratio,
        x1=max_x,
        y1=max_y,
        fillcolor="rgba(245, 54, 92, 0.15)",
        line=dict(width=0),
        layer="below"
    )

    # 添加象限标注 - 低费比区域
    fig_region_cost_sales_analysis.add_annotation(
        x=max_x * 0.2,
        y=avg_cost_sales_ratio * 0.5,
        text="低费比区域<br>(理想状态)",
        showarrow=False,
        font=dict(size=12, color="#2dce89"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#2dce89",
        borderwidth=1,
        borderpad=4
    )

    # 添加象限标注 - 高费比区域
    fig_region_cost_sales_analysis.add_annotation(
        x=max_x * 0.2,
        y=min(avg_cost_sales_ratio * 1.5, max_y * 0.8),
        text="高费比区域<br>(需改进)",
        showarrow=False,
        font=dict(size=12, color="#f5365c"),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#f5365c",
        borderwidth=1,
        borderpad=4
    )

    # 配置图表布局
    fig_region_cost_sales_analysis = configure_plotly_chart(
        fig_region_cost_sales_analysis,
        title="区域费比分析",
        height=600
    )

    # 增强图表可视化效果
    fig_region_cost_sales_analysis.update_layout(
        xaxis=dict(
            title=dict(text='销售贡献度 (%)', font=dict(size=14)),
            ticksuffix="%",
            zeroline=True,
            zerolinecolor='#e0e0e0',
            zerolinewidth=1,
            tickfont=dict(size=12),
            range=[0, max_x]
        ),
        yaxis=dict(
            title=dict(text='费比 (%)', font=dict(size=14)),
            ticksuffix="%",
            zeroline=True,
            zerolinecolor='#e0e0e0',
            zerolinewidth=1,
            tickfont=dict(size=12),
            range=[0, max_y]
        ),
        margin=dict(l=60, r=60, t=80, b=60)
    )

    return fig_region_cost_sales_analysis


# 创建聚合数据和计算指标
@st.cache_data(ttl=3600)
def create_aggregations(df_material, df_sales):
    """
    创建聚合数据和计算指标

    参数:
    - df_material: 物料数据DataFrame
    - df_sales: 销售数据DataFrame

    返回:
    - 包含各种聚合指标的字典
    """
    try:
        # 验证输入数据
        if df_material is None or df_sales is None:
            st.error("无法创建聚合数据：输入数据为空")
            return None

        # 验证必要的列是否存在
        required_material_cols = ['所属区域', '省份', '城市', '客户代码', '经销商名称', '物料代码', '物料名称',
                                  '物料数量', '物料总成本', '发运月份']
        required_sales_cols = ['所属区域', '省份', '城市', '客户代码', '经销商名称', '销售总额', '求和项:数量（箱）',
                               '发运月份']

        missing_material_cols = [col for col in required_material_cols if col not in df_material.columns]
        missing_sales_cols = [col for col in required_sales_cols if col not in df_sales.columns]

        if missing_material_cols or missing_sales_cols:
            error_msg = "数据列缺失: "
            if missing_material_cols:
                error_msg += f"物料数据缺少 {', '.join(missing_material_cols)}. "
            if missing_sales_cols:
                error_msg += f"销售数据缺少 {', '.join(missing_sales_cols)}."
            st.error(error_msg)
            return None

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
        region_metrics['费比'] = calculate_fee_ratio(region_metrics['物料总成本'], region_metrics['销售总额'])
        region_metrics['物料单位效益'] = np.where(
            region_metrics['物料数量'] > 0,
            region_metrics['销售总额'] / region_metrics['物料数量'],
            0
        )

        # 合并省份数据计算费比
        province_metrics = pd.merge(material_by_province, sales_by_province, on='省份', how='outer')
        province_metrics['费比'] = calculate_fee_ratio(province_metrics['物料总成本'], province_metrics['销售总额'])
        province_metrics['物料单位效益'] = np.where(
            province_metrics['物料数量'] > 0,
            province_metrics['销售总额'] / province_metrics['物料数量'],
            0
        )

        # 合并客户数据计算费比
        customer_metrics = pd.merge(material_by_customer, sales_by_customer, on=['客户代码', '经销商名称'], how='outer')
        customer_metrics['费比'] = calculate_fee_ratio(customer_metrics['物料总成本'], customer_metrics['销售总额'])
        customer_metrics['物料单位效益'] = np.where(
            customer_metrics['物料数量'] > 0,
            customer_metrics['销售总额'] / customer_metrics['物料数量'],
            0
        )

        # 合并时间数据计算费比
        time_metrics = pd.merge(material_by_time, sales_by_time, on='发运月份', how='outer')
        time_metrics['费比'] = calculate_fee_ratio(time_metrics['物料总成本'], time_metrics['销售总额'])
        time_metrics['物料单位效益'] = np.where(
            time_metrics['物料数量'] > 0,
            time_metrics['销售总额'] / time_metrics['物料数量'],
            0
        )

        # 按销售人员聚合
        salesperson_metrics = pd.merge(
            df_material.groupby('申请人').agg({'物料总成本': 'sum'}),
            df_sales.groupby('申请人').agg({'销售总额': 'sum'}),
            on='申请人'
        )
        salesperson_metrics['费比'] = calculate_fee_ratio(salesperson_metrics['物料总成本'],
                                                          salesperson_metrics['销售总额'])
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

        material_product_corr['关联强度'] = np.where(
            material_product_corr['物料数量'] > 0,
            material_product_corr['销售总额'] / material_product_corr['物料数量'],
            0
        )

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

    except Exception as e:
        st.error(f"创建聚合数据时出错: {str(e)}")
        # 记录详细错误信息到日志
        import traceback
        print(f"聚合数据错误详情: {traceback.format_exc()}")
        return None


def render_customer_value_tab(filtered_material, filtered_sales):
    """
    渲染客户价值分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>客户价值分析</h2>", unsafe_allow_html=True)

    # 计算客户价值指标
    if 'customer_value' not in st.session_state:
        # 合并客户的物料和销售数据
        customer_material = filtered_material.groupby(['客户代码', '经销商名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        customer_sales = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
            '求和项:数量（箱）': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        customer_value = pd.merge(customer_material, customer_sales, on=['客户代码', '经销商名称'], how='outer')

        # 计算客户价值指标
        customer_value['费比'] = calculate_fee_ratio(customer_value['物料总成本'], customer_value['销售总额'])
        customer_value['物料效率'] = customer_value['销售总额'] / customer_value['物料数量'].where(
            customer_value['物料数量'] > 0, np.nan)
        customer_value['客户价值'] = customer_value['销售总额'] - customer_value['物料总成本']

        # 计算百分比和排名
        total_sales = customer_value['销售总额'].sum() if not customer_value.empty else 0
        customer_value['销售贡献比例'] = (customer_value['销售总额'] / total_sales * 100) if total_sales > 0 else 0
        customer_value['价值排名'] = customer_value['客户价值'].rank(ascending=False, method='min')

        st.session_state.customer_value = customer_value
    else:
        customer_value = st.session_state.customer_value

    # 创建选项卡
    value_subtabs = st.tabs([
        "客户价值分布",
        "客户分群分析",
        "潜力客户识别",
        "客户详情表"
    ])

    # 客户价值分布选项卡
    with value_subtabs[0]:
        if not customer_value.empty:
            # 创建客户价值分布图
            try:
                customer_value_sorted = customer_value.sort_values('客户价值', ascending=False)
                customer_value_sorted = customer_value_sorted.head(20)  # 取前20名客户

                fig_customer_value = px.bar(
                    customer_value_sorted,
                    x='经销商名称',
                    y='客户价值',
                    color='费比',
                    labels={'经销商名称': '经销商', '客户价值': '客户价值 (元)', '费比': '费比 (%)'},
                    title="客户价值分布 (前20名)",
                    color_continuous_scale='RdYlGn_r',
                    text='客户价值'
                )

                fig_customer_value.update_traces(
                    texttemplate='￥%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '客户价值: <b>￥%{y:,.0f}</b><br>' +
                                  '费比: <b>%{marker.color:.2f}%</b><br>' +
                                  '<extra></extra>'
                )

                fig_customer_value.update_layout(
                    xaxis=dict(tickangle=-45),
                    yaxis=dict(title='客户价值 (元)', tickprefix='￥', tickformat=','),
                    coloraxis_colorbar=dict(title='费比 (%)')
                )

                # 配置图表
                fig_customer_value = configure_plotly_chart(
                    fig_customer_value,
                    title="客户价值分布 (前20名)",
                    height=550
                )

                create_chart_container(
                    chart_figure=fig_customer_value,
                    title="客户价值分布",
                    description="该图表展示了贡献最大价值的前20名客户。柱状高度表示客户价值(销售额减去物料成本)，颜色表示费比(费比越低越好)。",
                    tips=[
                        "客户价值 = 销售总额 - 物料总成本",
                        "颜色越绿表示费比越低，即投入产出比越高",
                        "高价值但高费比的客户(红色柱)有优化空间",
                        "重点关注左侧高价值客户，优化其物料投放策略"
                    ],
                    insight_text="前5名客户贡献了大部分价值，但部分高价值客户费比较高，有改进空间。"
                )

            except Exception as e:
                st.error(f"生成客户价值分布图表时出错: {str(e)}")
        else:
            st.warning("没有足够的数据来生成客户价值分布图表。")

    # 客户分群分析选项卡
    with value_subtabs[1]:
        if not customer_value.empty:
            try:
                # 添加RFM得分(这里用销售额代替频率和近度)
                customer_value['价值得分'] = pd.qcut(customer_value['客户价值'], q=4, labels=[1, 2, 3, 4]).astype(int)
                customer_value['效率得分'] = pd.qcut(customer_value['物料效率'].fillna(0), q=4,
                                                     labels=[1, 2, 3, 4]).astype(int)

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

                # 计算每个分群的统计数据
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

                # 计算每个分群的占比
                total_customers = group_stats['客户数量'].sum()
                group_stats['客户占比'] = group_stats['客户数量'] / total_customers * 100
                group_stats['价值占比'] = group_stats['客户价值总和'] / group_stats['客户价值总和'].sum() * 100

                # 创建分群散点图
                fig_segments = px.scatter(
                    customer_value,
                    x='客户价值',
                    y='物料效率',
                    color='客户分群',
                    size='销售总额',
                    hover_name='经销商名称',
                    labels={
                        '客户价值': '客户价值 (元)',
                        '物料效率': '物料效率 (元/件)',
                        '客户分群': '客户分群',
                        '销售总额': '销售总额 (元)'
                    },
                    color_discrete_map={
                        '核心客户': '#4CAF50',
                        '高潜力客户': '#FFC107',
                        '高效率客户': '#2196F3',
                        '一般客户': '#9E9E9E'
                    }
                )

                fig_segments.update_traces(
                    marker=dict(opacity=0.8, line=dict(width=1, color='white')),
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '客户价值: <b>￥%{x:,.0f}</b><br>' +
                                  '物料效率: <b>￥%{y:,.2f}/件</b><br>' +
                                  '销售总额: <b>￥%{marker.size:,.0f}</b><br>' +
                                  '客户分群: <b>%{marker.color}</b><br>' +
                                  '<extra></extra>'
                )

                # 设置平均线
                avg_value = customer_value['客户价值'].median()
                avg_efficiency = customer_value['物料效率'].median()

                fig_segments.add_shape(
                    type='line',
                    x0=avg_value,
                    y0=0,
                    x1=avg_value,
                    y1=customer_value['物料效率'].max() * 1.1,
                    line=dict(color='gray', width=1, dash='dash')
                )

                fig_segments.add_shape(
                    type='line',
                    x0=0,
                    y0=avg_efficiency,
                    x1=customer_value['客户价值'].max() * 1.1,
                    y1=avg_efficiency,
                    line=dict(color='gray', width=1, dash='dash')
                )

                fig_segments = configure_plotly_chart(
                    fig_segments,
                    title="客户分群矩阵",
                    height=600
                )

                # 使用create_chart_container显示图表
                create_chart_container(
                    chart_figure=fig_segments,
                    title="客户分群矩阵",
                    description="该图表将客户按价值和物料效率分为四个象限。气泡大小表示销售额，不同颜色代表不同客户分群。",
                    tips=[
                        "右上象限: 核心客户 (高价值且高效率)",
                        "右下象限: 高潜力客户 (高价值但效率较低)",
                        "左上象限: 高效率客户 (价值较低但高效率)",
                        "左下象限: 一般客户 (价值和效率均较低)"
                    ],
                    insight_text="核心客户是业务支柱，高潜力客户可通过优化物料策略提高效率，高效率客户可扩大合作规模。"
                )

                # 显示分群统计数据
                st.markdown("### 客户分群统计")

                # 使用Streamlit列布局展示不同分群的卡片
                segment_cols = st.columns(4)
                segment_colors = {
                    '核心客户': '#4CAF50',
                    '高潜力客户': '#FFC107',
                    '高效率客户': '#2196F3',
                    '一般客户': '#9E9E9E'
                }

                segments = ['核心客户', '高潜力客户', '高效率客户', '一般客户']

                for i, segment in enumerate(segments):
                    segment_data = group_stats[group_stats['客户分群'] == segment]
                    if not segment_data.empty:
                        with segment_cols[i % 4]:
                            st.markdown(f"""
                            <div style='border-radius: 10px; border-left: 5px solid {segment_colors[segment]}; padding: 15px; margin-bottom: 15px; background-color: rgba({int(segment_colors[segment][1:3], 16)}, {int(segment_colors[segment][3:5], 16)}, {int(segment_colors[segment][5:7], 16)}, 0.1);'>
                                <h4 style='color: {segment_colors[segment]}; margin-top: 0;'>{segment}</h4>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                    <span>客户数量:</span>
                                    <span><strong>{int(segment_data['客户数量'].values[0])}</strong></span>
                                </div>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                    <span>客户占比:</span>
                                    <span><strong>{segment_data['客户占比'].values[0]:.1f}%</strong></span>
                                </div>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                    <span>价值总和:</span>
                                    <span><strong>￥{segment_data['客户价值总和'].values[0]:,.0f}</strong></span>
                                </div>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                    <span>价值占比:</span>
                                    <span><strong>{segment_data['价值占比'].values[0]:.1f}%</strong></span>
                                </div>
                                <div style='display: flex; justify-content: space-between; margin-bottom: 5px;'>
                                    <span>平均费比:</span>
                                    <span><strong>{segment_data['平均费比'].values[0]:.2f}%</strong></span>
                                </div>
                                <div style='display: flex; justify-content: space-between;'>
                                    <span>平均物料效率:</span>
                                    <span><strong>￥{segment_data['平均物料效率'].values[0]:,.0f}/件</strong></span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"生成客户分群分析图表时出错: {str(e)}")
        else:
            st.warning("没有足够的数据来生成客户分群分析图表。")

    # 潜力客户识别选项卡
    with value_subtabs[2]:
        if not customer_value.empty:
            try:
                # 计算潜力指数
                # 潜力指数 = 物料效率 * (1 - 费比/100) * 0.7 + 销售增长率 * 0.3
                # 由于没有时间序列数据，这里简化计算，不考虑销售增长率
                customer_value['潜力指数'] = customer_value['物料效率'] * (1 - customer_value['费比'] / 100)

                # 标准化潜力指数到0-100
                max_potential = customer_value['潜力指数'].max()
                min_potential = customer_value['潜力指数'].min()
                range_potential = max_potential - min_potential

                if range_potential > 0:
                    customer_value['潜力得分'] = ((customer_value['潜力指数'] - min_potential) / range_potential * 100)
                else:
                    customer_value['潜力得分'] = 50  # 默认值

                # 筛选潜力客户 (潜力得分 > 60 且销售额不在前20%)
                sales_threshold = np.percentile(customer_value['销售总额'], 80)
                potential_customers = customer_value[
                    (customer_value['潜力得分'] > 60) &
                    (customer_value['销售总额'] < sales_threshold)
                    ]

                potential_customers = potential_customers.sort_values('潜力得分', ascending=False).head(15)

                # 创建潜力客户气泡图
                fig_potential = px.scatter(
                    potential_customers,
                    x='物料效率',
                    y='费比',
                    size='销售总额',
                    color='潜力得分',
                    hover_name='经销商名称',
                    text='经销商名称',
                    labels={
                        '物料效率': '物料效率 (元/件)',
                        '费比': '费比 (%)',
                        '销售总额': '销售总额 (元)',
                        '潜力得分': '潜力得分'
                    },
                    color_continuous_scale='Viridis',
                    size_max=50
                )

                fig_potential.update_traces(
                    marker=dict(opacity=0.8, line=dict(width=1, color='white')),
                    textposition="top center",
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '物料效率: <b>￥%{x:,.2f}/件</b><br>' +
                                  '费比: <b>%{y:.2f}%</b><br>' +
                                  '销售总额: <b>￥%{marker.size:,.0f}</b><br>' +
                                  '潜力得分: <b>%{marker.color:.1f}</b><br>' +
                                  '<extra></extra>'
                )

                fig_potential = configure_plotly_chart(
                    fig_potential,
                    title="潜力客户矩阵",
                    height=600
                )

                # 设置坐标轴
                fig_potential.update_layout(
                    xaxis=dict(title='物料效率 (元/件)', tickprefix='￥', tickformat=',.0f'),
                    yaxis=dict(title='费比 (%)', ticksuffix='%')
                )

                # 添加说明区域
                fig_potential.add_annotation(
                    x=potential_customers['物料效率'].max() * 0.9,
                    y=potential_customers['费比'].min() * 1.1,
                    text="高物料效率<br>低费比<br>⬅ 最具潜力",
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#666",
                    bgcolor="rgba(255, 255, 255, 0.8)",
                    bordercolor="#666",
                    borderwidth=1,
                    borderpad=4,
                    font=dict(size=12, color="#333")
                )

                create_chart_container(
                    chart_figure=fig_potential,
                    title="潜力客户矩阵",
                    description="该图表展示了最具发展潜力的客户。理想的潜力客户具有高物料效率(横轴)和低费比(纵轴)。",
                    tips=[
                        "气泡大小表示当前销售额，颜色深浅表示潜力得分",
                        "左下角客户最具潜力，物料投入产出比最高",
                        "这些客户虽然当前销售额不高，但物料使用效率好",
                        "建议增加对这些客户的物料投入和销售支持"
                    ],
                    insight_text="这些潜力客户有望通过适当增加物料投入，产生更大的销售增长，提高整体ROI。"
                )

                # 显示潜力客户列表
                st.markdown("### 重点潜力客户名单")

                potential_df = potential_customers[
                    ['经销商名称', '销售总额', '物料总成本', '费比', '物料效率', '潜力得分']].copy()
                potential_df.columns = ['经销商名称', '销售总额(元)', '物料成本(元)', '费比(%)', '物料效率(元/件)',
                                        '潜力得分']

                # 添加增长建议列
                def get_growth_suggestion(row):
                    if row['费比(%)'] < 3:
                        return '增加30%物料投入，提高市场份额'
                    elif row['费比(%)'] < 5:
                        return '增加20%物料投入，关注转化效果'
                    else:
                        return '增加10%物料投入，同时优化物料使用'

                potential_df['增长建议'] = potential_df.apply(get_growth_suggestion, axis=1)

                # 设置列格式
                potential_df['销售总额(元)'] = potential_df['销售总额(元)'].apply(lambda x: f"￥{x:,.0f}")
                potential_df['物料成本(元)'] = potential_df['物料成本(元)'].apply(lambda x: f"￥{x:,.0f}")
                potential_df['费比(%)'] = potential_df['费比(%)'].apply(lambda x: f"{x:.2f}%")
                potential_df['物料效率(元/件)'] = potential_df['物料效率(元/件)'].apply(lambda x: f"￥{x:,.0f}")
                potential_df['潜力得分'] = potential_df['潜力得分'].apply(lambda x: f"{x:.1f}")

                # 显示表格
                st.dataframe(potential_df, use_container_width=True)

            except Exception as e:
                st.error(f"生成潜力客户图表时出错: {str(e)}")
        else:
            st.warning("没有足够的数据来生成潜力客户图表。")

    # 客户详情表选项卡修改
    with value_subtabs[3]:
        if not customer_value.empty:
            try:
                st.markdown("### 客户价值可视化")

                # 创建一个更直观的客户数据可视化
                detailed_df = customer_value[['客户代码', '经销商名称', '销售总额', '物料总成本',
                                              '物料数量', '费比', '物料效率', '客户价值', '价值排名']].copy()

                # 计算ROI
                detailed_df['ROI'] = detailed_df['销售总额'] / detailed_df['物料总成本'].where(
                    detailed_df['物料总成本'] > 0, np.nan)

                # 创建TOP20客户价值图表
                top20_customers = detailed_df.sort_values('客户价值', ascending=False).head(20)

                fig_customer_ranking = px.bar(
                    top20_customers,
                    x='经销商名称',
                    y='客户价值',
                    color='费比',
                    labels={
                        '经销商名称': '经销商',
                        '客户价值': '客户价值 (元)',
                        '费比': '费比 (%)'
                    },
                    title="客户价值TOP20",
                    color_continuous_scale='RdYlGn_r',
                    text='客户价值'
                )

                # 更新图表样式并添加悬停详情
                fig_customer_ranking.update_traces(
                    texttemplate='￥%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '客户价值: <b>￥%{y:,.0f}</b><br>' +
                                  '费比: <b>%{marker.color:.2f}%</b><br>' +
                                  '销售额: <b>￥%{customdata[0]:,.0f}</b><br>' +
                                  '物料成本: <b>￥%{customdata[1]:,.0f}</b><br>' +
                                  '<extra></extra>',
                    customdata=top20_customers[['销售总额', '物料总成本']].values
                )

                # 使用优化后的图表容器显示
                create_chart_container(
                    chart_figure=fig_customer_ranking,
                    title="客户价值TOP20",
                    description="该图表展示了客户价值排名前20名的经销商。柱形高度表示客户价值，颜色表示费比(越绿越好)。",
                    tips=[
                        "客户价值 = 销售总额 - 物料总成本",
                        "颜色越绿表示费比越低，物料使用效率越高",
                        "将鼠标悬停在柱形上可查看详细数据",
                        "重点关注高价值但费比较高(红色/黄色)的客户，这些客户有改进空间"
                    ],
                    insight_text="价值最高的客户占总价值的大部分，针对这些客户优化物料策略将带来最大回报。"
                )

                # 添加客户卡片显示（现代化图形化替代表格）
                st.markdown("### 客户价值卡片")

                # 添加搜索与筛选功能
                col1, col2 = st.columns([2, 1])

                with col1:
                    search_term = st.text_input("搜索经销商:", "")

                with col2:
                    value_filter = st.selectbox(
                        "价值筛选:",
                        ["全部客户", "高价值客户(前20%)", "中价值客户(中间60%)", "低价值客户(后20%)"],
                        index=0
                    )

                # 根据筛选条件过滤数据
                filtered_customers = detailed_df.copy()

                if search_term:
                    filtered_customers = filtered_customers[
                        filtered_customers['经销商名称'].str.contains(search_term, case=False)]

                if value_filter != "全部客户":
                    if value_filter == "高价值客户(前20%)":
                        threshold = np.percentile(detailed_df['客户价值'], 80)
                        filtered_customers = filtered_customers[filtered_customers['客户价值'] >= threshold]
                    elif value_filter == "中价值客户(中间60%)":
                        low = np.percentile(detailed_df['客户价值'], 20)
                        high = np.percentile(detailed_df['客户价值'], 80)
                        filtered_customers = filtered_customers[
                            (filtered_customers['客户价值'] >= low) &
                            (filtered_customers['客户价值'] < high)]
                    else:
                        threshold = np.percentile(detailed_df['客户价值'], 20)
                        filtered_customers = filtered_customers[filtered_customers['客户价值'] < threshold]

                # 显示卡片式布局
                if not filtered_customers.empty:
                    st.markdown(f"#### 找到{len(filtered_customers)}个符合条件的客户")

                    # 建立分页系统
                    items_per_page = 6
                    total_pages = int(np.ceil(len(filtered_customers) / items_per_page))
                    current_page = st.slider("页码", 1, max(1, total_pages), 1)

                    start_idx = (current_page - 1) * items_per_page
                    end_idx = min(start_idx + items_per_page, len(filtered_customers))

                    # 获取当前页客户数据
                    page_customers = filtered_customers.sort_values('客户价值', ascending=False).iloc[start_idx:end_idx]

                    # 创建3列布局显示客户卡片
                    cols = st.columns(3)

                    for i, (_, customer) in enumerate(page_customers.iterrows()):
                        # 根据ROI和费比设置颜色
                        roi_color = "#48BB78" if customer['ROI'] > 3 else "#ECC94B" if customer[
                                                                                           'ROI'] > 1 else "#F56565"
                        fee_color = "#48BB78" if customer['费比'] < 3 else "#ECC94B" if customer[
                                                                                            '费比'] < 5 else "#F56565"

                        with cols[i % 3]:
                            st.markdown(f"""
                            <div style="background-color: white; border-radius: 10px; padding: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 15px; border-left: 5px solid {roi_color};">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                                    <h4 style="margin: 0;">{customer['经销商名称']}</h4>
                                    <span style="background-color: {roi_color}; color: white; padding: 3px 10px; border-radius: 20px; font-size: 14px;">
                                        #{int(customer['价值排名'])} 名
                                    </span>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 10px;">
                                    <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                        <div style="font-size: 0.8rem; color: #718096;">客户价值</div>
                                        <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">￥{customer['客户价值']:,.0f}</div>
                                    </div>
                                    <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                        <div style="font-size: 0.8rem; color: #718096;">销售总额</div>
                                        <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">￥{customer['销售总额']:,.0f}</div>
                                    </div>
                                </div>
                                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;">
                                    <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                        <div style="font-size: 0.8rem; color: #718096;">ROI</div>
                                        <div style="font-size: 1.1rem; font-weight: bold; color: {roi_color};">{customer['ROI']:.2f}</div>
                                    </div>
                                    <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                        <div style="font-size: 0.8rem; color: #718096;">费比</div>
                                        <div style="font-size: 1.1rem; font-weight: bold; color: {fee_color};">{customer['费比']:.2f}%</div>
                                    </div>
                                    <div style="text-align: center; padding: 8px; background-color: #f7fafc; border-radius: 5px;">
                                        <div style="font-size: 0.8rem; color: #718096;">物料成本</div>
                                        <div style="font-size: 1.1rem; font-weight: bold; color: #2D3748;">￥{customer['物料总成本']:,.0f}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    # 显示分页信息
                    st.markdown(
                        f"**第 {current_page}/{total_pages} 页，显示 {start_idx + 1}-{end_idx}/{len(filtered_customers)} 条记录**")
                else:
                    st.warning("没有找到符合条件的客户记录")

                # 保留下载功能以便离线分析
                csv = detailed_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="下载完整客户数据",
                    data=csv,
                    file_name="客户价值分析表.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.error(f"生成客户详情图表时出错: {str(e)}")
        else:
            st.warning("没有数据来显示客户详情表。")


def render_material_effectiveness_tab(filtered_material, filtered_sales):
    """
    渲染物料效益分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>物料效益分析</h2>", unsafe_allow_html=True)

    # 合并经销商维度的物料和销售数据
    try:
        # 按经销商和月份聚合物料数据
        material_by_customer = filtered_material.groupby(['客户代码', '经销商名称', '发运月份']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 按经销商和月份聚合销售数据
        sales_by_customer = filtered_sales.groupby(['客户代码', '经销商名称', '发运月份']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        effectiveness_data = pd.merge(
            material_by_customer,
            sales_by_customer,
            on=['客户代码', '经销商名称', '发运月份'],
            how='outer'
        )

        # 计算物料效益 (销售额/物料数量)
        effectiveness_data['物料效益'] = effectiveness_data['销售总额'] / effectiveness_data['物料数量'].where(
            effectiveness_data['物料数量'] > 0, np.nan)

        # 移除缺失值和异常值
        effectiveness_data = effectiveness_data.dropna(subset=['物料效益'])

        # 过滤掉物料效益异常大的值 (超过99.5%分位数)
        upper_limit = effectiveness_data['物料效益'].quantile(0.995)
        effectiveness_data = effectiveness_data[effectiveness_data['物料效益'] <= upper_limit]

        # 检查数据有效性
        if effectiveness_data.empty:
            st.warning("经过数据清洗后，没有足够的有效数据来分析物料效益。")
            return

        # 创建物料投放效果散点图
        fig_material_effectiveness, r_value, slope = create_material_effectiveness_chart(effectiveness_data)

        # 使用优化的图表容器显示
        create_chart_container(
            chart_figure=fig_material_effectiveness,
            title="物料投放量与销售额关系",
            description="该散点图展示了物料投放量与销售额之间的相关关系，每个点代表一个经销商在某月的数据。",
            tips=[
                f"相关系数 r² = {r_value ** 2:.2f}，表示两者相关程度 (值越接近1关系越强)",
                f"每增加1件物料平均增加 ￥{slope:.2f} 销售额",
                "颜色越深表示物料效益(每件物料产生的销售额)越高",
                "气泡越大表示物料成本投入越多"
            ],
            insight_text="理想状态下，应增加对落在趋势线上方(投入产出比高于平均)的经销商的物料投放。"
        )

        # 添加物料效益直方图
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        if not effectiveness_data.empty:
            # 创建物料效益直方图
            fig_effectiveness_hist = px.histogram(
                effectiveness_data,
                x='物料效益',
                nbins=30,
                labels={'物料效益': '物料效益 (元/件)'},
                title="物料效益分布",
                color_discrete_sequence=['#5e72e4']
            )

            # 添加物料效益中位数线
            median_effectiveness = effectiveness_data['物料效益'].median()
            fig_effectiveness_hist.add_vline(
                x=median_effectiveness,
                line_dash="dash",
                line_color="#ff5a36",
                annotation=dict(
                    text=f"中位数: ￥{median_effectiveness:.2f}/件",
                    font=dict(color="#ff5a36"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4
                )
            )

            # 添加平均值线
            mean_effectiveness = effectiveness_data['物料效益'].mean()
            fig_effectiveness_hist.add_vline(
                x=mean_effectiveness,
                line_dash="dot",
                line_color="#2dce89",
                annotation=dict(
                    text=f"平均值: ￥{mean_effectiveness:.2f}/件",
                    font=dict(color="#2dce89"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#2dce89",
                    borderwidth=1,
                    borderpad=4,
                    y=1.1
                )
            )

            # 配置图表
            fig_effectiveness_hist = configure_plotly_chart(
                fig_effectiveness_hist,
                title="物料效益分布",
                height=450
            )

            # 增强图表可视化效果
            fig_effectiveness_hist.update_layout(
                xaxis=dict(
                    title=dict(text='物料效益 (元/件)', font=dict(size=14)),
                    tickprefix='￥',
                    tickformat=',',
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title=dict(text='频数', font=dict(size=14)),
                    tickfont=dict(size=12),
                ),
                bargap=0.1
            )

            # 使用优化的图表容器显示
            create_chart_container(
                chart_figure=fig_effectiveness_hist,
                title="物料效益分布",
                description="该直方图展示了所有客户物料效益(每件物料产生销售额)的分布情况。",
                tips=[
                    "物料效益中位数(红色虚线)为数据集的中心点",
                    "平均值(绿色点线)受极端值影响，通常高于中位数",
                    "分布越集中，说明物料使用效率越稳定",
                    "分布右侧尾部展示效益最高的案例"
                ],
                insight_text="分析分布右侧(高物料效益)客户的物料使用方式，可提取最佳实践并推广到其他客户。"
            )
        else:
            st.warning("没有足够的数据来生成物料效益分布图表。")

        st.markdown("</div>", unsafe_allow_html=True)

        # 物料效益TOP10与BOTTOM10比较
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        # 聚合到经销商级别计算平均效益
        customer_avg_effectiveness = effectiveness_data.groupby(['客户代码', '经销商名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum',
            '物料效益': 'mean'
        }).reset_index()

        # 筛选销售额和物料数量超过一定阈值的客户，确保分析有意义
        min_sales = customer_avg_effectiveness['销售总额'].quantile(0.1)
        min_material = customer_avg_effectiveness['物料数量'].quantile(0.1)

        valid_customers = customer_avg_effectiveness[
            (customer_avg_effectiveness['销售总额'] >= min_sales) &
            (customer_avg_effectiveness['物料数量'] >= min_material)
            ]

        if not valid_customers.empty and len(valid_customers) >= 6:
            # 获取TOP5和BOTTOM5
            top5 = valid_customers.nlargest(5, '物料效益')
            bottom5 = valid_customers.nsmallest(5, '物料效益')

            # 合并数据并添加类别标签
            top5['类别'] = '高效益'
            bottom5['类别'] = '低效益'
            comparison_df = pd.concat([top5, bottom5])

            # 创建比较图表
            fig_comparison = px.bar(
                comparison_df,
                x='经销商名称',
                y='物料效益',
                color='类别',
                barmode='group',
                labels={
                    '经销商名称': '经销商',
                    '物料效益': '物料效益 (元/件)',
                    '类别': '效益类别'
                },
                title="高效益VS低效益客户比较",
                color_discrete_map={
                    '高效益': '#4CAF50',
                    '低效益': '#FF5252'
                },
                text='物料效益'
            )

            # 更新柱状图样式
            fig_comparison.update_traces(
                texttemplate='￥%{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>' +
                              '物料效益: <b>￥%{y:,.2f}/件</b><br>' +
                              '类别: <b>%{marker.color}</b><br>' +
                              '<extra></extra>'
            )

            # 配置图表
            fig_comparison = configure_plotly_chart(
                fig_comparison,
                title="高效益VS低效益客户比较",
                height=550
            )

            # 增强图表可视化效果
            fig_comparison.update_layout(
                xaxis=dict(
                    title=dict(text='经销商', font=dict(size=14)),
                    tickangle=-45,
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title=dict(text='物料效益 (元/件)', font=dict(size=14)),
                    tickprefix='￥',
                    tickformat=',',
                    tickfont=dict(size=12),
                ),
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99
                )
            )

            # 使用优化的图表容器显示
            create_chart_container(
                chart_figure=fig_comparison,
                title="高效益VS低效益客户比较",
                description="该图表对比了物料效益最高和最低的经销商。通过分析两组客户差异，可以发现提高物料效益的关键因素。",
                tips=[
                    "高效益客户(绿色)代表物料使用效率最佳实践",
                    "低效益客户(红色)代表物料使用效率有提升空间",
                    "对比两组客户的物料投放策略、销售渠道和市场环境",
                    "将高效益客户的成功经验复制到低效益客户"
                ],
                insight_text="高效益客户平均物料效益是低效益客户的约10倍，说明物料使用策略存在显著差异，有较大优化空间。"
            )

            # 添加差异分析表格
            st.markdown("### 高效益与低效益客户差异分析")

            # 计算两组平均值
            high_avg = top5[['物料数量', '物料总成本', '销售总额', '物料效益']].mean()
            low_avg = bottom5[['物料数量', '物料总成本', '销售总额', '物料效益']].mean()

            # 计算差异和倍数
            diff = high_avg - low_avg
            ratio = high_avg / low_avg

            # 创建对比表格数据
            comparison_table = pd.DataFrame({
                '指标': ['物料数量(件)', '物料总成本(元)', '销售总额(元)', '物料效益(元/件)'],
                '高效益客户均值': [f"{high_avg['物料数量']:,.0f}", f"￥{high_avg['物料总成本']:,.0f}",
                                   f"￥{high_avg['销售总额']:,.0f}", f"￥{high_avg['物料效益']:,.2f}"],
                '低效益客户均值': [f"{low_avg['物料数量']:,.0f}", f"￥{low_avg['物料总成本']:,.0f}",
                                   f"￥{low_avg['销售总额']:,.0f}", f"￥{low_avg['物料效益']:,.2f}"],
                '差异': [f"{diff['物料数量']:,.0f}", f"￥{diff['物料总成本']:,.0f}",
                         f"￥{diff['销售总额']:,.0f}", f"￥{diff['物料效益']:,.2f}"],
                '倍数': [f"{ratio['物料数量']:.2f}倍", f"{ratio['物料总成本']:.2f}倍",
                         f"{ratio['销售总额']:.2f}倍", f"{ratio['物料效益']:.2f}倍"]
            })

            # 显示表格
            st.dataframe(comparison_table, use_container_width=True)

            # 添加改进建议
            st.markdown("""
            <div style='background-color: rgba(66, 153, 225, 0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #4299E1;'>
                <h4 style='color: #2B6CB0; margin-top: 0;'>物料效益改进建议</h4>
                <ol style='margin-bottom: 0;'>
                    <li><strong>优化物料组合：</strong> 分析高效益客户使用的物料组合，调整低效益客户的物料配比</li>
                    <li><strong>改进物料使用方式：</strong> 组织低效益客户向高效益客户学习物料的陈列和使用技巧</li>
                    <li><strong>调整物料投放：</strong> 对低效益客户可能需要适当减少物料数量，更注重质量而非数量</li>
                    <li><strong>加强销售跟进：</strong> 确保物料投放后有相应的销售活动和效果跟踪</li>
                    <li><strong>针对性培训：</strong> 为低效益客户提供物料营销技巧的专项培训</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

        else:
            st.warning("没有足够的有效客户数据来进行高效益与低效益客户比较分析。")

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"渲染物料效益分析选项卡时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")


def render_material_product_correlation_tab(filtered_material, filtered_sales):
    """
    渲染物料-产品关联分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>物料-产品关联分析</h2>", unsafe_allow_html=True)

    try:
        # 准备物料-产品关联数据
        # 步骤1: 合并物料和销售数据，按客户代码、经销商名称和月份
        material_product = pd.merge(
            filtered_material[['发运月份', '客户代码', '经销商名称', '物料代码', '物料名称', '物料数量', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '经销商名称', '产品代码', '产品名称', '销售总额']],
            on=['发运月份', '客户代码', '经销商名称'],
            how='inner'
        )

        # 检查合并后的数据是否有效
        if material_product.empty:
            st.warning("没有找到匹配的物料和产品销售记录，无法进行关联分析。")
            return

        # 步骤2: 按物料名称和产品名称分组，聚合数据
        material_product_sales = material_product.groupby(['物料名称', '产品名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        # 计算物料-产品的关联强度
        material_product_sales['投入产出比'] = material_product_sales['销售总额'] / material_product_sales[
            '物料总成本'].where(
            material_product_sales['物料总成本'] > 0, np.nan)
        material_product_sales['物料效益'] = material_product_sales['销售总额'] / material_product_sales[
            '物料数量'].where(
            material_product_sales['物料数量'] > 0, np.nan)

        # 创建物料-产品透视表
        pivot_data = material_product_sales.pivot_table(
            index='物料名称',
            columns='产品名称',
            values='销售总额',
            aggfunc='sum',
            fill_value=0
        )

        # 创建物料-产品热力图
        fig_heatmap, success = create_material_product_heatmap(pivot_data, material_product_sales)

        if success:
            # 使用优化的图表容器显示
            create_chart_container(
                chart_figure=fig_heatmap,
                title="物料-产品销售关联热力图",
                description="该热力图展示了不同物料与产品之间的销售关联度。颜色越深表示该物料对应产品的销售额越高。",
                tips=[
                    "深色块表示该物料与该产品高度相关",
                    "可用于发现最佳物料-产品组合",
                    "横向查看哪种物料对多个产品有促进作用",
                    "纵向查看哪种产品需要多种物料支持"
                ],
                insight_text="识别最有效的物料-产品组合，可优化物料投放策略，提高销售转化率。"
            )
        else:
            st.warning("无法创建物料-产品热力图，可能是由于数据稀疏或不足。")

        # 创建物料-产品关联强度分析
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        # 确保有足够的数据
        if len(material_product_sales) > 5:
            # 筛选有效数据
            valid_pairs = material_product_sales.dropna(subset=['投入产出比'])
            valid_pairs = valid_pairs[valid_pairs['物料总成本'] > 0]
            valid_pairs = valid_pairs[valid_pairs['销售总额'] > 0]

            if not valid_pairs.empty:
                # 取投入产出比最高的15个组合
                top_pairs = valid_pairs.nlargest(15, '投入产出比')

                # 创建条形图
                fig_top_pairs = px.bar(
                    top_pairs,
                    x='投入产出比',
                    y='物料名称',
                    color='产品名称',
                    labels={
                        '投入产出比': '投入产出比 (销售额/物料成本)',
                        '物料名称': '物料名称',
                        '产品名称': '产品名称'
                    },
                    title="最佳物料-产品组合 (按投入产出比)",
                    orientation='h',
                    color_discrete_sequence=px.colors.qualitative.Bold,
                    text='投入产出比'
                )

                # 更新柱状图样式
                fig_top_pairs.update_traces(
                    texttemplate='%{text:.1f}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b> - <b>%{color}</b><br>' +
                                  '投入产出比: <b>%{x:.2f}</b><br>' +
                                  '销售总额: <b>￥%{customdata[0]:,.0f}</b><br>' +
                                  '物料成本: <b>￥%{customdata[1]:,.0f}</b><br>' +
                                  '<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    ),
                    customdata=top_pairs[['销售总额', '物料总成本']]
                )

                # 配置图表
                fig_top_pairs = configure_plotly_chart(
                    fig_top_pairs,
                    title="最佳物料-产品组合 (按投入产出比)",
                    height=600
                )

                # 增强图表可视化效果
                fig_top_pairs.update_layout(
                    xaxis=dict(
                        title=dict(text='投入产出比 (销售额/物料成本)', font=dict(size=14)),
                        tickfont=dict(size=12),
                    ),
                    yaxis=dict(
                        title=dict(text='物料名称', font=dict(size=14)),
                        tickfont=dict(size=12),
                        autorange="reversed"  # 使y轴从上到下排列
                    ),
                    legend=dict(
                        title=dict(text='产品名称'),
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_top_pairs,
                    title="最佳物料-产品组合",
                    description="该图表展示了投入产出比最高的物料-产品组合。投入产出比 = 销售额 ÷ 物料成本，值越高表示物料使用效率越高。",
                    tips=[
                        "同一种物料可能对不同产品的促销效果不同",
                        "投入产出比高意味着相对少量的物料投入带来较大销售回报",
                        "根据产品目标，选择对应效果最好的物料",
                        "可作为物料分配决策的重要依据"
                    ],
                    insight_text="顶部的物料-产品组合投入产出比最高，应优先考虑在这些组合上增加物料投入。"
                )
            else:
                st.warning("没有有效的物料-产品组合数据来分析投入产出比。")

            # 分析物料对产品销售的影响
            material_impact = material_product.groupby('物料名称').agg({
                '物料数量': 'sum',
                '物料总成本': 'sum',
                '产品代码': 'nunique',  # 计算一种物料影响的产品数量
                '销售总额': 'sum'
            }).reset_index()

            material_impact.columns = ['物料名称', '物料数量', '物料总成本', '影响产品数', '销售总额']
            material_impact['平均单产品销售额'] = material_impact['销售总额'] / material_impact['影响产品数'].where(
                material_impact['影响产品数'] > 0, np.nan)

            # 筛选有效数据
            valid_materials = material_impact.dropna()

            if not valid_materials.empty:
                # 创建物料影响力气泡图
                fig_impact = px.scatter(
                    valid_materials,
                    x='影响产品数',
                    y='平均单产品销售额',
                    size='物料数量',
                    color='物料总成本',
                    hover_name='物料名称',
                    text='物料名称',
                    labels={
                        '影响产品数': '影响产品数量',
                        '平均单产品销售额': '平均单产品销售额 (元)',
                        '物料数量': '物料数量 (件)',
                        '物料总成本': '物料总成本 (元)'
                    },
                    color_continuous_scale='Viridis',
                    size_max=50
                )

                # 更新气泡图样式
                fig_impact.update_traces(
                    textposition="top center",
                    marker=dict(opacity=0.85, line=dict(width=1, color='white')),
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '影响产品数: <b>%{x}</b><br>' +
                                  '平均单产品销售额: <b>￥%{y:,.0f}</b><br>' +
                                  '物料数量: <b>%{marker.size:,}件</b><br>' +
                                  '物料总成本: <b>￥%{marker.color:,.0f}</b><br>' +
                                  '<extra></extra>'
                )

                # 配置图表
                fig_impact = configure_plotly_chart(
                    fig_impact,
                    title="物料影响力矩阵",
                    height=600
                )

                # 增强图表可视化效果
                fig_impact.update_layout(
                    xaxis=dict(
                        title=dict(text='影响产品数量', font=dict(size=14)),
                        tickfont=dict(size=12),
                    ),
                    yaxis=dict(
                        title=dict(text='平均单产品销售额 (元)', font=dict(size=14)),
                        tickprefix='￥',
                        tickformat=',',
                        tickfont=dict(size=12),
                    ),
                    coloraxis_colorbar=dict(
                        title='物料总成本 (元)',
                        tickprefix='￥',
                        tickformat=','
                    )
                )

                # 添加象限说明
                # 右上角：高影响力-高单产品销售额
                fig_impact.add_annotation(
                    x=valid_materials['影响产品数'].max() * 0.9,
                    y=valid_materials['平均单产品销售额'].max() * 0.9,
                    text="多产品<br>高销售额<br>⬅ 明星物料",
                    showarrow=True,
                    arrowhead=1,
                    arrowcolor="#2dce89",
                    font=dict(color="#2dce89"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#2dce89",
                    borderwidth=1,
                    borderpad=4
                )

                # 左下角：低影响力-低单产品销售额
                fig_impact.add_annotation(
                    x=valid_materials['影响产品数'].min() * 1.1,
                    y=valid_materials['平均单产品销售额'].min() * 1.1,
                    text="少产品<br>低销售额<br>⬅ 待优化物料",
                    showarrow=True,
                    arrowhead=1,
                    arrowcolor="#ff5a36",
                    font=dict(color="#ff5a36"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_impact,
                    title="物料影响力矩阵",
                    description="该矩阵展示了各物料的影响广度和深度。横轴表示一种物料能够影响的产品数量，纵轴表示平均每种产品的销售额。",
                    tips=[
                        "右上象限为明星物料，既能影响多种产品，又能带来高销售额",
                        "气泡大小表示物料数量，颜色深浅表示物料成本",
                        "理想物料应位于右上角，小气泡（数量少）但带来高收益",
                        "左下角的物料需要优化使用方式或考虑替换"
                    ],
                    insight_text="识别并重点投放明星物料，同时优化或淘汰左下象限的低效物料，可提高整体物料使用效率。"
                )
            else:
                st.warning("没有有效的物料影响力数据来创建矩阵图。")
        else:
            st.warning("物料-产品组合数据不足，无法生成关联强度分析图表。")

        st.markdown("</div>", unsafe_allow_html=True)

        # 物料组合分析
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("### 最佳物料组合分析")

        # 分析组合物料的效果
        try:
            # 计算每个客户-月份组合使用的物料组合
            material_combinations = material_product.groupby(['客户代码', '经销商名称', '发运月份']).agg({
                '物料名称': lambda x: ', '.join(sorted(set(x))),
                '物料数量': 'sum',
                '物料总成本': 'sum',
                '销售总额': 'sum'
            }).reset_index()

            # 计算物料组合的效益指标
            material_combinations['投入产出比'] = material_combinations['销售总额'] / material_combinations[
                '物料总成本'].where(
                material_combinations['物料总成本'] > 0, np.nan)
            material_combinations['物料效益'] = material_combinations['销售总额'] / material_combinations[
                '物料数量'].where(
                material_combinations['物料数量'] > 0, np.nan)

            # 聚合分析物料组合效果
            combo_analysis = material_combinations.groupby('物料名称').agg({
                '客户代码': 'count',
                '物料数量': 'sum',
                '物料总成本': 'sum',
                '销售总额': 'sum',
                '投入产出比': 'mean',
                '物料效益': 'mean'
            }).reset_index()

            combo_analysis.columns = ['物料组合', '使用次数', '物料总数量', '物料总成本', '销售总额', '平均投入产出比',
                                      '平均物料效益']

            # 筛选出现次数>=3次的物料组合
            frequent_combos = combo_analysis[combo_analysis['使用次数'] >= 3]

            if not frequent_combos.empty:
                # 按平均投入产出比排序，取前15名
                top_combos = frequent_combos.nlargest(15, '平均投入产出比')

                # 创建条形图
                fig_combos = px.bar(
                    top_combos,
                    x='平均投入产出比',
                    y='物料组合',
                    color='平均物料效益',
                    labels={
                        '平均投入产出比': '平均投入产出比',
                        '物料组合': '物料组合',
                        '平均物料效益': '平均物料效益 (元/件)'
                    },
                    title="最佳物料组合 (按投入产出比)",
                    orientation='h',
                    text='平均投入产出比',
                    color_continuous_scale='Viridis'
                )

                # 更新柱状图样式
                fig_combos.update_traces(
                    texttemplate='%{text:.1f}',
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>' +
                                  '平均投入产出比: <b>%{x:.2f}</b><br>' +
                                  '平均物料效益: <b>￥%{marker.color:,.0f}/件</b><br>' +
                                  '使用次数: <b>%{customdata[0]}</b><br>' +
                                  '销售总额: <b>￥%{customdata[1]:,.0f}</b><br>' +
                                  '<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    ),
                    customdata=top_combos[['使用次数', '销售总额']]
                )

                # 配置图表
                fig_combos = configure_plotly_chart(
                    fig_combos,
                    title="最佳物料组合 (按投入产出比)",
                    height=700
                )

                # 增强图表可视化效果
                fig_combos.update_layout(
                    xaxis=dict(
                        title=dict(text='平均投入产出比', font=dict(size=14)),
                        tickfont=dict(size=12),
                    ),
                    yaxis=dict(
                        title=dict(text='物料组合', font=dict(size=14)),
                        tickfont=dict(size=12),
                        autorange="reversed"  # 使y轴从上到下排列
                    ),
                    coloraxis_colorbar=dict(
                        title='平均物料效益 (元/件)',
                        tickprefix='￥',
                        tickformat=','
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_combos,
                    title="最佳物料组合",
                    description="该图表展示了投入产出比最高的物料组合。一个物料组合包含多种同时使用的物料类型，可能产生协同效应。",
                    tips=[
                        "物料组合可能比单一物料产生更好的效果",
                        "分析高效组合中常见的物料类型",
                        "使用次数表示该组合被多少客户采用",
                        "投入产出比高的组合应考虑推广到更多客户"
                    ],
                    insight_text="最佳物料组合通常包含2-4种互补性物料，可促进多个层面的消费者认知和购买决策。"
                )

                # 添加物料组合详情表
                st.markdown("#### 最佳物料组合详情")

                detail_table = top_combos.copy()
                detail_table['物料组合'] = detail_table['物料组合'].apply(
                    lambda x: x if len(x) < 100 else x[:97] + '...'
                )
                detail_table['物料总成本'] = detail_table['物料总成本'].apply(lambda x: f"￥{x:,.0f}")
                detail_table['销售总额'] = detail_table['销售总额'].apply(lambda x: f"￥{x:,.0f}")
                detail_table['平均投入产出比'] = detail_table['平均投入产出比'].apply(lambda x: f"{x:.2f}")
                detail_table['平均物料效益'] = detail_table['平均物料效益'].apply(lambda x: f"￥{x:,.0f}/件")

                # 显示表格
                st.dataframe(detail_table, use_container_width=True)

                # 添加组合建议
                st.markdown("""
                                    <div style='background-color: rgba(66, 153, 225, 0.1); border-radius: 8px; padding: 15px; margin-top: 15px; border-left: 4px solid #4299E1;'>
                                        <h4 style='color: #2B6CB0; margin-top: 0;'>物料组合优化建议</h4>
                                        <ol style='margin-bottom: 0;'>
                                            <li><strong>找出共性：</strong> 分析高效物料组合中频繁出现的物料类型</li>
                                            <li><strong>互补原则：</strong> 组合应包含不同类型的物料，覆盖消费者接触点、展示和促销功能</li>
                                            <li><strong>控制数量：</strong> 最佳组合通常包含2-4种物料，数量过多可能降低效率</li>
                                            <li><strong>标准化组合：</strong> 将高效组合标准化，形成物料套餐，便于推广和复制</li>
                                            <li><strong>持续测试：</strong> 对比不同组合的效果，持续优化组合内容</li>
                                        </ol>
                                    </div>
                                    """, unsafe_allow_html=True)

            else:
                st.warning("没有足够使用次数的物料组合数据来进行分析。")

        except Exception as e:
            st.error(f"生成物料组合分析时出错: {str(e)}")

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"渲染物料-产品关联分析选项卡时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")


def render_fee_ratio_tab(filtered_material, filtered_sales, overall_cost_sales_ratio):
    """
    渲染费比分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    - overall_cost_sales_ratio: 总体费比
    """
    st.markdown("<h2 class='section-header'>费比分析</h2>", unsafe_allow_html=True)

    try:
        # 按经销商聚合物料数据
        customer_material = filtered_material.groupby(['客户代码', '经销商名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 按经销商聚合销售数据
        customer_sales = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        customer_metrics = pd.merge(customer_material, customer_sales, on=['客户代码', '经销商名称'], how='outer')

        # 计算费比
        customer_metrics['费比'] = calculate_fee_ratio(customer_metrics['物料总成本'], customer_metrics['销售总额'])

        # 移除无效数据
        customer_metrics = customer_metrics.dropna(subset=['费比'])

        # 检查数据有效性
        if customer_metrics.empty:
            st.warning("没有足够的数据来进行费比分析。")
            return

        # 创建费比分布直方图
        fig_fee_ratio_hist = px.histogram(
            customer_metrics,
            x='费比',
            nbins=30,
            labels={'费比': '费比 (%)'},
            color_discrete_sequence=['#5e72e4'],
            opacity=0.8
        )

        # 添加平均费比线
        avg_fee_ratio = customer_metrics['费比'].mean()
        fig_fee_ratio_hist.add_vline(
            x=avg_fee_ratio,
            line_dash="dash",
            line_color="#ff5a36",
            annotation=dict(
                text=f"平均费比: {avg_fee_ratio:.2f}%",
                font=dict(color="#ff5a36"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ff5a36",
                borderwidth=1,
                borderpad=4
            )
        )

        # 添加全局平均费比线
        fig_fee_ratio_hist.add_vline(
            x=overall_cost_sales_ratio,
            line_dash="dot",
            line_color="#2dce89",
            annotation=dict(
                text=f"总体平均费比: {overall_cost_sales_ratio:.2f}%",
                font=dict(color="#2dce89"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#2dce89",
                borderwidth=1,
                borderpad=4,
                y=1.1
            )
        )

        # 配置图表
        fig_fee_ratio_hist = configure_plotly_chart(
            fig_fee_ratio_hist,
            title="费比分布",
            height=500
        )

        # 增强图表可视化效果
        fig_fee_ratio_hist.update_layout(
            xaxis=dict(
                title=dict(text='费比 (%)', font=dict(size=14)),
                ticksuffix='%',
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                title=dict(text='经销商数量', font=dict(size=14)),
                tickfont=dict(size=12),
            ),
            bargap=0.1
        )

        # 使用优化的图表容器显示
        create_chart_container(
            chart_figure=fig_fee_ratio_hist,
            title="费比分布",
            description="该直方图展示了各经销商费比的分布情况。费比 = (物料成本 ÷ 销售总额) × 100%，费比越低越好，表示物料使用效率越高。",
            tips=[
                "红色虚线表示当前筛选条件下的平均费比",
                "绿色点线表示全局平均费比",
                "分布右侧的经销商费比偏高，需要重点关注",
                "理想情况下，分布应集中在较低的费比区间"
            ],
            insight_text="部分经销商费比显著高于平均水平，优化这些经销商的物料使用可显著提高整体效益。"
        )

        # 费比异常值识别
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        # 识别费比异常值
        # 使用1.5倍平均费比作为阈值，或更保守的1.5倍全局平均费比
        anomaly_threshold = max(overall_cost_sales_ratio * 1.5, avg_fee_ratio * 1.5)
        anomalies = customer_metrics[customer_metrics['费比'] > anomaly_threshold]

        # 显示费比异常警告卡片
        display_fee_ratio_anomalies(anomalies, overall_cost_sales_ratio)

        st.markdown("</div>", unsafe_allow_html=True)

        # 费比与销售额散点图
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)

        # 创建费比-销售额散点图
        fig_fee_sales = px.scatter(
            customer_metrics,
            x='销售总额',
            y='费比',
            size='物料总成本',
            color='物料数量',
            hover_name='经销商名称',
            labels={
                '销售总额': '销售总额 (元)',
                '费比': '费比 (%)',
                '物料总成本': '物料总成本 (元)',
                '物料数量': '物料数量 (件)'
            },
            color_continuous_scale='Viridis',
            log_x=True,  # 使用对数刻度，更好地展示不同量级的销售额
            size_max=50
        )

        # 更新散点图样式
        fig_fee_sales.update_traces(
            marker=dict(opacity=0.85, line=dict(width=1, color='white')),
            hovertemplate='<b>%{hovertext}</b><br>' +
                          '销售总额: <b>￥%{x:,.0f}</b><br>' +
                          '费比: <b>%{y:.2f}%</b><br>' +
                          '物料总成本: <b>￥%{marker.size:,.0f}</b><br>' +
                          '物料数量: <b>%{marker.color:,}件</b><br>' +
                          '<extra></extra>'
        )

        # 添加参考线
        fig_fee_sales.add_hline(
            y=overall_cost_sales_ratio,
            line_dash="dash",
            line_color="#2dce89",
            annotation=dict(
                text=f"平均费比: {overall_cost_sales_ratio:.2f}%",
                font=dict(color="#2dce89"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#2dce89",
                borderwidth=1,
                borderpad=4
            )
        )

        # 配置图表
        fig_fee_sales = configure_plotly_chart(
            fig_fee_sales,
            title="费比与销售额关系",
            height=600
        )

        # 增强图表可视化效果
        fig_fee_sales.update_layout(
            xaxis=dict(
                title=dict(text='销售总额 (元) - 对数刻度', font=dict(size=14)),
                tickprefix='￥',
                tickformat=',',
                tickfont=dict(size=12),
            ),
            yaxis=dict(
                title=dict(text='费比 (%)', font=dict(size=14)),
                ticksuffix='%',
                tickfont=dict(size=12),
            ),
            coloraxis_colorbar=dict(
                title='物料数量 (件)',
                tickformat=','
            )
        )

        # 使用优化的图表容器显示
        create_chart_container(
            chart_figure=fig_fee_sales,
            title="费比与销售额关系",
            description="该散点图展示了经销商的费比与销售额之间的关系。气泡大小表示物料成本，颜色表示物料数量。理想状态是低费比、高销售额。",
            tips=[
                "绿色虚线表示平均费比，位于线下方的经销商表现优于平均水平",
                "右下角是高效客户(高销售额，低费比)",
                "左上角是最需要优化的客户(低销售额，高费比)",
                "横轴使用对数刻度，便于同时查看大小客户"
            ],
            insight_text="销售额较高的经销商费比通常较低，表明规模效应对物料使用效率有正面影响。"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # 费比趋势分析
        st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("### 费比趋势分析")

        # 按月份聚合物料和销售数据
        monthly_material = filtered_material.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
            '物料总成本': 'sum'
        }).reset_index()

        monthly_sales = filtered_sales.groupby(pd.Grouper(key='发运月份', freq='M')).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并月度数据
        monthly_metrics = pd.merge(monthly_material, monthly_sales, on='发运月份', how='outer')

        # 计算月度费比
        monthly_metrics['费比'] = calculate_fee_ratio(monthly_metrics['物料总成本'], monthly_metrics['销售总额'])

        # 格式化月份显示
        monthly_metrics['月份'] = monthly_metrics['发运月份'].dt.strftime('%Y-%m')

        if not monthly_metrics.empty and len(monthly_metrics) >= 3:
            # 创建月度费比趋势图
            fig_monthly_fee = px.line(
                monthly_metrics.sort_values('发运月份'),
                x='月份',
                y='费比',
                markers=True,
                labels={
                    '月份': '月份',
                    '费比': '费比 (%)'
                },
                title="月度费比趋势",
                line_shape='spline',  # 使线条更平滑
                color_discrete_sequence=['#11cdef']
            )

            # 更新线图样式
            fig_monthly_fee.update_traces(
                mode='lines+markers',
                line=dict(width=3),
                marker=dict(size=8, line=dict(width=1, color='white')),
                hovertemplate='<b>%{x}</b><br>' +
                              '费比: <b>%{y:.2f}%</b><br>' +
                              '物料成本: <b>￥%{customdata[0]:,.0f}</b><br>' +
                              '销售总额: <b>￥%{customdata[1]:,.0f}</b><br>' +
                              '<extra></extra>',
                customdata=monthly_metrics[['物料总成本', '销售总额']]
            )

            # 添加平均费比参考线
            avg_monthly_fee = monthly_metrics['费比'].mean()
            fig_monthly_fee.add_hline(
                y=avg_monthly_fee,
                line_dash="dash",
                line_color="#ff5a36",
                annotation=dict(
                    text=f"平均费比: {avg_monthly_fee:.2f}%",
                    font=dict(color="#ff5a36"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4
                )
            )

            # 配置图表
            fig_monthly_fee = configure_plotly_chart(
                fig_monthly_fee,
                title="月度费比趋势",
                height=500
            )

            # 增强图表可视化效果
            fig_monthly_fee.update_layout(
                xaxis=dict(
                    title=dict(text='月份', font=dict(size=14)),
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title=dict(text='费比 (%)', font=dict(size=14)),
                    ticksuffix='%',
                    tickfont=dict(size=12),
                    zeroline=True,
                    zerolinecolor='#e0e0e0',
                    zerolinewidth=1
                )
            )

            # 使用优化的图表容器显示
            create_chart_container(
                chart_figure=fig_monthly_fee,
                title="月度费比趋势",
                description="该图表展示了月度费比的变化趋势。费比下降表示物料使用效率提高，费比上升表示效率下降。",
                tips=[
                    "观察费比是否呈现下降趋势，这是理想的状态",
                    "留意费比的季节性变化，某些月份可能有特殊情况",
                    "连续3个月费比上升需要警惕，可能存在系统性问题",
                    "结合促销活动时间分析费比波动原因"
                ],
                insight_text="分析费比波动与营销活动的关系，可以评估不同营销策略的物料使用效率。"
            )

            # 分析费比波动幅度
            # 计算环比变化
            monthly_metrics['费比环比变化'] = monthly_metrics['费比'].diff()
            monthly_metrics['费比环比变化率'] = monthly_metrics['费比环比变化'] / monthly_metrics['费比'].shift(1) * 100

            # 移除第一行（无环比数据）
            monthly_change = monthly_metrics.dropna(subset=['费比环比变化率'])

            if not monthly_change.empty:
                # 创建费比波动图
                fig_fee_change = go.Figure()

                # 添加费比柱状图
                fig_fee_change.add_trace(
                    go.Bar(
                        x=monthly_change['月份'],
                        y=monthly_change['费比'],
                        name='费比',
                        marker_color='#5e72e4',
                        opacity=0.7,
                        hovertemplate='月份: %{x}<br>费比: %{y:.2f}%<br><extra></extra>'
                    )
                )

                # 添加环比变化率线图
                fig_fee_change.add_trace(
                    go.Scatter(
                        x=monthly_change['月份'],
                        y=monthly_change['费比环比变化率'],
                        name='环比变化率',
                        line=dict(color='#ff5a36', width=3),
                        mode='lines+markers',
                        marker=dict(size=8, symbol='diamond', line=dict(width=1, color='white')),
                        yaxis='y2',
                        hovertemplate='月份: %{x}<br>环比变化率: %{y:.2f}%<br><extra></extra>'
                    )
                )

                # 配置双Y轴
                fig_fee_change.update_layout(
                    title='费比及环比变化率',
                    title_font=dict(size=18, color='#1f3867'),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    height=500,
                    margin=dict(l=60, r=60, t=80, b=60),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='#e2e8f0',
                        borderwidth=1
                    ),
                    hovermode='x unified',
                    yaxis=dict(
                        title='费比 (%)',
                        ticksuffix='%',
                        side='left',
                        gridcolor='#f4f4f4'
                    ),
                    yaxis2=dict(
                        title='环比变化率 (%)',
                        ticksuffix='%',
                        side='right',
                        overlaying='y',
                        rangemode='tozero',
                        gridcolor='#f4f4f4'
                    ),
                    xaxis=dict(
                        title='月份',
                        tickangle=-45,
                        gridcolor='#f4f4f4'
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_fee_change,
                    title="费比波动分析",
                    description="该图表展示了月度费比(柱状图)和环比变化率(折线图)。环比变化率反映费比的月度波动强度。",
                    tips=[
                        "环比变化率为负(折线低于0)表示费比下降，效率提高",
                        "环比变化率为正(折线高于0)表示费比上升，效率下降",
                        "波动过大说明物料投放策略不稳定，需要规范化",
                        "持续下降的环比变化率反映出物料使用效率的系统性改善"
                    ],
                    insight_text="通过控制费比波动，可以使物料投放效果更稳定，提高预算规划的准确性。"
                )
            else:
                st.warning("没有足够的月度数据来分析费比波动。")
        else:
            st.warning("没有足够的月度数据来生成费比趋势图。")

        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"渲染费比分析选项卡时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")


def render_profit_maximization_tab(filtered_material, filtered_sales):
    """
    渲染利润最大化分析选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>利润最大化分析</h2>", unsafe_allow_html=True)

    try:
        # 计算物料ROI
        # 按物料分组，聚合数据
        material_roi_data = filtered_material.groupby(['物料代码', '物料名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 匹配各物料对应的销售情况
        # 创建物料-销售映射表
        # 为简化分析，假设物料与销售存在一对一关系
        # 实际情况可能需要更复杂的分配算法

        # 先按客户和月份合并物料和销售数据
        material_sales_map = pd.merge(
            filtered_material[['发运月份', '客户代码', '物料代码', '物料名称', '物料总成本']],
            filtered_sales[['发运月份', '客户代码', '销售总额']],
            on=['发运月份', '客户代码'],
            how='inner'
        )

        # 然后按物料聚合销售额
        material_sales = material_sales_map.groupby(['物料代码', '物料名称']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并物料ROI数据和销售数据
        material_roi = pd.merge(material_roi_data, material_sales, on=['物料代码', '物料名称'], how='left')

        # 处理可能的空值
        material_roi['销售总额'].fillna(0, inplace=True)

        # 计算ROI
        material_roi['ROI'] = material_roi['销售总额'] / material_roi['物料总成本'].where(
            material_roi['物料总成本'] > 0, np.nan)

        # 移除无效数据
        material_roi = material_roi.dropna(subset=['ROI'])

        if not material_roi.empty:
            # 创建物料ROI矩阵
            fig_roi_matrix = px.scatter(
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
                color_continuous_scale='RdYlGn',  # 红黄绿色谱，ROI越高越绿
                size_max=50,
                log_x=True,  # 使用对数刻度更好地展示不同量级
                log_y=True  # 使用对数刻度更好地展示不同量级
            )

            # 更新散点图样式
            fig_roi_matrix.update_traces(
                textposition="top center",
                marker=dict(opacity=0.85, line=dict(width=1, color='white')),
                hovertemplate='<b>%{hovertext}</b><br>' +
                              '物料总成本: <b>￥%{x:,.0f}</b><br>' +
                              '销售总额: <b>￥%{y:,.0f}</b><br>' +
                              '物料数量: <b>%{marker.size:,}件</b><br>' +
                              'ROI: <b>%{marker.color:.2f}</b><br>' +
                              '<extra></extra>'
            )

            # 添加ROI=1参考线
            max_cost = material_roi['物料总成本'].max() * 1.2
            min_cost = material_roi['物料总成本'].min() / 1.2

            fig_roi_matrix.add_shape(
                type="line",
                x0=min_cost,
                y0=min_cost,
                x1=max_cost,
                y1=max_cost,
                line=dict(
                    color="#ff5a36",
                    width=2,
                    dash="dash",
                ),
                name="ROI=1"
            )

            # 添加ROI=1标签
            fig_roi_matrix.add_annotation(
                x=max_cost / 2,
                y=max_cost / 2,
                text="ROI=1",
                showarrow=True,
                arrowhead=1,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="#ff5a36",
                font=dict(size=12, color="#ff5a36"),
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="#ff5a36",
                borderwidth=1,
                borderpad=4
            )

            # 配置图表
            fig_roi_matrix = configure_plotly_chart(
                fig_roi_matrix,
                title="物料ROI矩阵",
                height=700
            )

            # 增强图表可视化效果
            fig_roi_matrix.update_layout(
                xaxis=dict(
                    title=dict(text='物料总成本 (元) - 对数刻度', font=dict(size=14)),
                    tickprefix='￥',
                    tickformat=',',
                    tickfont=dict(size=12),
                ),
                yaxis=dict(
                    title=dict(text='销售总额 (元) - 对数刻度', font=dict(size=14)),
                    tickprefix='￥',
                    tickformat=',',
                    tickfont=dict(size=12),
                ),
                coloraxis_colorbar=dict(
                    title='ROI',
                    tickformat='.1f'
                )
            )

            # 使用优化的图表容器显示
            create_chart_container(
                chart_figure=fig_roi_matrix,
                title="物料ROI矩阵",
                description="该矩阵展示了各类物料的投资回报率(ROI)。横轴表示物料总成本，纵轴表示销售总额，气泡大小表示物料数量，颜色表示ROI。",
                tips=[
                    "红色虚线表示ROI=1的分界线，线上方的物料ROI>1，有正回报",
                    "颜色越绿表示ROI越高，投资回报率越好",
                    "理想物料应位于右上角，且颜色为绿色",
                    "左下角红色物料ROI低，应考虑减少投入或改进使用方式"
                ],
                insight_text="通过优化物料投资组合，将资源向高ROI物料倾斜，可显著提高整体投资回报率。"
            )

            # 显示最优物料分配建议
            display_optimal_material_allocation(material_roi, filtered_material, filtered_sales)

        else:
            st.warning("没有足够的数据来生成物料ROI矩阵。")

    except Exception as e:
        st.error(f"渲染利润最大化分析选项卡时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")
def render_geographic_distribution_tab(filtered_material, filtered_sales):
    """
    渲染地理分布可视化选项卡

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>地理分布可视化</h2>", unsafe_allow_html=True)

    # 创建选项卡
    geo_subtabs = st.tabs([
        "省份分布",
        "城市分布",
        "区域热力图"
    ])

    # 准备省份级别的数据
    try:
        # 按省份聚合物料数据
        province_material = filtered_material.groupby('省份').agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 按省份聚合销售数据
        province_sales = filtered_sales.groupby('省份').agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        province_metrics = pd.merge(province_material, province_sales, on='省份', how='outer')

        # 计算费比和物料效率
        province_metrics['费比'] = calculate_fee_ratio(province_metrics['物料总成本'], province_metrics['销售总额'])
        province_metrics['物料效率'] = province_metrics['销售总额'] / province_metrics['物料数量'].where(
            province_metrics['物料数量'] > 0, np.nan)

        # 计算销售贡献占比
        total_sales = province_metrics['销售总额'].sum() if not province_metrics.empty else 0
        province_metrics['销售占比'] = (province_metrics['销售总额'] / total_sales * 100) if total_sales > 0 else 0

        # 省份分布选项卡
        with geo_subtabs[0]:
            if not province_metrics.empty:
                # 创建省份销售分布图
                province_metrics_sorted = province_metrics.sort_values('销售总额', ascending=False)

                fig_province_sales = px.bar(
                    province_metrics_sorted,
                    x='省份',
                    y='销售总额',
                    color='费比',
                    labels={'省份': '省份', '销售总额': '销售总额 (元)', '费比': '费比 (%)'},
                    color_continuous_scale='RdYlGn_r',  # 红黄绿反转颜色，费比低的为绿色
                    text='销售总额'
                )

                # 增强柱状图
                fig_province_sales.update_traces(
                    texttemplate='￥%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '销售总额: <b>￥%{y:,.0f}</b><br>' +
                                  '费比: <b>%{marker.color:.2f}%</b><br>' +
                                  '<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    )
                )

                # 配置图表
                fig_province_sales = configure_plotly_chart(
                    fig_province_sales,
                    title="省份销售分布",
                    height=500
                )

                # 增强图表可视化效果
                fig_province_sales.update_layout(
                    xaxis=dict(
                        title=dict(text='省份', font=dict(size=14)),
                        tickangle=-45,
                        tickfont=dict(size=12),
                        categoryorder='total descending'
                    ),
                    yaxis=dict(
                        title=dict(text='销售总额 (元)', font=dict(size=14)),
                        tickprefix='￥',
                        tickformat=',',
                        tickfont=dict(size=12),
                    ),
                    coloraxis_colorbar=dict(
                        title='费比 (%)',
                        ticksuffix='%'
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_province_sales,
                    title="省份销售分布",
                    description="该图表展示了各省份的销售总额排名。柱形高度表示销售额，颜色表示费比(越绿越好)。",
                    tips=[
                        "颜色越绿表示费比越低，物料使用效率越高",
                        "通过对比柱形高度和颜色，可快速识别高销售低费比的优秀省份",
                        "红色和橙色柱子是需要优化物料使用的省份",
                        "鼠标悬停可查看详细数据"
                    ],
                    insight_text="销售额前三的省份贡献了总销售额的大部分，其中一些省份费比较高，有优化空间。"
                )

                # 创建省份物料效率图
                fig_province_efficiency = px.bar(
                    province_metrics_sorted,
                    x='省份',
                    y='物料效率',
                    color='销售占比',
                    labels={'省份': '省份', '物料效率': '物料效率 (元/件)', '销售占比': '销售占比 (%)'},
                    color_continuous_scale='Blues',
                    text='物料效率'
                )

                # 更新物料效率柱状图
                fig_province_efficiency.update_traces(
                    texttemplate='￥%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '物料效率: <b>￥%{y:,.2f}/件</b><br>' +
                                  '销售占比: <b>%{marker.color:.2f}%</b><br>' +
                                  '<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    )
                )

                # 配置图表
                fig_province_efficiency = configure_plotly_chart(
                    fig_province_efficiency,
                    title="省份物料效率",
                    height=500
                )

                # 增强图表可视化效果
                fig_province_efficiency.update_layout(
                    xaxis=dict(
                        title=dict(text='省份', font=dict(size=14)),
                        tickangle=-45,
                        tickfont=dict(size=12),
                        categoryorder='total descending'
                    ),
                    yaxis=dict(
                        title=dict(text='物料效率 (元/件)', font=dict(size=14)),
                        tickprefix='￥',
                        tickformat=',',
                        tickfont=dict(size=12),
                    ),
                    coloraxis_colorbar=dict(
                        title='销售占比 (%)',
                        ticksuffix='%'
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_province_efficiency,
                    title="省份物料效率",
                    description="该图表展示了各省份的物料效率(每件物料产生的销售额)。颜色深浅表示该省份销售占比。",
                    tips=[
                        "物料效率 = 销售总额 ÷ 物料数量",
                        "高物料效率意味着单位物料创造更多销售额",
                        "颜色越深表示该省份销售贡献越大",
                        "特别关注高销售占比但物料效率低的省份"
                    ],
                    insight_text="物料效率排名前三的省份与销售额排名前三的省份不完全一致，说明高销售不等于高效率。"
                )

            else:
                st.warning("没有足够的数据来生成省份分布图表。")

        # 准备城市级别的数据
        city_material = filtered_material.groupby('城市').agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        city_sales = filtered_sales.groupby('城市').agg({
            '销售总额': 'sum'
        }).reset_index()

        city_metrics = pd.merge(city_material, city_sales, on='城市', how='outer')

        # 计算费比和物料效率
        city_metrics['费比'] = calculate_fee_ratio(city_metrics['物料总成本'], city_metrics['销售总额'])
        city_metrics['物料效率'] = city_metrics['销售总额'] / city_metrics['物料数量'].where(
            city_metrics['物料数量'] > 0, np.nan)

        # 城市分布选项卡
        with geo_subtabs[1]:
            if not city_metrics.empty:
                # 只显示销售额前15名城市
                top_cities = city_metrics.nlargest(15, '销售总额')

                # 创建TOP15城市销售气泡图
                fig_city_bubble = px.scatter(
                    top_cities,
                    x='物料效率',
                    y='费比',
                    size='销售总额',
                    color='物料数量',
                    hover_name='城市',
                    text='城市',
                    labels={
                        '物料效率': '物料效率 (元/件)',
                        '费比': '费比 (%)',
                        '销售总额': '销售总额 (元)',
                        '物料数量': '物料数量 (件)'
                    },
                    color_continuous_scale='Viridis',
                    size_max=50
                )

                # 更新气泡图样式
                fig_city_bubble.update_traces(
                    textposition="top center",
                    marker=dict(opacity=0.85, line=dict(width=1, color='white')),
                    hovertemplate='<b>%{hovertext}</b><br>' +
                                  '物料效率: <b>￥%{x:,.2f}/件</b><br>' +
                                  '费比: <b>%{y:.2f}%</b><br>' +
                                  '销售总额: <b>￥%{marker.size:,.0f}</b><br>' +
                                  '物料数量: <b>%{marker.color:,}件</b><br>' +
                                  '<extra></extra>'
                )

                # 添加参考线
                avg_efficiency = top_cities['物料效率'].mean()
                avg_fee_ratio = top_cities['费比'].mean()

                fig_city_bubble.add_hline(
                    y=avg_fee_ratio,
                    line_dash="dash",
                    line_color="#ff5a36",
                    annotation=dict(
                        text=f"平均费比: {avg_fee_ratio:.2f}%",
                        font=dict(color="#ff5a36"),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#ff5a36",
                        borderwidth=1,
                        borderpad=4
                    )
                )

                fig_city_bubble.add_vline(
                    x=avg_efficiency,
                    line_dash="dash",
                    line_color="#2dce89",
                    annotation=dict(
                        text=f"平均物料效率: ￥{avg_efficiency:.2f}/件",
                        font=dict(color="#2dce89"),
                        bgcolor="rgba(255,255,255,0.8)",
                        bordercolor="#2dce89",
                        borderwidth=1,
                        borderpad=4
                    )
                )

                # 配置图表
                fig_city_bubble = configure_plotly_chart(
                    fig_city_bubble,
                    title="TOP15城市物料效益矩阵",
                    height=600
                )

                # 增强图表可视化效果
                fig_city_bubble.update_layout(
                    xaxis=dict(
                        title=dict(text='物料效率 (元/件)', font=dict(size=14)),
                        tickprefix='￥',
                        tickformat=',',
                        tickfont=dict(size=12),
                    ),
                    yaxis=dict(
                        title=dict(text='费比 (%)', font=dict(size=14)),
                        ticksuffix='%',
                        tickfont=dict(size=12),
                    ),
                    coloraxis_colorbar=dict(
                        title='物料数量 (件)',
                        tickformat=','
                    )
                )

                # 添加象限说明
                fig_city_bubble.add_annotation(
                    x=top_cities['物料效率'].max() * 0.9,
                    y=top_cities['费比'].min() * 1.1,
                    text="高效率<br>低费比<br>⬅ 理想区域",
                    showarrow=True,
                    arrowhead=1,
                    arrowcolor="#2dce89",
                    font=dict(color="#2dce89"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#2dce89",
                    borderwidth=1,
                    borderpad=4
                )

                fig_city_bubble.add_annotation(
                    x=top_cities['物料效率'].min() * 1.1,
                    y=top_cities['费比'].max() * 0.9,
                    text="低效率<br>高费比<br>⬅ 需改进",
                    showarrow=True,
                    arrowhead=1,
                    arrowcolor="#ff5a36",
                    font=dict(color="#ff5a36"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="#ff5a36",
                    borderwidth=1,
                    borderpad=4
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_city_bubble,
                    title="TOP15城市物料效益矩阵",
                    description="该气泡图展示了销售额前15名城市的物料效率(横轴)和费比(纵轴)。气泡大小表示销售额，颜色表示物料数量。",
                    tips=[
                        "右下象限(高效率、低费比)是最理想的状态",
                        "左上象限(低效率、高费比)需要优先改进",
                        "气泡越大表示该城市销售额越高",
                        "颜色越深表示该城市物料投放量越大"
                    ],
                    insight_text="部分主要城市位于低效率、高费比区域，表明这些地区的物料营销策略有较大优化空间。"
                )

                # 创建城市销售TOP15条形图
                fig_city_sales = px.bar(
                    top_cities.sort_values('销售总额', ascending=False),
                    x='城市',
                    y='销售总额',
                    color='费比',
                    labels={'城市': '城市', '销售总额': '销售总额 (元)', '费比': '费比 (%)'},
                    color_continuous_scale='RdYlGn_r',
                    text='销售总额'
                )

                # 更新柱状图样式
                fig_city_sales.update_traces(
                    texttemplate='￥%{text:,.0f}',
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>' +
                                  '销售总额: <b>￥%{y:,.0f}</b><br>' +
                                  '费比: <b>%{marker.color:.2f}%</b><br>' +
                                  '<extra></extra>',
                    marker=dict(
                        line=dict(width=1, color='white'),
                        opacity=0.9
                    )
                )

                # 配置图表
                fig_city_sales = configure_plotly_chart(
                    fig_city_sales,
                    title="TOP15城市销售排名",
                    height=500
                )

                # 增强图表可视化效果
                fig_city_sales.update_layout(
                    xaxis=dict(
                        title=dict(text='城市', font=dict(size=14)),
                        tickangle=-45,
                        tickfont=dict(size=12),
                    ),
                    yaxis=dict(
                        title=dict(text='销售总额 (元)', font=dict(size=14)),
                        tickprefix='￥',
                        tickformat=',',
                        tickfont=dict(size=12),
                    ),
                    coloraxis_colorbar=dict(
                        title='费比 (%)',
                        ticksuffix='%'
                    )
                )

                # 使用优化的图表容器显示
                create_chart_container(
                    chart_figure=fig_city_sales,
                    title="TOP15城市销售排名",
                    description="该图表展示了销售额前15名城市的销售额排名。柱形颜色表示费比，绿色表示费比较低(好)，红色表示费比较高(差)。",
                    tips=[
                        "重点关注高销售额的城市，特别是那些费比较高的(红色柱)",
                        "颜色鲜明反映了物料使用效率",
                        "绿色柱状的城市可作为标杆，分析其成功经验",
                        "红色柱状的城市应优先优化物料投放策略"
                    ],
                    insight_text="城市间物料使用效率差异明显，可通过城市间的经验交流提高整体物料使用效率。"
                )

            else:
                st.warning("没有足够的数据来生成城市分布图表。")

        # 区域热力图选项卡
        with geo_subtabs[2]:
            # 准备区域-省份热力图数据
            try:
                # 按区域和省份聚合销售数据
                region_province_sales = filtered_sales.groupby(['所属区域', '省份']).agg({
                    '销售总额': 'sum'
                }).reset_index()

                # 按区域和省份聚合物料数据
                region_province_material = filtered_material.groupby(['所属区域', '省份']).agg({
                    '物料总成本': 'sum'
                }).reset_index()

                # 合并数据
                region_province_metrics = pd.merge(
                    region_province_sales,
                    region_province_material,
                    on=['所属区域', '省份'],
                    how='outer'
                )

                # 计算费比
                region_province_metrics['费比'] = calculate_fee_ratio(
                    region_province_metrics['物料总成本'],
                    region_province_metrics['销售总额']
                )

                # 创建透视表，用于热力图
                if not region_province_metrics.empty:
                    # 销售额热力图
                    sales_pivot = region_province_metrics.pivot(
                        index='所属区域',
                        columns='省份',
                        values='销售总额'
                    )

                    fig_sales_heatmap = px.imshow(
                        sales_pivot,
                        labels=dict(x="省份", y="区域", color="销售额 (元)"),
                        x=sales_pivot.columns,
                        y=sales_pivot.index,
                        color_continuous_scale="Blues",
                        aspect="auto",
                        text_auto='.2s'
                    )

                    fig_sales_heatmap.update_traces(
                        hovertemplate='<b>区域:</b> %{y}<br>' +
                                      '<b>省份:</b> %{x}<br>' +
                                      '<b>销售额:</b> ￥%{z:,.0f}<br>' +
                                      '<extra></extra>'
                    )

                    fig_sales_heatmap = configure_plotly_chart(
                        fig_sales_heatmap,
                        title="区域-省份销售额热力图",
                        height=500
                    )

                    # 增强图表可视化效果
                    fig_sales_heatmap.update_layout(
                        xaxis=dict(
                            title=dict(text='省份', font=dict(size=14)),
                            tickangle=-45,
                            tickfont=dict(size=12),
                        ),
                        yaxis=dict(
                            title=dict(text='区域', font=dict(size=14)),
                            tickfont=dict(size=12),
                        ),
                        coloraxis_colorbar=dict(
                            title='销售额 (元)',
                            tickprefix='￥',
                            tickformat=','
                        )
                    )

                    # 使用优化的图表容器显示
                    create_chart_container(
                        chart_figure=fig_sales_heatmap,
                        title="区域-省份销售额热力图",
                        description="该热力图展示了各区域下各省份的销售额分布。颜色越深表示销售额越高。",
                        tips=[
                            "深蓝色块表示销售额高的区域-省份组合",
                            "白色或浅色块表示销售额低或没有数据",
                            "通过热力图可快速识别各区域销售重点省份",
                            "点击图例可调整颜色范围"
                        ],
                        insight_text="销售额分布存在明显的区域差异，每个区域都有其销售重点省份，应针对性制定策略。"
                    )

                    # 费比热力图
                    fee_ratio_pivot = region_province_metrics.pivot(
                        index='所属区域',
                        columns='省份',
                        values='费比'
                    )

                    fig_fee_ratio_heatmap = px.imshow(
                        fee_ratio_pivot,
                        labels=dict(x="省份", y="区域", color="费比 (%)"),
                        x=fee_ratio_pivot.columns,
                        y=fee_ratio_pivot.index,
                        color_continuous_scale="RdYlGn_r",  # 红黄绿反转，低费比(好)用绿色
                        aspect="auto",
                        text_auto='.2f'
                    )

                    fig_fee_ratio_heatmap.update_traces(
                        hovertemplate='<b>区域:</b> %{y}<br>' +
                                      '<b>省份:</b> %{x}<br>' +
                                      '<b>费比:</b> %{z:.2f}%<br>' +
                                      '<extra></extra>'
                    )

                    fig_fee_ratio_heatmap = configure_plotly_chart(
                        fig_fee_ratio_heatmap,
                        title="区域-省份费比热力图",
                        height=500
                    )

                    # 增强图表可视化效果
                    fig_fee_ratio_heatmap.update_layout(
                        xaxis=dict(
                            title=dict(text='省份', font=dict(size=14)),
                            tickangle=-45,
                            tickfont=dict(size=12),
                        ),
                        yaxis=dict(
                            title=dict(text='区域', font=dict(size=14)),
                            tickfont=dict(size=12),
                        ),
                        coloraxis_colorbar=dict(
                            title='费比 (%)',
                            ticksuffix='%'
                        )
                    )

                    # 使用优化的图表容器显示
                    create_chart_container(
                        chart_figure=fig_fee_ratio_heatmap,
                        title="区域-省份费比热力图",
                        description="该热力图展示了各区域下各省份的费比分布。颜色越绿表示费比越低(好)，越红表示费比越高(差)。",
                        tips=[
                            "绿色块表示物料使用效率高的区域-省份组合",
                            "红色块表示需要优化物料策略的区域-省份组合",
                            "可与销售额热力图对比，找出高销售额但高费比的区域-省份组合",
                            "白色或无色块表示没有数据"
                        ],
                        insight_text="不同区域下省份的物料使用效率差异明显，应重点优化红色区域的物料投放策略。"
                    )
                else:
                    st.warning("没有足够的数据来生成区域-省份热力图。")

            except Exception as e:
                st.error(f"生成区域热力图时出错: {str(e)}")

    except Exception as e:
        st.error(f"渲染地理分布可视化选项卡时出错: {str(e)}")
        import traceback
        st.error(f"详细错误: {traceback.format_exc()}")


# 辅助函数：按区域、省份和日期筛选数据
def filter_data(df, regions=None, provinces=None, start_date=None, end_date=None):
    """
    增强版数据筛选函数
    """
    # 验证输入数据
    if df is None or df.empty:
        st.warning("筛选数据失败: 输入数据为空")
        return pd.DataFrame()

    try:
        filtered_df = df.copy()

        # 区域筛选
        if regions and len(regions) > 0:
            if '所属区域' not in filtered_df.columns:
                st.warning("筛选数据警告: 数据中缺少'所属区域'列")
            else:
                # 处理区域列中的空值
                if filtered_df['所属区域'].isna().any():
                    # 统计空值数量
                    na_count = filtered_df['所属区域'].isna().sum()
                    if na_count > 0:
                        st.info(f"数据中包含{na_count}条缺失区域信息的记录，这些记录将被标记为'未知区域'")

                    # 填充空值
                    filtered_df['所属区域'] = filtered_df['所属区域'].fillna("未知区域")

                # 应用筛选
                if "未知区域" in regions:
                    # 包括原始NaN值
                    original_regions = [r for r in regions if r != "未知区域"]
                    filtered_df = filtered_df[filtered_df['所属区域'].isin(original_regions) |
                                              filtered_df['所属区域'].isna()]
                else:
                    filtered_df = filtered_df[filtered_df['所属区域'].isin(regions)]

        # 省份筛选，类似逻辑
        if provinces and len(provinces) > 0:
            if '省份' not in filtered_df.columns:
                st.warning("筛选数据警告: 数据中缺少'省份'列")
            else:
                # 处理省份列中的空值
                if filtered_df['省份'].isna().any():
                    na_count = filtered_df['省份'].isna().sum()
                    if na_count > 0:
                        st.info(f"数据中包含{na_count}条缺失省份信息的记录，这些记录将被标记为'未知省份'")

                    filtered_df['省份'] = filtered_df['省份'].fillna("未知省份")

                # 应用筛选
                if "未知省份" in provinces:
                    original_provinces = [p for p in provinces if p != "未知省份"]
                    filtered_df = filtered_df[filtered_df['省份'].isin(original_provinces) |
                                              filtered_df['省份'].isna()]
                else:
                    filtered_df = filtered_df[filtered_df['省份'].isin(provinces)]

        # 日期筛选
        if start_date and end_date:
            if '发运月份' not in filtered_df.columns:
                st.warning("筛选数据警告: 数据中缺少'发运月份'列")
            else:
                try:
                    # 确保日期列为datetime类型
                    if not pd.api.types.is_datetime64_any_dtype(filtered_df['发运月份']):
                        st.info("正在将'发运月份'列转换为日期类型...")
                        # 尝试转换，将无效日期值设为NaT
                        filtered_df['发运月份'] = pd.to_datetime(filtered_df['发运月份'], errors='coerce')

                    # 检查是否有NaT值
                    nat_count = filtered_df['发运月份'].isna().sum()
                    if nat_count > 0:
                        st.info(f"数据中有{nat_count}条日期无效的记录，这些记录将在日期筛选中被排除")

                    # 确保日期参数格式正确
                    start_date = pd.to_datetime(start_date)
                    end_date = pd.to_datetime(end_date)

                    # 确保日期顺序正确
                    if start_date > end_date:
                        start_date, end_date = end_date, start_date

                    # 将结束日期调整为当天结束
                    end_date = end_date + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)

                    # 应用日期筛选
                    filtered_df = filtered_df.dropna(subset=['发运月份'])  # 移除日期为NaT的行
                    filtered_df = filtered_df[(filtered_df['发运月份'] >= start_date) &
                                              (filtered_df['发运月份'] <= end_date)]

                    # 报告筛选后结果
                    if filtered_df.empty:
                        st.warning(
                            f"在选定的日期范围内({start_date.strftime('%Y-%m-%d')}至{end_date.strftime('%Y-%m-%d')})没有找到数据")

                except Exception as e:
                    st.warning(f"日期筛选错误: {str(e)}")
                    import traceback
                    print(f"日期筛选详细错误: {traceback.format_exc()}")

        return filtered_df

    except Exception as e:
        st.error(f"筛选数据时出错: {str(e)}")
        import traceback
        print(f"数据筛选详细错误: {traceback.format_exc()}")
        return pd.DataFrame()


# 主函数
def main():
    """
    主函数 - 优化版本
    """
    # 应用自定义CSS样式
    add_custom_css()

    # 页面标题
    st.markdown("<h1 class='main-header'>口力营销物料与销售分析仪表盘</h1>", unsafe_allow_html=True)

    # 加载数据
    with st.spinner("正在加载数据，请稍候..."):
        df_material, df_sales, df_material_price = load_data()

    # 如果数据加载失败，显示错误并退出
    if df_material is None or df_sales is None:
        st.error("数据加载失败。请检查数据文件是否存在并格式正确。")
        return

    # 创建聚合数据
    with st.spinner("正在处理数据..."):
        aggregations = create_aggregations(df_material, df_sales)

    # 创建侧边栏筛选器
    create_sidebar_filters(df_material, df_sales)

    # 获取筛选选项
    selected_regions = st.session_state.get('selected_regions', [])
    selected_provinces = st.session_state.get('selected_provinces', [])
    start_date = st.session_state.get('start_date')
    end_date = st.session_state.get('end_date')

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
    avg_material_effectiveness = total_sales / filtered_material['物料数量'].sum() if filtered_material['物料数量'].sum() > 0 else 0

    # 显示KPI卡片
    display_kpi_cards(total_material_cost, total_sales, overall_cost_sales_ratio, avg_material_effectiveness)

    # 创建选项卡
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "区域性能分析",
        "时间趋势分析",
        "客户价值分析",
        "物料效益分析",
        "地理分布可视化",
        "物料-产品关联分析",
        "费比分析",
        "利润最大化分析"
    ])

    # 渲染各选项卡内容
    with tab1:
        render_region_performance_tab(filtered_material, filtered_sales)

    with tab2:
        render_time_trend_tab(filtered_material, filtered_sales)

    with tab3:
        render_customer_value_tab(filtered_material, filtered_sales)

    with tab4:
        render_material_effectiveness_tab(filtered_material, filtered_sales)

    with tab5:
        render_geographic_distribution_tab(filtered_material, filtered_sales)

    with tab6:
        render_material_product_correlation_tab(filtered_material, filtered_sales)

    with tab7:
        render_fee_ratio_tab(filtered_material, filtered_sales, overall_cost_sales_ratio)

    with tab8:
        render_profit_maximization_tab(filtered_material, filtered_sales)


def create_sidebar_filters(df_material, df_sales):
    """
    创建侧边栏筛选器

    参数:
    - df_material: 物料数据
    - df_sales: 销售数据
    """
    st.sidebar.header("数据筛选")

    # 获取所有过滤选项
    regions = sorted(df_material['所属区域'].unique())
    provinces = sorted(df_material['省份'].unique())

    # 区域筛选器
    st.session_state.selected_regions = st.sidebar.multiselect(
        "选择区域:",
        options=regions,
        default=[]
    )

    # 省份筛选器
    st.session_state.selected_provinces = st.sidebar.multiselect(
        "选择省份:",
        options=provinces,
        default=[]
    )

    # 改进的日期范围筛选器
    try:
        # 检查日期列是否存在
        if '发运月份' in df_material.columns:
            # 确保日期列为datetime类型
            if not pd.api.types.is_datetime64_any_dtype(df_material['发运月份']):
                df_material['发运月份'] = pd.to_datetime(df_material['发运月份'], errors='coerce')

            # 排除无效日期
            valid_dates = df_material['发运月份'].dropna()

            if not valid_dates.empty:
                min_date = valid_dates.min().date()
                max_date = valid_dates.max().date()

                # 处理日期相同的情况
                if min_date == max_date:
                    min_date = min_date - timedelta(days=30)
            else:
                # 无有效日期，使用默认范围
                min_date = datetime.now().date() - timedelta(days=365)
                max_date = datetime.now().date()
        else:
            st.warning("数据中缺少'发运月份'列，使用默认日期范围")
            min_date = datetime.now().date() - timedelta(days=365)
            max_date = datetime.now().date()
    except Exception as e:
        st.warning(f"设置日期范围出错: {e}，使用默认值")
        import traceback
        print(f"日期处理详细错误: {traceback.format_exc()}")
        min_date = datetime.now().date() - timedelta(days=365)
        max_date = datetime.now().date()

    # 确保日期选择器至少有一天的范围
    if min_date >= max_date:
        max_date = min_date + timedelta(days=1)

    # 显示日期选择器
    date_range = st.sidebar.date_input(
        "选择日期范围:",
        value=(min_date, max_date),
        min_value=min_date - timedelta(days=365 * 5),  # 允许选择更早的日期
        max_value=datetime.now().date() + timedelta(days=30),  # 允许选择近期将来的日期
    )

    # 处理日期选择结果
    if len(date_range) == 2:
        st.session_state.start_date, st.session_state.end_date = date_range
        # 确保开始日期不晚于结束日期
        if st.session_state.start_date > st.session_state.end_date:
            st.warning("开始日期晚于结束日期，自动交换两个日期")
            st.session_state.start_date, st.session_state.end_date = st.session_state.end_date, st.session_state.start_date
    elif len(date_range) == 1:
        # 只选择了一天
        st.session_state.start_date = date_range[0]
        st.session_state.end_date = date_range[0]
    else:
        # 避免空列表情况
        st.warning("日期选择无效，使用完整数据范围")
        st.session_state.start_date = min_date
        st.session_state.end_date = max_date

    # 添加侧边栏信息
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


def render_region_performance_tab(filtered_material, filtered_sales):
    """
    渲染区域性能分析选项卡 - 优化版

    参数:
    - filtered_material: 过滤后的物料数据
    - filtered_sales: 过滤后的销售数据
    """
    st.markdown("<h2 class='section-header'>区域性能分析</h2>", unsafe_allow_html=True)

    # 区域销售表现图表和区域物料效率图表
    region_cols = st.columns(2)

    with region_cols[0]:
        st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index().sort_values('销售总额', ascending=False)

        # 使用函数创建图表
        if not region_sales.empty:
            fig_region_sales = create_region_sales_chart(region_sales)

            # 使用优化后的函数创建带解释的图表容器
            create_chart_container(
                chart_figure=fig_region_sales,
                title="区域销售表现",
                description="该图表展示了各区域的销售总额排名。柱形越高，表示该区域销售额越大，业绩越好。",
                tips=[
                    "鼠标悬停在柱形上可查看详细销售金额",
                    "通过左侧过滤器选择不同区域或时间段进行比较分析",
                    "重点关注排名靠前的区域，分析其成功经验",
                    "对于排名靠后的区域，考虑改进销售策略或增加物料投入"
                ],
                insight_text="从图表可见，销售额排名前三的区域贡献了超过50%的总销售额，建议分析这些区域的成功经验。"
            )
        else:
            st.warning("没有足够的数据来生成区域销售表现图表。")
        st.markdown("</div>", unsafe_allow_html=True)

    with region_cols[1]:
        st.markdown("<div class='chart-wrapper'>", unsafe_allow_html=True)
        # 区域物料效率图表
        region_material_efficiency = filtered_material.groupby('所属区域').agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        region_sales_for_efficiency = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index()

        region_efficiency = pd.merge(region_material_efficiency, region_sales_for_efficiency, on='所属区域',
                                     how='outer')
        region_efficiency['物料效率'] = region_efficiency['销售总额'] / region_efficiency['物料数量'].where(
            region_efficiency['物料数量'] > 0, np.nan)
        region_efficiency = region_efficiency.sort_values('物料效率', ascending=False)

        if not region_efficiency.empty and not region_efficiency['物料效率'].isnull().all():
            # 创建物料效率图表
            fig_region_efficiency = px.bar(
                region_efficiency,
                x='所属区域',
                y='物料效率',
                color='所属区域',
                labels={'物料效率': '物料效率 (元/件)', '所属区域': '区域'},
                text='物料效率',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )

            # 更新柱状图样式
            fig_region_efficiency.update_traces(
                texttemplate='￥%{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}区域</b><br>' +
                              '物料效率: <b>￥%{y:,.2f}/件</b><br>' +
                              '物料数量: <b>%{customdata[0]:,}件</b><br>' +
                              '物料成本: <b>￥%{customdata[1]:,.0f}</b><br>' +
                              '销售总额: <b>￥%{customdata[2]:,.0f}</b><br>' +
                              '<extra></extra>',
                customdata=region_efficiency[['物料数量', '物料总成本', '销售总额']].values,
                marker=dict(
                    line=dict(width=1, color='white'),
                    opacity=0.9
                )
            )

            # 配置图表布局
            fig_region_efficiency = configure_plotly_chart(
                fig_region_efficiency,
                title="各区域物料效率",
                height=500
            )

            # 调整x轴
            fig_region_efficiency.update_layout(
                xaxis=dict(
                    title=dict(text="区域", font=dict(size=14)),
                    tickfont=dict(size=13),
                    categoryorder='total descending'
                ),
                yaxis=dict(
                    title=dict(text="物料效率 (元/件)", font=dict(size=14)),
                    tickprefix="￥",
                    tickformat=",.0f",
                    tickfont=dict(size=13)
                )
            )

            create_chart_container(
                chart_figure=fig_region_efficiency,
                title="区域物料效率",
                description="该图表展示了各区域每件物料产生的销售额。柱形越高，表示该区域物料使用效率越高。",
                tips=[
                    "物料效率 = 销售总额 ÷ 物料数量",
                    "鼠标悬停可查看物料数量、成本和销售额详情",
                    "高效率区域的物料使用经验值得借鉴",
                    "低效率区域需要改进物料使用策略"
                ],
                insight_text="物料效率排名前三的区域每件物料平均产生的销售额是后三名区域的2倍以上，说明物料使用策略存在显著差异。"
            )
        else:
            st.warning("没有足够的数据来生成区域物料效率图表。")
        st.markdown("</div>", unsafe_allow_html=True)

    # 区域费比分析图表
    st.markdown("<div class='chart-wrapper' style='margin-top: 30px;'>", unsafe_allow_html=True)
    region_material = filtered_material.groupby('所属区域').agg({
        '物料总成本': 'sum'
    }).reset_index()

    region_sales = filtered_sales.groupby('所属区域').agg({
        '销售总额': 'sum'
    }).reset_index()

    region_cost_sales = pd.merge(region_material, region_sales, on='所属区域', how='outer')

    # 计算费比和销售额百分比
    total_sales = region_cost_sales['销售总额'].sum()
    region_cost_sales['费比'] = calculate_fee_ratio(region_cost_sales['物料总成本'], region_cost_sales['销售总额'])
    region_cost_sales['销售额百分比'] = region_cost_sales['销售总额'] / total_sales * 100 if total_sales > 0 else 0

    if not region_cost_sales.empty:
        fig_region_cost_sales = create_region_cost_sales_analysis(region_cost_sales)

        create_chart_container(
            chart_figure=fig_region_cost_sales,
            title="区域费比分析",
            description="该图表通过气泡展示了各区域的销售贡献度、费比情况和物料成本规模。费比越低越好，表示物料投入产出比更高。",
            tips=[
                "横轴表示销售贡献度（占总销售额的百分比）",
                "纵轴表示费比（物料成本占销售额的百分比）",
                "气泡大小表示物料成本规模",
                "红色虚线表示平均费比基准",
                "绿色区域表示低费比区域（理想状态），红色区域表示高费比区域（需改进）"
            ],
            insight_text="优先关注位于右上方的区域（销售贡献高但费比也高），这些区域通过优化物料使用可以显著提升整体效益。"
        )
    else:
        st.warning("没有足够的数据来生成区域费比分析图表。")
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()