"""Viewport governance, zone rhythm, and column layout constants."""

# Viewport width governance (enterprise addon §1.3)
VIEWPORT_MAX_WIDTH = 1600
VIEWPORT_PADDING_X = 40

BREAKPOINT_ULTRAWIDE = 1920
BREAKPOINT_DESKTOP = 1280
BREAKPOINT_LAPTOP = 1024
BREAKPOINT_TABLET = 768

# Column ratios — ratio-based only, never fixed pixels
COLUMNS_HERO_SUPPORT = [3, 2]
COLUMNS_EQUAL = [1, 1]
COLUMNS_FULL = [1]
COLUMNS_LAB_CONTROL = [4, 1]
COLUMNS_KPI_PRIMARY = [1, 1, 1, 1]

# Zone vertical rhythm
ZONE_COMMAND_MARGIN_BOTTOM = 24
ZONE_INVESTIGATION_MARGIN_BOTTOM = 24
ZONE_CONTEXT_MARGIN_TOP = 64

# Analytics density governance
MAX_EAGER_CHARTS = 2
MAX_KPI_PRIMARY_ROW = 4
MAX_KPI_SECONDARY_ROW = 4

# Chart height presets by breakpoint role (desktop baseline)
CHART_HEIGHT_HERO = 540
CHART_HEIGHT_SUPPORT = 360
CHART_HEIGHT_COMPACT = 300
