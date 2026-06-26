# Qlik Sense Dashboard Detailed Design Specification

This specification expands the executive dashboard design into implementation-ready Qlik Sense settings. Use it together with:

- `docs/qlik_sense_supply_chain_emissions_build_guide.md`
- `docs/qlik_sense_dashboard_object_property_matrix.md`
- `qlik/supply_chain_dashboard_design_tokens.json`
- `qvf/supply_chain_emissions_qvf_spec.json`

## 1. Design intent

The dashboard should feel like an executive what-if control room: fast to scan, precise enough for analyst validation, and stable under filter/slider changes. The visual hierarchy is:

1. Scenario context in the header and left control panel.
2. KPI outcome summary in the top row.
3. Time-series behavior in the main chart.
4. Distribution and industry contribution in the right panel.
5. Audit detail in the bottom table.

## 2. Canvas and grid

| Property | Desktop value | Tablet value | Mobile value |
| --- | --- | --- | --- |
| Aspect ratio | 16:9, optimized for 1920 x 1080 | 4:3 or responsive browser | Single column |
| Grid columns | 24 | 12 | 4 |
| Grid rows | 14 | auto | auto |
| Outer margin | 12 px | 10 px | 8 px |
| Gutter | 8 px | 8 px | 6 px |
| Card radius | 8 px | 8 px | 6 px |
| Card padding | 12 px | 10 px | 8 px |
| Header height | 54 px | 54 px | 64 px |
| Left panel width | 4/24 columns | 12/12 top accordion | full width accordion |

### Desktop placement

| Object | Col | Row | Col span | Row span | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| Header | 1 | 1 | 24 | 1 | Full width, dark gradient. |
| Filter panel | 1 | 2 | 4 | 4 | Three required filters plus optional details. |
| Scenario controls | 1 | 6 | 4 | 5 | Sliders and reset button. |
| KPI cards | 5 | 2 | 20 | 2 | Six equal-height cards. |
| Main forecast line | 5 | 4 | 14 | 6 | Dominant visual. |
| Assumptions callout | 16 | 5 | 3 | 2 | Inside or overlay on line chart. |
| Donut chart | 19 | 4 | 6 | 3 | Method distribution. |
| Industry bar | 19 | 7 | 6 | 3 | Selected forecast year. |
| Table | 1 | 11 | 24 | 4 | Compact audit grid. |

## 3. Typography

| Element | Font | Size | Weight | Color |
| --- | --- | ---: | ---: | --- |
| Header title | Arial/Helvetica | 22 px | 700 | `#FFFFFF` |
| Header subtitle | Arial/Helvetica italic | 13 px | 600 | `#FFFFFF` |
| Last updated | Arial/Helvetica | 10 px | 600 | `#DDEBFF` |
| Section title | Arial/Helvetica | 12 px | 700 | `#111827` |
| KPI title | Arial/Helvetica | 10 px | 700 | `#334155` |
| KPI value | Arial/Helvetica | 22 px | 700 | series color |
| KPI unit | Arial/Helvetica | 10 px | 600 | `#475569` |
| Axis label | Arial/Helvetica | 10 px | 400 | `#475569` |
| Legend | Arial/Helvetica | 10 px | 500 | `#334155` |
| Table header | Arial/Helvetica | 10 px | 700 | `#111827` |
| Table body | Arial/Helvetica | 9 px | 500 | `#334155` |

## 4. Color system

| Token | Hex | Usage |
| --- | --- | --- |
| `navy900` | `#002B5C` | Header gradient start. |
| `navy800` | `#003D7A` | Header gradient end. |
| `actualBlue` | `#173B7A` | Historical actual line and actual table rows. |
| `forecastGreen` | `#43A047` | Forecast line, supplier target, positive reduction. |
| `forecastGreenDark` | `#2E7D32` | KPI values and hover states. |
| `expertOrange` | `#FB8C00` | Expert judgement and growth control. |
| `baselineRed` | `#EF5350` | Baseline line and low-performance state. |
| `netZeroGray` | `#8E8E8E` | Net-zero pathway. |
| `purple` | `#7E57C2` | Reduction percent and expert adjustment. |
| `teal` | `#00838F` | Supplier target KPI. |
| `canvas` | `#F6F8FB` | Sheet background. |
| `card` | `#FFFFFF` | Card background. |
| `border` | `#E5E7EB` | Card and control borders. |
| `textPrimary` | `#111827` | Primary text. |
| `textSecondary` | `#475569` | Secondary text. |

## 5. Header design

- Background: linear gradient `#002B5C` to `#003D7A`.
- Left/center alignment: center the title and subtitle across the dashboard width.
- Right alignment: last updated block, two lines.
- Header should not respond to selections.
- If using an image extension is not allowed, use a Text & image object with a solid `#002B5C` background and white typography.

## 6. Left panel detail

### Filter card

- Title: `Filters`.
- Required filter panes: Supplier Name, Industry, Forecast Method.
- Optional compact filters: Region, Country, Product Category.
- Search: enabled for Supplier Name and Country.
- Selection style: Qlik default green selection state; keep object background white.
- Empty state: show all values; no default selections.

### Scenario controls card

Each slider should show the variable label, selected value, and min/max endpoints.

| Slider | Track | Thumb | Value display |
| --- | --- | --- | --- |
| Forecast Year | `#DCEFE0` | `#43A047` | integer, bold green |
| Additional Reduction | `#DBEAFE` | `#2563EB` | percent, bold blue |
| Expert Judgement Adj. | `#EDE7F6` | `#7E57C2` | percent, bold purple |
| Growth Adjustment | `#FFF3E0` | `#FB8C00` | signed percent, bold orange |
| Net Zero Target Year | `#E5E7EB` | `#757575` | integer, bold gray |

Reset button:

- Label: `Reset to Default`.
- Icon: reset/refresh.
- Background: `#F8FAFC`.
- Border: `#CBD5E1`.
- Hover background: `#E2E8F0`.

## 7. KPI card design

KPI card anatomy:

1. Top-left icon at 24 px.
2. Title in small uppercase or title case.
3. Value centered, 22 px bold.
4. Unit/subtitle beneath value.
5. Optional micro-caption for selected forecast year where relevant.

| KPI | Icon concept | Tint | Value color | Tooltip |
| --- | --- | --- | --- | --- |
| Total Current Emissions | Factory | `#E8F5E9` | `#2E7D32` | Current 2025 sum after filters. |
| Total Forecast Emissions | Cloud | `#EAF2FF` | `#2563EB` | Forecast at selected `vForecastYear`. |
| Total Reduction | Declining bars | `#E8F5E9` | `#2E7D32` | Current minus selected forecast. |
| Reduction Achieved | Pie/progress | `#F3ECFF` | `#7E57C2` | Reduction divided by current emissions. |
| Suppliers with Target | Target | `#E0F7FA` | `#00838F` | Count of suppliers with target flag. |
| Expert Judgement | People | `#FFF3E0` | `#FB8C00` | Count using expert judgement method. |

## 8. Main forecast chart design

Chart goals:

- Historical line must be visually stronger than forecast uncertainty.
- Forecast line must clearly start after 2025.
- Baseline and net-zero lines are reference paths, not primary measures.

| Series | Color | Width | Style | Marker | Labeling |
| --- | --- | ---: | --- | --- | --- |
| Historical Emissions (Actual) | `#173B7A` | 3 px | solid | circle, 4 px | label first, 2025 point |
| Forecast Emissions (What-If) | `#43A047` | 2 px | dotted | circle, 4 px | label selected forecast year and end point |
| Baseline Emissions | `#EF5350` | 2 px | dashed | none | label at right edge only |
| Net Zero Pathway | `#8E8E8E` | 2 px | dashed | none | label at 2030 and 2050 if room |

Axes:

- X-axis: 2018 to 2050; show tick every 2 years on desktop, every 5 years on smaller screens.
- Y-axis: fixed start at 0 when possible; abbreviation labels as `0K`, `100K`, `200K`.
- Tooltip: include Year, Actual, Forecast, Baseline, Net Zero Pathway, Reduction vs 2025, and Reduction %.
- Reference marker: vertical rule at `$(vForecastYear)` if available; otherwise callout point.

## 9. Right panel design

### Donut chart

- Inner radius: 60%.
- Segment order: Supplier Target first, Expert Judgement second.
- Label format: percent in center and count in legend.
- Center label: `Forecast Method` or total supplier count.
- Legend placement: right on desktop, bottom on tablet/mobile.

### Industry bar chart

- Orientation: horizontal.
- Sort: measure descending.
- Bar color: `#43A047`; hover color `#2E7D32`.
- Show data labels outside bars when space permits.
- Axis label: `Emissions (tCO2e)`.
- Limit: show all 10 industries; if more industries are added later, show top 10 plus Others.

## 10. Bottom table design

- Use straight table for Qlik-native implementation; use pivot only if columns must become years.
- Freeze first column if supported by the Qlik environment.
- Compact density: row height 26 px.
- Header background: `#F8FAFC`.
- Actual-year cells: blue text `#173B7A`.
- Forecast-year cells: green text `#2E7D32`.
- Null actual reduction cells: display `-`.
- Enable export data.
- Use conditional text color based on `YearStatus`.

## 11. Interaction behavior

| Interaction | Expected behavior |
| --- | --- |
| Supplier selection | All KPIs and charts recalculate for selected suppliers. |
| Industry selection | Donut, KPIs, line chart, bar chart, and table all reduce to selected industry. |
| Forecast Method selection | Donut segment remains selected; all forecast values recalculate. |
| Slider movement | KPI forecast, reduction, line chart, industry bar, assumptions box, and table update immediately. |
| Reset button | Restores all five scenario variables to defaults without clearing filters. |
| Clear selections | Clears Qlik selections but does not reset scenario variables. |

## 12. Responsive rules

| Breakpoint | Behavior |
| --- | --- |
| Desktop >= 1440 px | Full layout: left controls, KPI row, main chart, right panel, bottom table. |
| Laptop 1024-1439 px | Keep layout but reduce table height and hide non-critical data labels. |
| Tablet 768-1023 px | Collapse left filters above KPI row; stack right charts below main line chart. |
| Mobile < 768 px | Single-column scroll: filters, sliders, KPIs two per row, line chart, donut, bar, table. |

## 13. Accessibility and governance

- Do not rely on color alone: line styles and labels distinguish series.
- Keep contrast at or above WCAG AA for text.
- Add descriptive titles to all objects.
- Use `tCO2e` consistently as the unit label.
- Keep number formatting consistent: emissions `#,##0`; percentages `0.0%`.
- Avoid abbreviating supplier names in filters; use search instead.
- Include a footer or help tooltip explaining that sliders are scenario assumptions, not changed source data.

## 14. QA checklist

| Check | Expected result |
| --- | --- |
| Header visible | Title, subtitle, last updated display correctly. |
| KPI alignment | All KPI cards have equal height and aligned value baselines. |
| Slider labels | Labels, values, min, max, and reset work as specified. |
| Chart series | Actual solid, forecast dotted, baseline dashed red, net-zero dashed gray. |
| Tooltip | Includes all relevant measures and units. |
| Donut colors | Supplier Target green, Expert Judgement orange. |
| Bar sort | Industries sort by selected-year forecast emissions descending. |
| Table colors | Actual years blue, forecast years green. |
| Export | Sheet image/PDF and table data export work. |
| Selection state | Filter selections are visible and clearable. |
