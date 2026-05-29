"""Chart and report export utilities — deep-copy figures; no Streamlit imports."""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import datetime
from io import BytesIO
from typing import Any, Mapping

import plotly.graph_objects as go

from utils.formatters import fmt_export_timestamp, fmt_filter_summary

DASHBOARD_CODES = {"traffic": "TRF", "aqi": "AQI"}

PNG_EXPORT_WIDTH = 1200
PNG_EXPORT_HEIGHT = 700
PNG_EXPORT_SCALE = 2

EXPORT_PAPER_BG = "#FFFFFF"
EXPORT_PLOT_BG = "#F8F9FA"
EXPORT_TEXT = "#1F2937"
EXPORT_MUTED = "#6B7280"
EXPORT_GRID = "#E5E7EB"


class ExportError(RuntimeError):
    """Raised when PNG/PDF generation fails."""


def dashboard_code(dashboard: str) -> str:
    return DASHBOARD_CODES.get(dashboard, dashboard.upper()[:3])


def chart_code_from_key(fullscreen_key: str | None = None, chart_id: str | None = None) -> str:
    if chart_id:
        return re.sub(r"[^A-Za-z0-9]", "", chart_id).upper()
    if fullscreen_key:
        return fullscreen_key.upper().replace("_", "")
    return "CHART"


def build_export_filename(
    dashboard_code_str: str,
    chart_code: str,
    generated_at: datetime | None = None,
    extension: str = "png",
) -> str:
    """Return BUIP_[DashboardCode]_[ChartCode]_[YYYYMMDD]_[HHMMSS].ext"""
    ts = generated_at or datetime.now()
    safe_dash = re.sub(r"[^A-Za-z0-9]", "", dashboard_code_str)
    safe_chart = re.sub(r"[^A-Za-z0-9]", "", chart_code)
    stamp = ts.strftime("%Y%m%d_%H%M%S")
    ext = extension.lstrip(".")
    return f"BUIP_{safe_dash}_{safe_chart}_{stamp}.{ext}"


def apply_export_theme(fig: go.Figure, dashboard: str = "traffic") -> go.Figure:
    """Return a light-background copy of fig suitable for print/PDF export."""
    out = deepcopy(fig)
    out.update_layout(
        paper_bgcolor=EXPORT_PAPER_BG,
        plot_bgcolor=EXPORT_PLOT_BG,
        font=dict(color=EXPORT_TEXT, size=12),
        title_font=dict(color=EXPORT_TEXT, size=14),
        legend=dict(font=dict(color=EXPORT_MUTED, size=10)),
        hoverlabel=dict(
            bgcolor=EXPORT_PAPER_BG,
            bordercolor=EXPORT_GRID,
            font=dict(color=EXPORT_TEXT, size=11),
        ),
    )
    out.update_xaxes(
        gridcolor=EXPORT_GRID,
        linecolor=EXPORT_GRID,
        tickfont=dict(color=EXPORT_MUTED),
        title_font=dict(color=EXPORT_TEXT),
    )
    out.update_yaxes(
        gridcolor=EXPORT_GRID,
        linecolor=EXPORT_GRID,
        tickfont=dict(color=EXPORT_MUTED),
        title_font=dict(color=EXPORT_TEXT),
    )
    return out


def _append_export_footer(fig: go.Figure, title: str, active_filters: Mapping[str, Any], dashboard: str) -> None:
    summary = fmt_filter_summary(active_filters, dashboard=dashboard)
    footer = f"{title} | {summary} | Generated {fmt_export_timestamp()}"
    fig.add_annotation(
        text=footer,
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.14,
        showarrow=False,
        font=dict(size=9, color=EXPORT_MUTED),
        align="center",
    )
    fig.update_layout(margin=dict(b=100))


def figure_to_png_bytes(fig: go.Figure) -> bytes:
    try:
        return fig.to_image(
            format="png",
            width=PNG_EXPORT_WIDTH,
            height=PNG_EXPORT_HEIGHT,
            scale=PNG_EXPORT_SCALE,
        )
    except Exception as exc:
        raise ExportError(
            "PNG export failed. Ensure kaleido is installed (pip install 'kaleido>=0.2.1,<0.3')."
        ) from exc


def export_chart_png(
    fig: go.Figure,
    title: str,
    active_filters: Mapping[str, Any],
    *,
    dashboard: str = "traffic",
) -> bytes:
    """Render a Plotly figure as PNG bytes with export-safe theme and metadata."""
    themed = apply_export_theme(fig, dashboard=dashboard)
    _append_export_footer(themed, title, active_filters, dashboard)
    return figure_to_png_bytes(themed)


def resolve_export_figure(cfg: Mapping[str, Any] | None) -> go.Figure | None:
    """Resolve eager or lazy chart figures for export (no Streamlit session)."""
    if not cfg:
        return None
    fig = cfg.get("fig")
    if fig is not None:
        return fig
    builder = cfg.get("fig_builder")
    if callable(builder):
        built = builder()
        return built if built is not None else None
    return None


def _slot_exportable(cfg: Mapping[str, Any]) -> bool:
    if not cfg:
        return False
    if cfg.get("fig") is not None:
        return True
    return callable(cfg.get("fig_builder"))


def _bundle_chart_slots(bundle: Mapping[str, Any]) -> list[tuple[str, Mapping[str, Any]]]:
    slots: list[tuple[str, Mapping[str, Any]]] = []
    for key in ("hero_chart", "support_chart"):
        cfg = bundle.get(key) or {}
        if _slot_exportable(cfg):
            slots.append((key, cfg))
    for idx, cfg in enumerate(bundle.get("secondary_charts") or []):
        if _slot_exportable(cfg):
            slots.append((f"secondary_charts_{idx}", cfg))
    collapsed = bundle.get("collapsed_chart") or {}
    if _slot_exportable(collapsed):
        slots.append(("collapsed_chart", collapsed))
    return slots


def _pdf_styles():
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet

    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "BuipTitle",
            parent=base["Heading1"],
            fontSize=18,
            spaceAfter=12,
            textColor=EXPORT_TEXT,
        ),
        "heading": ParagraphStyle(
            "BuipHeading",
            parent=base["Heading2"],
            fontSize=13,
            spaceBefore=14,
            spaceAfter=8,
            textColor=EXPORT_TEXT,
        ),
        "body": ParagraphStyle(
            "BuipBody",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            textColor=EXPORT_MUTED,
        ),
    }


def generate_pdf_report(
    bundle: Mapping[str, Any],
    active_filters: Mapping[str, Any],
    *,
    dashboard: str = "traffic",
    page_title: str = "Dashboard Report",
) -> bytes:
    """Generate a dashboard report PDF: cover, KPIs, chart pages, notes, metadata."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = _pdf_styles()
    story: list[Any] = []

    dash_code = dashboard_code(dashboard)
    filter_line = fmt_filter_summary(active_filters, dashboard=dashboard)
    generated = fmt_export_timestamp()

    story.append(Paragraph("Bangalore Urban Intelligence Platform", styles["title"]))
    story.append(Paragraph(page_title, styles["heading"]))
    story.append(Paragraph(f"Dashboard: {dash_code} · {generated}", styles["body"]))
    story.append(Paragraph(f"Active scope: {filter_line}", styles["body"]))
    story.append(Spacer(1, 0.25 * inch))

    story.append(Paragraph("Executive KPI Summary", styles["heading"]))
    for tier, label in (("primary_kpis", "Primary"), ("secondary_kpis", "Secondary")):
        kpis = bundle.get(tier) or []
        if not kpis:
            continue
        for kpi in kpis:
            line = f"{label} · {kpi.get('label', '')}: {kpi.get('value', '—')}"
            if kpi.get("note"):
                line += f" ({kpi['note']})"
            story.append(Paragraph(line, styles["body"]))

    insight = bundle.get("insight")
    if insight:
        story.append(Spacer(1, 0.15 * inch))
        insight_heading = "What This Means" if dashboard == "aqi" else "Operational Interpretation"
        story.append(Paragraph(insight_heading, styles["heading"]))
        story.append(Paragraph(str(insight), styles["body"]))

    record_count = bundle.get("record_count", "")
    if record_count:
        story.append(Paragraph(f"Record count: {record_count}", styles["body"]))

    for slot_name, cfg in _bundle_chart_slots(bundle):
        fig = resolve_export_figure(cfg)
        if fig is None:
            continue
        title = cfg.get("title", slot_name)
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph(title, styles["heading"]))
        if cfg.get("subtitle"):
            story.append(Paragraph(str(cfg["subtitle"]), styles["body"]))
        try:
            png = export_chart_png(
                fig,
                title,
                active_filters,
                dashboard=dashboard,
            )
            img_buf = BytesIO(png)
            story.append(RLImage(img_buf, width=6.5 * inch, height=3.8 * inch))
        except ExportError as exc:
            story.append(Paragraph(f"Chart export unavailable: {exc}", styles["body"]))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph("Data Notes", styles["heading"]))
    story.append(
        Paragraph(
            "Governed canonical parquet and validated processed parquet drive this build. "
            "Filters and timestamps above reproduce the analytical scope visible when the report was generated.",
            styles["body"],
        ),
    )
    story.append(Paragraph(f"Report metadata · {filter_line} · {generated}", styles["body"]))

    doc.build(story)
    return buffer.getvalue()


def generate_executive_summary(
    bundle: Mapping[str, Any],
    active_filters: Mapping[str, Any],
    *,
    dashboard: str = "traffic",
    page_title: str = "Executive Summary",
) -> bytes:
    """One-page stakeholder PDF with hero chart and top KPIs."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch
    from reportlab.platypus import Image as RLImage
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = _pdf_styles()
    story: list[Any] = []

    dash_code = dashboard_code(dashboard)
    filter_line = fmt_filter_summary(active_filters, dashboard=dashboard)

    story.append(Paragraph("BUIP Executive Summary", styles["title"]))
    story.append(Paragraph(f"{page_title} · {dash_code}", styles["heading"]))
    story.append(Paragraph(filter_line, styles["body"]))
    story.append(Spacer(1, 0.12 * inch))

    for kpi in (bundle.get("primary_kpis") or [])[:4]:
        story.append(
            Paragraph(f"{kpi.get('label', '')}: {kpi.get('value', '—')}", styles["body"]),
        )

    hero = bundle.get("hero_chart") or {}
    hero_fig = resolve_export_figure(hero)
    if hero_fig is not None:
        try:
            png = export_chart_png(
                hero_fig,
                hero.get("title", "Hero chart"),
                active_filters,
                dashboard=dashboard,
            )
            story.append(Spacer(1, 0.1 * inch))
            story.append(RLImage(BytesIO(png), width=6.8 * inch, height=4.0 * inch))
        except ExportError as exc:
            story.append(Paragraph(str(exc), styles["body"]))

    if bundle.get("insight"):
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(str(bundle["insight"]), styles["body"]))

    story.append(Paragraph(f"Generated {fmt_export_timestamp()}", styles["body"]))
    doc.build(story)
    return buffer.getvalue()
