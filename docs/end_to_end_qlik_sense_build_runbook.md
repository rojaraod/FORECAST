# End-to-End Qlik Sense Build Runbook

This runbook explains how to build the Supply Chain Emissions Forecasting what-if dashboard in Qlik Sense from the included source files. It is written for a Qlik Sense developer or analyst who needs to recreate the attached dashboard image inside the Qlik Sense platform.

## 1. Files you need

Use these repository files:

| File | Purpose |
| --- | --- |
| `data/supply_chain_emissions_suppliers_50.csv` | Main 50-supplier source data. |
| `data/supply_chain_emissions_supplier_year_default_forecast.csv` | Optional QA extract with 1,650 supplier-year forecast rows. |
| `data/supply_chain_emissions_scope_breakdown_2025.csv` | Optional Scope 1/2/3 breakdown for supplier detail views. |
| `qlik/supply_chain_emissions_what_if_model.qvs` | Qlik Data Load Editor script. |
| `qlik/supply_chain_emissions_theme.json` | Optional custom Qlik theme. |
| `qlik/supply_chain_dashboard_design_tokens.json` | Detailed colors, grid, typography, and placement tokens. |
| `docs/qlik_sense_supply_chain_emissions_build_guide.md` | Object expressions and base dashboard build guide. |
| `docs/qlik_sense_dashboard_detailed_design_spec.md` | Detailed design and responsive layout specification. |
| `docs/qlik_sense_dashboard_object_property_matrix.md` | Object-level property matrix. |
| `qvf/supply_chain_emissions_qvf_spec.json` | Machine-readable app/QVF source specification. |

## 2. Qlik Sense prerequisites

You need one of these environments:

- Qlik Sense Cloud
- Qlik Sense Enterprise on Windows
- Qlik Sense Desktop

Recommended extensions:

- Dashboard bundle Variable input object for sliders.
- Vizlib Input Box or Vizlib Slider if you want advanced what-if input controls.
- Vizlib Writeback Table if you want to input many supplier-specific scenarios at once.

## 3. Create the Qlik app

1. Open Qlik Sense.
2. Create a new app.
3. Name the app:

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

4. Open the app.
5. Go to Data Load Editor.

## 4. Add the data connection

Create a folder or data-files connection named exactly:

```text
SupplyChainData
```

Upload this file into that connection:

```text
data/supply_chain_emissions_suppliers_50.csv
```

The load script expects this Qlik path:

```qlik
lib://SupplyChainData/supply_chain_emissions_suppliers_50.csv
```

If your connection name is different, edit this line in the script:

```qlik
SET vDataConnection = 'lib://SupplyChainData';
```

## 5. Load the data model

1. Open `qlik/supply_chain_emissions_what_if_model.qvs`.
2. Copy the full script.
3. Paste it into Qlik Sense Data Load Editor.
4. Click Load data.

Expected model:

| Table | Expected result |
| --- | --- |
| `FactSupplierYear` | 1,650 rows: 50 suppliers x 33 years. |
| `IndustrySort` | 10 industry sort values. |

Validation expressions:

```qlik
Count(DISTINCT SupplierID)
```

Expected:

```text
50
```

```qlik
Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
```

Expected:

```text
619700
```

## 6. Create variables

Create these variables in Qlik Sense.

| Variable | Default | Notes |
| --- | ---: | --- |
| `vCurrentYear` | `2025` | Current emissions year. |
| `vBaselineYear` | `2026` | Baseline reference year. |
| `vForecastYear` | `2030` | Forecast KPI year. |
| `vAdditionalReductionPct` | `0.05` | Global extra reduction. |
| `vExpertJudgementAdjPct` | `0.03` | Extra adjustment for Expert Judgement suppliers. |
| `vGrowthAdjustmentPct` | `0.02` | Annual growth assumption. |
| `vNetZeroTargetYear` | `2050` | Net-zero endpoint. |
| `vLastUpdated` | `25 May 2025` | Header date label. |

## 7. Build the sheet layout

Create one sheet named:

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

Use a 24-column style layout.

| Area | Placement | Objects |
| --- | --- | --- |
| Header | Full width top | Title, subtitle, last updated. |
| Left panel | Left side | Filters and what-if controls. |
| KPI row | Top center/right | Six KPI cards. |
| Main chart | Center | Historical vs forecast line chart. |
| Right panel | Right side | Donut and industry bar chart. |
| Bottom panel | Full width bottom | Year-by-year table. |

## 8. Build the header

Use a Text & image object.

Title:

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

Subtitle:

```text
Historical (Thick Line) vs Forecast (Dotted Line)
```

Last updated text:

```qlik
='Last Updated:' & Chr(10) & '$(vLastUpdated)'
```

Style:

| Setting | Value |
| --- | --- |
| Background | Navy gradient or solid `#002B5C` |
| Title color | `#FFFFFF` |
| Subtitle color | `#FFFFFF` |
| Subtitle style | Italic |

## 9. Add filters

Create filter panes for:

| Filter title | Field |
| --- | --- |
| Supplier Name | `SupplierName` |
| Industry | `Industry` |
| Forecast Method | `ForecastMethod` |

Optional filters:

```text
Region
Country
ProductCategory
ContactOwner
```

## 10. Add what-if controls

Use Qlik Dashboard bundle Variable input controls, or Vizlib Input Box/Slider controls.

| Control | Variable | Min | Max | Step | Color |
| --- | --- | ---: | ---: | ---: | --- |
| Forecast Year | `vForecastYear` | 2026 | 2050 | 1 | `#43A047` |
| Additional Reduction | `vAdditionalReductionPct` | 0 | 0.50 | 0.01 | `#2563EB` |
| Expert Judgement Adj. | `vExpertJudgementAdjPct` | 0 | 0.30 | 0.01 | `#7E57C2` |
| Growth Adjustment | `vGrowthAdjustmentPct` | -0.10 | 0.20 | 0.01 | `#FB8C00` |
| Net Zero Target Year | `vNetZeroTargetYear` | 2035 | 2050 | 1 | `#757575` |

Add a Reset to Default button with actions:

```text
Set vForecastYear = 2030
Set vAdditionalReductionPct = 0.05
Set vExpertJudgementAdjPct = 0.03
Set vGrowthAdjustmentPct = 0.02
Set vNetZeroTargetYear = 2050
```

## 11. Create reusable forecast measure

Use this expression for dynamic forecast emissions:

```qlik
Sum({<YearStatus={'Forecast'}>}
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), YearsFromCurrent)
  * RangeMax(
      0,
      1
      - RangeMin(
          0.95,
          (BaseReduction2030Rate + $(vAdditionalReductionPct) + If(ForecastMethod = 'Expert Judgement', $(vExpertJudgementAdjPct), 0))
          * RangeMin(YearsFromCurrent, 5) / 5
        )
      - If(
          Year > $(vForecastYear),
          RangeMin(1, (Year - $(vForecastYear)) / RangeMax(1, $(vNetZeroTargetYear) - $(vForecastYear)))
          * RangeMax(0, 1 - (BaseReduction2030Rate + $(vAdditionalReductionPct) + If(ForecastMethod = 'Expert Judgement', $(vExpertJudgementAdjPct), 0))),
          0
        )
    )
)
```

Use this expression for forecast emissions at selected forecast year:

```qlik
Sum({<Year={$(=$(vForecastYear))}>}
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), YearsFromCurrent)
  * RangeMax(
      0,
      1
      - RangeMin(
          0.95,
          (BaseReduction2030Rate + $(vAdditionalReductionPct) + If(ForecastMethod = 'Expert Judgement', $(vExpertJudgementAdjPct), 0))
          * RangeMin(YearsFromCurrent, 5) / 5
        )
      - If(
          Year > $(vForecastYear),
          RangeMin(1, (Year - $(vForecastYear)) / RangeMax(1, $(vNetZeroTargetYear) - $(vForecastYear)))
          * RangeMax(0, 1 - (BaseReduction2030Rate + $(vAdditionalReductionPct) + If(ForecastMethod = 'Expert Judgement', $(vExpertJudgementAdjPct), 0))),
          0
        )
    )
)
```

## 12. Build KPI cards

Create six KPI objects.

### KPI 1: Total Current Emissions

```qlik
Num(Sum({<Year={2025}>} CurrentEmissions2025_tCO2e), '#,##0')
```

### KPI 2: Total Forecast Emissions

Use the selected forecast-year expression from section 11 wrapped in:

```qlik
Num(<forecast_selected_year_expression>, '#,##0')
```

### KPI 3: Total Reduction

```qlik
Num(
  Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
  - <forecast_selected_year_expression>,
  '#,##0'
)
```

### KPI 4: Reduction Achieved

```qlik
Num(
  (Sum({<Year={2025}>} CurrentEmissions2025_tCO2e) - <forecast_selected_year_expression>)
  / Sum({<Year={2025}>} CurrentEmissions2025_tCO2e),
  '0.0%'
)
```

### KPI 5: Suppliers with Target

```qlik
Count({<SupplierTargetFlag={'Y'}>} DISTINCT SupplierID)
```

### KPI 6: Suppliers Expert Judgement

```qlik
Count({<ForecastMethod={'Expert Judgement'}>} DISTINCT SupplierID)
```

## 13. Build the main line chart

Object type:

```text
Line chart
```

Dimension:

```text
Year
```

Measures:

### Historical Actual

```qlik
Sum({<YearStatus={'Actual'}>} CurrentEmissions2025_tCO2e * ActualFactor)
```

### Forecast What-If

Use the dynamic forecast expression from section 11.

### Baseline Emissions

```qlik
Sum(
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), $(vBaselineYear) - $(vCurrentYear))
)
```

### Net Zero Pathway

```qlik
Sum(
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), $(vForecastYear) - $(vCurrentYear))
  * RangeMax(0, ($(vNetZeroTargetYear) - Year) / RangeMax(1, $(vNetZeroTargetYear) - $(vForecastYear)))
)
```

Style:

| Series | Color | Line style |
| --- | --- | --- |
| Actual | `#173B7A` | Thick solid |
| Forecast | `#43A047` | Dotted |
| Baseline | `#EF5350` | Dashed |
| Net Zero Pathway | `#8E8E8E` | Dashed |

## 14. Add assumptions callout

Use a Text & image object.

```qlik
='Forecast Year: ' & $(vForecastYear) & Chr(10) &
'Additional Reduction: ' & Num($(vAdditionalReductionPct), '0%') & Chr(10) &
'Expert Judgement Adj.: ' & Num($(vExpertJudgementAdjPct), '0%') & Chr(10) &
'Growth Adjustment: ' & Num($(vGrowthAdjustmentPct), '0%') & Chr(10) &
'Net Zero Target: ' & $(vNetZeroTargetYear)
```

## 15. Build the donut chart

Object type:

```text
Pie chart, donut mode
```

Dimension:

```text
ForecastMethod
```

Measure:

```qlik
Count(DISTINCT SupplierID)
```

Colors:

| Value | Color |
| --- | --- |
| Supplier Target | `#43A047` |
| Expert Judgement | `#FB8C00` |

## 16. Build the industry bar chart

Object type:

```text
Horizontal bar chart
```

Dimension:

```text
Industry
```

Measure:

```text
Forecast emissions at selected vForecastYear
```

Sort:

```text
Measure descending
```

Color:

```text
#43A047
```

## 17. Build the year-by-year table

Object type:

```text
Straight table
```

Dimension:

```text
Year
```

Measures:

| Measure | Logic |
| --- | --- |
| Total Emissions | Actual expression for actual years, forecast expression for forecast years. |
| Reduction vs 2025 | 2025 current emissions minus forecast emissions. |
| Reduction vs 2025 % | Reduction divided by 2025 current emissions. |
| Forecast Status | `Only(YearStatus)` |

Format:

| Row type | Color |
| --- | --- |
| Actual | `#173B7A` |
| Forecast | `#2E7D32` |

## 18. Optional: supplier-specific Vizlib input

If you want one selected supplier at a time:

1. Add a SupplierName filter.
2. Add Vizlib Input Box controls for supplier scenario variables.
3. Use the same forecast expression, replacing global variables with supplier variables.
4. Add supplier-level KPIs and a supplier forecast line chart.

Recommended supplier variables:

```text
vSupplierForecastYear
vSupplierAdditionalReductionPct
vSupplierGrowthAdjustmentPct
vSupplierExpertAdjPct
vSupplierNetZeroTargetYear
```

## 19. Optional: all-supplier Vizlib Writeback

If you need users to input assumptions for many suppliers at one time, use Vizlib Writeback Table.

Recommended writeback table columns:

```text
SupplierID
SupplierName
ScenarioName
ForecastYear
AdditionalReductionPct
GrowthAdjustmentPct
ExpertAdjustmentPct
NetZeroTargetYear
IsActive
Comment
```

Use this when each supplier needs different inputs. Use Variable Input sliders when all selected suppliers share the same assumption values.

## 20. Apply theme and design

Use these files:

```text
qlik/supply_chain_emissions_theme.json
qlik/supply_chain_dashboard_design_tokens.json
docs/qlik_sense_dashboard_detailed_design_spec.md
```

Core design values:

| Element | Value |
| --- | --- |
| Header | `#002B5C` to `#003D7A` |
| Canvas | `#F6F8FB` |
| Cards | `#FFFFFF` |
| Actual | `#173B7A` |
| Forecast | `#43A047` |
| Expert Judgement | `#FB8C00` |
| Baseline | `#EF5350` |
| Net Zero | `#8E8E8E` |

## 21. Final validation

Check these numbers with no filters selected:

| Test | Expected |
| --- | ---: |
| Supplier count | 50 |
| Current emissions 2025 | 619,700 |
| Supplier Target count | 30 |
| Expert Judgement count | 20 |
| Supplier-year rows | 1,650 |

Slider tests:

1. Move Forecast Year from 2030 to 2035.
2. Confirm forecast KPI changes.
3. Confirm reduction KPI changes.
4. Confirm line chart changes.
5. Confirm industry bar chart changes.
6. Click Reset to Default and confirm values return to defaults.

Filter tests:

1. Select one industry.
2. Confirm KPIs, line chart, donut, bar chart, and table all filter.
3. Select one supplier.
4. Confirm current and forecast values reduce to that supplier.
5. Clear selections.

## 22. Save and export QVF

After the dashboard is complete:

1. Save the app.
2. Reload once more.
3. Validate key metrics.
4. Export the app as:

```text
Supply_Chain_Emissions_Forecasting_What_If.qvf
```

If using Qlik Sense Desktop with local engine access, the included helper can create the app shell:

```bash
node scripts/create_qvf_local_engine.mjs
```

Then finish the visual objects in Qlik Sense and export the `.qvf`.

## 23. Recommended build order

Follow this order to avoid rework:

1. Data connection.
2. Load script reload.
3. Variables.
4. Filters.
5. KPI cards.
6. Forecast expressions.
7. Main line chart.
8. Donut and industry bar chart.
9. Year table.
10. Theme and styling.
11. Optional Vizlib supplier input/writeback.
12. Validation.
13. QVF export.
