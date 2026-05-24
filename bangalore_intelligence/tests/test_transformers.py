import pandas as pd

from data_layer.transformers import bucket_month, grouped_rolling_mean, numeric_bin


def test_bucket_month_adds_month_column():
    df = pd.DataFrame({"date": pd.to_datetime(["2022-01-15", "2022-02-10"])})
    out = bucket_month(df, "date")
    assert "month" in out.columns
    assert out["month"].iloc[0].startswith("2022-01")


def test_bucket_month_empty_frame():
    out = bucket_month(pd.DataFrame(), "date")
    assert out.empty


def test_bucket_month_missing_column_returns_copy():
    df = pd.DataFrame({"x": [1]})
    out = bucket_month(df, "date")
    assert list(out.columns) == ["x"]


def test_numeric_bin_labels():
    s = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    binned = numeric_bin(s, bins=2, labels=["low", "high"])
    assert binned.notna().any()


def test_grouped_rolling_mean():
    df = pd.DataFrame(
        {
            "area": ["A", "A", "A", "B", "B"],
            "date": pd.to_datetime(
                ["2022-01-01", "2022-02-01", "2022-03-01", "2022-01-01", "2022-02-01"]
            ),
            "value": [10.0, 20.0, 30.0, 5.0, 15.0],
        }
    )
    out = grouped_rolling_mean(df, ["area"], "value", 2, "date")
    assert "value_roll_2" in out.columns
    assert out["value_roll_2"].notna().all()
