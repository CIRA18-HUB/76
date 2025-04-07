import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import calendar
import warnings

warnings.filterwarnings('ignore')


# 加载数据
def load_data():
    try:
        # 尝试加载真实数据
        df_material = pd.read_excel("2025物料源数据.xlsx")
        df_sales = pd.read_excel("25物料源销售数据.xlsx")
        df_material_price = pd.read_excel("物料单价.xlsx")

        print("成功加载真实数据文件")

    except Exception as e:
        print(f"无法加载Excel文件: {e}")
        print("创建模拟数据用于演示...")

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

    # 清理和标准化数据 (与原始代码相同)
    # 确保日期格式一致
    df_material['发运月份'] = pd.to_datetime(df_material['发运月份'])
    df_sales['发运月份'] = pd.to_datetime(df_sales['发运月份'])

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


# 创建仪表盘
def create_dashboard(df_material, df_sales, aggregations):
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # 获取所有过滤选项
    regions = sorted(df_material['所属区域'].unique())
    provinces = sorted(df_material['省份'].unique())
    customers = sorted(df_material['经销商名称'].unique())
    materials = sorted(df_material['物料名称'].unique())
    products = sorted(df_sales['产品名称'].unique())
    salespersons = sorted(df_material['申请人'].unique())

    # 计算KPI
    total_material_cost = df_material['物料总成本'].sum()
    total_sales = df_sales['销售总额'].sum()
    overall_cost_sales_ratio = (total_material_cost / total_sales) * 100
    avg_material_effectiveness = total_sales / df_material['物料数量'].sum()

    # 构建布局
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("口力营销物料与销售分析仪表盘", className="text-center mb-4"), width=12)
        ]),

        # KPI卡片
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("总物料成本"),
                dbc.CardBody(html.H4(f"￥{total_material_cost:,.2f}", className="card-title"))
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("总销售额"),
                dbc.CardBody(html.H4(f"￥{total_sales:,.2f}", className="card-title"))
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("总体费比"),
                dbc.CardBody(html.H4(f"{overall_cost_sales_ratio:.2f}%", className="card-title"))
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardHeader("平均物料效益"),
                dbc.CardBody(html.H4(f"￥{avg_material_effectiveness:.2f}", className="card-title"))
            ]), width=3)
        ], className="mb-4"),

        # 过滤器
        dbc.Row([
            dbc.Col([
                html.Label("选择区域:"),
                dcc.Dropdown(
                    id='region-filter',
                    options=[{'label': i, 'value': i} for i in regions],
                    multi=True,
                    placeholder="全部区域"
                )
            ], width=3),
            dbc.Col([
                html.Label("选择省份:"),
                dcc.Dropdown(
                    id='province-filter',
                    options=[{'label': i, 'value': i} for i in provinces],
                    multi=True,
                    placeholder="全部省份"
                )
            ], width=3),
            dbc.Col([
                html.Label("选择月份:"),
                dcc.DatePickerRange(
                    id='date-filter',
                    min_date_allowed=df_material['发运月份'].min().date(),
                    max_date_allowed=df_material['发运月份'].max().date(),
                    start_date=df_material['发运月份'].min().date(),
                    end_date=df_material['发运月份'].max().date()
                )
            ], width=6)
        ], className="mb-4"),

        # 选项卡布局
        dbc.Tabs([
            # 区域性能分析选项卡
            dbc.Tab(label="区域性能分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("区域销售表现", className="text-center"),
                        dcc.Graph(id="region-sales-chart")
                    ], width=6),
                    dbc.Col([
                        html.H4("区域物料效率", className="text-center"),
                        dcc.Graph(id="region-efficiency-chart")
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("区域费比对比", className="text-center"),
                        dcc.Graph(id="region-cost-sales-chart")
                    ], width=12)
                ])
            ]),

            # 时间趋势分析选项卡
            dbc.Tab(label="时间趋势分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("销售额和物料投放趋势", className="text-center"),
                        dcc.Graph(id="time-trend-chart")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("月度费比变化", className="text-center"),
                        dcc.Graph(id="monthly-cost-sales-chart")
                    ], width=6),
                    dbc.Col([
                        html.H4("物料效益趋势", className="text-center"),
                        dcc.Graph(id="material-effectiveness-trend")
                    ], width=6)
                ])
            ]),

            # 客户价值分析选项卡
            dbc.Tab(label="客户价值分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("客户价值排名", className="text-center"),
                        dcc.Graph(id="customer-value-chart")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("客户投入产出比", className="text-center"),
                        dcc.Graph(id="customer-roi-chart")
                    ], width=12)
                ])
            ]),

            # 物料效益分析选项卡
            dbc.Tab(label="物料效益分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("物料投放效果评估", className="text-center"),
                        dcc.Graph(id="material-effectiveness-chart")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("物料与销售相关性", className="text-center"),
                        dcc.Graph(id="material-sales-correlation")
                    ], width=12)
                ])
            ]),

            # 地理分布可视化选项卡
            dbc.Tab(label="地理分布可视化", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("省份销售热力图", className="text-center"),
                        dcc.Graph(id="province-sales-map")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("城市物料分布", className="text-center"),
                        dcc.Graph(id="city-material-map")
                    ], width=12)
                ])
            ]),

            # 物料-产品关联分析选项卡
            dbc.Tab(label="物料-产品关联分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("物料-产品关联热力图", className="text-center"),
                        dcc.Graph(id="material-product-heatmap")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("最佳物料组合", className="text-center"),
                        dcc.Graph(id="best-material-combinations")
                    ], width=12)
                ])
            ]),

            # 经销商绩效对比选项卡
            dbc.Tab(label="经销商绩效对比", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("经销商销售效率", className="text-center"),
                        dcc.Graph(id="distributor-efficiency")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("经销商物料使用情况", className="text-center"),
                        dcc.Graph(id="distributor-material-usage")
                    ], width=12)
                ])
            ]),

            # 费比分析选项卡
            dbc.Tab(label="费比分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("区域费比分析", className="text-center"),
                        dcc.Graph(id="region-cost-sales-analysis")
                    ], width=6),
                    dbc.Col([
                        html.H4("销售人员费比分析", className="text-center"),
                        dcc.Graph(id="salesperson-cost-sales-analysis")
                    ], width=6)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("经销商费比分析", className="text-center"),
                        dcc.Graph(id="distributor-cost-sales-analysis")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("费比异常值提醒", className="text-center"),
                        html.Div(id="cost-sales-anomalies", className="alert alert-warning")
                    ], width=12)
                ])
            ]),

            # 利润最大化分析选项卡
            dbc.Tab(label="利润最大化分析", children=[
                dbc.Row([
                    dbc.Col([
                        html.H4("物料ROI分析", className="text-center"),
                        dcc.Graph(id="material-roi-analysis")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H4("最优物料分配建议", className="text-center"),
                        html.Div(id="optimal-material-allocation")
                    ], width=12)
                ])
            ])
        ])
    ], fluid=True)

    # 回调函数

    # 区域销售表现图表
    @app.callback(
        Output("region-sales-chart", "figure"),
        [Input("region-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_region_sales_chart(selected_regions, start_date, end_date):
        filtered_sales = filter_data(df_sales, selected_regions, None, start_date, end_date)

        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index().sort_values('销售总额', ascending=False)

        # 创建更现代化的图表
        fig = px.bar(
            region_sales,
            x='所属区域',
            y='销售总额',
            labels={'销售总额': '销售总额 (元)', '所属区域': '区域'},
            color='所属区域',
            text='销售总额',
            color_discrete_sequence=px.colors.qualitative.G10,  # 使用更现代的调色板
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:,.2f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>销售总额: ¥%{y:,.2f}<extra></extra>'
        )

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了各区域的销售总额排名。柱形越高，表示该区域销售额越大，业绩越好。通过此图可以直观了解哪些区域的销售表现最佳，哪些区域需要加强。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停在柱形上可查看详细销售金额"),
                html.Li("通过上方过滤器选择不同区域或时间段进行比较分析"),
                html.Li("重点关注排名靠前的区域，分析其成功经验"),
                html.Li("对于排名靠后的区域，考虑改进销售策略或增加物料投入")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 区域物料效率图表
    @app.callback(
        Output("region-efficiency-chart", "figure"),
        [Input("region-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_region_efficiency_chart(selected_regions, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, None, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, None, start_date, end_date)

        region_material = filtered_material.groupby('所属区域').agg({
            '物料数量': 'sum'
        }).reset_index()

        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index()

        region_efficiency = pd.merge(region_material, region_sales, on='所属区域', how='outer')
        region_efficiency['物料效率'] = region_efficiency['销售总额'] / region_efficiency['物料数量']
        region_efficiency = region_efficiency.sort_values('物料效率', ascending=False)

        # 创建更现代化的图表
        fig = px.bar(
            region_efficiency,
            x='所属区域',
            y='物料效率',
            labels={'物料效率': '物料效率 (元/件)', '所属区域': '区域'},
            color='所属区域',
            text='物料效率',
            color_discrete_sequence=px.colors.qualitative.Vivid  # 使用更鲜明的颜色
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:,.2f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '物料效率: ¥%{y:,.2f}/件<br>' +
                          '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料数量: %{customdata[1]:,}件<extra></extra>',
            customdata=region_efficiency[['销售总额', '物料数量']].values
        )

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了各区域的物料使用效率。每个柱形代表该区域每单位物料所产生的销售额，数值越高表示物料利用效率越高。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的物料效率、总销售额和物料数量"),
                html.Li("重点关注物料效率最高的区域，分析其成功经验"),
                html.Li("物料效率低的区域可能需要改进物料使用策略或培训销售人员更有效地使用物料"),
                html.Li("比较物料效率与销售总额，有些区域虽然总销售额高，但物料效率可能不高")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 区域费比对比图表
    @app.callback(
        Output("region-cost-sales-chart", "figure"),
        [Input("region-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_region_cost_sales_chart(selected_regions, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, None, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, None, start_date, end_date)

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
        avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales['销售总额'].sum()) * 100

        # 创建更现代化的图表
        fig = px.bar(
            region_cost_sales,
            x='所属区域',
            y='费比',
            labels={'费比': '费比 (%)', '所属区域': '区域'},
            text='费比',
            color='费比',
            color_continuous_scale='RdYlGn_r',  # 红色表示高费比(不好)，绿色表示低费比(好)
            range_color=[min(region_cost_sales['费比']) * 0.9, max(region_cost_sales['费比']) * 1.1]  # 调整颜色范围更明显
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '费比: %{y:.2f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=region_cost_sales[['物料总成本', '销售总额']].values
        )

        # 添加平均线并美化
        fig.add_hline(
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

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="费比",
                ticksuffix="%",
                tickfont=dict(size=12),
                len=0.5,
                thickness=15,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了各区域的费比情况（物料成本占销售额的百分比）。费比越低越好，表示投入的物料成本产生了更多的销售额。"),
            html.P("颜色说明: 绿色表示费比较低（好），红色表示费比较高（需要改进）。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("红色虚线表示平均费比基准线，可用于快速判断区域表现"),
                html.Li("低于平均线的区域表现较好，高于平均线的区域需要关注"),
                html.Li("鼠标悬停可查看详细的费比、物料成本和销售总额数据"),
                html.Li("对于费比过高的区域，建议分析物料使用是否合理，或者销售策略是否需要调整")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 时间趋势分析图表
    @app.callback(
        Output("time-trend-chart", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_time_trend_chart(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建更现代化的图表
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加销售额线图 - 使用更现代的样式
        fig.add_trace(
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

        # 添加物料成本线图 - 使用更现代的样式
        fig.add_trace(
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

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='#f4f4f4',
                tickformat='%Y-%m',
                tickangle=-45
            )
        )

        # 更新Y轴标题和格式
        fig.update_yaxes(
            title_text="销售总额 (元)",
            secondary_y=False,
            gridcolor='#f4f4f4',
            tickprefix="¥",
            tickformat=",.0f"
        )
        fig.update_yaxes(
            title_text="物料总成本 (元)",
            secondary_y=True,
            gridcolor='#f4f4f4',
            tickprefix="¥",
            tickformat=",.0f"
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了销售额(绿色实线)和物料成本(红色虚线)随时间的变化趋势。左侧Y轴代表销售额，右侧Y轴代表物料成本。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看每月详细数据和同比增长率"),
                html.Li("观察销售额与物料成本的变化关系，理想情况是销售额增长快于物料成本增长"),
                html.Li("注意季节性波动和长期趋势，判断物料投放的时机"),
                html.Li("关注销售额与物料成本线之间的距离变化，距离越大表示利润空间越大")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 月度费比变化图表
    @app.callback(
        Output("monthly-cost-sales-chart", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_monthly_cost_sales_chart(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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
        avg_cost_sales_ratio = (time_cost_sales['物料总成本'].sum() / time_cost_sales['销售总额'].sum()) * 100

        # 创建更现代化的图表
        fig = go.Figure()

        # 添加费比折线图
        fig.add_trace(
            go.Scatter(
                x=time_cost_sales['发运月份'],
                y=time_cost_sales['费比'],
                mode='lines+markers',
                name='月度费比',
                line=dict(
                    color='#5e72e4',
                    width=3,
                    shape='spline'  # 使用平滑曲线
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

        # 添加区域填充，显示高于平均和低于平均的区域
        fig.add_trace(
            go.Scatter(
                x=time_cost_sales['发运月份'],
                y=[avg_cost_sales_ratio] * len(time_cost_sales),
                fill='tonexty',
                fillcolor='rgba(255, 99, 71, 0.2)',  # 高于平均的红色区域
                line=dict(width=0),
                hoverinfo='skip',
                showlegend=False
            )
        )

        # 添加平均线
        fig.add_hline(
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

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
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
            showlegend=False
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表显示了月度费比的变化趋势。费比是物料成本占销售额的百分比，费比越低表示物料投入产出效率越高。"),
            html.P("红色虚线表示平均费比基准线，高于此线的月份表现不佳（红色区域），低于此线的月份表现较好（白色区域）。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看每月详细的费比、物料成本和销售额数据"),
                html.Li("关注费比的波动趋势，判断物料使用效率是否正在改善"),
                html.Li("分析高于平均线的月份，查找原因并提出改进措施"),
                html.Li("结合销售旺季和促销活动时间，评估物料投入的合理性")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 物料效益趋势图表
    @app.callback(
        Output("material-effectiveness-trend", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_material_effectiveness_trend(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建更现代化的图表
        fig = go.Figure()

        # 添加面积图作为背景，体现趋势
        fig.add_trace(
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

        # 添加主折线图
        fig.add_trace(
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

        # 添加平均线
        fig.add_hline(
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

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
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
            showlegend=False
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表展示了物料效益(每单位物料带来的销售额)随时间的变化趋势。物料效益越高，表示物料使用越有效率。"),
            html.P("蓝色虚线表示平均物料效益水平，可用作基准线比较不同时期的表现。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看每月详细的物料效益、销售总额、物料数量和环比变化"),
                html.Li("注意物料效益的上升或下降趋势，判断物料使用效率是否在提高"),
                html.Li("关注环比变化较大的月份，分析原因并总结经验"),
                html.Li("将月度物料效益与销售活动、促销策略等结合分析，找出最有效的物料使用方式")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 客户价值排名图表
    @app.callback(
        Output("customer-value-chart", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_customer_value_chart(selected_regions, selected_provinces, start_date, end_date):
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

        customer_value = filtered_sales.groupby(['客户代码', '经销商名称']).agg({
            '销售总额': 'sum'
        }).reset_index().sort_values('销售总额', ascending=False).head(10)

        # 为了更好的展示，添加销售占比
        total_sales = filtered_sales['销售总额'].sum()
        customer_value['销售占比'] = customer_value['销售总额'] / total_sales * 100

        # 创建更现代化的图表
        fig = px.bar(
            customer_value,
            x='销售总额',
            y='经销商名称',
            title="前10名高价值客户",
            labels={'销售总额': '销售总额 (元)', '经销商名称': '经销商'},
            orientation='h',
            color='销售总额',
            color_continuous_scale='Blues',  # 使用蓝色渐变色
            text='销售占比'  # 显示销售占比
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '销售总额: ¥%{x:,.2f}<br>' +
                          '销售占比: %{text:.2f}%<br>' +
                          '客户代码: %{customdata}<extra></extra>',
            customdata=customer_value['客户代码'].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从大到小排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="销售总额",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了销售额最高的前10名客户。横条越长，表示该客户的销售额越高。横条上的数字表示该客户销售额占总销售额的百分比。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看客户详细的销售总额、销售占比和客户代码"),
                html.Li("关注销售额占比高的重点客户，确保维护好客户关系"),
                html.Li("分析前10名客户占总销售额的比例，评估客户集中度风险"),
                html.Li("研究高价值客户的物料使用情况，找出物料与销售的最佳配比"),
                html.Li("考虑为高价值客户提供更加个性化的物料支持")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 客户投入产出比图表
    @app.callback(
        Output("customer-roi-chart", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_customer_roi_chart(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建更现代化的图表
        fig = px.bar(
            customer_roi,
            x='投入产出比',
            y='经销商名称',
            labels={'投入产出比': 'ROI (销售额/物料成本)', '经销商名称': '经销商'},
            orientation='h',
            color='投入产出比',
            color_continuous_scale='Viridis',  # 使用渐变色展示ROI高低
            text='投入产出比'
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          'ROI: %{x:.2f}<br>' +
                          '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料总成本: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=customer_roi[['销售总额', '物料总成本']].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从高到低排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="ROI",
                len=0.5,
                thickness=15,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了投入产出比(ROI)最高的前10名客户。ROI是销售额与物料成本的比值，表示每投入1元物料成本产生的销售额。ROI越高，表示物料使用效率越高。"),
            html.P("注意: 此图表只包含物料成本超过1000元的客户，避免小额投入造成的ROI虚高。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看客户详细的ROI、销售总额和物料成本"),
                html.Li("分析高ROI客户的物料使用和销售策略，总结成功经验"),
                html.Li("考虑将更多物料资源向高ROI客户倾斜，提高整体投资回报"),
                html.Li("比较高ROI客户与高销售额客户的重合度，找出最具价值的核心客户")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 物料投放效果评估图表
    @app.callback(
        Output("material-effectiveness-chart", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_material_effectiveness_chart(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建更现代化的图表 - 散点图
        fig = px.scatter(
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
            color_continuous_scale='viridis',  # 使用科学可视化专业配色
            opacity=0.8,
            size_max=50  # 控制气泡最大尺寸
        )

        # 增强悬停信息
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                          '物料数量: %{x:,}件<br>' +
                          '销售总额: ¥%{y:,.2f}<br>' +
                          '物料成本: ¥%{marker.size:,.2f}<br>' +
                          '物料效益: ¥%{marker.color:.2f}/件<br>' +
                          '月份: %{customdata}<extra></extra>',
            customdata=effectiveness_data['发运月份'].dt.strftime('%Y-%m').values
        )

        # 添加趋势线
        import numpy as np
        from scipy import stats

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

        # 添加回归线
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=y_range,
                mode='lines',
                line=dict(color='rgba(255, 99, 132, 0.8)', width=2, dash='dash'),
                name=f'趋势线 (r²={r_value ** 2:.2f})',
                hoverinfo='skip'
            )
        )

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="物料效益",
                tickprefix="¥",
                ticksuffix="/件",
                len=0.75,
                thickness=15,
                y=0.5
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该散点图展示了物料投放量与销售额之间的关系。每个点代表一个客户的某月表现，点的大小表示物料成本，颜色表示物料效益(销售额/物料数量)。"),
            html.P(
                f"红色虚线是趋势线，显示了物料投放量与销售额的一般关系。决定系数(r²)为{r_value ** 2:.2f}，表示物料投放量与销售额的相关程度。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的客户名称、物料数量、销售额、物料成本和物料效益"),
                html.Li("关注位于趋势线上方的点，这些是物料使用效率高于平均的客户和月份"),
                html.Li("大而明亮的点表示物料成本高且效益好的情况，值得学习"),
                html.Li("小而暗淡的点表示物料成本低且效益较差的情况，需要改进")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 物料与销售相关性图表
    @app.callback(
        Output("material-sales-correlation", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_material_sales_correlation(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建更现代化的横条图
        fig = px.bar(
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
            color_continuous_scale='teal',  # 使用青色渐变配色
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='¥%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '单位物料销售额: ¥%{x:.2f}/件<br>' +
                          '总销售额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料总数量: %{customdata[1]:,}件<extra></extra>',
            customdata=material_sales_corr[['销售总额', '物料数量']].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从高到低排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="单位销售额",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表展示了每种物料带来的单位销售额排名。横条越长，表示该物料每单位带来的销售额越高，效益越好。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的单位物料销售额、总销售额和物料总数量"),
                html.Li("分析排名靠前的物料特点，了解为什么这些物料能带来更高的销售额"),
                html.Li("考虑增加高效益物料的投入，减少低效益物料的使用"),
                html.Li("结合物料成本信息，进一步计算投资回报率")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 省份销售热力图
    @app.callback(
        Output("province-sales-map", "figure"),
        [Input("region-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_province_sales_map(selected_regions, start_date, end_date):
        filtered_sales = filter_data(df_sales, selected_regions, None, start_date, end_date)

        province_sales = filtered_sales.groupby('省份').agg({
            '销售总额': 'sum'
        }).reset_index()

        # 创建一个现代化的条形图（替代热力图，因为缺少地理坐标数据）
        fig = px.bar(
            province_sales.sort_values('销售总额', ascending=False),
            x='省份',
            y='销售总额',
            color='销售总额',
            color_continuous_scale='Reds',  # 使用红色渐变色表示热度
            text='销售总额',
            labels={
                '销售总额': '销售总额 (元)',
                '省份': '省份'
            }
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='¥%{text:,.0f}',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '销售总额: ¥%{y:,.2f}<extra></extra>'
        )

        # 美化布局
        fig.update_layout(
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
            margin=dict(l=40, r=40, t=80, b=80),  # 增加底部空间，避免标签重叠
            xaxis={
                'title': '省份',
                'tickangle': -45,  # 倾斜标签避免重叠
                'categoryorder': 'total descending'  # 从高到低排序
            },
            yaxis={
                'title': '销售总额 (元)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickprefix': '¥',
                'tickformat': ',.0f'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="销售额",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表展示了各省份的销售额分布。柱形越高，颜色越深，表示该省份销售额越大。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的省份销售额数据"),
                html.Li("关注销售额较高的省份，确保资源投入充足"),
                html.Li("分析销售额较低的省份，寻找增长机会"),
                html.Li("结合区域划分，评估区域销售策略的效果")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 城市物料分布图
    @app.callback(
        Output("city-material-map", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_city_material_map(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)

        city_material = filtered_material.groupby('城市').agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        # 只显示前15个城市，避免图表过于拥挤
        top_cities = city_material.sort_values('物料数量', ascending=False).head(15)

        # 创建现代化条形图
        fig = px.bar(
            top_cities,
            x='城市',
            y='物料数量',
            color='物料总成本',
            color_continuous_scale='Blues',  # 蓝色渐变表示物料成本
            text='物料数量',
            labels={
                '物料数量': '物料数量 (件)',
                '城市': '城市',
                '物料总成本': '物料总成本 (元)'
            }
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:,}件',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '物料数量: %{y:,}件<br>' +
                          '物料总成本: ¥%{marker.color:,.2f}<extra></extra>'
        )

        # 美化布局
        fig.update_layout(
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
            margin=dict(l=40, r=40, t=80, b=80),  # 增加底部空间
            xaxis={
                'title': '城市',
                'tickangle': -45,  # 倾斜标签避免重叠
                'categoryorder': 'total descending'  # 从高到低排序
            },
            yaxis={
                'title': '物料数量 (件)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'tickformat': ',d'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="物料成本",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了物料数量最多的前15个城市。柱形高度表示物料数量，颜色深浅表示物料总成本，颜色越深表示成本越高。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的物料数量和总成本数据"),
                html.Li("注意对比物料数量和物料成本的关系，颜色较浅但高度较高的城市表示单位物料成本较低"),
                html.Li("结合销售数据分析各城市物料使用效率"),
                html.Li("关注物料投入较多的城市，评估物料分配是否合理")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 物料-产品关联热力图
    @app.callback(
        Output("material-product-heatmap", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_material_product_heatmap(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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
        top_materials = material_product_sales.groupby('物料名称')['销售总额'].sum().nlargest(8).index
        top_products = material_product_sales.groupby('产品名称')['销售总额'].sum().nlargest(8).index

        # 筛选数据
        filtered_pivot = pivot_data.loc[pivot_data.index.isin(top_materials), pivot_data.columns.isin(top_products)]

        # 创建现代化热力图
        fig = px.imshow(
            filtered_pivot,
            labels=dict(x="产品名称", y="物料名称", color="销售总额 (元)"),
            x=filtered_pivot.columns,
            y=filtered_pivot.index,
            color_continuous_scale='YlGnBu',  # 使用黄绿蓝渐变色
            text_auto='.2s',  # 显示数值，使用科学计数法简化大数字
            aspect="auto"  # 自动调整宽高比，避免过度拉伸
        )

        # 增强热力图
        fig.update_traces(
            hovertemplate='<b>物料名称: %{y}</b><br>' +
                          '<b>产品名称: %{x}</b><br>' +
                          '销售总额: ¥%{z:,.2f}<extra></extra>',
            showscale=True
        )

        # 美化布局
        fig.update_layout(
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
                'tickangle': -45,  # 倾斜标签避免重叠
                'side': 'bottom'
            },
            yaxis={
                'title': '物料名称',
                'tickangle': 0
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="销售总额",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该热力图展示了物料与产品之间的关联强度，颜色越深表示该组合带来的销售额越高。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看具体物料-产品组合的销售总额数据"),
                html.Li("关注颜色最深的组合，了解哪些物料对哪些产品的销售贡献最大"),
                html.Li("分析同一物料对不同产品的促销效果差异"),
                html.Li("根据热力图结果优化物料分配，提高销售效率")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 最佳物料组合图表
    @app.callback(
        Output("best-material-combinations", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_best_material_combinations(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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
            '销售总额': 'mean'  # 使用平均值，因为每个客户-月份组合只有一个销售总额
        }).reset_index()

        # 分析物料组合表现
        combo_performance = material_combinations.groupby('物料名称').agg({
            '销售总额': ['mean', 'count']
        }).reset_index()

        combo_performance.columns = ['物料组合', '平均销售额', '使用次数']

        # 筛选使用次数>1的组合，并按平均销售额排序
        top_combos = combo_performance[combo_performance['使用次数'] > 1].sort_values('平均销售额',
                                                                                      ascending=False).head(10)

        # 创建现代化的横向条形图
        fig = px.bar(
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
            color_continuous_scale='Teal',  # 青色渐变表示使用频率
            hover_data=['使用次数']
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='¥%{text:,.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '平均销售额: ¥%{x:,.2f}<br>' +
                          '使用次数: %{customdata[0]}<extra></extra>',
            customdata=top_combos[['使用次数']].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从大到小排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="使用次数",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了平均销售额最高的物料组合。横条越长表示该组合平均产生的销售额越高，颜色越深表示该组合被使用的次数越多。"),
            html.P("注意: 只显示使用次数大于1的组合，以确保结果可靠性。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看组合的平均销售额和使用次数"),
                html.Li("关注排名靠前的物料组合，分析它们的共同特点"),
                html.Li("结合使用次数评估结果可靠性，使用次数越多越可靠"),
                html.Li("考虑推广表现最佳的物料组合，提高整体销售效果")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 经销商销售效率图表
    @app.callback(
        Output("distributor-efficiency", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_distributor_efficiency(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建现代化的横向条形图
        fig = px.bar(
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
            color_continuous_scale='Purples',  # 使用紫色渐变表示销售规模
            hover_data=['销售总额', '物料数量']
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='¥%{text:.2f}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>' +
                          '销售效率: ¥%{x:.2f}/件<br>' +
                          '销售总额: ¥%{customdata[0]:,.2f}<br>' +
                          '物料数量: %{customdata[1]:,}件<extra></extra>',
            customdata=top_distributors[['销售总额', '物料数量']].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从大到小排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="销售总额",
                tickprefix="¥",
                len=0.5,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了销售效率最高的前10名经销商。销售效率是销售总额与物料数量的比值，表示单位物料带来的销售额。"),
            html.P("横条越长表示效率越高，颜色越深表示销售总额越大。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看经销商的销售效率、销售总额和物料数量"),
                html.Li("关注既有高销售效率又有高销售总额（颜色深）的经销商，他们是最有价值的合作伙伴"),
                html.Li("分析高效率经销商的物料使用策略，用于培训其他经销商"),
                html.Li("考虑向高效率经销商倾斜更多资源，提高整体投资回报")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 经销商物料使用情况图表
    @app.callback(
        Output("distributor-material-usage", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_distributor_material_usage(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)

        # 获取数量最多的物料类型
        top_materials = filtered_material.groupby('物料名称')['物料数量'].sum().nlargest(5).index.tolist()

        # 筛选数据
        filtered_for_chart = filtered_material[filtered_material['物料名称'].isin(top_materials)]

        # 分析经销商物料使用情况
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

        # 创建现代化的堆叠水平条形图
        fig = px.bar(
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
            barmode='stack',  # 堆叠模式
            color_discrete_sequence=px.colors.qualitative.Bold  # 使用醒目的颜色区分物料
        )

        # 增强悬停信息
        fig.update_traces(
            hovertemplate='<b>%{y}</b><br>' +
                          '物料类型: %{customdata}<br>' +
                          '物料数量: %{x:,}件<extra></extra>',
            customdata=melted_data['物料名称'].values
        )

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从大到小排序
                'categoryorder': 'total ascending'
            },
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,  # 将图例放在图表下方
                xanchor="center",
                x=0.5,
                title=""
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表展示了前10名经销商使用的前5种物料分布情况。每个横条代表一个经销商，不同颜色代表不同物料类型。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的物料类型和数量"),
                html.Li("观察经销商物料使用的多样性，使用物料种类越多的颜色越丰富"),
                html.Li("分析顶级经销商的物料偏好，了解他们的成功策略"),
                html.Li("比较相似规模经销商的物料组合差异，找出最佳实践")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 区域费比分析图表
    @app.callback(
        Output("region-cost-sales-analysis", "figure"),
        [Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_region_cost_sales_analysis(start_date, end_date):
        filtered_material = filter_date_data(df_material, start_date, end_date)
        filtered_sales = filter_date_data(df_sales, start_date, end_date)

        region_material = filtered_material.groupby('所属区域').agg({
            '物料总成本': 'sum'
        }).reset_index()

        region_sales = filtered_sales.groupby('所属区域').agg({
            '销售总额': 'sum'
        }).reset_index()

        region_cost_sales = pd.merge(region_material, region_sales, on='所属区域', how='outer')
        region_cost_sales['费比'] = (region_cost_sales['物料总成本'] / region_cost_sales['销售总额']) * 100

        # 添加辅助列以便于绘制散点图
        region_cost_sales['销售额百分比'] = region_cost_sales['销售总额'] / region_cost_sales['销售总额'].sum() * 100

        # 创建现代化的气泡图
        fig = px.scatter(
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
            size_max=60,  # 控制气泡最大尺寸
            color_discrete_sequence=px.colors.qualitative.Safe  # 使用适合色盲的配色方案
        )

        # 增强悬停信息
        fig.update_traces(
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>' +
                          '销售贡献度: %{x:.2f}%<br>' +
                          '费比: %{y:.2f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=region_cost_sales[['物料总成本', '销售总额']].values
        )

        # 添加参考线 - 平均费比
        avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales['销售总额'].sum()) * 100
        fig.add_hline(
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

        # 添加象限区域（使用区域背景色）
        fig.add_shape(
            type="rect",
            x0=0,
            y0=0,
            x1=region_cost_sales['销售额百分比'].max() * 1.1,
            y1=avg_cost_sales_ratio,
            fillcolor="rgba(144, 238, 144, 0.15)",  # 浅绿色（低费比区域）
            line=dict(width=0),
            layer="below"
        )
        fig.add_shape(
            type="rect",
            x0=0,
            y0=avg_cost_sales_ratio,
            x1=region_cost_sales['销售额百分比'].max() * 1.1,
            y1=region_cost_sales['费比'].max() * 1.1,
            fillcolor="rgba(255, 182, 193, 0.15)",  # 浅红色（高费比区域）
            line=dict(width=0),
            layer="below"
        )

        # 美化布局
        fig.update_layout(
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
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                title=""
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该气泡图展示了各区域的费比与销售贡献度的关系。横轴表示区域销售额占总销售额的百分比，纵轴表示费比(物料成本/销售额)，气泡大小表示物料总成本。"),
            html.P("红色虚线表示平均费比，绿色区域表示费比低于平均（良好），粉色区域表示费比高于平均（需改进）。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的区域、销售贡献度、费比、物料成本和销售总额数据"),
                html.Li("理想情况是气泡位于绿色区域且靠右侧，表示费比低且销售贡献大"),
                html.Li("重点关注位于粉色区域右侧的大气泡，这些区域费比高且销售额大，改进空间大"),
                html.Li("分析不同区域间的差异，找出费比低的区域的成功经验")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 销售人员费比分析图表
    @app.callback(
        Output("salesperson-cost-sales-analysis", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_salesperson_cost_sales_analysis(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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
            '销售总额'].sum()) * 100

        # 创建现代化的条形图
        fig = px.bar(
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
            color_continuous_scale='RdYlGn_r',  # 红色表示高费比(不好)，绿色表示低费比(好)
            hover_data=['物料总成本', '销售总额']
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>' +
                          '费比: %{y:.2f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=top_salespersons[['物料总成本', '销售总额']].values
        )

        # 添加平均费比线
        fig.add_hline(
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

        # 美化布局
        fig.update_layout(
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
            margin=dict(l=40, r=40, t=80, b=100),  # 增加底部空间
            xaxis={
                'title': '销售人员',
                'tickangle': -45,  # 倾斜标签避免重叠
                'categoryorder': 'total ascending'  # 按总费比排序
            },
            yaxis={
                'title': '费比 (%)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'ticksuffix': '%'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="费比",
                ticksuffix="%",
                tickfont=dict(size=12),
                len=0.5,
                thickness=15,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了费比最低的15名销售人员。费比是物料成本占销售额的百分比，费比越低表示销售人员使用物料的效率越高。"),
            html.P("颜色说明: 绿色表示费比较低（好），红色表示费比较高（需要改进）。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("红色虚线表示全公司平均费比基准线"),
                html.Li("鼠标悬停可查看详细的费比、物料成本和销售总额数据"),
                html.Li("分析费比低的销售人员使用物料的策略，作为最佳实践推广"),
                html.Li("考虑为费比过高的销售人员提供培训，提高物料使用效率")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 经销商费比分析图表
    @app.callback(
        Output("distributor-cost-sales-analysis", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_distributor_cost_sales_analysis(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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
        upper_limit = distributor_cost_sales['费比'].quantile(0.95)  # 只保留95%分位数以内的数据
        distributor_cost_sales = distributor_cost_sales[distributor_cost_sales['费比'] <= upper_limit]

        # 选择每个区域费比最低的3个经销商，总共不超过15个
        top_distributors = []
        for region in distributor_cost_sales['所属区域'].unique():
            region_distributors = distributor_cost_sales[distributor_cost_sales['所属区域'] == region]
            top_region = region_distributors.sort_values('费比').head(3)
            top_distributors.append(top_region)

        top_distributors_df = pd.concat(top_distributors).sort_values(['所属区域', '费比'])

        # 计算平均费比
        avg_cost_sales_ratio = (distributor_cost_sales['物料总成本'].sum() / distributor_cost_sales[
            '销售总额'].sum()) * 100

        # 创建现代化的分组条形图
        fig = px.bar(
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
            barmode='group',  # 分组模式，同一区域经销商并排展示
            color_discrete_sequence=px.colors.qualitative.Pastel  # 使用柔和的颜色区分区域
        )

        # 增强悬停信息
        fig.update_traces(
            texttemplate='%{text:.2f}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b> (%{customdata[2]})<br>' +
                          '费比: %{y:.2f}%<br>' +
                          '物料成本: ¥%{customdata[0]:,.2f}<br>' +
                          '销售总额: ¥%{customdata[1]:,.2f}<extra></extra>',
            customdata=top_distributors_df[['物料总成本', '销售总额', '所属区域']].values
        )

        # 添加平均费比线
        fig.add_hline(
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

        # 美化布局
        fig.update_layout(
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
            margin=dict(l=40, r=40, t=80, b=120),  # 增加底部空间
            xaxis={
                'title': '经销商',
                'tickangle': -45,  # 倾斜标签避免重叠
            },
            yaxis={
                'title': '费比 (%)',
                'showgrid': True,
                'gridcolor': '#f4f4f4',
                'ticksuffix': '%'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,  # 将图例放在图表下方
                xanchor="center",
                x=0.5,
                title=""
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P("该图表展示了每个区域费比最低的经销商。费比越低表示经销商使用物料的效率越高，创造的销售价值越大。"),
            html.P("不同颜色代表不同区域，同一区域的经销商并排展示，便于区域内和区域间比较。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("红色虚线表示全公司平均费比基准线"),
                html.Li("鼠标悬停可查看详细的经销商、区域、费比、物料成本和销售总额数据"),
                html.Li("分析低费比经销商的成功经验，形成可复制的最佳实践"),
                html.Li("比较不同区域的费比水平，找出区域间的差异和改进空间")
            ])
        ], className="chart-explanation mt-3")

        return fig

    # 费比异常值提醒
    @app.callback(
        Output("cost-sales-anomalies", "children"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_cost_sales_anomalies(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

        # 计算总体费比
        total_material_cost = filtered_material['物料总成本'].sum()
        total_sales = filtered_sales['销售总额'].sum()
        overall_cost_sales_ratio = (total_material_cost / total_sales) * 100

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
            # 创建现代化的异常值警告卡片
            anomaly_cards = []
            for i, (_, row) in enumerate(anomalies.iterrows()):
                # 每行最多放3个卡片
                if i % 3 == 0:
                    card_row = dbc.Row([], className="mb-2")
                    anomaly_cards.append(card_row)

                # 计算异常程度
                anomaly_level = row['费比'] / overall_cost_sales_ratio

                # 根据异常程度设置不同颜色
                if anomaly_level > 2:
                    card_color = "danger"  # 严重异常 - 红色
                else:
                    card_color = "warning"  # 中等异常 - 黄色

                card = dbc.Col(
                    dbc.Card([
                        dbc.CardHeader(
                            html.H6(row['经销商名称'], className="m-0"),
                            style={"background-color": "#f8d7da" if card_color == "danger" else "#fff3cd"}
                        ),
                        dbc.CardBody([
                            html.P([
                                html.Strong("费比: "),
                                f"{row['费比']:.2f}% ",
                                html.Span(
                                    f"(高出平均{anomaly_level:.1f}倍)",
                                    style={"color": "red", "font-weight": "bold"}
                                )
                            ]),
                            html.P([html.Strong("物料成本: "), f"¥{row['物料总成本']:,.2f}"]),
                            html.P([html.Strong("销售额: "), f"¥{row['销售总额']:,.2f}"])
                        ])
                    ], color=card_color, outline=True),
                    width=4  # 每行3个卡片
                )

                anomaly_cards[-1].children.append(card)

            # 确保最后一行卡片也是满的，添加空卡片填充
            if len(anomaly_cards[-1].children) < 3:
                for _ in range(3 - len(anomaly_cards[-1].children)):
                    anomaly_cards[-1].children.append(dbc.Col(width=4))

            # 添加总结和建议
            summary = dbc.Card([
                dbc.CardHeader(html.H5("费比异常分析总结", className="m-0")),
                dbc.CardBody([
                    html.P([
                        f"共发现 {len(anomalies)} 个费比异常值。平均费比为 ",
                        html.Strong(f"{overall_cost_sales_ratio:.2f}%"),
                        "，但这些经销商的费比远高于平均值。"
                    ]),
                    html.P("可能的原因:"),
                    html.Ul([
                        html.Li("物料使用效率低，未转化为有效销售"),
                        html.Li("销售策略不当，导致投入产出比不佳"),
                        html.Li("物料分配不合理，未针对客户需求定制")
                    ]),
                    html.P("建议行动:"),
                    html.Ul([
                        html.Li("与这些经销商沟通，了解物料使用情况"),
                        html.Li("提供针对性培训，提高物料使用效率"),
                        html.Li("调整物料分配策略，减少费比异常高的经销商的物料投入")
                    ])
                ])
            ], color="info", className="mt-3")

            return [
                html.H5(f"费比异常值警告 ({len(anomalies)}个)", className="alert-heading"),
                html.Hr(),
                *anomaly_cards,
                summary
            ]
        else:
            # 返回正面信息卡片
            positive_card = dbc.Card([
                dbc.CardHeader(html.H5("良好费比控制", className="text-success m-0")),
                dbc.CardBody([
                    html.P([
                        "恭喜! 未发现费比异常值。所有经销商的费比都在平均值的1.5倍范围内，表明物料使用效率整体良好。"
                    ]),
                    html.P([
                        "当前平均费比为 ",
                        html.Strong(f"{overall_cost_sales_ratio:.2f}%"),
                        "，继续保持这一水平将有利于提高整体投资回报率。"
                    ]),
                    html.P("建议行动:"),
                    html.Ul([
                        html.Li("分享优秀经销商的物料使用经验"),
                        html.Li("继续监控费比变化趋势，及时发现潜在问题"),
                        html.Li("探索进一步优化物料投放策略的机会")
                    ])
                ])
            ], color="success")

            return positive_card

    # 物料ROI分析图表
    @app.callback(
        Output("material-roi-analysis", "figure"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_material_roi_analysis(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 创建现代化的横向条形图
        fig = px.bar(
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
            color_continuous_scale='Viridis',  # 使用科学可视化专业配色
            hover_data=['物料总成本', '销售总额', '物料数量']
        )

        # 增强悬停信息
        fig.update_traces(
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
        avg_roi = material_roi['销售总额'].sum() / material_roi['物料总成本'].sum()

        # 添加平均ROI线
        fig.add_vline(
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

        # 美化布局
        fig.update_layout(
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
                'autorange': 'reversed',  # 从高到低排序
                'categoryorder': 'total ascending'
            },
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            coloraxis_colorbar=dict(
                title="ROI",
                len=0.5,
                thickness=15,
                y=0.5
            )
        )

        # 添加图表解释
        chart_explanation = html.Div([
            html.H6("图表解读:", className="mt-2"),
            html.P(
                "该图表展示了投资回报率(ROI)最高的物料。ROI是销售额与物料成本的比值，表示每投入1元物料成本产生的销售额。"),
            html.P(f"绿色虚线表示平均ROI（{avg_roi:.2f}），显示所有物料的整体表现水平。"),
            html.P("注意: 此图表只包含物料成本>1000元且销售额>10000元的物料，以确保结果可靠性。"),
            html.P("使用提示:", style={"font-weight": "bold"}),
            html.Ul([
                html.Li("鼠标悬停可查看详细的ROI、物料成本、销售总额和物料数量"),
                html.Li("关注ROI高于平均线的物料，这些是最值得投资的物料"),
                html.Li("分析高ROI物料的特点，了解为什么它们比其他物料更有效"),
                html.Li("建议增加高ROI物料的投入，减少低ROI物料的使用，提高整体投资回报")
            ])
        ], className="chart-explanation mt-3")

        return fig
    # 最优物料分配建议
    @app.callback(
        Output("optimal-material-allocation", "children"),
        [Input("region-filter", "value"),
         Input("province-filter", "value"),
         Input("date-filter", "start_date"),
         Input("date-filter", "end_date")]
    )
    def update_optimal_material_allocation(selected_regions, selected_provinces, start_date, end_date):
        filtered_material = filter_data(df_material, selected_regions, selected_provinces, start_date, end_date)
        filtered_sales = filter_data(df_sales, selected_regions, selected_provinces, start_date, end_date)

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

        # 剔除极端异常值，保留可视化效果
        upper_limit = material_roi['ROI'].quantile(0.95)  # 只保留95%分位数以内的数据
        material_roi = material_roi[material_roi['ROI'] <= upper_limit]

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

        # 分析高效和低效物料
        high_roi_materials = material_roi.sort_values('ROI', ascending=False).head(5)
        low_roi_materials = material_roi.sort_values('ROI').head(5)

        # 计算整体ROI
        total_material_cost = filtered_material['物料总成本'].sum()
        total_sales = filtered_sales['销售总额'].sum()
        overall_roi = total_sales / total_material_cost

        # 创建现代化的信息卡片布局
        # 1. 现状分析卡片
        status_card = dbc.Card([
            dbc.CardHeader(html.H5("物料投入现状分析", className="m-0")),
            dbc.CardBody([
                html.P([
                    "当前整体ROI: ",
                    html.Strong(f"{overall_roi:.2f}"),
                    f" (总销售额: ¥{total_sales:,.2f} / 总物料成本: ¥{total_material_cost:,.2f})"
                ]),
                dbc.Progress(
                    value=int(overall_roi * 10) if overall_roi <= 10 else 100,  # 将ROI转换为进度条
                    color="success" if overall_roi >= 5 else "warning" if overall_roi >= 3 else "danger",
                    className="mb-3",
                    style={"height": "20px"}
                ),
                html.P("通过优化物料分配，预估可将整体ROI提高15-20%，直接提升销售业绩。"),
            ])
        ], className="mb-3")

        # 2. 高ROI物料卡片
        high_roi_card = dbc.Card([
            dbc.CardHeader(html.H5("高ROI物料 (建议增加投放)", className="text-success m-0")),
            dbc.CardBody([
                dbc.ListGroup([
                    dbc.ListGroupItem([
                        html.Div([
                            html.H6(row['物料名称'], className="d-flex justify-content-between"),
                            html.Div([
                                html.Span("ROI: ", className="font-weight-bold"),
                                html.Span(f"{row['ROI']:.2f}", className="text-success")
                            ], className="d-flex justify-content-between"),
                            html.Small([
                                f"投入: ¥{row['物料总成本']:,.2f} | ",
                                f"销售: ¥{row['销售总额']:,.2f} | ",
                                f"数量: {row['物料数量']:,}件"
                            ], className="text-muted"),
                            dbc.Progress(
                                value=int(row['ROI'] * 10) if row['ROI'] <= 10 else 100,
                                color="success",
                                className="mt-2",
                                style={"height": "8px"}
                            )
                        ])
                    ], className="border-left border-success border-3")
                    for _, row in high_roi_materials.iterrows()
                ])
            ])
        ], className="mb-3")

        # 3. 低ROI物料卡片
        low_roi_card = dbc.Card([
            dbc.CardHeader(html.H5("低ROI物料 (建议减少或优化投放)", className="text-danger m-0")),
            dbc.CardBody([
                dbc.ListGroup([
                    dbc.ListGroupItem([
                        html.Div([
                            html.H6(row['物料名称'], className="d-flex justify-content-between"),
                            html.Div([
                                html.Span("ROI: ", className="font-weight-bold"),
                                html.Span(f"{row['ROI']:.2f}", className="text-danger")
                            ], className="d-flex justify-content-between"),
                            html.Small([
                                f"投入: ¥{row['物料总成本']:,.2f} | ",
                                f"销售: ¥{row['销售总额']:,.2f} | ",
                                f"数量: {row['物料数量']:,}件"
                            ], className="text-muted"),
                            dbc.Progress(
                                value=int(row['ROI'] * 10) if row['ROI'] <= 10 else 100,
                                color="danger",
                                className="mt-2",
                                style={"height": "8px"}
                            )
                        ])
                    ], className="border-left border-danger border-3")
                    for _, row in low_roi_materials.iterrows()
                ])
            ])
        ], className="mb-3")

        # 4. 优化建议卡片
        if len(customer_material_effect) > 0:
            # 找到物料ROI表现最好的客户
            best_customer_material = customer_material_effect.sort_values('ROI', ascending=False).head(3)

            optimization_card = dbc.Card([
                dbc.CardHeader(html.H5("最佳实践与优化建议", className="m-0")),
                dbc.CardBody([
                    html.H6("最佳客户-物料组合:", className="mb-3"),
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            html.Div([
                                html.H6([
                                    f"经销商 '{row['经销商名称']}' + '{row['物料名称']}'",
                                ], className="d-flex justify-content-between"),
                                html.Div([
                                    html.Span("ROI: ", className="font-weight-bold"),
                                    html.Span(f"{row['ROI']:.2f}", className="text-primary")
                                ], className="d-flex justify-content-between"),
                                html.Small([
                                    f"投入: ¥{row['物料总成本']:,.2f} | ",
                                    f"销售: ¥{row['销售总额']:,.2f}"
                                ], className="text-muted")
                            ])
                        ], className="border-left border-primary border-3")
                        for _, row in best_customer_material.iterrows()
                    ]),
                    html.Hr(),
                    html.H6("优化策略:", className="mb-2 mt-4"),
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            html.Strong("投资重分配: "),
                            "将物料预算从低ROI物料重新分配到高ROI物料，预计可提高整体ROI 15-20%"
                        ]),
                        dbc.ListGroupItem([
                            html.Strong("客户定制策略: "),
                            "根据最佳客户-物料组合的模式，为不同客户提供定制化的物料配置"
                        ]),
                        dbc.ListGroupItem([
                            html.Strong("培训提升: "),
                            "向所有销售人员和经销商分享高ROI物料的最佳使用方式"
                        ]),
                        dbc.ListGroupItem([
                            html.Strong("持续监控: "),
                            "定期评估各物料ROI变化，及时调整投资策略"
                        ])
                    ])
                ])
            ])
        else:
            optimization_card = dbc.Card([
                dbc.CardHeader(html.H5("优化建议", className="m-0")),
                dbc.CardBody([
                    html.P("暂无足够数据生成客户-物料组合分析，请确保数据完整性或调整筛选条件。"),
                    html.Hr(),
                    html.H6("一般优化策略:", className="mb-2"),
                    dbc.ListGroup([
                        dbc.ListGroupItem([
                            html.Strong("投资重分配: "),
                            "将物料预算从低ROI物料重新分配到高ROI物料"
                        ]),
                        dbc.ListGroupItem([
                            html.Strong("持续监控: "),
                            "定期评估各物料ROI变化，及时调整投资策略"
                        ])
                    ])
                ])
            ])

        # 合并所有卡片
        return [
            html.H5("最优物料分配策略", className="mb-3 text-primary"),
            status_card,
            dbc.Row([
                dbc.Col(high_roi_card, width=6),
                dbc.Col(low_roi_card, width=6)
            ]),
            optimization_card
        ]

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

    # 辅助函数：只按日期筛选数据
    def filter_date_data(df, start_date=None, end_date=None):
        filtered_df = df.copy()

        if start_date and end_date:
            filtered_df = filtered_df[(filtered_df['发运月份'] >= pd.to_datetime(start_date)) &
                                      (filtered_df['发运月份'] <= pd.to_datetime(end_date))]

        return filtered_df

    return app


# 主函数
def main():
    # 加载数据
    df_material, df_sales, df_material_price = load_data()

    # 创建聚合数据
    aggregations = create_aggregations(df_material, df_sales)

    # 创建仪表盘
    app = create_dashboard(df_material, df_sales, aggregations)

    # 运行仪表盘
    app.run_server(debug=True)


if __name__ == "__main__":
    main()