import importlib
import pkgutil


def test_no_dashboard_imports_altair_helpers():
    import dashboards

    for _finder, name, _ispkg in pkgutil.walk_packages(dashboards.__path__, dashboards.__name__ + "."):
        if "charts" not in name:
            continue
        mod = importlib.import_module(name)
        source_path = getattr(mod, "__file__", "") or ""
        if source_path.endswith(".py"):
            text = open(source_path, encoding="utf-8").read()
            assert "altair_helpers" not in text, f"{name} must not import altair_helpers"


def test_altair_helpers_are_deferred_stubs():
    from utils import altair_helpers

    assert altair_helpers.build_ridgeline_base([], "x", "g") is None
    assert altair_helpers.build_pairplot_base([], [], "c") is None
