# Qlik Sense Build Guide - Supply Chain Emissions Forecasting What-If Analysis

This guide implements the dashboard in the reference image using:

- `data/supply_chain_emissions_suppliers_50.csv`: 50 supplier records.
- `qlik/supply_chain_emissions_what_if_model.qvs`: Qlik Sense load script and data model.

The unfiltered 2025 current emissions total is `619,700 tCO2e`. The sample distribution is 30 suppliers with a supplier target and 20 suppliers using expert judgement.

## 1. Data model

### Source CSV grain

One record equals one supplier. The CSV includes supplier attributes, industry, forecast method, 2025 emissions, reduction assumptions, growth defaults, and net-zero target year.

### Qlik model grain

The load script creates `FactSupplierYear` at this grain:

```text
SupplierID + Year
```

Expected model row count after reload:

```text
50 suppliers x 33 years (2018-2050) = 1,650 rows
```

`FactSupplierYear` contains all filter dimensions and all measure inputs so the dashboard has one clear fact table and no synthetic-key risk. `IndustrySort` provides controlled sorting for industry visuals.

### Reload setup

1. Upload `data/supply_chain_emissions_suppliers_50.csv` to Qlik Sense.
2. Create a data connection named `SupplyChainData`.
3. Paste `qlik/supply_chain_emissions_what_if_model.qvs` into the Data Load Editor.
4. Reload and validate:

```qlik
Count(DISTINCT SupplierID) = 50
Sum({<Year={2025}>} CurrentEmissions2025_tCO2e) = 619700
```

## 2. Variables and sliders

Create the variables below in Qlik Sense and bind each to a Dashboard bundle **Variable input** object.

| Control | Variable | Default | Min | Max | Step | Display | Color |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Forecast Year | `vForecastYear` | `2030` | `2026` | `2050` | `1` | integer | green `#43A047` |
| Additional Reduction (%) | `vAdditionalReductionPct` | `0.05` | `0` | `0.50` | `0.01` | percent | blue `#2563EB` |
| Expert Judgement Adj. (%) | `vExpertJudgementAdjPct` | `0.03` | `0` | `0.30` | `0.01` | percent | purple `#7E57C2` |
| Growth Adjustment (%) | `vGrowthAdjustmentPct` | `0.02` | `-0.10` | `0.20` | `0.01` | percent | orange `#FB8C00` |
| Net Zero Target Year | `vNetZeroTargetYear` | `2050` | `2035` | `2050` | `1` | integer | grey `#757575` |

### Reset button

Use a Button object with these actions:

1. Set `vForecastYear` to `2030`.
2. Set `vAdditionalReductionPct` to `0.05`.
3. Set `vExpertJudgementAdjPct` to `0.03`.
4. Set `vGrowthAdjustmentPct` to `0.02`.
5. Set `vNetZeroTargetYear` to `2050`.

Button text: `Reset to Default`.
Button background: `#F8FAFC`; border: `#CBD5E1`; icon: reset/refresh, `#64748B`.

## 3. Sheet layout and theme

| Area | Placement | Contents |
| --- | --- | --- |
| Header | full width | title, subtitle, last updated |
| Left panel | 20% width | filters and sliders |
| KPI row | top center | six KPI cards |
| Main panel | center | line chart and assumptions box |
| Right panel | right side | donut and industry bar chart |
| Bottom panel | full width | year-by-year table |

### Colors

| Element | Color |
| --- | --- |
| Header gradient start | `#002B5C` |
| Header gradient end | `#003D7A` |
| Sheet background | `#F6F8FB` |
| Card background | `#FFFFFF` |
| Card border | `#E5E7EB` |
| Actual line | `#173B7A` |
| Forecast line | `#43A047` |
| Baseline line | `#EF5350` |
| Net-zero line | `#8E8E8E` |
| Supplier Target | `#43A047` |
| Expert Judgement | `#FB8C00` |
| KPI purple | `#7E57C2` |
| KPI teal | `#00838F` |

## 4. Filters

Use filter panes in the left panel.

| Filter | Dimension | Options |
| --- | --- | --- |
| Supplier Name | `SupplierName` | dropdown or list, search on |
| Industry | `Industry` | dropdown or list, sort by `IndustrySortOrder` |
| Forecast Method | `ForecastMethod` | dropdown or list, colors match donut chart |

Optional filters: `Region`, `Country`, `ProductCategory`, `ContactOwner`.

## 5. Master measures

Create these as reusable master measures.

### Current emissions, 2025

```qlik
Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
```

### Dynamic forecast emissions

Use this expression for forecast line points. It reacts to all sliders because the variables are evaluated in the chart.

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

### Dynamic forecast emissions at selected forecast year

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

### Reduction at selected forecast year

```qlik
Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
-
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

### Reduction percentage at selected forecast year

```qlik
(
  Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
  -
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
)
/
Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
```

## 6. Object-by-object build

### Header object

- Object: Text & image.
- Title: `Supply Chain Emissions Forecasting - What-If Analysis`.
- Subtitle: `Historical (Thick Line) vs Forecast (Dotted Line)`.
- Last updated expression: `='Last Updated:' & Chr(10) & '$(vLastUpdated)'`.
- Background: horizontal gradient from `#002B5C` to `#003D7A`.
- Title color: `#FFFFFF`; subtitle color: `#FFFFFF`; subtitle italic.

### KPI 1 - Total Current Emissions (2025)

- Object: KPI.
- Measure:

```qlik
Num(Sum({<Year={2025}>} CurrentEmissions2025_tCO2e), '#,##0')
```

- Unit: `tCO2e`.
- Background: `#E8F5E9`; number color: `#2E7D32`; icon: factory.

### KPI 2 - Total Forecast Emissions

- Object: KPI.
- Title expression: `='Total Forecast Emissions (' & $(vForecastYear) & ')'`.
- Measure:

```qlik
Num(Sum({<Year={$(=$(vForecastYear))}>}
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
), '#,##0')
```

- Unit: `tCO2e`.
- Background: `#EAF2FF`; number color: `#2563EB`; icon: cloud/rain.

### KPI 3 - Total Reduction

- Object: KPI.
- Title expression: `='Total Reduction (2025 to ' & $(vForecastYear) & ')'`.
- Measure:

```qlik
Num(
  Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)
  - Sum({<Year={$(=$(vForecastYear))}>}
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
),
  '#,##0'
)
```

- Unit: `tCO2e`.
- Background: `#E8F5E9`; number color: `#2E7D32`; icon: declining bar.

### KPI 4 - Reduction Achieved

- Object: KPI.
- Measure:

```qlik
Num(
  (Sum({<Year={2025}>} CurrentEmissions2025_tCO2e) - Sum({<Year={$(=$(vForecastYear))}>}
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
))
  / Sum({<Year={2025}>} TOTAL CurrentEmissions2025_tCO2e),
  '0.0%'
)
```

- Subtitle: `vs Current`.
- Background: `#F3ECFF`; number color: `#7E57C2`; icon: pie/progress.

### KPI 5 - Suppliers with Target

- Object: KPI.
- Measure:

```qlik
Count({<SupplierTargetFlag={'Y'}>} DISTINCT SupplierID)
```

- Subtitle: `Suppliers`.
- Background: `#E0F7FA`; number color: `#00838F`; icon: target.

### KPI 6 - Suppliers (Expert Judgement)

- Object: KPI.
- Measure:

```qlik
Count({<ForecastMethod={'Expert Judgement'}>} DISTINCT SupplierID)
```

- Subtitle: `Suppliers`.
- Background: `#FFF3E0`; number color: `#FB8C00`; icon: people.

### Main line chart - Emissions Forecast by Year

- Object: Line chart.
- Dimension: `Year`.
- Sort: numeric ascending.
- Y-axis title: `Emissions (tCO2e)`.
- X-axis title: `Year`.
- Title: `Emissions Forecast by Year (All Suppliers) - Historical vs Forecast (What-If Scenario)`.

Measures:

```qlik
// Historical Emissions (Actual)
Sum({<YearStatus={'Actual'}>} CurrentEmissions2025_tCO2e * ActualFactor)
```

```qlik
// Forecast Emissions (What-If)
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

```qlik
// Baseline Emissions (at Baseline Year)
Sum(
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), $(vBaselineYear) - $(vCurrentYear))
)
```

```qlik
// Net Zero Pathway
Sum(
  CurrentEmissions2025_tCO2e
  * Pow(1 + $(vGrowthAdjustmentPct), $(vForecastYear) - $(vCurrentYear))
  * RangeMax(0, ($(vNetZeroTargetYear) - Year) / RangeMax(1, $(vNetZeroTargetYear) - $(vForecastYear)))
)
```

Options:

- Actual line: solid, width 3, color `#173B7A`, markers on.
- Forecast line: dotted, width 2, color `#43A047`, markers on.
- Baseline line: dashed, width 2, color `#EF5350`, markers off.
- Net zero line: dashed, width 2, color `#8E8E8E`, markers off.
- Legend: top.
- Data labels: on for compact desktop view; turn off for smaller screens.
- Tooltip: include Year, all four measures, and reduction percentage.

### Assumptions box

- Object: Text & image.
- Title: `What-If Scenario Assumptions`.
- Body expression:

```qlik
='Forecast Year: ' & $(vForecastYear) & Chr(10) &
'Additional Reduction: ' & Num($(vAdditionalReductionPct), '0%') & Chr(10) &
'Expert Judgement Adj.: ' & Num($(vExpertJudgementAdjPct), '0%') & Chr(10) &
'Growth Adjustment: ' & Num($(vGrowthAdjustmentPct), '0%') & Chr(10) &
'Net Zero Target: ' & $(vNetZeroTargetYear)
```

- Background: `#FFFFFF`; border: `#D1D5DB`; text: `#111827`.

### Donut chart - Forecast Method Distribution

- Object: Pie chart, donut mode.
- Dimension: `ForecastMethod`.
- Measure:

```qlik
Count(DISTINCT SupplierID)
```

Options:

- Labels: percentage and count.
- Legend: right.
- Colors by dimension:
  - Supplier Target: `#43A047`.
  - Expert Judgement: `#FB8C00`.
- Sort: Supplier Target first, Expert Judgement second.

### Horizontal bar chart - Forecast Emissions by Industry

- Object: Bar chart, horizontal.
- Title expression: `='Forecast Emissions by Industry (' & $(vForecastYear) & ')'`.
- Dimension: `Industry`.
- Measure:

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

Options:

- Sort: measure descending.
- Color: single color `#43A047`.
- Data labels: on.
- Number format: `#,##0`.
- Axis title: `Emissions (tCO2e)`.

### Year-by-year forecast table

- Object: Straight table.
- Dimension: `Year`.
- Sort: numeric ascending.

Measures:

```qlik
// Total Emissions
If(
  Only(YearStatus) = 'Actual',
  Sum(CurrentEmissions2025_tCO2e * ActualFactor),
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
)
```

```qlik
// Reduction vs 2025
If(
  Only(YearStatus) = 'Actual',
  Null(),
  Sum({<Year={2025}>} TOTAL CurrentEmissions2025_tCO2e) - Sum({<YearStatus={'Forecast'}>}
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
)
```

```qlik
// Reduction vs 2025 (%)
If(
  Only(YearStatus) = 'Actual',
  Null(),
  (Sum({<Year={2025}>} TOTAL CurrentEmissions2025_tCO2e) - Sum({<YearStatus={'Forecast'}>}
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
))
  / Sum({<Year={2025}>} TOTAL CurrentEmissions2025_tCO2e)
)
```

```qlik
// Forecast Status
Only(YearStatus)
```

Options:

- Header background: `#F8FAFC`.
- Actual row text: `#173B7A`.
- Forecast row text: `#2E7D32`.
- Null display for actual-year reductions: `-`.
- Number formatting: emissions and reduction `#,##0`; reduction percent `0.0%`.

## 7. Validation checklist

- `Count(DISTINCT SupplierID)` returns `50`.
- `Sum({<Year={2025}>} CurrentEmissions2025_tCO2e)` returns `619,700`.
- Forecast Method donut returns 60% Supplier Target and 40% Expert Judgement.
- Changing any slider immediately changes forecast KPI, line, industry bar, and forecast table values.
- Selecting Supplier Name, Industry, or Forecast Method filters every object consistently.
