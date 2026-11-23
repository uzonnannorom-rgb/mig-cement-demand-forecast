import pandas as pd
import dash
from dash import dcc, html, dash_table, callback, Input, Output
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Load the necessary data
kpi_summary = pd.read_csv("../data/processed/MIG_KPI_Summary.csv")
results_df = pd.read_csv("../data/processed/cement_forecast_results.csv")  # CSV: parquet is blocked on this machine
site_meta = pd.read_csv("../data/processed/site_metadata.csv").set_index("site_id")  # capacities used in the simulation

# Ensure correct data types
results_df["date"] = pd.to_datetime(results_df["date"])
kpi_summary["stockout_pct"] = kpi_summary["stockout_pct"].astype(float)
kpi_summary["overstocking_pct"] = kpi_summary["overstocking_pct"].astype(float)

# Initialize Dash app with Bootstrap styling
# suppress_callback_exceptions=True lets callbacks refer to pages that are not on screen yet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "MIG Cement Operational Planner"

# Custom CSS for white theme with glass-morphism
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                font-family: 'Inter', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, #f0f4f8 0%, #e8edf3 50%, #dce4ed 100%);
                min-height: 100vh;
                margin: 0;
                padding: 0;
            }
            
            .main-container {
                min-height: 100vh;
                padding: 20px;
                background: rgba(255, 255, 255, 0.4);
                backdrop-filter: blur(10px);
            }
            
            .glass-card {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 20px;
                box-shadow: 0 8px 32px rgba(21, 99, 116, 0.08);
                transition: all 0.3s ease;
                overflow: hidden;
                position: relative;
            }
            
            .glass-card::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.4) 0%, transparent 100%);
                pointer-events: none;
            }
            
            .glass-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 40px rgba(21, 99, 116, 0.15);
                border-color: rgba(21, 99, 116, 0.2);
            }
            
            .kpi-card {
                background: rgba(255, 255, 255, 0.75);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.9);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
                height: 130px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
            }
            
            .kpi-card::after {
                content: '';
                position: absolute;
                top: -50%;
                right: -50%;
                width: 100%;
                height: 100%;
                background: radial-gradient(circle, rgba(21, 99, 116, 0.03) 0%, transparent 70%);
                pointer-events: none;
            }
            
            .kpi-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(21, 99, 116, 0.12);
                border-color: rgba(21, 99, 116, 0.2);
            }
            
            .kpi-value {
                font-size: 28px;
                font-weight: 700;
                color: #1a2a3a;
                margin: 4px 0;
                letter-spacing: -0.5px;
            }
            
            .kpi-label {
                font-size: 13px;
                font-weight: 500;
                color: #5a6a7a;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .kpi-accent {
                position: absolute;
                top: 0;
                left: 0;
                width: 4px;
                height: 100%;
                background: linear-gradient(180deg, #156374, #1a8a9e);
                border-radius: 4px 0 0 4px;
            }
            
            .title-primary {
                color: #1a2a3a;
                font-weight: 700;
                font-size: 2.2rem;
                letter-spacing: -1px;
            }
            
            .title-accent {
                color: #156374;
            }
            
            .subtitle {
                color: #5a6a7a;
                font-weight: 300;
                font-size: 16px;
            }
            
            .dropdown-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 12px;
                padding: 12px 16px;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1000;
            }
            
            .dropdown-container label {
                color: #2a3a4a;
                font-weight: 500;
                font-size: 14px;
                letter-spacing: 0.3px;
            }
            
            /* Fix for dropdown z-index */
            .Select {
                position: relative;
                z-index: 1000;
            }
            
            .Select-control {
                background: rgba(255, 255, 255, 0.8) !important;
                border: 1px solid rgba(21, 99, 116, 0.15) !important;
                border-radius: 8px !important;
                color: #1a2a3a !important;
                box-shadow: 0 2px 8px rgba(21, 99, 116, 0.04);
                position: relative;
                z-index: 1000;
            }
            
            .Select-control:hover {
                border-color: #156374 !important;
            }
            
            .Select-menu-outer {
                background: #ffffff !important;
                border: 1px solid rgba(21, 99, 116, 0.1) !important;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 24px rgba(21, 99, 116, 0.15);
                z-index: 9999 !important;
                position: absolute !important;
                max-height: 300px !important;
                overflow-y: auto !important;
            }
            
            .Select-menu {
                max-height: 280px !important;
                overflow-y: auto !important;
            }
            
            .Select-option {
                color: #1a2a3a !important;
                background: transparent !important;
                padding: 8px 12px !important;
                cursor: pointer !important;
            }
            
            .Select-option.is-focused {
                background: rgba(21, 99, 116, 0.08) !important;
                color: #156374 !important;
            }
            
            .Select-option.is-selected {
                background: rgba(21, 99, 116, 0.12) !important;
                color: #156374 !important;
            }
            
            .Select-value-label {
                color: #1a2a3a !important;
            }
            
            .Select-placeholder {
                color: #8a9aaa !important;
            }
            
            .Select-clear-zone, .Select-arrow-zone {
                color: #5a6a7a !important;
            }
            
            /* Fix for dropdown in modal/popup contexts */
            .is-open .Select-menu-outer {
                z-index: 9999 !important;
            }
            
            /* Ensure dropdown appears above all content */
            .Select.is-open {
                z-index: 9999 !important;
            }
            
            .chart-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 16px;
                padding: 20px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1;
            }
            
            .chart-container:hover {
                border-color: rgba(21, 99, 116, 0.2);
                box-shadow: 0 8px 32px rgba(21, 99, 116, 0.1);
            }
            
            .table-container {
                background: rgba(255, 255, 255, 0.7);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.8);
                border-radius: 16px;
                padding: 20px;
                max-height: 450px;
                overflow-y: auto;
                box-shadow: 0 4px 16px rgba(21, 99, 116, 0.06);
                position: relative;
                z-index: 1;
            }
            
            .table-container::-webkit-scrollbar {
                width: 8px;
            }
            
            .table-container::-webkit-scrollbar-track {
                background: rgba(21, 99, 116, 0.05);
                border-radius: 4px;
            }
            
            .table-container::-webkit-scrollbar-thumb {
                background: linear-gradient(180deg, #156374, #1a8a9e);
                border-radius: 4px;
            }
            
            .table-container::-webkit-scrollbar-thumb:hover {
                background: #156374;
            }
            
            .section-title {
                color: #1a2a3a;
                font-weight: 600;
                font-size: 1.1rem;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            
            .section-title::after {
                content: '';
                flex: 1;
                height: 2px;
                background: linear-gradient(90deg, rgba(21, 99, 116, 0.2), transparent);
            }
            
            .dash-table-container {
                background: transparent !important;
            }
            
            .dash-spreadsheet-container {
                background: transparent !important;
            }
            
            .dash-spreadsheet {
                background: transparent !important;
                color: #1a2a3a !important;
            }
            
            .dash-spreadsheet td {
                color: #2a3a4a !important;
                background: transparent !important;
                border-bottom: 1px solid rgba(21, 99, 116, 0.06) !important;
            }
            
            .dash-spreadsheet th {
                color: #1a2a3a !important;
                background: rgba(21, 99, 116, 0.06) !important;
                border-bottom: 2px solid rgba(21, 99, 116, 0.15) !important;
                font-weight: 600 !important;
            }
            
            .dash-spreadsheet tr:hover td {
                background: rgba(21, 99, 116, 0.04) !important;
            }
            
            .dash-spreadsheet tr:nth-child(even) td {
                background: rgba(21, 99, 116, 0.02) !important;
            }
            
            .section-spacing {
                margin-top: 24px;
            }
            
            @media (max-width: 768px) {
                .kpi-value {
                    font-size: 22px;
                }
                .title-primary {
                    font-size: 1.8rem;
                }
                .kpi-card {
                    height: 110px;
                    padding: 16px;
                }
                .Select-menu-outer {
                    max-width: 90vw !important;
                }
            }
            
            .status-badge {
                display: inline-block;
                padding: 3px 12px;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.3px;
            }
            
            .badge-success { background: rgba(21, 99, 116, 0.1); color: #156374; }
            .badge-warning { background: rgba(255, 193, 7, 0.15); color: #856404; }
            .badge-danger { background: rgba(220, 53, 69, 0.1); color: #721c24; }
            
            .glass-divider {
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(21, 99, 116, 0.1), transparent);
                margin: 20px 0;
            }
            
            /* Loading spinner */
            .loading-spinner {
                border: 3px solid rgba(21, 99, 116, 0.1);
                border-top: 3px solid #156374;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Ensure dropdown container has proper z-index context */
            .row:first-child {
                position: relative;
                z-index: 100;
            }

            /* Page menu */
            .nav-bar { display: flex; justify-content: center; gap: 12px; margin-bottom: 28px; }
            .nav-pill {
                padding: 10px 22px; border-radius: 30px; font-weight: 600; font-size: 14px;
                color: #156374; background: rgba(255, 255, 255, 0.7);
                border: 1px solid rgba(21, 99, 116, 0.2); text-decoration: none;
            }
            .nav-pill:hover { background: rgba(21, 99, 116, 0.08); color: #156374; }
            .nav-pill.active { background: #156374; color: #ffffff; border-color: #156374; }
        </style>
    </head>
    <body>
        <div class="main-container">
            {%app_entry%}
        </div>
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# =======================
# Network summary (used by the Planner page)
# =======================
# One row per site, built from the simulation results
network = results_df.groupby("site_id").agg(
    total_forecast=("forecasted_consumption", "sum"),
    avg_daily_forecast=("forecasted_consumption", "mean"),
    planned_reorders=("reorder_flag", "sum"),
    avg_inventory=("sim_inventory", "mean"),
)

# Stock on the last day of the forecast period
last_rows = results_df.sort_values("date").groupby("site_id").tail(1).set_index("site_id")
network["current_stock"] = last_rows["sim_inventory"]
last_day = results_df["date"].max().strftime("%d %b %Y")

# Add silo capacity and reorder level for each site
network = network.join(site_meta[["silo_capacity", "reorder_threshold"]])

network["utilisation_pct"] = network["avg_inventory"] / network["silo_capacity"] * 100
network["fill_pct"] = network["current_stock"] / network["silo_capacity"] * 100
network["days_cover"] = network["current_stock"] / network["avg_daily_forecast"]

# Alert status for each site
network["status"] = np.select(
    [network["current_stock"] <= network["reorder_threshold"], network["fill_pct"] >= 90],
    ["Reorder now", "Near capacity"],
    default="OK",
)
network = network.reset_index()

status_colours = {"Reorder now": "#dc3545", "Near capacity": "#e0a800", "OK": "#156374"}


# =======================
# Small helpers
# =======================
def kpi_card(value, label):
    return dbc.Col(
        html.Div([
            html.Div(className="kpi-accent"),
            html.Div(value, className="kpi-value"),
            html.Div(label, className="kpi-label")
        ], className="kpi-card"),
        width=6, md=3
    )


table_cell_style = {
    "textAlign": "center", "padding": "12px 16px", "fontSize": "14px",
    "color": "#2a3a4a", "background": "transparent", "border": "none"
}
table_header_style = {
    "backgroundColor": "rgba(21, 99, 116, 0.06)", "fontWeight": "600", "color": "#1a2a3a",
    "borderBottom": "2px solid rgba(21, 99, 116, 0.15)", "padding": "12px 16px"
}


# =======================
# Page 1: Network Overview (multi-site planners)
# =======================
def planner_layout():
    # KPI cards for the whole network
    sites_alert = (network["status"] == "Reorder now").sum()
    kpis = [
        kpi_card(f"{network['total_forecast'].sum():,.0f}", "Network Forecast Demand (t)"),
        kpi_card(f"{network['planned_reorders'].sum():,.0f}", "Planned Reorders"),
        kpi_card(f"{network['utilisation_pct'].mean():.1f}%", "Average Silo Utilization"),
        kpi_card(f"{sites_alert} of {len(network)}", "Sites Needing Reorder"),
    ]

    # Chart 1: how full each silo is on the last day
    fill = network.sort_values("fill_pct")
    fill_fig = go.Figure(go.Bar(
        x=fill["fill_pct"], y=fill["site_id"], orientation="h",
        marker_color=fill["status"].map(status_colours),
        customdata=fill[["current_stock", "silo_capacity", "status"]],
        hovertemplate="<b>%{y}</b><br>%{x:.0f}% full<br>%{customdata[0]:,.0f} of %{customdata[1]:,.0f} t"
                      "<br>%{customdata[2]}<extra></extra>"
    ))
    fill_fig.add_vline(x=20, line_dash="dash", line_color="#dc3545",
                       annotation_text="Reorder level (20%)", annotation_font=dict(color="#dc3545", size=11))
    fill_fig.update_layout(
        template="plotly_white", height=720, margin=dict(l=80, r=30, t=30, b=50),
        xaxis=dict(title="Silo fill (%)", range=[0, 100]), yaxis=dict(title=None),
        paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0.3)"
    )

    # Chart 2: past stockout and overstocking rates from the KPI summary, one colour per site behaviour
    behaviour_colours = {"aggressive": "#C8641E", "conservative": "#156374", "chaotic": "#7B61C9"}
    hist_fig = go.Figure()
    for behaviour, group in kpi_summary.groupby("behavior"):
        hist_fig.add_trace(go.Scatter(
            x=group["stockout_pct"], y=group["overstocking_pct"],
            mode="markers", name=str(behaviour).title(), text=group["site_id"],
            marker=dict(size=13, color=behaviour_colours.get(str(behaviour).lower(), "#8C979D"),
                        opacity=0.85, line=dict(color="white", width=1)),
            hovertemplate="<b>%{text}</b><br>Stockout days: %{x:.1f}%<br>Overstocked days: %{y:.1f}%<extra></extra>"
        ))
    hist_fig.update_layout(
        template="plotly_white", height=720, margin=dict(l=60, r=30, t=30, b=50),
        xaxis=dict(title="Stockout days (%)"), yaxis=dict(title="Overstocked days (%)"),
        legend=dict(title="Site behaviour", orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(255,255,255,0)", plot_bgcolor="rgba(255,255,255,0.3)"
    )

    # Alert table: sites with the least cover first
    # Add each site's past record from the KPI summary
    alerts = network.merge(kpi_summary[["site_id", "behavior", "stockout_pct", "overstocking_pct"]],
                           on="site_id", how="left")
    alerts["behavior"] = alerts["behavior"].str.title()
    alerts = alerts.sort_values("days_cover")[[
        "site_id", "behavior", "status", "current_stock", "silo_capacity", "fill_pct", "days_cover",
        "planned_reorders", "stockout_pct", "overstocking_pct"
    ]].round(1)

    return html.Div([
        dbc.Row(kpis, className="mb-4 g-3"),
        dbc.Row([
            dbc.Col(html.Div([
                html.Div(f"Silo Fill by Site ({last_day})", className="section-title"),
                dcc.Graph(figure=fill_fig, config={"displayModeBar": False})
            ], className="chart-container"), lg=6, className="mb-4"),
            dbc.Col(html.Div([
                html.Div("Past Stockouts vs Overstocking (2022–2024)", className="section-title"),
                dcc.Graph(figure=hist_fig, config={"displayModeBar": False})
            ], className="chart-container"), lg=6, className="mb-4"),
        ]),
        html.Div([
            html.Div("Reorder Alerts Across All Sites", className="section-title"),
            dash_table.DataTable(
                columns=[
                    {"name": "Site", "id": "site_id"},
                    {"name": "Behaviour", "id": "behavior"},
                    {"name": "Status", "id": "status"},
                    {"name": "Stock (t)", "id": "current_stock"},
                    {"name": "Silo Capacity (t)", "id": "silo_capacity"},
                    {"name": "Fill (%)", "id": "fill_pct"},
                    {"name": "Days of Cover", "id": "days_cover"},
                    {"name": "Planned Reorders", "id": "planned_reorders"},
                    {"name": "Past Stockout (%)", "id": "stockout_pct"},
                    {"name": "Past Overstock (%)", "id": "overstocking_pct"},
                ],
                data=alerts.to_dict("records"),
                sort_action="native",
                page_size=10,
                style_table={"overflowX": "auto"},
                style_cell=table_cell_style,
                style_header=table_header_style,
                style_data_conditional=[
                    {"if": {"filter_query": '{status} = "Reorder now"', "column_id": "status"},
                     "color": "#dc3545", "fontWeight": "600"},
                    {"if": {"filter_query": '{status} = "Near capacity"', "column_id": "status"},
                     "color": "#b38600", "fontWeight": "600"},
                ]
            )
        ], className="table-container")
    ])


# =======================
# Page 2: Site View (individual site managers)
# =======================
def site_layout():
    sites = sorted(results_df["site_id"].unique())
    return html.Div([
        # Site Selection
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Label("Select Site", className="mb-2 d-block"),
                    dcc.Dropdown(id="site-dropdown",
                                 options=[{"label": s, "value": s} for s in sites],
                                 value=sites[0], clearable=False)
                ], className="dropdown-container", style={"position": "relative", "zIndex": 9999})
            ], width=6, lg=4, xl=3)
        ], className="mb-4", style={"position": "relative", "zIndex": 1000}),

        # KPI Cards
        dbc.Row(id="kpi-cards", className="mb-4 g-3", style={"position": "relative", "zIndex": 1}),

        # Inventory Time Series
        html.Div([
            html.Div("Inventory and Demand Analysis", className="section-title"),
            dcc.Graph(id="inventory-timeseries", config={"displayModeBar": False})
        ], className="chart-container mb-4"),

        # Reorder Recommendations
        html.Div([
            html.Div("Upcoming Reorder Recommendations", className="section-title"),
            dash_table.DataTable(
                id="reorder-table",
                columns=[
                    {"name": "Date", "id": "date"},
                    {"name": "Inventory (t)", "id": "sim_inventory"},
                    {"name": "Delivery Date", "id": "recommended_delivery_date"},
                    {"name": "Quantity (t)", "id": "recommended_delivery_quantity"},
                    {"name": "Rain Buffer", "id": "buffer_applied"}
                ],
                page_size=5,
                style_table={"overflowX": "auto"},
                style_cell=table_cell_style,
                style_header=table_header_style,
            )
        ], className="table-container")
    ])


# =======================
# App Layout (header + page menu + page area)
# =======================
app.layout = dbc.Container([
    dcc.Location(id="url"),
    html.Div([
        html.H1(["MIG Cement ", html.Span("Operational Planner", className="title-accent")],
                className="title-primary text-center mb-2"),
        html.P("Cement demand forecasts, projected inventory and reorder alerts",
               className="subtitle text-center mb-3")
    ]),
    html.Div([
        dcc.Link("Network Overview", href="/", id="link-planner", className="nav-pill"),
        dcc.Link("Site View", href="/site", id="link-site", className="nav-pill"),
    ], className="nav-bar"),
    html.Div(id="page-content")
], fluid=True, className="px-4 py-3")


# =======================
# Callbacks
# =======================
# Show the right page for the address in the browser
@app.callback(
    [Output("page-content", "children"),
     Output("link-planner", "className"),
     Output("link-site", "className")],
    [Input("url", "pathname")]
)
def show_page(pathname):
    if pathname == "/site":
        return site_layout(), "nav-pill", "nav-pill active"
    return planner_layout(), "nav-pill active", "nav-pill"


# Site View: update KPI cards, chart and table when a site is chosen
@app.callback(
    [Output("inventory-timeseries", "figure"),
     Output("reorder-table", "data"),
     Output("kpi-cards", "children")],
    [Input("site-dropdown", "value")]
)
def update_site_view(site_id):
    site_df = results_df[results_df["site_id"] == site_id].copy()

    # KPI Calculations
    total_forecast = site_df["forecasted_consumption"].sum()
    total_reorders = site_df["reorder_flag"].sum()
    avg_inventory = site_df["sim_inventory"].mean()
    silo_capacity = site_meta.loc[site_id, "silo_capacity"]  # same capacity the simulation used
    utilization = (avg_inventory / silo_capacity) * 100

    kpi_cards = [
        kpi_card(f"{total_forecast:,.0f}", "Total Forecasted Consumption"),
        kpi_card(f"{total_reorders}", "Planned Reorders"),
        kpi_card(f"{avg_inventory:,.0f}", "Average Inventory (t)"),
        kpi_card(f"{utilization:.1f}%", "Capacity Utilization"),
    ]

    # Time Series Plot
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=site_df["date"], y=site_df["sim_inventory"], mode="lines", name="Inventory Level",
        line=dict(color="#156374", width=2.5), fill="tozeroy", fillcolor="rgba(21, 99, 116, 0.1)",
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Inventory: %{y:,.0f} t<extra></extra>"
    ))
    fig.add_hline(
        y=silo_capacity, line_dash="dash", line_color="#dc3545", line_width=1.5,
        annotation_text=f"Capacity: {silo_capacity:,.0f} t", annotation_position="top right",
        annotation_font=dict(color="#dc3545", size=11)
    )
    fig.add_trace(go.Bar(
        x=site_df["date"], y=site_df["forecasted_consumption"], name="Forecasted Demand",
        yaxis="y2", marker_color="rgba(255, 193, 7, 0.5)",
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Demand: %{y:,.0f} t<extra></extra>"
    ))
    reorder_points = site_df[site_df["reorder_flag"] == True]
    fig.add_trace(go.Scatter(
        x=reorder_points["date"], y=reorder_points["sim_inventory"], mode="markers",
        name="Reorder Trigger",
        marker=dict(color="#dc3545", size=10, symbol="diamond", line=dict(color="white", width=1.5)),
        hovertemplate="<b>%{x|%Y-%m-%d}</b><br>Reorder Trigger<br>Inventory: %{y:,.0f} t<extra></extra>"
    ))
    fig.update_layout(
        template="plotly_white",
        title=dict(text=f"<b>{site_id}</b> - Inventory and Demand Forecast",
                   font=dict(size=16, color="#1a2a3a"), x=0.5, xanchor="center"),
        xaxis=dict(title=dict(text="Date")),
        yaxis=dict(title=dict(text="Inventory (t)")),
        yaxis2=dict(title=dict(text="Demand (t)"), overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        plot_bgcolor="rgba(255,255,255,0.3)", paper_bgcolor="rgba(255,255,255,0)",
        margin=dict(l=60, r=60, t=80, b=50), height=450
    )

    # Reorder Table Data
    reorder_data = site_df[site_df["reorder_flag"] == True][[
        "date", "sim_inventory", "recommended_delivery_date",
        "recommended_delivery_quantity", "buffer_applied"
    ]].copy()
    reorder_data["date"] = reorder_data["date"].dt.strftime("%Y-%m-%d")
    reorder_data["sim_inventory"] = reorder_data["sim_inventory"].round(1)
    reorder_data["recommended_delivery_quantity"] = reorder_data["recommended_delivery_quantity"].round(1)
    reorder_data["buffer_applied"] = reorder_data["buffer_applied"].map({True: "Yes", False: "No"})

    return fig, reorder_data.to_dict("records"), kpi_cards


# =======================
# Run the app
# =======================
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8050)
