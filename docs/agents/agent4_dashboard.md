# Agent 4 — Dashboard

## Role

Builds the Streamlit dashboard that visualizes the Swedish Municipality
Opportunity Index, reading from the `MARTS` schema and allowing users to
filter by region of birth (All / Born in Sweden / Born abroad).

## Inputs Required Before Starting

- `docs/contracts/data_contract_marts.md`.
- Populated `MARTS` tables from Agent 3 (`dim_municipality`,
  `fct_opportunity_scores`).
- A populated `.env` file with valid Snowflake credentials.
- Python virtual environment from Agent 1 with `requirements.txt`
  installed (includes `streamlit`, `pandas`, `plotly`).

## Outputs

- Streamlit application under `dashboard/` (entry point, e.g.
  `dashboard/app.py`).
- Dashboard reads only from `OPPORTUNITY_INDEX.MARTS`
  (`dim_municipality`, `fct_opportunity_scores`).
- A region-of-birth filter (`total` / `born_in_sweden` / `born_abroad`)
  that updates the displayed Opportunity Index and component scores.
- Visualizations (e.g. map/table/charts via Plotly) showing the
  Opportunity Index and its components per municipality.
- Updated status log in this file.

## Constraints

- Do NOT write Python ingestion logic or dbt models.
- Do NOT query `RAW`, `STAGING`, or `INTERMEDIATE` schemas directly —
  only `MARTS`.
- Do NOT hardcode credentials — load all Snowflake connection details from
  environment variables via `.env`.
- Do NOT change the `MARTS` contract — if additional fields are needed,
  flag this for Agent 3 and document the request in this log.

## Status Log

<!-- Append updates below as work progresses -->

### 2026-06-10 — Streamlit dashboard complete

**App structure:** `dashboard/app.py` (single-page Streamlit app),
`dashboard/snowflake_connector.py` (data access), `dashboard/requirements.txt`,
`dashboard/.streamlit/config.toml`. Verified running locally at
`http://localhost:8501` via `streamlit run dashboard/app.py`.

**Design system:** Implemented the full color palette
(`#F5F0E8` background, `#EDE8DC` surface, `#8B7355` accent, `#2C2C2C` /
`#6B6B6B` text, `#5B8A6F` positive / `#C17A5A` negative, `#D4CFC6`
borders), system sans-serif font stack, 1px solid borders, and a 4px max
border radius (2px on small chips/bars) via a single `inject_css()`
function injected with `st.markdown(unsafe_allow_html=True)`.

**`.streamlit/config.toml` extended beyond the literal spec:** the brief
only required `base = "light"`, but native Streamlit widgets (sliders,
primary buttons, tab underline/indicator, focus rings) are styled from the
`[theme]` tokens at a layer CSS injection can't reliably override across
Streamlit versions. Added `primaryColor`, `backgroundColor`,
`secondaryBackgroundColor`, `textColor`, and `font` alongside
`base = "light"` so these widgets pick up the design-system colors
consistently. This is a deliberate combination (config.toml for native
widget chrome + CSS injection for layout/typography/custom components),
not a deviation from the design intent.

**Custom HTML tables instead of `st.dataframe`:** Both the Rankings table
and the Compare table are rendered as hand-built `<table>` HTML strings
(`.ranking-table` / `.compare-table` CSS classes) via `st.markdown`. This
was necessary to get (a) per-cell gradient coloring of the Opportunity
Score (terracotta `#C17A5A` → green `#5B8A6F` via `score_color()`) and (b)
inline sparkline bars for the four component scores (`render_bar()`) —
neither is achievable with `st.dataframe`'s Styler support in the pinned
Streamlit version.

**Opportunity Index calculation (Python, not dbt):** implemented exactly
as specified —
`(employment*w_employment + income*w_income + education*w_education + mobility*w_mobility) / 100`
— recomputed on every rerun from the four `MARTS.fct_opportunity_scores`
component scores, so the four sidebar weight sliders update the Rankings
table, metric cards, and Compare tab immediately. The "Total weight: X%"
indicator turns green (`#5B8A6F`) at exactly 100% and red (`#C17A5A`)
otherwise, per spec.

**Compare tab defaults:** the multiselect (max 5 municipalities) defaults
to the **top 3 municipalities by Opportunity Index** for the currently
selected region-of-birth/weights, recomputed each time weights or the
region filter change (so the default selection stays relevant rather than
being a fixed list of names).

**Data loading / caching:** `get_opportunity_data(region_of_birth)` in
`snowflake_connector.py` is `st.cache_data(ttl=3600)`, joins
`fct_opportunity_scores` to `dim_municipality` on
`(municipality_code, year)`, and is keyed on the mapped
`region_of_birth` value (`total` / `born_in_sweden` / `born_abroad`) from
the "Population group" dropdown (`All residents` / `Born in Sweden` /
`Born abroad`). Credentials are loaded from the repo-root `.env` via
`python-dotenv` — never hardcoded. Note that **only `employment_score`
varies by `region_of_birth`** (per Agent 3's normalization methodology —
income/education/mobility are computed once per municipality and repeated
across the three `region_of_birth` rows), so switching the Population
group dropdown re-ranks municipalities primarily through the employment
component.

**Local verification (Playwright):** Navigated to
`http://localhost:8501` — page loads with header, sidebar (Population
group, 4 weight sliders + total-weight indicator, Municipality size,
County, Top N), and all three tabs render with live Snowflake data (290
municipalities, 3 region_of_birth groups). Confirmed dynamically: (1)
nudging the Mobility weight slider from 10% to 20% turns the total-weight
text red ("Total weight: 110% (should equal 100%)"), recomputes every row's
Opportunity Score, and re-sorts the table (Gällivare jumps to #1 on the
strength of its mobility score); (2) switching Population group from
"Born abroad" to "All residents" refetches data and changes the ranking
(Lomma becomes #1); (3) Compare tab radar chart + comparison table render
correctly for the default top-3 selection; (4) About tab renders the data
sources table (with working SCB endpoint links), methodology code block,
architecture diagram, and GitHub link
(`https://github.com/nelsonwv/swedish-municipality-explorer`). Zero
console errors (only standard Streamlit dev-server warnings).

**Data issues:** none — `MARTS.dim_municipality` and
`MARTS.fct_opportunity_scores` matched `data_contract_marts.md` exactly,
no additional fields were needed from Agent 3.

**Status:** Dashboard is complete and verified locally at
`http://localhost:8501`. Ready for **Agent 5 (Deployment)**.

### 2026-06-11 — Follow-up pass: map tab, grouped bars, presets, auto-normalize

**Weight auto-normalization:** `calculate_opportunity_index()` now divides
the weighted sum by `sum(weights.values())` instead of a hardcoded `/100`,
so the Opportunity Index stays on a 0-100 scale for any combination of
slider values (including all-zero, guarded to return 0). The sidebar
"Total weight" indicator was simplified to "Weights sum to X%
(auto-normalized)", always rendered in the accent color
(`#8B7355`) — the red "should equal 100%" warning state was removed
entirely since it's no longer a validity concern.

**Compare tab: radar chart -> grouped bar chart.** Replaced the
`go.Scatterpolar` radar chart with a `go.Bar` grouped bar chart
(`barmode="group"`): x-axis = Employment/Income/Education/Mobility, one
bar series per selected municipality (up to 5, using the existing
`trace_colors` design-system palette), with `textposition="outside"` data
labels showing each score to one decimal. The Opportunity Index (which
isn't one of the four bar categories) is now shown as a row of
`st.metric` cards above the chart, one per selected municipality. The old
`.compare-table` HTML table (and its now-unused `.compare-table` CSS and
`hex_to_rgba()` helper, which existed only for the radar fill colors) were
removed as redundant.

**New "Map" tab (3rd of 4 tabs):** Added `px.choropleth_mapbox` showing
the Opportunity Index for all 290 municipalities (unaffected by the
Rankings tab's size/county/top-N filters, but does respond to the
Population group and weight controls). Color scale is
`[COLOR_NEGATIVE, COLOR_POSITIVE]` (`#C17A5A` -> `#5B8A6F`) over a fixed
`range_color=(0, 100)`, `mapbox_style="carto-positron"` (no token
required), centered on `lat=62.5, lon=16.5` at `zoom=3.5`. Hover shows the
municipality name, county, Opportunity Index, and all four component
scores (`hover_data` with `:.1f` formatting and relabeled via `labels=`).

**GeoJSON source:** Tried the 3 sources in the brief in order. Source 1
(`https://raw.githubusercontent.com/okfse/sweden-geojson/...`) had the
right repo but the brief's exact filename (`swedish_regions.geojson`) is
21 *län* (county) polygons, not municipalities. The same repo's
`swedish_municipalities.geojson` (290 features, `properties.id` = 4-digit
SCB municipality code, e.g. `"0114"`) was the right file and is what's
used. Sources 2/3 were not needed. Saved to
`dashboard/data/sweden_municipalities.geojson` (818 KB, committed) and
loaded via a new `@st.cache_data`-wrapped `load_municipality_geojson()`.

**GeoJSON code matching:** Verified by querying
`MARTS.dim_municipality.municipality_code` directly against the GeoJSON's
290 `properties.id` values — **exact 1:1 match**, no remapping or
placeholder needed (`px.choropleth_mapbox(..., locations="municipality_code",
featureidkey="properties.id")`).

**4 weight presets:** Added "Balanced" / "Job seeker" / "Quality of life"
/ "Family focused" buttons in a 2x2 grid above the weight sliders
(picking up the existing global `.stButton` accent-color styling — no
extra CSS needed). Each button's `on_click` calls
`apply_weight_preset(preset_values)`, which writes directly into
`st.session_state["{dim}_weight"]`; the four sliders are now
`key`-bound (`employment_weight` / `income_weight` / `education_weight` /
`mobility_weight`) with `WEIGHT_DEFAULTS` seeded into session state via
`setdefault` on first run, so presets, manual slider drags, and reruns all
stay in sync.

**Local verification (Playwright):** Re-ran `streamlit run dashboard/app.py`
and checked all 4 tabs at `http://localhost:8502` (8501 was busy). (1)
Rankings: preset buttons render in the sidebar above the sliders;
clicking "Job seeker" set sliders to 50/30/15/5, updated "Weights sum to
100% (auto-normalized)" in accent color, and re-ranked the table (Lomma ->
#1, score 78.6). (2) Compare: grouped bar chart renders for the default
3-municipality selection with per-bar data labels and a legend, with
Opportunity Index metric cards above; no leftover comparison table. (3)
Map: choropleth renders all 290 municipalities over `carto-positron`,
centered on Sweden; inspected the live Plotly trace in-browser and
confirmed `hovertemplate` includes county + all 4 component scores,
`coloraxis.colorscale` is `[[0,"#C17A5A"],[1,"#5B8A6F"]]` with
`cmin=0/cmax=100`, and `mapbox.center/zoom/style` match the spec exactly.
(4) About: methodology code block and weight-slider description updated
to describe auto-normalization. Zero console errors/warnings.

**Status:** v2 changes complete and verified locally. Still ready for
**Agent 5 (Deployment)** — no new environment variables or dependencies
were introduced (GeoJSON is a static file bundled in `dashboard/data/`).
