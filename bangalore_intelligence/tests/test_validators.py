import pandas as pd

from utils.validators import validate_filter_date_range, validate_required_columns, validate_row_count


def test_validate_required_columns_reports_missing_column():
    df = pd.DataFrame({"a": [1]})
    result = validate_required_columns(df, ["a", "missing"])
    assert not result.ok
    assert "missing" in result.message


def test_validate_filter_date_range_rejects_reversed():
    assert not validate_filter_date_range("2024-01-01", "2022-01-01").ok


def test_validate_row_count_empty_warning():
    result = validate_row_count(pd.DataFrame())
    assert not result.ok
    assert result.is_warning
