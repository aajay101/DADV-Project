import plotly.graph_objects as go

import importlib

t01_scorecard = importlib.import_module("dashboards.traffic.charts.t01_scorecard")
t03_stream_graph = importlib.import_module("dashboards.traffic.charts.t03_stream_graph")
t13_compound_radar = importlib.import_module("dashboards.traffic.charts.t13_compound_radar")
t15_bubble_matrix = importlib.import_module("dashboards.traffic.charts.t15_bubble_matrix")
a01_crisis_scorecard = importlib.import_module("dashboards.aqi.charts.a01_crisis_scorecard")
a02_calendar_heatmap = importlib.import_module("dashboards.aqi.charts.a02_calendar_heatmap")
from config.data_config import COL_CONGESTION
from data_layer.traffic_transforms import (
    get_area_summary,
    get_area_stress_heatmap,
    get_monthly_bubble_data,
    get_monthly_stream_data,
    get_parallel_coords_data,
    get_road_distribution_profiles,
)
from data_layer.aqi_transforms import get_daily_aqi_calendar


def test_t01_render_returns_plotly_figure(sample_traffic_df):
    area_data = get_area_summary(sample_traffic_df)
    fig = t01_scorecard.render(
        area_data,
        {
            "dashboard": "traffic",
            "role": "hero",
            "system_congestion": float(sample_traffic_df[COL_CONGESTION].mean()),
        },
    )
    assert isinstance(fig, go.Figure)


def test_t03_render_returns_plotly_figure(sample_traffic_df):
    fig = t03_stream_graph.render(
        get_monthly_stream_data(sample_traffic_df),
        {"dashboard": "traffic", "role": "hero"},
    )
    assert isinstance(fig, go.Figure)


def test_t11_profiles_render_returns_plotly_figure(sample_traffic_df):
    profiles = importlib.import_module("dashboards.traffic.charts.t11_ridgeline")
    fig = profiles.render(
        get_road_distribution_profiles(sample_traffic_df),
        {"dashboard": "traffic", "role": "hero"},
    )
    assert isinstance(fig, go.Figure)


def test_t13_heatmap_render_returns_plotly_figure(sample_traffic_df):
    fig = t13_compound_radar.render_heatmap(
        get_area_stress_heatmap(sample_traffic_df),
        {"dashboard": "traffic", "role": "hero"},
    )
    assert isinstance(fig, go.Figure)


def test_t02_area_render_returns_plotly_figure(sample_traffic_df):
    t02 = importlib.import_module("dashboards.traffic.charts.t02_parallel_coords")
    fig = t02.render(get_parallel_coords_data(sample_traffic_df), {"dashboard": "traffic"})
    assert isinstance(fig, go.Figure)


def test_t15_render_returns_plotly_figure(sample_traffic_df):
    fig = t15_bubble_matrix.render(
        get_monthly_bubble_data(sample_traffic_df),
        {"dashboard": "traffic", "role": "supporting"},
    )
    assert isinstance(fig, go.Figure)


def test_a02_render_returns_plotly_figure(sample_aqi_df):
    cal = get_daily_aqi_calendar(sample_aqi_df)
    fig = a02_calendar_heatmap.render(cal, {"dashboard": "aqi", "role": "hero"})
    assert isinstance(fig, go.Figure)


def test_a01_renders_category_bars_without_embedded_indicator(sample_aqi_df):
    fig = a01_crisis_scorecard.render(sample_aqi_df, {"dashboard": "aqi", "role": "hero"})

    assert [trace.type for trace in fig.data] == ["bar"]
    assert tuple(fig.layout.yaxis.domain) == (0, 1)
