from utils.formatters import (
    fmt_aqi_category,
    fmt_confidence_interval,
    fmt_coordinate,
    fmt_date_range,
    fmt_filter_summary,
    fmt_model_version,
    fmt_severity,
    fmt_temperature,
    fmt_visibility,
    fmt_wind_speed,
    hover_incidents,
    hover_pm25,
    hover_radar_theta_r,
    hover_template,
)


def test_fmt_date_range_outputs_month_year_range():
    assert fmt_date_range("2022-01-01", "2024-08-31") == "Jan 2022 - Aug 2024"


def test_fmt_aqi_category_boundaries():
    assert fmt_aqi_category(30) == "Good"
    assert fmt_aqi_category(31) == "Satisfactory"
    assert fmt_aqi_category(251) == "Severe"


def test_fmt_filter_summary_all_areas():
    summary = fmt_filter_summary(
        {"traffic_date_start": "2022-01-01", "traffic_date_end": "2024-01-01", "traffic_selected_areas": []},
        dashboard="traffic",
    )
    assert "Areas: All" in summary


def test_fmt_severity_maps_semantic_tokens():
    assert fmt_severity("critical") == "CRITICAL"
    assert fmt_severity("neutral") == "NEUTRAL"


def test_fmt_temperature_and_aliases():
    assert fmt_temperature(22.5) == "22.5°C"
    assert fmt_wind_speed(3.2) == "3.2 m/s"
    assert fmt_visibility(8) == "8.0 km"


def test_fmt_coordinate_bangalore():
    assert fmt_coordinate(12.97, 77.59) == "12.97°N, 77.59°E"


def test_fmt_confidence_interval_with_unit():
    assert fmt_confidence_interval(142, 218, unit="µg/m³") == "142.0–218.0 µg/m³"


def test_fmt_model_version():
    assert fmt_model_version("2.1") == "v2.1"
    assert fmt_model_version("v3") == "v3"


def test_hover_template_helpers():
    assert hover_pm25() == "PM2.5 %{y:.1f} µg/m³"
    assert hover_template("Month %{x}", hover_pm25()) == "Month %{x}<br>PM2.5 %{y:.1f} µg/m³<extra></extra>"
    assert hover_incidents() == "Incidents %{y:.1f}"
    assert hover_radar_theta_r() == "%{theta}: %{r:.0f}"


def test_no_mock_content_module_in_runtime():
    import importlib.util

    assert importlib.util.find_spec("config.mock_content") is None
