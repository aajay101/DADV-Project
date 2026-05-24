"""Phase 2 finalization governance checks."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIRS = ("app.py", "components", "dashboards", "data_layer", "filters", "services", "utils")

ANALYTICAL_KEYS = (
    "traffic_selected_area",
    "traffic_selected_road",
    "traffic_selected_month",
    "traffic_selected_quadrant",
    "traffic_radar_focus_area",
    "traffic_focus_chart",
    "traffic_focus_mode",
    "traffic_investigation_scope",
    "aqi_selected_date",
    "aqi_selected_month",
    "aqi_selected_regime",
    "aqi_selected_season",
    "aqi_selected_category",
    "aqi_selected_year",
    "aqi_selected_week",
    "aqi_selected_pollutant",
    "aqi_focus_chart",
    "aqi_focus_mode",
    "aqi_context_pm25",
    "aqi_investigation_scope",
    "traffic_selected_areas",
    "traffic_selected_weather",
    "traffic_selected_roadwork",
    "traffic_selected_roads",
    "traffic_filters_active",
    "aqi_selected_categories",
    "aqi_selected_seasons",
    "aqi_filters_active",
    "traffic_radar_visible_areas",
    "traffic_radar_dimmed_areas",
    "traffic_radar_comparison_mode",
    "traffic_radar_comparison_n",
    "traffic_lab_use_full_dataset",
    "traffic_lab_t13_view",
    "aqi_pairplot_visible_categories",
    "aqi_pairplot_category_preset",
    "aqi_lab_use_full_dataset",
)


def test_analytical_session_writes_are_reducer_owned():
    offenders: list[str] = []
    pattern = re.compile(r"st\.session_state\[[\"']([^\"']+)[\"']\]\s*=")
    for path in _runtime_python_files():
        if path.name in {"transitions.py", "lazy_charts.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        for match in pattern.finditer(text):
            if match.group(1) in ANALYTICAL_KEYS:
                rel = path.relative_to(ROOT)
                offenders.append(f"{rel}:{text[:match.start()].count(chr(10)) + 1}:{match.group(1)}")

    assert offenders == []


def test_cache_clearing_is_runtime_orchestrated():
    offenders: list[str] = []
    for path in _runtime_python_files():
        if path.name in {"transitions.py", "lazy_charts.py"}:
            continue
        text = path.read_text(encoding="utf-8")
        if "cache_data.clear" in text or "clear_lazy_chart_cache(" in text:
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == []


def _runtime_python_files() -> list[Path]:
    files: list[Path] = []
    for entry in AUDIT_DIRS:
        path = ROOT / entry
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(path.rglob("*.py"))
    return files
