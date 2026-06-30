# Qlik Sense Expression Catalog

Use these expressions with the load script in
`qlik/supply_chain_emissions_what_if_load_script.qvs`.

All expressions use native Qlik Sense syntax only. No third-party extensions,
external JavaScript, or server-side plugins are required.

## 1. Scenario control variables

The load script creates these default variables. Expose them on the sheet as
variable controls.

| Variable | Default | Recommended UI control | Min | Max | Step |
| --- | ---: | --- | ---: | ---: | ---: |
| `vForecastYear` | `2030` | Slider | `$(vDataCurrentYear)` | `$(vNetZeroYear)` | `1` |
| `vAdditionalReductionPct` | `0.05` | Slider | `0` | `0.50` | `0.01` |
| `vExpertJudgementAdjustmentPct` | `0.03` | Slider | `0` | `0.30` | `0.01` |
| `vGrowthAdjustmentPct` | `0.02` | Slider | `-0.10` | `0.20` | `0.01` |
| `vNetZeroYear` | `2050` | Slider | `2040` | `2050` | `1` |

> If your Qlik tenant disables Qlik's Dashboard bundle, keep the variables in
> Variable overview and adjust values there. The chart expressions still work
> without any extension objects.

## 2. Helper variables for reusable expressions

Create these in **Assets > Variables** after reloading the data model. These are
not data-load variables; they are expression snippets that keep master measures
readable and make the what-if controls recalculate dynamically.

### `vEffectiveReductionPct`

Final supplier reduction percentage after the global additional reduction and
the expert-judgement adjustment are applied. The result is clamped between 0%
and 100%.

```qlik
RangeMin(
    1,
    RangeMax(
        0,
        Only([Final Reduction Pct])
        + $(vAdditionalReductionPct)
        + If(
            Only([Forecast Method]) = 'Expert Judgement',
            $(vExpertJudgementAdjustmentPct),
            0
        )
    )
)
```

### `vScenarioTargetEmissions`

Target emissions at the supplier target year. The expression prevents forecast
backsliding when a supplier has already reduced more than its stated target.

```qlik
RangeMin(
    Only([Current Emissions]),
    Only([Baseline Emissions]) * (1 - $(vEffectiveReductionPct))
)
```

### `vHistoricalEmissionsAtYear($1)`

Parameterized expression. Pass a year expression as `$1`, for example:
`$(vHistoricalEmissionsAtYear(Only([Scenario Year])))`.

```qlik
If(
    $1 < Only([Baseline Year]),
    Null(),
    RangeMax(
        0,
        Only([Baseline Emissions])
        - (
            (Only([Baseline Emissions]) - Only([Current Emissions]))
            * (
                ($1 - Only([Baseline Year]))
                / RangeMax(1, Only([Current Year]) - Only([Baseline Year]))
            )
        )
    )
)
```

### `vForecastEmissionsAtYear($1)`

Parameterized what-if forecast expression. It uses:

- historical interpolation from baseline year to current year;
- current emissions to supplier target emissions by target year;
- target emissions to net zero by the net-zero year;
- growth adjustment compounded after current year;
- clamping so emissions do not fall below zero.

```qlik
If(
    $1 <= Only([Current Year]),
    $(vHistoricalEmissionsAtYear($1)),
    RangeMax(
        0,
        If(
            $1 <= Only([Target Year]),
            Only([Current Emissions])
            - (
                (Only([Current Emissions]) - $(vScenarioTargetEmissions))
                * (
                    ($1 - Only([Current Year]))
                    / RangeMax(1, Only([Target Year]) - Only([Current Year]))
                )
            ),
            $(vScenarioTargetEmissions)
            * (
                1
                - (
                    ($1 - Only([Target Year]))
                    / RangeMax(1, $(vNetZeroYear) - Only([Target Year]))
                )
            )
        )
        * Pow(
            1 + $(vGrowthAdjustmentPct),
            RangeMax(0, $1 - Only([Current Year]))
        )
    )
)
```

### `vNetZeroPathwayAtYear($1)`

Native straight-line pathway from current emissions to zero by the selected
net-zero year.

```qlik
If(
    $1 <= Only([Current Year]),
    Null(),
    RangeMax(
        0,
        Only([Current Emissions])
        * (
            1
            - (
                ($1 - Only([Current Year]))
                / RangeMax(1, $(vNetZeroYear) - Only([Current Year]))
            )
        )
    )
)
```

## 3. KPI master measures

Create these as **Master items > Measures**.

### Total Current Emissions

Format: `#,##0 tCO2e`

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

### Total Forecast Emissions

Format: `#,##0 tCO2e`

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsAtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

### Total Reduction

Format: `#,##0 tCO2e`

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
-
Sum(
    Aggr(
        $(vForecastEmissionsAtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

### Reduction Achieved

Format: `0.0%`

```qlik
(
    Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
    -
    Sum(
        Aggr(
            $(vForecastEmissionsAtYear($(vForecastYear))),
            [Supplier ID]
        )
    )
)
/
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

### Suppliers with Target

Format: `#,##0`

```qlik
Count({<[Forecast Method] = {'Supplier Target'}>} DISTINCT [Supplier ID])
```

### Suppliers Using Expert Judgement

Format: `#,##0`

```qlik
Count({<[Forecast Method] = {'Expert Judgement'}>} DISTINCT [Supplier ID])
```

## 4. Main line chart measures

Dimension: `[Scenario Year]`

### Historical Emissions

Style: navy, thick line, markers on.

```qlik
Sum(
    Aggr(
        If(
            Only([Scenario Year]) <= Only([Current Year]),
            $(vHistoricalEmissionsAtYear(Only([Scenario Year])))
        ),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Forecast Emissions (What-if)

Style: green, dotted or dashed line if available in your Qlik version, markers
on. If line-style controls are not available, use the green color and measure
label to distinguish the forecast while remaining native.

```qlik
Sum(
    Aggr(
        If(
            Only([Scenario Year]) >= Only([Current Year]),
            $(vForecastEmissionsAtYear(Only([Scenario Year])))
        ),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Baseline Emissions

Style: muted red, dashed line.

```qlik
Sum(
    Aggr(
        If(
            Only([Scenario Year]) >= Only([Current Year]),
            Only([Baseline Emissions])
        ),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Net Zero Pathway

Style: gray, dashed line.

```qlik
Sum(
    Aggr(
        $(vNetZeroPathwayAtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year]
    )
)
```

## 5. Right-side charts

### Forecast Method Distribution

Object: Pie chart or donut chart

Dimension:

```qlik
[Forecast Method]
```

Measure:

```qlik
Count(DISTINCT [Supplier ID])
```

Color by expression:

```qlik
Only([Forecast Method Color])
```

### Forecast Emissions by Industry

Object: Bar chart

Dimension:

```qlik
[Industry]
```

Measure:

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsAtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

Sort: descending by measure.

Format: `#,##0 tCO2e`

## 6. Year-by-year forecast table

Object: Straight table

Dimension:

```qlik
[Scenario Year]
```

Measures:

### Historical Emissions

```qlik
Sum(
    Aggr(
        If(
            Only([Scenario Year]) <= Only([Current Year]),
            $(vHistoricalEmissionsAtYear(Only([Scenario Year])))
        ),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Forecast Emissions

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsAtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Reduction vs Current

```qlik
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
-
Sum(
    Aggr(
        $(vForecastEmissionsAtYear(Only([Scenario Year]))),
        [Supplier ID],
        [Scenario Year]
    )
)
```

### Reduction vs Current %

```qlik
(
    Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
    -
    Sum(
        Aggr(
            $(vForecastEmissionsAtYear(Only([Scenario Year]))),
            [Supplier ID],
            [Scenario Year]
        )
    )
)
/
Sum(Aggr(Only([Current Emissions]), [Supplier ID]))
```

### Forecast Phase

```qlik
If(
    Only([Scenario Year]) <= Max(TOTAL [Current Year]),
    'Actual',
    'Forecast'
)
```
