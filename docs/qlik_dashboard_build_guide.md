# Supply Chain Emissions Forecasting - What-If Dashboard Build Guide

This guide builds a Qlik Sense Enterprise dashboard matching the supplied
reference sheet for corporate ESG and supply-chain emissions analysis.

The design uses only Qlik-native data load script, variables, master measures,
filter panes, KPIs, line charts, pie/donut charts, bar charts, and straight
tables. No third-party extensions are required.

## 1. App setup

1. Open **Qlik Sense Enterprise**.
2. Create a new app named:
   **Supply Chain Emissions Forecasting - What-If Analysis**.
3. Upload `supplier_emissions_source_100_records_c6ee.csv` to a governed data
   connection, for example:
   `lib://ESG_Source_Data/`.
4. Open **Data load editor**.
5. Paste the script from:
   `qlik/supply_chain_emissions_what_if_load_script.qvs`.
6. If needed, update:

   ```qlik
   SET vSourceDataFile=lib://ESG_Source_Data/supplier_emissions_source_100_records_c6ee.csv;
   ```

7. Reload the app.
8. Confirm these tables exist in the data model viewer:
   - `Supplier`
   - `Scenario_Year`
   - `Forecast_Method_Color`
   - `What_If_Assumptions`

`Scenario_Year` should remain an island table. This is intentional: the selected
supplier population is controlled by supplier dimensions, while each scenario
year is evaluated through chart expressions.

## 2. Create helper variables

1. Open **Assets > Variables**.
2. Keep the scenario variables created by the script:
   - `vForecastYear`
   - `vAdditionalReductionPct`
   - `vExpertJudgementAdjustmentPct`
   - `vGrowthAdjustmentPct`
   - `vNetZeroYear`
3. Add the helper variables listed in
   `docs/qlik_expression_catalog.md`:
   - `vEffectiveReductionPct`
   - `vScenarioTargetEmissions`
   - `vHistoricalEmissionsAtYear`
   - `vForecastEmissionsAtYear`
   - `vNetZeroPathwayAtYear`

For parameterized variables, paste the expression exactly as provided. Qlik
expands `$1` with the year argument passed by each chart measure.

## 3. Create master measures

Open **Assets > Master items > Measures** and create the measures from
`docs/qlik_expression_catalog.md`.

Recommended names:

1. `Total Current Emissions`
2. `Total Forecast Emissions`
3. `Total Reduction`
4. `Reduction Achieved`
5. `Suppliers with Target`
6. `Suppliers Using Expert Judgement`
7. `Historical Emissions`
8. `Forecast Emissions What-If`
9. `Baseline Emissions`
10. `Net Zero Pathway`
11. `Forecast Emissions by Industry`

Recommended formatting:

- Emissions: `#,##0 tCO2e`
- Percentages: `0.0%`
- Counts: `#,##0`

## 4. Create the sheet

Create a new sheet named:
**Supply Chain Emissions Forecasting - What-If Analysis**.

Recommended layout:

- Header across the top.
- Left control panel for filters and what-if controls.
- KPI row across the upper center.
- Main historical-vs-forecast line chart in the center.
- Forecast method distribution and industry bar chart on the right.
- Year-by-year straight table across the bottom.

## 5. Header

Use a **Text & image** object.

Title:

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

Subtitle:

```text
Historical (Thick Line) vs Forecast (Dotted Line)
```

Optional last-updated expression:

```qlik
='Last Updated: ' & Date(Today(), 'DD MMM YYYY')
```

Styling:

- Background: dark navy, for example `#082F5F`
- Title text: white, bold
- Subtitle text: white or light gray

## 6. Filters

Use native **Filter pane** objects.

Add these fields:

1. `[Supplier Name]`
2. `[Industry]`
3. `[Country]`
4. `[Forecast Method]`

Place them in the left control panel under a text label named **Filters**.

## 7. What-if scenario controls

Preferred native Qlik-managed option:

1. Add **Variable input** controls from the Qlik Dashboard bundle if enabled in
   your Enterprise tenant. This is Qlik-provided, not a third-party extension.
2. Configure each control as a slider:

| Label | Variable | Min | Max | Step | Display |
| --- | --- | ---: | ---: | ---: | --- |
| Forecast Year | `vForecastYear` | `$(vDataCurrentYear)` | `$(vNetZeroYear)` | `1` | number |
| Additional Reduction (%) | `vAdditionalReductionPct` | `0` | `0.50` | `0.01` | percent |
| Expert Judgement Adj. (%) | `vExpertJudgementAdjustmentPct` | `0` | `0.30` | `0.01` | percent |
| Growth Adjustment (%) | `vGrowthAdjustmentPct` | `-0.10` | `0.20` | `0.01` | percent |
| Net Zero Target Year | `vNetZeroYear` | `2040` | `2050` | `1` | number |

Strict no-extension-bundle option:

- Keep the same variables in **Variable overview** and allow authorized analysts
  to update them there.
- Use bookmarks for common scenarios such as Base Case, Accelerated Reduction,
  and High Growth.
- All KPIs and charts remain native because the calculations are standard Qlik
  expressions.

Optional reset button if your tenant includes Qlik's native button object:

- Add a button named **Reset to Default**.
- Add actions to set:
  - `vForecastYear = 2030`
  - `vAdditionalReductionPct = 0.05`
  - `vExpertJudgementAdjustmentPct = 0.03`
  - `vGrowthAdjustmentPct = 0.02`
  - `vNetZeroYear = 2050`

## 8. KPI row

Use six native **KPI** objects.

| KPI | Measure | Suggested color |
| --- | --- | --- |
| Total Current Emissions | `Total Current Emissions` | green |
| Total Forecast Emissions | `Total Forecast Emissions` | blue |
| Total Reduction | `Total Reduction` | green |
| Reduction Achieved | `Reduction Achieved` | purple |
| Suppliers with Target | `Suppliers with Target` | teal |
| Suppliers Using Expert Judgement | `Suppliers Using Expert Judgement` | orange |

Recommended secondary text:

- Current: `='Current Year: ' & Max([Current Year])`
- Forecast: `='Forecast Year: ' & $(vForecastYear)`
- Reduction: `='From current to forecast year'`
- Supplier counts: `='Suppliers'`

## 9. Main chart: historical vs forecast

Object: native **Line chart**.

Title:

```text
Emissions Forecast by Year - Historical vs Forecast (What-If Scenario)
```

Dimension:

```qlik
[Scenario Year]
```

Measures:

1. `Historical Emissions`
2. `Forecast Emissions What-If`
3. `Baseline Emissions`
4. `Net Zero Pathway`

Recommended presentation:

- Y-axis title: `Emissions (tCO2e)`
- X-axis title: `Year`
- Historical emissions: navy, thicker line, markers enabled.
- Forecast emissions: green, markers enabled, dotted or dashed if your Qlik
  version exposes per-measure line style.
- Baseline emissions: muted red, dashed.
- Net-zero pathway: gray, dashed.
- Enable data labels only for selected points if the chart becomes crowded.

Add a small **Text & image** object beside the chart with this dynamic text:

```qlik
='What-if Scenario Assumptions' & Chr(10)
& 'Forecast Year: ' & $(vForecastYear) & Chr(10)
& 'Additional Reduction: ' & Num($(vAdditionalReductionPct), '0.0%') & Chr(10)
& 'Expert Judgement Adj.: ' & Num($(vExpertJudgementAdjustmentPct), '0.0%') & Chr(10)
& 'Growth Adjustment: ' & Num($(vGrowthAdjustmentPct), '0.0%') & Chr(10)
& 'Net Zero Target: ' & $(vNetZeroYear)
```

## 10. Forecast method distribution

Object: native **Pie chart** or **Donut chart**.

Title:

```text
Forecast Method Distribution
```

Dimension:

```qlik
[Forecast Method]
```

Measure:

```qlik
Count(DISTINCT [Supplier ID])
```

Colors:

- Supplier Target: green `#43A047`
- Expert Judgement: orange `#FB8C00`

## 11. Forecast emissions by industry

Object: native **Bar chart**.

Title:

```qlik
='Forecast Emissions by Industry (' & $(vForecastYear) & ')'
```

Dimension:

```qlik
[Industry]
```

Measure:

Use `Forecast Emissions by Industry` from the expression catalog.

Presentation:

- Horizontal bars.
- Sort descending by measure.
- Color: green `#43A047`.
- Axis title: `Emissions (tCO2e)`.

## 12. Year-by-year forecast table

Object: native **Straight table**.

Title:

```text
Year-by-Year Forecast Data
```

Dimension:

```qlik
[Scenario Year]
```

Measures:

1. Historical Emissions
2. Forecast Emissions
3. Reduction vs Current
4. Reduction vs Current %
5. Forecast Phase

Sort ascending by `[Scenario Year]`.

Conditional formatting:

- Forecast Phase = `Actual`: navy text.
- Forecast Phase = `Forecast`: green text.
- Reduction vs Current %: use a positive green color scale.

## 13. ESG interpretation notes

Use a footnote text object:

```text
Note: Historical emissions are interpolated from supplier baseline emissions to
the current emissions year. Forecast emissions use supplier target reductions
where available and expert judgement assumptions where supplier targets are not
available. What-if variables adjust the forecast dynamically without data reload.
```

## 14. Validation checklist

After building the sheet:

1. Select one supplier and confirm the line chart recalculates.
2. Change `vForecastYear` and confirm the forecast KPI and industry chart update.
3. Increase `vAdditionalReductionPct` and confirm forecast emissions decrease.
4. Increase `vGrowthAdjustmentPct` and confirm future emissions increase.
5. Select `Forecast Method = Expert Judgement` and confirm the expert adjustment
   affects only the selected population.
6. Clear all selections and compare supplier counts to the source data.
