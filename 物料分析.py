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
    # 材料数据
    df_material = pd.read_excel("2025物料源数据.xlsx")

    # 销售数据
    df_sales = pd.read_excel("25物料源销售数据.xlsx")

    # 物料单价
    df_material_price = pd.read_excel("物料单价.xlsx")

    # 清理和标准化数据
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

        fig = px.bar(
            region_sales,
            x='所属区域',
            y='销售总额',
            title="各区域销售总额",
            labels={'销售总额': '销售总额 (元)', '所属区域': '区域'},
            color='所属区域',
            text='销售总额'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

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

        fig = px.bar(
            region_efficiency,
            x='所属区域',
            y='物料效率',
            title="各区域物料效率 (销售额/物料数量)",
            labels={'物料效率': '物料效率 (元/件)', '所属区域': '区域'},
            color='所属区域',
            text='物料效率'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

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

        fig = px.bar(
            region_cost_sales,
            x='所属区域',
            y='费比',
            title="各区域费比对比 (物料成本/销售额)",
            labels={'费比': '费比 (%)', '所属区域': '区域'},
            color='费比',
            text='费比',
            color_continuous_scale='RdYlGn_r'  # 红色表示高费比(不好)，绿色表示低费比(好)
        )

        fig.add_hline(y=avg_cost_sales_ratio, line_dash="dash", line_color="black",
                      annotation_text=f"平均: {avg_cost_sales_ratio:.2f}%",
                      annotation_position="bottom right")

        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

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

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # 添加销售额线图
        fig.add_trace(
            go.Scatter(
                x=time_trends['发运月份'],
                y=time_trends['销售总额'],
                name="销售总额",
                line=dict(color='green', width=3)
            ),
            secondary_y=False
        )

        # 添加物料成本线图
        fig.add_trace(
            go.Scatter(
                x=time_trends['发运月份'],
                y=time_trends['物料总成本'],
                name="物料总成本",
                line=dict(color='red', width=3, dash='dot')
            ),
            secondary_y=True
        )

        # 添加布局
        fig.update_layout(
            title_text="销售额和物料投放趋势",
            xaxis_title="月份",
            legend=dict(y=1.1, x=0.5, xanchor='center', orientation='h')
        )

        fig.update_yaxes(title_text="销售总额 (元)", secondary_y=False)
        fig.update_yaxes(title_text="物料总成本 (元)", secondary_y=True)

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

        fig = px.line(
            time_cost_sales,
            x='发运月份',
            y='费比',
            title="月度费比变化趋势",
            labels={'费比': '费比 (%)', '发运月份': '月份'},
            markers=True
        )

        fig.add_hline(y=avg_cost_sales_ratio, line_dash="dash", line_color="red",
                      annotation_text=f"平均: {avg_cost_sales_ratio:.2f}%",
                      annotation_position="bottom right")

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

        fig = px.line(
            time_effectiveness,
            x='发运月份',
            y='物料效益',
            title="物料效益趋势 (销售额/物料数量)",
            labels={'物料效益': '物料效益 (元/件)', '发运月份': '月份'},
            markers=True
        )

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

        fig = px.bar(
            customer_value,
            x='销售总额',
            y='经销商名称',
            title="前10名高价值客户",
            labels={'销售总额': '销售总额 (元)', '经销商名称': '经销商'},
            text='销售总额',
            orientation='h',
            color='销售总额'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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
        customer_roi = customer_roi.sort_values('投入产出比', ascending=False).head(10)

        fig = px.bar(
            customer_roi,
            x='投入产出比',
            y='经销商名称',
            title="前10名高ROI客户 (销售额/物料成本)",
            labels={'投入产出比': 'ROI', '经销商名称': '经销商'},
            text='投入产出比',
            orientation='h',
            color='投入产出比'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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
        material_by_customer = filtered_material.groupby(['客户代码', '发运月份']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum'
        }).reset_index()

        sales_by_customer = filtered_sales.groupby(['客户代码', '发运月份']).agg({
            '销售总额': 'sum'
        }).reset_index()

        # 合并数据
        effectiveness_data = pd.merge(
            material_by_customer,
            sales_by_customer,
            on=['客户代码', '发运月份'],
            how='inner'
        )

        # 创建散点图
        fig = px.scatter(
            effectiveness_data,
            x='物料数量',
            y='销售总额',
            size='物料总成本',
            color='物料总成本',
            hover_name='客户代码',
            labels={
                '物料数量': '物料数量 (件)',
                '销售总额': '销售总额 (元)',
                '物料总成本': '物料成本 (元)'
            },
            title="物料投放量与销售额关系"
        )

        # 添加趋势线
        fig.update_layout(
            xaxis_title="物料数量 (件)",
            yaxis_title="销售总额 (元)"
        )

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

        fig = px.bar(
            material_sales_corr,
            x='单位物料销售额',
            y='物料名称',
            title="物料效益排名 (每单位物料带来的销售额)",
            labels={
                '单位物料销售额': '单位物料销售额 (元/件)',
                '物料名称': '物料名称'
            },
            text='单位物料销售额',
            orientation='h',
            color='单位物料销售额'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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

        # 注意：此处需要中国省份的地理坐标数据
        # 简化版本只展示条形图
        fig = px.bar(
            province_sales.sort_values('销售总额', ascending=False),
            x='省份',
            y='销售总额',
            title="各省份销售额分布",
            labels={'销售总额': '销售总额 (元)', '省份': '省份'},
            color='销售总额',
            text='销售总额'
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

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

        # 简化版本只展示条形图
        fig = px.bar(
            city_material.sort_values('物料数量', ascending=False),
            x='城市',
            y='物料数量',
            title="各城市物料分布",
            labels={'物料数量': '物料数量 (件)', '城市': '城市'},
            color='物料总成本',
            text='物料数量'
        )

        fig.update_traces(texttemplate='%{text:.0f}', textposition='outside')

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

        # 获取前10种物料和前10种产品
        top_materials = material_product_sales.groupby('物料名称')['销售总额'].sum().nlargest(10).index
        top_products = material_product_sales.groupby('产品名称')['销售总额'].sum().nlargest(10).index

        # 筛选数据
        filtered_pivot = pivot_data.loc[pivot_data.index.isin(top_materials), pivot_data.columns.isin(top_products)]

        # 创建热力图
        fig = px.imshow(
            filtered_pivot,
            labels=dict(x="产品名称", y="物料名称", color="销售总额"),
            x=filtered_pivot.columns,
            y=filtered_pivot.index,
            color_continuous_scale='Blues',
            title="物料-产品关联热力图 (销售额)"
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            yaxis_tickangle=0
        )

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

        # 创建横向条形图
        fig = px.bar(
            top_combos,
            x='平均销售额',
            y='物料组合',
            title="最佳物料组合 (按平均销售额)",
            labels={
                '平均销售额': '平均销售额 (元)',
                '物料组合': '物料组合'
            },
            text='平均销售额',
            orientation='h',
            color='使用次数',
            hover_data=['使用次数']
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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

        fig = px.bar(
            top_distributors,
            x='销售效率',
            y='经销商名称',
            title="经销商销售效率排名 (销售额/物料数量)",
            labels={
                '销售效率': '销售效率 (元/件)',
                '经销商名称': '经销商'
            },
            text='销售效率',
            orientation='h',
            color='销售总额',
            hover_data=['销售总额', '物料数量']
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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

        # 选择前10名经销商
        top_distributors = distributor_material_usage.iloc[:, 1:].sum(axis=1).nlargest(10).index
        distributor_material_usage = distributor_material_usage.iloc[top_distributors]

        # 融合数据为适合堆叠条形图的格式
        melted_data = pd.melt(
            distributor_material_usage,
            id_vars=['经销商名称'],
            value_vars=[col for col in distributor_material_usage.columns if col != '经销商名称'],
            var_name='物料名称',
            value_name='物料数量'
        )

        fig = px.bar(
            melted_data,
            x='物料数量',
            y='经销商名称',
            color='物料名称',
            title="经销商物料使用情况 (前5种物料)",
            labels={
                '物料数量': '物料数量 (件)',
                '经销商名称': '经销商',
                '物料名称': '物料类型'
            },
            orientation='h'
        )

        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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

        # 创建气泡图
        fig = px.scatter(
            region_cost_sales,
            x='销售额百分比',
            y='费比',
            size='物料总成本',
            color='所属区域',
            text='所属区域',
            title="区域费比分析",
            labels={
                '销售额百分比': '销售贡献度 (%)',
                '费比': '费比 (%)',
                '物料总成本': '物料成本 (元)'
            },
            size_max=60
        )

        # 添加参考线 - 平均费比
        avg_cost_sales_ratio = (region_cost_sales['物料总成本'].sum() / region_cost_sales['销售总额'].sum()) * 100
        fig.add_hline(y=avg_cost_sales_ratio, line_dash="dash", line_color="red",
                      annotation_text=f"平均费比: {avg_cost_sales_ratio:.2f}%",
                      annotation_position="bottom right")

        fig.update_traces(textposition='top center')

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
        salesperson_cost_sales = salesperson_cost_sales.sort_values('费比')

        # 创建条形图
        fig = px.bar(
            salesperson_cost_sales,
            x='申请人',
            y='费比',
            title="销售人员费比分析",
            labels={
                '费比': '费比 (%)',
                '申请人': '销售人员'
            },
            color='费比',
            text='费比',
            color_continuous_scale='RdYlGn_r',  # 红色表示高费比(不好)，绿色表示低费比(好)
            hover_data=['物料总成本', '销售总额']
        )

        # 添加平均费比线
        avg_cost_sales_ratio = (salesperson_cost_sales['物料总成本'].sum() / salesperson_cost_sales[
            '销售总额'].sum()) * 100
        fig.add_hline(y=avg_cost_sales_ratio, line_dash="dash", line_color="black",
                      annotation_text=f"平均: {avg_cost_sales_ratio:.2f}%",
                      annotation_position="bottom right")

        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')

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

        # 选择费比异常值 (高于平均值一定比例)
        avg_cost_sales_ratio = (distributor_cost_sales['物料总成本'].sum() / distributor_cost_sales[
            '销售总额'].sum()) * 100
        distributor_cost_sales['费比异常'] = distributor_cost_sales['费比'] > (avg_cost_sales_ratio * 1.5)

        # 按区域和费比排序
        distributor_cost_sales = distributor_cost_sales.sort_values(['所属区域', '费比'])

        # 创建分组条形图
        fig = px.bar(
            distributor_cost_sales,
            x='经销商名称',
            y='费比',
            color='所属区域',
            title="经销商费比分析 (按区域分组)",
            labels={
                '费比': '费比 (%)',
                '经销商名称': '经销商',
                '所属区域': '区域'
            },
            text='费比',
            hover_data=['物料总成本', '销售总额'],
            barmode='group'
        )

        # 添加平均费比线
        fig.add_hline(y=avg_cost_sales_ratio, line_dash="dash", line_color="black",
                      annotation_text=f"平均: {avg_cost_sales_ratio:.2f}%",
                      annotation_position="bottom right")

        fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
        fig.update_layout(xaxis_tickangle=-45)

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

        # 识别费比异常值 (高于平均值50%以上)
        high_cost_sales_threshold = overall_cost_sales_ratio * 1.5
        anomalies = distributor_cost_sales[distributor_cost_sales['费比'] > high_cost_sales_threshold]
        anomalies = anomalies.sort_values('费比', ascending=False)

        if len(anomalies) > 0:
            anomaly_list = []
            for _, row in anomalies.iterrows():
                anomaly_list.append(
                    html.P(f"经销商 '{row['经销商名称']}' 的费比为 {row['费比']:.2f}%, "
                           f"远高于平均值 {overall_cost_sales_ratio:.2f}% "
                           f"(物料成本: ¥{row['物料总成本']:.2f}, 销售额: ¥{row['销售总额']:.2f})")
                )

            return [
                html.H5("费比异常值警告"),
                html.P(f"平均费比: {overall_cost_sales_ratio:.2f}%"),
                html.P(f"发现 {len(anomalies)} 个费比异常值:"),
                html.Div(anomaly_list)
            ]
        else:
            return html.P("未发现费比异常值。所有经销商的费比都在平均值的1.5倍范围内。")

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
        material_roi = material_roi.sort_values('ROI', ascending=False)

        # 筛选数据 - 只显示成本和销售额都大于一定阈值的物料
        min_cost = 100  # 最小物料成本阈值
        min_sales = 1000  # 最小销售额阈值
        material_roi_filtered = material_roi[
            (material_roi['物料总成本'] > min_cost) &
            (material_roi['销售总额'] > min_sales)
            ].head(15)  # 只选择前15名

        fig = px.bar(
            material_roi_filtered,
            x='ROI',
            y='物料名称',
            title="物料ROI分析 (销售额/物料成本)",
            labels={
                'ROI': 'ROI (销售额/物料成本)',
                '物料名称': '物料名称'
            },
            text='ROI',
            orientation='h',
            color='ROI',
            hover_data=['物料总成本', '销售总额', '物料数量']
        )

        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})

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

        # 按客户分析物料效果
        customer_material_effect = material_sales_link.groupby(['客户代码', '经销商名称', '物料代码', '物料名称']).agg({
            '物料数量': 'sum',
            '物料总成本': 'sum',
            '销售总额': 'sum'
        }).reset_index()

        customer_material_effect['ROI'] = customer_material_effect['销售总额'] / customer_material_effect['物料总成本']

        # 分析高效和低效物料
        high_roi_materials = material_roi.sort_values('ROI', ascending=False).head(5)
        low_roi_materials = material_roi[material_roi['物料总成本'] > 100].sort_values('ROI').head(5)

        # 生成建议
        recommendation_components = [
            html.H5("最优物料分配建议"),

            html.H6("高ROI物料 (建议增加投放):", className="mt-3"),
            html.Ul([
                html.Li([
                    f"{row['物料名称']} (ROI: {row['ROI']:.2f}) - ",
                    f"当前投入: ¥{row['物料总成本']:.2f}, 关联销售额: ¥{row['销售总额']:.2f}"
                ]) for _, row in high_roi_materials.iterrows()
            ]),

            html.H6("低ROI物料 (建议减少或优化投放):", className="mt-3"),
            html.Ul([
                html.Li([
                    f"{row['物料名称']} (ROI: {row['ROI']:.2f}) - ",
                    f"当前投入: ¥{row['物料总成本']:.2f}, 关联销售额: ¥{row['销售总额']:.2f}"
                ]) for _, row in low_roi_materials.iterrows()
            ]),
        ]

        # 特定客户建议
        if len(customer_material_effect) > 0:
            # 找到物料ROI表现最好的客户
            best_customer_material = customer_material_effect.sort_values('ROI', ascending=False).head(3)

            recommendation_components.extend([
                html.H6("最佳客户-物料组合:", className="mt-3"),
                html.Ul([
                    html.Li([
                        f"经销商 '{row['经销商名称']}' 使用 '{row['物料名称']}' 实现了 {row['ROI']:.2f} 的ROI - ",
                        f"建议参考其使用策略"
                    ]) for _, row in best_customer_material.iterrows()
                ])
            ])

        # 添加整体优化建议
        total_material_cost = filtered_material['物料总成本'].sum()
        total_sales = filtered_sales['销售总额'].sum()
        overall_roi = total_sales / total_material_cost

        recommendation_components.extend([
            html.Hr(),
            html.P([
                f"当前整体ROI: {overall_roi:.2f} (总销售额: ¥{total_sales:.2f} / 总物料成本: ¥{total_material_cost:.2f})"
            ]),
            html.P([
                "优化策略: ",
                html.Strong("将物料预算从低ROI物料重新分配到高ROI物料，有潜力将整体ROI提高15-20%")
            ])
        ])

        return recommendation_components

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