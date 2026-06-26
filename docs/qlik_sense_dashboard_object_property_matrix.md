# Qlik Sense Dashboard Object Property Matrix

Use this matrix with `qlik_sense_supply_chain_emissions_build_guide.md` when configuring the final Qlik Sense sheet or QVF app.

## Global sheet behavior

| Setting | Value |
| --- | --- |
| Sheet title | Supply Chain Emissions Forecasting - What-If Analysis |
| Grid | 24 columns, 14 rows |
| Responsive behavior | Keep left panel fixed; stack right-panel charts under line chart on tablet/mobile |
| Selection toolbar | On |
| Snapshot/export | Enabled for KPI row, line chart, donut, bar chart, and table |
| Theme | `qlik/supply_chain_emissions_theme.json` |
| Background | `#F6F8FB` |
| Card radius | 8 px |
| Card shadow | subtle, 10% opacity |

## Object property details

| Object | Qlik object type | Data settings | Presentation settings | Interaction settings |
| --- | --- | --- | --- | --- |
| Header | Text & image | Static title plus `$(vLastUpdated)` | Navy gradient, white title, italic subtitle | No selections |
| Supplier filter | Filter pane | Dimension `SupplierName`; search enabled | Dropdown/list, white card | Single or multiple selection |
| Industry filter | Filter pane | Dimension `Industry`; sort by `IndustrySortOrder` | Dropdown/list, white card | Multiple selection |
| Forecast method filter | Filter pane | Dimension `ForecastMethod` | Color hints: green/orange | Multiple selection |
| Variable sliders | Variable input | Bind five variables from guide | Show labels, min/max, current value | Slider mode, immediate update |
| Reset button | Button | Five set-variable actions | Light grey background, refresh icon | Clear scenario back to defaults |
| KPI cards | KPI | One measure each | Rounded cards, icon left, number center | Responsive, no drilldown |
| Main line chart | Line chart | Dimension `Year`; four measures | Actual solid/thick, forecast dotted, baseline and net-zero dashed | Tooltip on, zoom off, legend top |
| Assumptions box | Text & image | Variable-driven text expression | White card with grey border | No selections |
| Donut | Pie chart | `ForecastMethod`; count suppliers | Inner radius 60%, labels on | Select by segment enabled |
| Industry bar | Bar chart | `Industry`; forecast selected-year measure | Horizontal, labels on, green bars | Select by industry enabled |
| Year table | Straight table | `Year` and four measures | Compact rows, conditional actual/forecast colors | Export data enabled |

## Conditional formatting rules

| Target | Rule | Color/Format |
| --- | --- | --- |
| Forecast table status | `YearStatus='Actual'` | Blue `#173B7A` |
| Forecast table status | `YearStatus='Forecast'` | Green `#2E7D32` |
| Reduction percentage | value >= 0.30 | Green `#2E7D32` |
| Reduction percentage | value between 0.15 and 0.30 | Orange `#FB8C00` |
| Reduction percentage | value < 0.15 | Red `#EF5350` |
| Data quality score | value >= 90 | Green badge |
| Data quality score | value 80-89 | Amber badge |
| Data quality score | value < 80 | Red badge |

## Recommended master dimensions

| Label | Field/expression | Sort |
| --- | --- | --- |
| Supplier | `SupplierName` | A-Z |
| Industry | `Industry` | `IndustrySortOrder` ascending |
| Region | `Region` | A-Z |
| Forecast Method | `ForecastMethod` | Supplier Target, Expert Judgement |
| Year | `Year` | numeric ascending |
| Year Status | `YearStatus` | Actual, Forecast |

## Optional add-on sheets

| Sheet | Purpose | Suggested objects |
| --- | --- | --- |
| Supplier Detail | Drill into one supplier profile | Supplier KPI strip, scope breakdown stacked bar, forecast line, data quality card |
| Industry Deep Dive | Compare industries | Industry scatter, supplier table, regional contribution map |
| Scenario Comparison | Compare default and custom settings | Side-by-side KPIs, variance waterfall, assumptions table |
| Data Quality | Review input readiness | Data quality histogram, missing target list, owner filter |
