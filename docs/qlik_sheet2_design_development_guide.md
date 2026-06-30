# Sheet 2 Design and Development Guide

## Application name

Create a separate Qlik Sense Enterprise application:

```text
Supply Chain Emissions Forecasting - Supplier Scenario What-If
```

This app uses the same source CSV as Sheet 1, but its data model adds
multi-supplier scenario profiles and supplier-specific adjustment slots.

## 1. Dashboard objective

Sheet 2 answers these ESG and supply-chain analytics questions:

1. What happens if an overall additional reduction is applied across selected
   suppliers?
2. How do multiple scenario profiles compare across the forecast horizon?
3. Which top-emission suppliers need individual reduction adjustments?
4. How do expert-judgement suppliers compare with suppliers that provided
   formal targets?
5. Which industries retain the largest forecast emissions after the scenario
   assumptions are applied?

## 2. Native Qlik implementation note

The reference image shows many supplier-level sliders. Qlik Sense can implement
the analytical behavior natively by mapping supplier adjustment slots to Qlik
variables:

- `Supplier_Adjustment_Slot` identifies the top 20 suppliers by current
  emissions.
- `vSupplierReduction01` through `vSupplierReduction20` store the adjustment
  values for those suppliers.
- Helper expression `vSupplierSlotReductionPct` maps each supplier to the
  correct variable.

This avoids third-party extensions, custom JavaScript, external writeback
services, and unsupported object APIs. If your Qlik tenant has the Qlik-managed
Dashboard bundle enabled, use the native Variable input object for sliders. If
it is disabled, update the same variables in Variable overview or by bookmarks.

## 3. End-to-end data model

Use the script:

```text
qlik/sheet2_supplier_specific_what_if_load_script.qvs
```

### Source

```text
supplier_emissions_source_100_records_c6ee.csv
```

Expected fields:

- `Supplier_Id`
- `Supplier_Name`
- `Industry`
- `Country`
- `Revenue`
- `Spend`
- `Emissions_Year`
- `Total_Emissions`
- `Baseline_Year`
- `Target_Year`
- `Baseline_Emissions`
- `Target_Reduction_Pct`
- `Supplier_Forecast_Flag`
- `Expert_Judgement_Reduction_Percentage`
- `Final_Reduction_Pct`
- `Final_Forecast_Method`

### Data model tables

#### `Supplier`

Grain: one row per supplier.

Purpose:

- supplier dimensions;
- current emissions;
- baseline and target metadata;
- final forecast method;
- intensity metrics;
- target availability flags.

Key field:

```text
Supplier ID
```

#### `Supplier_Group_Bridge`

Grain: one row per supplier per group.

Purpose:

- active filter for supplier intervention groups;
- supports Top 25, Region A, Region B, Expert Judgement, Supplier Target, and
  All Suppliers groups.

Key field:

```text
Supplier ID
```

Filter field:

```text
Supplier Group
```

#### `Supplier_Adjustment_Slot`

Grain: one row per top-20 supplier adjustment slot.

Purpose:

- labels supplier-specific controls;
- maps adjustment slots to `vSupplierReduction01` through
  `vSupplierReduction20`;
- links each adjustment slot to a supplier.

Key field:

```text
Supplier ID
```

Important fields:

- `Adjustment Slot`
- `Adjustment Supplier Name`
- `Supplier Reduction Variable Name`
- `Supplier Adjustment Label`

#### `Scenario_Year`

Grain: one row per year from the earliest baseline year through the net-zero
target year.

Purpose:

- island table used by line charts and forecast tables.

Field:

```text
Scenario Year
```

#### `Scenario_Profile`

Grain: one row per governed scenario profile.

Purpose:

- compares Current Plan, What-if Scenario A, Accelerated Supplier Action, and
  High Growth Pressure without duplicating supplier facts.

Fields:

- `Scenario Profile`
- `Scenario Additional Reduction Pct`
- `Scenario Expert Adjustment Pct`
- `Scenario Growth Adjustment Pct`
- `Scenario Color`
- `Scenario Sort`

#### `Forecast_Method_Color`

Small color lookup for native chart coloring.

#### `What_If_Assumptions`

Display helper table for scenario assumptions and variable names.

## 4. Qlik application setup

1. Create the Qlik app:
   **Supply Chain Emissions Forecasting - Supplier Scenario What-If**.
2. Upload the CSV to a governed connection, for example:

   ```text
   lib://ESG_Source_Data/
   ```

3. Open **Data load editor**.
4. Paste the script from:

   ```text
   qlik/sheet2_supplier_specific_what_if_load_script.qvs
   ```

5. Update the source connection if needed:

   ```qlik
   SET vSourceDataFile=lib://ESG_Source_Data/supplier_emissions_source_100_records_c6ee.csv;
   ```

6. Reload the app.
7. Open **Data model viewer** and confirm the model contains:
   - `Supplier`
   - `Supplier_Group_Bridge`
   - `Supplier_Adjustment_Slot`
   - `Scenario_Year`
   - `Scenario_Profile`
   - `Forecast_Method_Color`
   - `What_If_Assumptions`

## 5. Create helper variables

In **Assets > Variables**, add the helper variables from:

```text
docs/qlik_sheet2_expression_catalog.md
```

Required helpers:

1. `vSupplierSlotReductionPct`
2. `vScenarioProfileAdditionalReductionPct`
3. `vScenarioProfileExpertAdjustmentPct`
4. `vScenarioProfileGrowthAdjustmentPct`
5. `vEffectiveReductionPctSheet2`
6. `vScenarioTargetEmissionsSheet2`
7. `vHistoricalEmissionsSheet2AtYear`
8. `vForecastEmissionsSheet2AtYear`
9. `vNetZeroPathwaySheet2AtYear`

## 6. Create master dimensions

Create these master dimensions:

| Name | Field |
| --- | --- |
| Supplier Name | `[Supplier Name]` |
| Supplier Group | `[Supplier Group]` |
| Industry | `[Industry]` |
| Country | `[Country]` |
| Forecast Method | `[Forecast Method]` |
| Scenario Year | `[Scenario Year]` |
| Scenario Profile | `[Scenario Profile]` |
| Supplier Adjustment Label | `[Supplier Adjustment Label]` |

## 7. Create master measures

Create the measures from:

```text
docs/qlik_sheet2_expression_catalog.md
```

Recommended master measure names:

1. Overall Additional Reduction
2. Total Current Emissions
3. Total Forecast Emissions
4. Total Reduction
5. Reduction Achieved
6. Suppliers with Target
7. Suppliers Using Expert Judgement
8. Scenario Forecast Emissions
9. Forecast Emissions by Industry
10. Supplier Adjustment Active Reduction

Recommended formats:

- emissions: `#,##0 tCO2e`
- percentages: `0.0%`
- counts: `#,##0`

## 8. Sheet layout

Create one sheet:

```text
Sheet 2 - Supplier Scenario What-If
```

Recommended layout:

1. Header across the top.
2. Left control panel for overall reduction, filters, supplier groups, and
   supplier-specific adjustments.
3. KPI card row across the top center.
4. Main multi-scenario forecast line chart in the center.
5. Right-side donut and industry bar charts.
6. Year-by-year forecast table across the bottom.

## 9. Header

Object: **Text & image**

Title:

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

Subtitle:

```text
Multi-Supplier Scenario and Supplier-Specific Reduction Controls
```

Optional dynamic date:

```qlik
='Last Updated: ' & Date(Today(), 'DD MMM YYYY')
```

Style:

- dark navy background `#082F5F`;
- white title text;
- compact subtitle below the title.

## 10. Left control panel

### Overall additional reduction control

Object: Qlik-managed **Variable input** slider if available.

Variable:

```text
vOverallAdditionalReductionPct
```

Settings:

- min: `0`
- max: `0.50`
- step: `0.01`
- display: percentage

Fallback with no variable input object:

- update `vOverallAdditionalReductionPct` in Variable overview;
- create bookmarks for common values such as 5%, 10%, 12%, and 20%.

### Filters

Use native **Filter pane** objects:

1. `[Forecast Method]`
2. `[Supplier Group]`
3. `[Supplier Name]`
4. `[Industry]`
5. `[Country]`
6. `[Scenario Profile]`

For the default dashboard view, select:

```text
Scenario Profile = What-if Scenario A - Multi-Supplier
```

Then create a bookmark named:

```text
Default Scenario A
```

### Supplier-specific reduction adjustments

Use 20 Qlik-managed Variable input sliders, one per top supplier adjustment
slot:

| Control | Variable | Min | Max | Step |
| --- | --- | ---: | ---: | ---: |
| Slot 01 supplier | `vSupplierReduction01` | `0` | `0.50` | `0.01` |
| Slot 02 supplier | `vSupplierReduction02` | `0` | `0.50` | `0.01` |
| Slot 03 supplier | `vSupplierReduction03` | `0` | `0.50` | `0.01` |
| Slot 04 supplier | `vSupplierReduction04` | `0` | `0.50` | `0.01` |
| Slot 05 supplier | `vSupplierReduction05` | `0` | `0.50` | `0.01` |
| Slot 06 supplier | `vSupplierReduction06` | `0` | `0.50` | `0.01` |
| Slot 07 supplier | `vSupplierReduction07` | `0` | `0.50` | `0.01` |
| Slot 08 supplier | `vSupplierReduction08` | `0` | `0.50` | `0.01` |
| Slot 09 supplier | `vSupplierReduction09` | `0` | `0.50` | `0.01` |
| Slot 10 supplier | `vSupplierReduction10` | `0` | `0.50` | `0.01` |
| Slot 11 supplier | `vSupplierReduction11` | `0` | `0.50` | `0.01` |
| Slot 12 supplier | `vSupplierReduction12` | `0` | `0.50` | `0.01` |
| Slot 13 supplier | `vSupplierReduction13` | `0` | `0.50` | `0.01` |
| Slot 14 supplier | `vSupplierReduction14` | `0` | `0.50` | `0.01` |
| Slot 15 supplier | `vSupplierReduction15` | `0` | `0.50` | `0.01` |
| Slot 16 supplier | `vSupplierReduction16` | `0` | `0.50` | `0.01` |
| Slot 17 supplier | `vSupplierReduction17` | `0` | `0.50` | `0.01` |
| Slot 18 supplier | `vSupplierReduction18` | `0` | `0.50` | `0.01` |
| Slot 19 supplier | `vSupplierReduction19` | `0` | `0.50` | `0.01` |
| Slot 20 supplier | `vSupplierReduction20` | `0` | `0.50` | `0.01` |

To display the supplier-to-slot mapping beside the sliders, add a native
straight table:

Dimension:

```qlik
[Supplier Adjustment Label]
```

Measures:

- `Only([Supplier Reduction Variable Name])`
- `Only([Adjustment Current Emissions])`
- `$(vSupplierSlotReductionPct)`

## 11. KPI row

Use native **KPI** objects.

| KPI | Measure |
| --- | --- |
| Overall Additional Reduction | Overall Additional Reduction |
| Total Current Emissions | Total Current Emissions |
| Total Forecast Emissions | Total Forecast Emissions |
| Total Reduction | Total Reduction |
| Reduction Achieved | Reduction Achieved |
| Suppliers with Target | Suppliers with Target |
| Suppliers Expert Judgement | Suppliers Using Expert Judgement |

Suggested colors:

- current emissions: green;
- forecast emissions: blue;
- reduction: green;
- reduction achieved: purple;
- supplier target: teal;
- expert judgement: orange.

## 12. Main chart

Object: native **Line chart**.

Title:

```text
Emissions Forecast by Year - Multi-Supplier What-If Scenario
```

Dimensions:

1. `[Scenario Year]`
2. `[Scenario Profile]`

Measure:

```text
Scenario Forecast Emissions
```

Presentation:

- color by expression: `Only([Scenario Color])`;
- show markers for key years;
- sort year ascending;
- sort scenario profile by `Only([Scenario Sort])`;
- Y-axis title: `Emissions (tCO2e)`;
- X-axis title: `Year`.

## 13. Scenario assumption card

Object: **Text & image**

Expression:

```qlik
='What-if Scenario' & Chr(10)
& 'Forecast Year: ' & $(vForecastYear) & Chr(10)
& 'Overall Additional Reduction: ' & Num($(vOverallAdditionalReductionPct), '0.0%') & Chr(10)
& 'Expert Judgement Adj.: ' & Num($(vExpertJudgementAdjustmentPct), '0.0%') & Chr(10)
& 'Growth Adjustment: ' & Num($(vGrowthAdjustmentPct), '0.0%') & Chr(10)
& 'Net Zero Target: ' & $(vNetZeroYear)
```

## 14. Right-side charts

### Forecast Method Distribution

Object: native **Donut chart** or **Pie chart**

Dimension:

```qlik
[Forecast Method]
```

Measure:

```qlik
Count(DISTINCT [Supplier ID])
```

Colors:

- Supplier Target: `#43A047`
- Expert Judgement: `#FB8C00`

### Forecast Emissions by Industry

Object: native **Bar chart**

Dimension:

```qlik
[Industry]
```

Measure:

```text
Forecast Emissions by Industry
```

Presentation:

- horizontal bars;
- sort descending by measure;
- green bars;
- number format `#,##0`.

## 15. Bottom table

Object: native **Straight table**

Title:

```text
Year-by-Year Forecast Data
```

Dimension:

```qlik
[Scenario Year]
```

Measures from the expression catalog:

1. Total Emissions
2. Reduction vs Current
3. Reduction vs Current %
4. Forecast Flag

Sort:

```text
Scenario Year ascending
```

Conditional formatting:

- `Actual`: navy;
- `Forecast`: green;
- positive reduction percentage: green scale.

## 16. Reset behavior

If the native button object is available, create **Reset to Default** with these
variable actions:

```text
vForecastYear = 2030
vOverallAdditionalReductionPct = 0.12
vExpertJudgementAdjustmentPct = 0.03
vGrowthAdjustmentPct = 0.02
vNetZeroYear = 2050
vSupplierReduction01 = 0.15
vSupplierReduction02 = 0.10
vSupplierReduction03 = 0.20
vSupplierReduction04 = 0.20
vSupplierReduction05 = 0.18
vSupplierReduction06 = 0.10
vSupplierReduction07 = 0.10
vSupplierReduction08 = 0.10
vSupplierReduction09 = 0.08
vSupplierReduction10 = 0.08
vSupplierReduction11 = 0.10
vSupplierReduction12 = 0.20
vSupplierReduction13 = 0.10
vSupplierReduction14 = 0.08
vSupplierReduction15 = 0.08
vSupplierReduction16 = 0.18
vSupplierReduction17 = 0.18
vSupplierReduction18 = 0.12
vSupplierReduction19 = 0.10
vSupplierReduction20 = 0.10
```

## 17. Validation checklist

1. Reload the app successfully.
2. Confirm supplier count equals the CSV supplier count.
3. Select `Supplier Group = Top 25 Suppliers`; confirm KPIs and charts reduce to
   that population.
4. Change `vOverallAdditionalReductionPct`; confirm forecast emissions change.
5. Change one top supplier variable such as `vSupplierReduction01`; confirm:
   - the selected top supplier forecast changes;
   - total forecast emissions changes;
   - suppliers outside the top 20 are unaffected by that specific variable.
6. Select each `Scenario Profile`; confirm the line chart and bottom table
   recalculate.
7. Compare Expert Judgement versus Supplier Target suppliers using the Forecast
   Method filter.
8. Clear selections and save the `Default Scenario A` bookmark.
