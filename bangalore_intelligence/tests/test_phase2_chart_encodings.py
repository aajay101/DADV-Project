"""Phase 2 — high-impact traffic chart encoding corrections."""

from __future__ import annotations

import importlib

import plotly.graph_objects as go
import pytest

from config.data_config import (
    COL_CONGESTION,
    COL_SPEED,
    COL_TRAFFIC_VOL,
    TRAFFIC_RUNTIME_SPEED_MAX,
    TRAFFIC_RUNTIME_SPEED_MIN,
    TRAFFIC_RUNTIME_VOLUME_MAX,
    TRAFFIC_RUNTIME_VOLUME_MIN,
)
from data_layer.traffic_transforms import (
    get_area_summary,
    get_congestion_speed_scatter,
    get_monthly_bubble_data,
    get_monthly_stream_data,
    get_traffic_volume_congestion,
)
from utils.plotly_engine import traffic_speed_axis_range, traffic_volume_axis_range

t01 = importlib.import_module("dashboards.traffic.charts.t01_scorecard")
t03 = importlib.import_module("dashboards.traffic.charts.t03_stream_graph")
t09 = importlib.import_module("dashboards.traffic.charts.t09_speed_threshold")
t14 = importlib.import_module("dashboards.traffic.charts.t14_density_hexbin")
t15 = importlib.import_module("dashboards.traffic.charts.t15_bubble_matrix")


def _trace_types(fig: go.Figure) -> list[str]:
    return [getattr(t, "type", "") for t in fig.data]


@pytest.fixture
def traffic_chart_cfg():
    return {"dashboard": "traffic", "role": "hero"}


def test_t03_line_chart_no_stacked_percent(sample_traffic_df, traffic_chart_cfg):
    stream = get_monthly_stream_data(sample_traffic_df)
    fig = t03.render(stream, traffic_chart_cfg)
    assert isinstance(fig, go.Figure)
    assert _trace_types(fig) == ["scatter"] * len(stream["Area Name"].unique())
    for trace in fig.data:
        assert getattr(trace, "stackgroup", None) is None
        assert getattr(trace, "groupnorm", None) is None
        assert "markers" in (trace.mode or "")


def test_t15_heatmap_not_bubble(sample_traffic_df, traffic_chart_cfg):
    monthly = get_monthly_bubble_data(sample_traffic_df)
    fig = t15.render(monthly, {**traffic_chart_cfg, "role": "supporting"})
    assert "heatmap" in _trace_types(fig)
    assert "scatter" not in _trace_types(fig)


def test_t01_bullet_not_gauge(sample_traffic_df, traffic_chart_cfg):
    area = get_area_summary(sample_traffic_df)
    mean_cong = float(sample_traffic_df[COL_CONGESTION].mean())
    fig = t01.render(
        area,
        {
            **traffic_chart_cfg,
            "system_congestion": mean_cong,
            "capacity_saturation_rate": 12.5,
        },
    )
    assert "indicator" not in _trace_types(fig)
    assert "bar" in _trace_types(fig)
    assert "scatter" in _trace_types(fig)


def test_t09_speed_axis_uses_runtime_domain(sample_traffic_df, traffic_chart_cfg):
    scatter = get_congestion_speed_scatter(sample_traffic_df)
    fig = t09.render(scatter, traffic_chart_cfg)
    expected = traffic_speed_axis_range(scatter[COL_SPEED])
    assert fig.layout.xaxis.range == pytest.approx(list(expected), rel=0, abs=0.01)


def test_t14_volume_axis_uses_runtime_domain(sample_traffic_df, traffic_chart_cfg):
    vol = get_traffic_volume_congestion(sample_traffic_df)
    fig = t14.render(vol, {**traffic_chart_cfg, "role": "supporting"})
    x = vol[COL_TRAFFIC_VOL]
    expected = traffic_volume_axis_range(x)
    assert fig.layout.xaxis.range == pytest.approx(list(expected), rel=0, abs=0.01)


def test_runtime_axis_constants_match_governed_parquet():
    from config.data_config import TRAFFIC_CLEAN_PATH
    import pandas as pd

    df = pd.read_parquet(TRAFFIC_CLEAN_PATH)
    assert df[COL_SPEED].min() == pytest.approx(TRAFFIC_RUNTIME_SPEED_MIN, abs=0.01)
    assert df[COL_SPEED].max() == pytest.approx(TRAFFIC_RUNTIME_SPEED_MAX, abs=0.01)
    assert df[COL_TRAFFIC_VOL].min() == pytest.approx(TRAFFIC_RUNTIME_VOLUME_MIN, abs=0.01)
    assert df[COL_TRAFFIC_VOL].max() == pytest.approx(TRAFFIC_RUNTIME_VOLUME_MAX, abs=0.01)
