# Sheet 2 Front Dashboard Design and Development Steps

## Document purpose

This document provides an end-to-end front-end build guide for the Qlik Sense
dashboard:

```text
Supply Chain Emissions Forecasting - What-If Analysis
Multi-Supplier Scenario and Supplier-Specific Reduction Controls
```

It explains how to design and develop each dashboard object shown in the Sheet 2
mockup using native Qlik Sense objects and native Qlik expressions.

Use this document together with:

- `qlik/sheet2_supplier_specific_what_if_load_script.qvs`
- `docs/qlik_sheet2_expression_catalog.md`
- `docs/qlik_sheet2_design_development_guide.md`

No third-party extensions are required.

## 1. Front-end prerequisites

Before starting the front-end build:

1. Create or open the Qlik Sense app:

   ```text
   Supply Chain Emissions Forecasting - Supplier Scenario What-If
   ```

2. Paste and reload the data model script:

   ```text
   qlik/sheet2_supplier_specific_what_if_load_script.qvs
   ```

3. Create all helper variables from:

   ```text
   docs/qlik_sheet2_expression_catalog.md
   ```

4. Create master dimensions and master measures from the same expression
   catalog.
5. Confirm the app contains these tables:
   - `Supplier`
   - `Supplier_Group_Bridge`
   - `Supplier_Adjustment_Slot`
   - `Scenario_Year`
   - `Scenario_Profile`
   - `Forecast_Method_Color`
   - `What_If_Assumptions`

## 2. Sheet canvas setup

### Object type

Native Qlik Sense sheet.

### Sheet name

```text
Sheet 2 - Multi-Supplier What-If Scenario
```

### Layout intent

Use a dashboard layout with five zones:

1. Header bar
2. Left control panel
3. KPI row
4. Main analytical canvas
5. Bottom forecast table

### Recommended grid

Use the Qlik Sense responsive grid and allocate space approximately as follows:

| Area | Width | Height |
| --- | ---: | ---: |
| Header | 100% | 7% |
| Left control panel | 22% | 86% |
| KPI row | 78% | 13% |
| Main line chart | 56% | 55% |
| Right insight panel | 22% | 55% |
| Bottom table | 78% | 24% |

### Global style

Use a clean ESG dashboard style:

- Page background: `#F7F9FC`
- Header background: `#061F3D`
- Card background: `#FFFFFF`
- Border color: `#E5E7EB`
- Primary navy: `#0B2E5F`
- ESG green: `#16A34A`
- Forecast blue: `#2563EB`
- Warning orange: `#FB8C00`
- High-growth red: `#DC2626`
- Neutral gray: `#6B7280`

## 3. Object 1 - Header bar

### Business purpose

Provides the dashboard title, scenario context, navigation identity, and last
updated date.

### Native object

Text and image object.

### Placement

Top full-width header.

### Title text

```text
Supply Chain Emissions Forecasting - What-If Analysis
```

### Subtitle text

```text
Multi-Supplier Scenario and Supplier-Specific Reduction Controls
```

### Last updated expression

```qlik
='Last updated: ' & Date(Today(), 'MMM DD, YYYY')
```

### Design steps

1. Open the sheet in edit mode.
2. Drag a native Text and image object to the top row.
3. Add the title as the primary text.
4. Add the subtitle below the title.
5. Add the last updated expression on the right side.
6. Apply dark navy background.
7. Set title color to white and subtitle color to light gray.

### Formatting

| Element | Setting |
| --- | --- |
| Background | `#061F3D` |
| Title font | 20 to 24 px, bold, white |
| Subtitle font | 10 to 12 px, italic, white |
| Last updated font | 10 px, white |

## 4. Object 2 - Overall Additional Reduction control

### Business purpose

Lets the user apply an extra emissions reduction percentage across the selected
supplier population.

### Native object

Qlik-managed Variable input slider. If the Dashboard bundle is disabled, use
Variable overview or bookmarks.

### Variable

```text
vOverallAdditionalReductionPct
```

### Placement

Top of the left control panel.

### Slider settings

| Property | Value |
| --- | --- |
| Input type | Slider |
| Minimum | `0` |
| Maximum | `0.30` or `0.50` |
| Step | `0.01` |
| Default | `0.12` |
| Display | Percentage |

### Display expression

```qlik
=Num($(vOverallAdditionalReductionPct), '0%')
```

### Design steps

1. Add a small Text and image object with the title:

   ```text
   Overall Additional Reduction (%)
   ```

2. Add the Variable input object below the title.
3. Bind it to `vOverallAdditionalReductionPct`.
4. Set slider min, max, step, and default value.
5. Add a center value label using the display expression.
6. Add helper text:

   ```text
   Evenly distributed across all suppliers
   ```

### Formatting

- Slider active color: green
- Value text: large green, 24 to 28 px
- Helper text: 9 px gray

## 5. Object 3 - Forecast Method filter

### Business purpose

Allows users to compare suppliers with disclosed supplier targets against
suppliers using expert judgement assumptions.

### Native object

Filter pane.

### Field

```qlik
[Forecast Method]
```

### Placement

Left control panel, below the overall reduction slider.

### Design steps

1. Drag a Filter pane object below the overall reduction control.
2. Add field `[Forecast Method]`.
3. Set title to:

   ```text
   Forecast Method
   ```

4. Enable single or multi-select based on business preference.
5. Optionally set the default selection to both methods.

### Formatting

- Compact dropdown style if available.
- White background.
- Thin border.

## 6. Object 4 - Supplier search filter

### Business purpose

Allows users to search and select individual suppliers.

### Native object

Filter pane.

### Field

```qlik
[Supplier Name]
```

### Placement

Left control panel under:

```text
What-If Scenario Controls
```

### Design steps

1. Add a Text and image title:

   ```text
   What-If Scenario Controls
   ```

2. Add a Filter pane for `[Supplier Name]`.
3. Enable search.
4. Use compact view so the object resembles a search box.

### Formatting

- Placeholder behavior: Qlik search box.
- Border color: `#CBD5E1`.
- Background: white.

## 7. Object 5 - Supplier Group filter buttons

### Business purpose

Lets users switch between intervention groups such as Top 25 Suppliers, Region A
Suppliers, Region B Suppliers, and Expert Judgement Suppliers.

### Native object

Filter pane using the linked supplier group bridge.

### Field

```qlik
[Supplier Group]
```

### Recommended values

- Top 25 Suppliers
- Region A Suppliers
- Region B Suppliers
- Expert Judgement Suppliers
- Supplier Target Suppliers
- All Suppliers

### Placement

Left control panel below the supplier search filter.

### Design steps

1. Add a Filter pane.
2. Add field `[Supplier Group]`.
3. Set presentation to list view.
4. Resize rows so they look like selectable buttons.
5. Use the default bookmark to select:

   ```text
   Top 25 Suppliers
   ```

### Formatting

- Selected item background: light blue `#E8F1FF`
- Border: `#CBD5E1`
- Text: `#111827`

## 8. Object 6 - Supplier-Specific Reduction Adjustments panel

### Business purpose

Allows selected high-emission suppliers to receive individual reduction
adjustments on top of global and scenario-level assumptions.

### Native objects

- Text and image objects for labels
- Qlik-managed Variable input sliders
- Text and image objects for percentage values
- Optional native straight table to show slot mapping

### Variables

```text
vSupplierReduction01 through vSupplierReduction20
```

### Placement

Lower left control panel.

### Panel title

```text
Supplier-Specific Reduction Adjustments (%)
```

### Two-column layout

Left column:

```text
Supplier A to Supplier J
```

Right column:

```text
Supplier K to Supplier T
```

### Slider settings

| Property | Value |
| --- | --- |
| Input type | Slider |
| Minimum | `0` |
| Maximum | `0.50` |
| Step | `0.01` |
| Display | Percentage |

### Supplier label source

Use the top supplier slot table:

```qlik
[Supplier Adjustment Label]
```

For static layout, label each slider manually. For governed mapping, add a small
straight table with `[Supplier Adjustment Label]` and
`[Supplier Reduction Variable Name]`.

### Value expressions

Supplier A / slot 01:

```qlik
=Num($(vSupplierReduction01), '0%')
```

Supplier B / slot 02:

```qlik
=Num($(vSupplierReduction02), '0%')
```

Continue through:

```qlik
=Num($(vSupplierReduction20), '0%')
```

### Design steps

1. Add a Text and image object for the section title.
2. Add two small column headers:

   ```text
   Supplier
   Reduction %
   ```

3. Add ten supplier rows in the left column.
4. Add ten supplier rows in the right column.
5. For each row:
   - add a label;
   - add a Variable input slider;
   - bind the slider to the matching supplier variable;
   - add a percentage value object.
6. Keep row heights consistent.
7. Add enough vertical space for the reset button below the panel.

### Example row

```text
Supplier A    [green slider bound to vSupplierReduction01]    15%
```

### Formatting

| Element | Setting |
| --- | --- |
| Panel background | `#FFFFFF` |
| Border | `#E5E7EB` |
| Section title | 12 px, bold |
| Supplier label | 9 to 10 px |
| Slider color | Green |
| Value box | Light gray background, centered text |

## 9. Object 7 - Reset to Default button

### Business purpose

Restores all scenario variables and supplier-specific controls to the governed
default values.

### Native object

Button.

### Placement

Bottom center of the left control panel.

### Button label

```text
Reset to Default
```

### Button actions

Add one Set variable action per variable:

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

### Formatting

- White background.
- Gray border.
- Optional refresh icon if available.
- Text color: `#1F2937`.

## 10. Object 8 - KPI cards

### Business purpose

Summarizes the selected scenario at executive level.

### Native object

KPI object. Use one KPI object per card.

### Placement

Top row of the main canvas, to the right of the left control panel.

### KPI 1 - Overall Additional Reduction

Measure:

```qlik
$(vOverallAdditionalReductionPct)
```

Number format:

```text
0.0%
```

Title:

```text
Overall Additional Reduction
```

### KPI 2 - Total Current Emissions

Measure:

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

Format:

```text
#,##0 tCO2e
```

### KPI 3 - Total Forecast Emissions

Measure:

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

Format:

```text
#,##0 tCO2e
```

### KPI 4 - Total Reduction

Measure:

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
-
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

Format:

```text
#,##0 tCO2e
```

### KPI 5 - Reduction Achieved

Measure:

```qlik
(
    Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
    -
    Sum(
        Aggr(
            $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
            [Supplier ID]
        )
    )
)
/
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

Format:

```text
0.0%
```

### KPI 6 - Suppliers with Target

Measure:

```qlik
Count({<[Forecast Method] = {'Supplier Target'}>} DISTINCT [Supplier ID])
```

### KPI 7 - Suppliers Expert Judgement

Measure:

```qlik
Count({<[Forecast Method] = {'Expert Judgement'}>} DISTINCT [Supplier ID])
```

### KPI formatting

| KPI | Accent color |
| --- | --- |
| Overall Additional Reduction | Green |
| Total Current Emissions | Navy |
| Total Forecast Emissions | Blue |
| Total Reduction | Green |
| Reduction Achieved | Green |
| Suppliers with Target | Blue |
| Suppliers Expert Judgement | Orange |

## 11. Object 9 - Main multi-supplier what-if line chart

### Business purpose

Shows historical emissions and multiple forecast scenarios through the net-zero
target year.

### Native object

Line chart.

### Placement

Center of the dashboard, below the KPI row.

### Title

```text
Emissions Forecast by Year - Multi-Supplier What-If Scenario
```

### Dimensions

Dimension 1:

```qlik
[Scenario Year]
```

Dimension 2:

```qlik
[Scenario Profile]
```

### Measure

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year],
        [Scenario Profile]
    )
)
```

### Color by expression

```qlik
Only([Scenario Color])
```

### Sort

1. Sort `[Scenario Year]` ascending.
2. Sort `[Scenario Profile]` by:

   ```qlik
   Only([Scenario Sort])
   ```

### Axis settings

| Axis | Setting |
| --- | --- |
| X-axis | Year |
| Y-axis | tCO2e |
| Y-axis number format | `#,##0` |

### Presentation

- Historical/current plan line: navy.
- Primary what-if line: green.
- Accelerated scenario line: blue.
- High-growth pressure line: red.
- Net-zero pathway line: gray dashed if line style is available.
- Show data labels only for important forecast years if labels become crowded.

### Development steps

1. Drag a native Line chart object to the main canvas.
2. Add `[Scenario Year]` as the first dimension.
3. Add `[Scenario Profile]` as the second dimension.
4. Add the scenario forecast emissions measure.
5. Enable color by expression and use `Only([Scenario Color])`.
6. Sort years ascending.
7. Sort scenario profiles by `Only([Scenario Sort])`.
8. Format Y-axis as emissions.
9. Enable legend at bottom.
10. Test selections by changing supplier group and scenario variables.

## 12. Object 10 - Scenario assumptions card

### Business purpose

Shows the active what-if assumptions used by the line chart and KPIs.

### Native object

Text and image object.

### Placement

Inside or next to the main chart area.

### Expression

```qlik
='Scenario Assumptions' & Chr(10)
& 'Forecast Year: ' & $(vForecastYear) & Chr(10)
& 'Additional Reduction: ' & Num($(vOverallAdditionalReductionPct), '0.0%') & Chr(10)
& 'Expert Judgement Adj.: ' & Num($(vExpertJudgementAdjustmentPct), '0.0%') & Chr(10)
& 'Growth Adjustment: ' & Num($(vGrowthAdjustmentPct), '0.0%') & Chr(10)
& 'Net Zero Target: ' & $(vNetZeroYear) & Chr(10)
& 'What-if Scenario: A - Multi-Supplier'
```

### Formatting

- White or very light gray background.
- Thin border.
- Small font.
- Bold first line.

## 13. Object 11 - Forecast Method Distribution donut chart

### Business purpose

Shows the supplier count split between supplier target and expert judgement
forecast methods.

### Native object

Pie chart or donut chart.

### Placement

Top right insight panel.

### Title

```text
Forecast Method Distribution
```

### Dimension

```qlik
[Forecast Method]
```

### Measure

```qlik
Count(DISTINCT [Supplier ID])
```

### Color setup

Use custom colors:

| Forecast Method | Color |
| --- | --- |
| Supplier Target | `#16A34A` |
| Expert Judgement | `#FB8C00` |

### Development steps

1. Drag a native Pie chart object to the right panel.
2. Add `[Forecast Method]` as dimension.
3. Add supplier count as measure.
4. Change presentation to donut if available.
5. Enable percentage labels.
6. Set legend to the right.
7. Apply green and orange colors.

## 14. Object 12 - Forecast Emissions by Industry bar chart

### Business purpose

Ranks industries by forecast emissions for the selected forecast year and
scenario assumptions.

### Native object

Bar chart.

### Placement

Right insight panel, below the donut chart.

### Title

```qlik
='Forecast Emissions by Industry (' & $(vForecastYear) & ')'
```

### Dimension

```qlik
[Industry]
```

### Measure

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

### Presentation

- Horizontal orientation.
- Sort descending by measure.
- Bar color: green.
- Data labels enabled.
- Axis label: `tCO2e`.

### Development steps

1. Drag a native Bar chart object to the lower right panel.
2. Add `[Industry]` as dimension.
3. Add the forecast emissions by industry measure.
4. Set orientation to horizontal.
5. Sort descending by measure.
6. Format measure as `#,##0`.
7. Enable data labels.

## 15. Object 13 - Year-by-Year Forecast Data table

### Business purpose

Provides detailed annual emissions, reduction, reduction percentage, and actual
or forecast flag for audit and export use cases.

### Native object

Straight table.

### Placement

Bottom full-width area to the right of the left control panel.

### Title

```text
Year-by-Year Forecast Data - Multi-Supplier What-If Scenario
```

### Dimension

```qlik
[Scenario Year]
```

### Measure 1 - Total Emissions

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year],
        [Scenario Profile]
    )
)
```

### Measure 2 - Reduction vs Current

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
-
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year],
        [Scenario Profile]
    )
)
```

### Measure 3 - Reduction vs Current %

```qlik
(
    Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
    -
    Sum(
        Aggr(
            $(vForecastEmissionsSheet2AtYear(Only([Scenario Year]))),
            [Supplier ID],
            [Scenario Year],
            [Scenario Profile]
        )
    )
)
/
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

### Measure 4 - Forecast Flag

```qlik
If(
    Only([Scenario Year]) <= Max(TOTAL [Current Year]),
    'Actual',
    'Forecast'
)
```

### Sort

Sort `[Scenario Year]` ascending.

### Formatting

| Column | Format |
| --- | --- |
| Total Emissions | `#,##0` |
| Reduction vs Current | `#,##0` |
| Reduction vs Current % | `0.0%` |
| Forecast Flag | Text |

### Development steps

1. Drag a native Straight table object to the bottom area.
2. Add `[Scenario Year]` as the dimension.
3. Add the four measures above.
4. Sort by year ascending.
5. Freeze or keep the year column visible if supported.
6. Apply conditional color:
   - `Actual`: navy
   - `Forecast`: blue or green
7. Enable download/export if permitted by governance.

## 16. Object 14 - Footnote and data governance note

### Business purpose

Documents assumptions and prevents users from interpreting what-if outputs as
externally assured emissions results.

### Native object

Text and image object.

### Placement

Below the bottom table.

### Text

```text
Note: Emissions are in tCO2e. Forecast values use supplier targets where
available and expert judgement where supplier targets are unavailable.
Supplier-specific adjustments and scenario variables are what-if assumptions and
do not overwrite source data.
```

### Formatting

- Font size: 9 px.
- Color: `#4B5563`.

## 17. End-to-end build sequence

Follow this order to develop the dashboard efficiently:

1. Reload the data model.
2. Create all variables.
3. Create master dimensions.
4. Create master measures.
5. Create the sheet canvas.
6. Build the header.
7. Build the left control panel.
8. Build the supplier-specific slider panel.
9. Build the reset button.
10. Build the KPI row.
11. Build the main line chart.
12. Build the scenario assumptions card.
13. Build the forecast method donut chart.
14. Build the industry bar chart.
15. Build the year-by-year forecast table.
16. Add the footnote.
17. Create the default bookmark.
18. Test all controls and selections.

## 18. Default bookmark setup

Create a bookmark named:

```text
Default - Multi-Supplier Scenario
```

Recommended default selections:

```text
Supplier Group = Top 25 Suppliers
Scenario Profile = What-if Scenario A - Multi-Supplier
Forecast Method = all
```

Default variable values:

```text
vForecastYear = 2030
vOverallAdditionalReductionPct = 0.12
vExpertJudgementAdjustmentPct = 0.03
vGrowthAdjustmentPct = 0.02
vNetZeroYear = 2050
```

## 19. Front-end testing checklist

Use this checklist before publishing the app:

1. Move the Overall Additional Reduction slider and confirm:
   - Total Forecast Emissions changes.
   - Total Reduction changes.
   - Reduction Achieved changes.
   - Main line chart changes.
2. Select `Top 25 Suppliers` and confirm all charts filter to that group.
3. Select `Expert Judgement Suppliers` and confirm supplier counts and method
   distribution update.
4. Move a supplier-specific slider and confirm the forecast changes.
5. Click Reset to Default and confirm all variables return to defaults.
6. Select each scenario profile and confirm the line chart changes.
7. Confirm industry bar chart sorts descending.
8. Confirm year-by-year table sorts ascending.
9. Confirm all number formats display emissions as tCO2e or percentages.
10. Confirm no third-party extension objects are used.

## 20. Publish checklist

Before publishing:

1. Apply the approved Qlik theme.
2. Verify object titles and subtitles.
3. Verify all expressions use master measures where possible.
4. Verify export permissions for the table.
5. Confirm reload ownership and data connection ownership.
6. Add the default bookmark.
7. Publish to the governed stream or managed space.
