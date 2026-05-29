"""T-02 · Parallel coordinates — eight-axis area profile and sampled record mode."""

import plotly.graph_objects as go

from config.data_config import COL_AREA
from data_layer.traffic_transforms import PARALLEL_AREA_DIMENSIONS, PARALLEL_RECORD_COLUMNS
from filters.interaction import trace_opacity
from utils.formatters import hover_template
from utils.plotly_engine import apply_dashboard_theme, empty_figure


def _line_opacity(area: str, config: dict) -> float:
    return trace_opacity(area, config.get("highlight_area"), base=0.38)


def _render_area_lines(data, config: dict) -> go.Figure:
    dashboard = config.get("dashboard", "traffic")
    dims = config.get("dimensions", PARALLEL_AREA_DIMENSIONS)

    fig = go.Figure()
    frame = data.copy()
    for col, _ in dims:
        if col not in frame.columns:
            continue
        mu = frame[col].mean()
        sd = frame[col].std() or 1.0
        frame[col] = (frame[col] - mu) / sd

    for _, row in frame.iterrows():
        area = row[COL_AREA]
        values = [float(row[col]) for col, _ in dims if col in row.index]
        if len(values) != len(dims):
            continue
        fig.add_trace(
            go.Scatter(
                x=list(range(len(dims))),
                y=values,
                mode="lines+markers",
                name=area,
                line=dict(width=2.8 if config.get("highlight_area") == area else 1.2),
                marker=dict(size=5),
                opacity=_line_opacity(area, config),
                hovertemplate=hover_template("<b>%{fullData.name}</b>"),
            )
        )

    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=list(range(len(dims))),
            ticktext=[label for _, label in dims],
            tickangle=-35,
            title="",
        ),
        yaxis=dict(title="Normalized scale (z-score per dimension)", showgrid=True),
    )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=config.get("role", "supporting"),
        show_legend=True,
        chart_type="parcoords",
    )


def _render_record_parcoords(data, config: dict) -> go.Figure:
    dashboard = config.get("dashboard", "traffic")
    dims = config.get("dimensions", PARALLEL_RECORD_COLUMNS)
    highlight = config.get("highlight_area")

    dimensions = []
    for col, label in dims:
        if col not in data.columns:
            continue
        dimensions.append(
            dict(
                label=label,
                values=data[col].tolist(),
            )
        )

    line_color = data[COL_AREA].map(
        lambda a: "rgba(229,56,59,0.75)" if highlight and a == highlight else "rgba(88,166,255,0.35)"
    )

    fig = go.Figure(
        data=go.Parcoords(
            line=dict(color=line_color.tolist(), showscale=False),
            dimensions=dimensions,
        )
    )
    sampling = getattr(data, "attrs", {}).get("sampling", {})
    if sampling.get("sampled"):
        fig.add_annotation(
            xref="paper",
            yref="paper",
            x=0.02,
            y=-0.12,
            text=(
                f"Sampled {sampling.get('sample_size'):,}/{sampling.get('source_rows'):,} "
                "records · random_state=42"
            ),
            showarrow=False,
            font=dict(size=10),
            xanchor="left",
        )
    return apply_dashboard_theme(
        fig,
        dashboard,
        role=config.get("role", "supporting"),
        show_legend=False,
        chart_type="parcoords",
    )


def render(data, config=None):
    if data is None or data.empty:
        return empty_figure("No multivariate area data", "traffic")

    cfg = config or {}
    if cfg.get("record_level"):
        return _render_record_parcoords(data, cfg)
    return _render_area_lines(data, cfg)
