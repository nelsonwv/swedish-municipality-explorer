"""
Agent 4 — Swedish Municipality Explorer dashboard.

Reads only from OPPORTUNITY_INDEX.MARTS via snowflake_connector.py.
The Opportunity Index is a weighted combination of the four MARTS
component scores, computed here in Python so the sidebar weight sliders
can recompute it dynamically.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from snowflake_connector import REGION_OF_BIRTH_MAP, get_opportunity_data

# ---------------------------------------------------------------------------
# Design system
# ---------------------------------------------------------------------------

COLOR_BACKGROUND = "#F5F0E8"
COLOR_SURFACE = "#EDE8DC"
COLOR_ACCENT = "#8B7355"
COLOR_TEXT_PRIMARY = "#2C2C2C"
COLOR_TEXT_SECONDARY = "#6B6B6B"
COLOR_POSITIVE = "#5B8A6F"
COLOR_NEGATIVE = "#C17A5A"
COLOR_BORDER = "#D4CFC6"

COMPONENT_LABELS = {
    "employment_score": "Employment",
    "income_score": "Income",
    "education_score": "Education",
    "mobility_score": "Mobility",
}

GITHUB_URL = "https://github.com/nelsonwv/swedish-municipality-explorer"


def inject_css():
    st.markdown(
        f"""
        <style>
        html, body, [class*="css"] {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                Helvetica, Arial, sans-serif;
        }}

        .stApp {{
            background-color: {COLOR_BACKGROUND};
            color: {COLOR_TEXT_PRIMARY};
        }}

        [data-testid="stSidebar"] {{
            background-color: {COLOR_SURFACE};
            border-right: 1px solid {COLOR_BORDER};
        }}

        h1, h2, h3, h4 {{
            color: {COLOR_TEXT_PRIMARY};
            font-weight: 600;
        }}

        p, span, label, div {{
            color: {COLOR_TEXT_PRIMARY};
        }}

        hr {{
            border-color: {COLOR_BORDER};
        }}

        a, a:visited {{
            color: {COLOR_ACCENT};
        }}

        /* Header */
        .app-header {{
            border-bottom: 1px solid {COLOR_BORDER};
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }}
        .app-header h1 {{
            margin-bottom: 0.25rem;
        }}
        .app-subtitle {{
            color: {COLOR_TEXT_SECONDARY};
            font-size: 1rem;
            margin: 0;
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background-color: {COLOR_SURFACE};
            border: 1px solid {COLOR_BORDER};
            border-radius: 4px;
            padding: 1rem;
        }}
        [data-testid="stMetricLabel"] {{
            color: {COLOR_TEXT_SECONDARY};
        }}
        [data-testid="stMetricValue"] {{
            color: {COLOR_TEXT_PRIMARY};
        }}
        [data-testid="stMetricDelta"] {{
            color: {COLOR_TEXT_SECONDARY};
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            border-bottom: 1px solid {COLOR_BORDER};
            gap: 1.5rem;
        }}
        .stTabs [data-baseweb="tab"] {{
            color: {COLOR_TEXT_SECONDARY};
            font-weight: 500;
        }}
        .stTabs [aria-selected="true"] {{
            color: {COLOR_ACCENT} !important;
        }}

        /* Buttons */
        .stButton > button, .stDownloadButton > button {{
            background-color: {COLOR_ACCENT};
            color: {COLOR_BACKGROUND};
            border: 1px solid {COLOR_ACCENT};
            border-radius: 4px;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {COLOR_TEXT_SECONDARY};
            border-color: {COLOR_TEXT_SECONDARY};
            color: {COLOR_BACKGROUND};
        }}

        /* Select / multiselect */
        [data-baseweb="select"] > div {{
            background-color: #FFFFFF;
            border-color: {COLOR_BORDER} !important;
            border-radius: 4px !important;
        }}
        [data-baseweb="tag"] {{
            background-color: {COLOR_ACCENT} !important;
            border-radius: 4px !important;
        }}

        /* Sliders */
        div[data-baseweb="slider"] div[role="slider"] {{
            background-color: {COLOR_ACCENT} !important;
            border-color: {COLOR_ACCENT} !important;
        }}

        /* Expander */
        [data-testid="stExpander"] {{
            border: 1px solid {COLOR_BORDER};
            border-radius: 4px;
            background-color: {COLOR_SURFACE};
        }}

        /* Custom tables */
        .ranking-table, .compare-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }}
        .ranking-table th {{
            text-align: left;
            padding: 8px 10px;
            border-bottom: 1px solid {COLOR_BORDER};
            color: {COLOR_TEXT_SECONDARY};
            font-weight: 600;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            white-space: nowrap;
        }}
        .ranking-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid {COLOR_BORDER};
            vertical-align: middle;
            white-space: nowrap;
        }}
        .ranking-table tr:nth-child(even) {{
            background-color: {COLOR_SURFACE};
        }}
        .ranking-table .rank-cell {{
            color: {COLOR_TEXT_SECONDARY};
            font-weight: 600;
            width: 32px;
        }}
        .ranking-table .name-cell {{
            font-weight: 600;
            color: {COLOR_TEXT_PRIMARY};
            white-space: normal;
        }}
        .ranking-table .num-cell {{
            text-align: right;
            font-variant-numeric: tabular-nums;
        }}
        .ranking-table .score-cell {{
            font-weight: 700;
            text-align: center;
            color: #FFFFFF;
            border-radius: 4px;
        }}

        .bar-track {{
            display: inline-block;
            width: 64px;
            height: 8px;
            background-color: {COLOR_BORDER};
            border-radius: 2px;
            vertical-align: middle;
            overflow: hidden;
        }}
        .bar-fill {{
            height: 100%;
            border-radius: 2px;
        }}
        .bar-label {{
            display: inline-block;
            margin-left: 6px;
            font-size: 0.78rem;
            color: {COLOR_TEXT_SECONDARY};
            vertical-align: middle;
            font-variant-numeric: tabular-nums;
            min-width: 28px;
        }}

        .compare-table th, .compare-table td {{
            padding: 8px 12px;
            border: 1px solid {COLOR_BORDER};
            text-align: center;
            font-variant-numeric: tabular-nums;
        }}
        .compare-table th {{
            background-color: {COLOR_SURFACE};
            color: {COLOR_TEXT_SECONDARY};
            font-weight: 600;
        }}
        .compare-table td:first-child, .compare-table th:first-child {{
            text-align: left;
            font-weight: 600;
            color: {COLOR_TEXT_PRIMARY};
            background-color: {COLOR_SURFACE};
            white-space: nowrap;
        }}
        .compare-table .score-cell {{
            color: #FFFFFF;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def hex_to_rgb(hex_color: str) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    r, g, b = hex_to_rgb(hex_color)
    return f"rgba({r},{g},{b},{alpha})"


def score_color(value: float) -> str:
    """Interpolate between negative (terracotta) and positive (green) on a 0-100 scale."""
    fraction = max(0.0, min(100.0, value)) / 100.0
    low = hex_to_rgb(COLOR_NEGATIVE)
    high = hex_to_rgb(COLOR_POSITIVE)
    rgb = tuple(round(low[i] + (high[i] - low[i]) * fraction) for i in range(3))
    return f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"


def render_bar(value: float) -> str:
    pct = max(0.0, min(100.0, value))
    return (
        f'<div class="bar-track">'
        f'<div class="bar-fill" style="width:{pct:.1f}%; background-color:{COLOR_ACCENT};"></div>'
        f"</div>"
        f'<span class="bar-label">{value:.0f}</span>'
    )


def calculate_opportunity_index(df: pd.DataFrame, weights: dict) -> pd.Series:
    """Weighted combination of the four MARTS component scores (each 0-100)."""
    score = (
        df["employment_score"] * weights["employment"]
        + df["income_score"] * weights["income"]
        + df["education_score"] * weights["education"]
        + df["mobility_score"] * weights["mobility"]
    ) / 100
    return score


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Swedish Municipality Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

st.markdown(
    """
    <div class="app-header">
        <h1>Swedish Municipality Explorer</h1>
        <p class="app-subtitle">
            Discover which municipalities offer the best conditions for residents
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------

st.sidebar.header("Filters & weights")

region_label = st.sidebar.selectbox(
    "Population group",
    options=list(REGION_OF_BIRTH_MAP.keys()),
    index=0,
    help="Filters the employment component to this population group.",
)
region_of_birth = REGION_OF_BIRTH_MAP[region_label]

st.sidebar.markdown("##### Opportunity Index weights")

employment_weight = st.sidebar.slider("Employment weight (%)", 0, 100, 35, step=5)
income_weight = st.sidebar.slider("Income weight (%)", 0, 100, 25, step=5)
education_weight = st.sidebar.slider("Education weight (%)", 0, 100, 25, step=5)
mobility_weight = st.sidebar.slider("Mobility weight (%)", 0, 100, 15, step=5)

total_weight = employment_weight + income_weight + education_weight + mobility_weight

if total_weight == 100:
    st.sidebar.markdown(
        f'<p style="color:{COLOR_POSITIVE}; font-weight:600;">Total weight: {total_weight}%</p>',
        unsafe_allow_html=True,
    )
else:
    st.sidebar.markdown(
        f'<p style="color:{COLOR_NEGATIVE}; font-weight:600;">'
        f"Total weight: {total_weight}% (should equal 100%)</p>",
        unsafe_allow_html=True,
    )

weights = {
    "employment": employment_weight,
    "income": income_weight,
    "education": education_weight,
    "mobility": mobility_weight,
}

st.sidebar.markdown("##### Municipality size")
size_options = {
    "Small (<20k)": "small",
    "Medium (20-100k)": "medium",
    "Large (>100k)": "large",
}
selected_size_labels = st.sidebar.multiselect(
    "Population category",
    options=list(size_options.keys()),
    default=list(size_options.keys()),
    label_visibility="collapsed",
)
selected_sizes = [size_options[label] for label in selected_size_labels]

st.sidebar.markdown("##### County")

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

data = get_opportunity_data(region_of_birth)
data["opportunity_index"] = calculate_opportunity_index(data, weights)

all_counties = sorted(data["county_name"].unique())
selected_counties = st.sidebar.multiselect(
    "County",
    options=all_counties,
    default=all_counties,
    label_visibility="collapsed",
)

top_n = st.sidebar.slider("Show top N municipalities", min_value=5, max_value=50, value=20)

# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

filtered = data[
    data["population_category"].isin(selected_sizes)
    & data["county_name"].isin(selected_counties)
].copy()

filtered = filtered.sort_values("opportunity_index", ascending=False).reset_index(drop=True)
filtered.insert(0, "rank", filtered.index + 1)

ranked = filtered.head(top_n)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab_rankings, tab_compare, tab_about = st.tabs(["Rankings", "Compare", "About"])

# --- Tab 1: Rankings -------------------------------------------------------

with tab_rankings:
    if ranked.empty:
        st.warning("No municipalities match the selected filters.")
    else:
        top = ranked.iloc[0]
        avg_score = ranked["opportunity_index"].mean()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Top municipality",
                top["municipality_name"],
                delta=f"Score: {top['opportunity_index']:.1f}",
                delta_color="off",
            )
        with col2:
            st.metric("Average score", f"{avg_score:.1f}")
        with col3:
            st.metric("Municipalities shown", f"{len(ranked)}")

        st.markdown("<br>", unsafe_allow_html=True)

        header_cols = (
            "<th>Rank</th><th>Municipality</th><th>County</th>"
            "<th>Population</th><th>Opportunity Score</th>"
            "<th>Employment</th><th>Income</th><th>Education</th><th>Mobility</th>"
        )

        rows_html = []
        for row in ranked.itertuples():
            score_bg = score_color(row.opportunity_index)
            rows_html.append(
                "<tr>"
                f'<td class="rank-cell">{row.rank}</td>'
                f'<td class="name-cell">{row.municipality_name}</td>'
                f"<td>{row.county_name}</td>"
                f'<td class="num-cell">{row.population:,.0f}</td>'
                f'<td class="score-cell" style="background-color:{score_bg};">'
                f"{row.opportunity_index:.1f}</td>"
                f"<td>{render_bar(row.employment_score)}</td>"
                f"<td>{render_bar(row.income_score)}</td>"
                f"<td>{render_bar(row.education_score)}</td>"
                f"<td>{render_bar(row.mobility_score)}</td>"
                "</tr>"
            )

        table_html = (
            f'<table class="ranking-table"><thead><tr>{header_cols}</tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody></table>'
        )
        st.markdown(table_html, unsafe_allow_html=True)

# --- Tab 2: Compare ----------------------------------------------------------

with tab_compare:
    st.markdown("##### Compare municipalities")

    default_selection = list(
        data.sort_values("opportunity_index", ascending=False)["municipality_name"].head(3)
    )

    compare_selection = st.multiselect(
        "Select up to 5 municipalities",
        options=sorted(data["municipality_name"].unique()),
        default=default_selection,
        max_selections=5,
    )

    if not compare_selection:
        st.info("Select one or more municipalities to compare.")
    else:
        compare_df = data[data["municipality_name"].isin(compare_selection)].copy()
        compare_df = compare_df.set_index("municipality_name").loc[compare_selection].reset_index()

        trace_colors = [COLOR_ACCENT, COLOR_POSITIVE, COLOR_NEGATIVE, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY]
        categories = list(COMPONENT_LABELS.values())

        fig = go.Figure()
        for i, row in enumerate(compare_df.itertuples()):
            values = [row.employment_score, row.income_score, row.education_score, row.mobility_score]
            color = trace_colors[i % len(trace_colors)]
            fig.add_trace(
                go.Scatterpolar(
                    r=values + values[:1],
                    theta=categories + categories[:1],
                    fill="toself",
                    name=row.municipality_name,
                    line=dict(color=color, width=2),
                    fillcolor=hex_to_rgba(color, 0.15),
                )
            )

        fig.update_layout(
            polar=dict(
                bgcolor=COLOR_SURFACE,
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=COLOR_BORDER, linecolor=COLOR_BORDER),
                angularaxis=dict(gridcolor=COLOR_BORDER, linecolor=COLOR_BORDER),
            ),
            paper_bgcolor=COLOR_BACKGROUND,
            font=dict(color=COLOR_TEXT_PRIMARY, family="-apple-system, Helvetica, Arial, sans-serif"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(t=30, b=30, l=40, r=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("##### Component scores")

        metric_rows = [("Opportunity Index", "opportunity_index")]
        for col, label in COMPONENT_LABELS.items():
            metric_rows.append((label, col))

        header_html = "<th></th>" + "".join(f"<th>{name}</th>" for name in compare_df["municipality_name"])

        body_rows = []
        for label, col in metric_rows:
            cells = [f"<td>{label}</td>"]
            for value in compare_df[col]:
                bg = score_color(value)
                cells.append(f'<td class="score-cell" style="background-color:{bg};">{value:.1f}</td>')
            body_rows.append(f"<tr>{''.join(cells)}</tr>")

        compare_table_html = (
            f'<table class="compare-table"><thead><tr>{header_html}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table>'
        )
        st.markdown(compare_table_html, unsafe_allow_html=True)

# --- Tab 3: About ------------------------------------------------------------

with tab_about:
    st.markdown("##### About this project")
    st.markdown(
        """
The **Swedish Municipality Explorer** builds a *Municipality Opportunity
Index* for all 290 Swedish municipalities, based on a 2021 snapshot of
public statistics from Statistics Sweden (SCB). The index combines four
dimensions — income, employment, education, and mobility (commuting) —
into a single comparable score, and can be filtered by **region of
birth** (all residents / born in Sweden / born abroad) to surface
disparities in opportunity across the country.
"""
    )

    st.markdown("##### Data sources (SCB PxWebApi v2)")
    st.markdown(
        """
| Dataset | SCB table | Endpoint |
|---|---|---|
| Population | `BE0101A/BefolkningNy` | [api.scb.se/.../BE/BE0101/BE0101A/BefolkningNy](https://api.scb.se/OV0104/v1/doris/en/ssd/BE/BE0101/BE0101A/BefolkningNy) |
| Median income | `AA0003F/IntGr5Kom` | [api.scb.se/.../AA/AA0003/AA0003F/IntGr5Kom](https://api.scb.se/OV0104/v1/doris/en/ssd/AA/AA0003/AA0003F/IntGr5Kom) |
| Employment | `AM0207Z/RamsForvInt04N` | [api.scb.se/.../AM/AM0207/AM0207Z/RamsForvInt04N](https://api.scb.se/OV0104/v1/doris/en/ssd/AM/AM0207/AM0207Z/RamsForvInt04N) |
| Education | `UF0506B/UtbBefRegionR` | [api.scb.se/.../UF/UF0506/UF0506B/UtbBefRegionR](https://api.scb.se/OV0104/v1/doris/en/ssd/UF/UF0506/UF0506B/UtbBefRegionR) |
| Commuting | `AM0207Z/PendlingKN` | [api.scb.se/.../AM/AM0207/AM0207Z/PendlingKN](https://api.scb.se/OV0104/v1/doris/en/ssd/AM/AM0207/AM0207Z/PendlingKN) |

All data reflects the **2021** snapshot year.
"""
    )

    st.markdown("##### Methodology")
    st.markdown(
        """
**Component scores** (`income_score`, `employment_score`,
`education_score`, `mobility_score`) are precomputed in `dbt`
(`MARTS.fct_opportunity_scores`) using min-max normalization across all
290 municipalities, scaled to 0–100:

- **Income, education**: higher raw value &rarr; higher score.
- **Mobility**: an *inverse* min-max scaling of the out-commuting rate, so
  municipalities with **less** out-commuting score higher.
- **Employment**: normalized separately within each region-of-birth
  group, so it reflects a municipality's standing among peers for that
  specific population group.

**Opportunity Index** (this dashboard, computed live in Python):

```python
def calculate_opportunity_index(df, weights):
    score = (
        df['employment_score'] * weights['employment'] +
        df['income_score'] * weights['income'] +
        df['education_score'] * weights['education'] +
        df['mobility_score'] * weights['mobility']
    ) / 100
    return score
```

Adjust the weight sliders in the sidebar to re-prioritize the four
dimensions. When the weights sum to 100%, the Opportunity Index stays on
the same 0–100 scale as the component scores.
"""
    )

    st.markdown("##### Architecture")
    st.markdown(
        """
```
SCB PxWebApi v2  -->  Snowflake RAW  -->  dbt (STAGING -> INTERMEDIATE -> MARTS)  -->  Streamlit (this app)
```

- **Ingestion**: Python pulls the 5 datasets above for snapshot year 2021
  into `OPPORTUNITY_INDEX.RAW`.
- **Transformation**: dbt models clean, join, and normalize the data
  through `STAGING`, `INTERMEDIATE`, and `MARTS`.
- **Dashboard**: this Streamlit app reads only from `OPPORTUNITY_INDEX.MARTS`
  (`dim_municipality`, `fct_opportunity_scores`).
"""
    )

    st.markdown("##### Source code")
    st.markdown(f"[{GITHUB_URL}]({GITHUB_URL})")
