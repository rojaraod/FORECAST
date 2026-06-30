# Sheet 2 Qlik Sense Expression Catalog

Use this catalog with:

`qlik/sheet2_supplier_specific_what_if_load_script.qvs`

The second Qlik application uses the same source CSV as Sheet 1, but adds a
multi-supplier scenario profile table and a top-supplier adjustment-slot table.
All expressions are native Qlik Sense expressions.

## 1. Scenario and supplier adjustment variables

The load script creates these variables.

### Global variables

| Variable | Default | Purpose |
| --- | ---: | --- |
| `vForecastYear` | `2030` | KPI forecast year |
| `vOverallAdditionalReductionPct` | `0.12` | Additional reduction applied across the selected supplier population |
| `vExpertJudgementAdjustmentPct` | `0.03` | Extra adjustment for suppliers using expert judgement |
| `vGrowthAdjustmentPct` | `0.02` | Annual growth pressure after current year |
| `vNetZeroYear` | `2050` | Target year for net-zero pathway |

### Supplier-specific variables

These variables map to the top 20 suppliers by current emissions at reload time.

| Variable range | Purpose |
| --- | --- |
| `vSupplierReduction01` to `vSupplierReduction20` | Additional supplier-specific reduction applied to adjustment slots 1 to 20 |

The table `Supplier_Adjustment_Slot` contains:

- `[Adjustment Slot]`
- `[Adjustment Supplier Name]`
- `[Supplier Reduction Variable Name]`
- `[Supplier Adjustment Label]`

Use that table to label the controls so users can see which supplier each
variable controls.

## 2. Helper expression variables

Create these helper variables in **Assets > Variables**.

### `vSupplierSlotReductionPct`

Maps the current supplier's adjustment slot to the correct Qlik variable. If a
supplier is outside the top 20 adjustment slots, the expression returns zero.

```qlik
Alt(
    Pick(
        Match(
            Only([Adjustment Slot]),
            1, 2, 3, 4, 5,
            6, 7, 8, 9, 10,
            11, 12, 13, 14, 15,
            16, 17, 18, 19, 20
        ),
        $(vSupplierReduction01),
        $(vSupplierReduction02),
        $(vSupplierReduction03),
        $(vSupplierReduction04),
        $(vSupplierReduction05),
        $(vSupplierReduction06),
        $(vSupplierReduction07),
        $(vSupplierReduction08),
        $(vSupplierReduction09),
        $(vSupplierReduction10),
        $(vSupplierReduction11),
        $(vSupplierReduction12),
        $(vSupplierReduction13),
        $(vSupplierReduction14),
        $(vSupplierReduction15),
        $(vSupplierReduction16),
        $(vSupplierReduction17),
        $(vSupplierReduction18),
        $(vSupplierReduction19),
        $(vSupplierReduction20)
    ),
    0
)
```

### `vScenarioProfileAdditionalReductionPct`

```qlik
Alt(Only([Scenario Additional Reduction Pct]), 0)
```

### `vScenarioProfileExpertAdjustmentPct`

```qlik
Alt(Only([Scenario Expert Adjustment Pct]), 0)
```

### `vScenarioProfileGrowthAdjustmentPct`

```qlik
Alt(Only([Scenario Growth Adjustment Pct]), 0)
```

### `vEffectiveReductionPctSheet2`

Combines the supplier's disclosed or expert reduction, global what-if controls,
scenario-profile assumptions, and supplier-specific adjustment slot.

```qlik
RangeMin(
    1,
    RangeMax(
        0,
        Only([Final Reduction Pct])
        + $(vOverallAdditionalReductionPct)
        + $(vScenarioProfileAdditionalReductionPct)
        + If(
            Only([Forecast Method]) = 'Expert Judgement',
            $(vExpertJudgementAdjustmentPct) + $(vScenarioProfileExpertAdjustmentPct),
            0
        )
        + $(vSupplierSlotReductionPct)
    )
)
```

### `vScenarioTargetEmissionsSheet2`

```qlik
RangeMin(
    Only([Current Emissions]),
    Only([Baseline Emissions]) * (1 - $(vEffectiveReductionPctSheet2))
)
```

### `vHistoricalEmissionsSheet2AtYear($1)`

Parameterized expression. Pass a year expression as `$1`.

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

### `vForecastEmissionsSheet2AtYear($1)`

```qlik
If(
    $1 <= Only([Current Year]),
    $(vHistoricalEmissionsSheet2AtYear($1)),
    RangeMax(
        0,
        If(
            $1 <= Only([Target Year]),
            Only([Current Emissions])
            - (
                (Only([Current Emissions]) - $(vScenarioTargetEmissionsSheet2))
                * (
                    ($1 - Only([Current Year]))
                    / RangeMax(1, Only([Target Year]) - Only([Current Year]))
                )
            ),
            $(vScenarioTargetEmissionsSheet2)
            * (
                1
                - (
                    ($1 - Only([Target Year]))
                    / RangeMax(1, $(vNetZeroYear) - Only([Target Year]))
                )
            )
        )
        * Pow(
            1 + $(vGrowthAdjustmentPct) + $(vScenarioProfileGrowthAdjustmentPct),
            RangeMax(0, $1 - Only([Current Year]))
        )
    )
)
```

### `vNetZeroPathwaySheet2AtYear($1)`

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

### Overall Additional Reduction

Format: `0.0%`

```qlik
$(vOverallAdditionalReductionPct)
```

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
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
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
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
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
            $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
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

## 4. Main multi-supplier scenario line chart

Use a native **Line chart** with two dimensions and one measure.

Dimension 1:

```qlik
[Scenario Year]
```

Dimension 2:

```qlik
[Scenario Profile]
```

Measure: **Scenario Forecast Emissions**

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

Color by expression:

```qlik
Only([Scenario Color])
```

Sort `[Scenario Profile]` by:

```qlik
Only([Scenario Sort])
```

## 5. Supporting chart measures

### Forecast Method Distribution

Dimension:

```qlik
[Forecast Method]
```

Measure:

```qlik
Count(DISTINCT [Supplier ID])
```

### Forecast Emissions by Industry

Dimension:

```qlik
[Industry]
```

Measure:

```qlik
Sum(
    Aggr(
        $(vForecastEmissionsSheet2AtYear($(vForecastYear))),
        [Supplier ID]
    )
)
```

### Supplier Adjustment Table - Current Emissions

```qlik
Only([Adjustment Current Emissions])
```

### Supplier Adjustment Table - Variable Name

```qlik
Only([Supplier Reduction Variable Name])
```

### Supplier Adjustment Table - Active Reduction

```qlik
$(vSupplierSlotReductionPct)
```

## 6. Year-by-year forecast table

Dimension:

```qlik
[Scenario Year]
```

Recommended default selection:

```text
Scenario Profile = What-if Scenario A - Multi-Supplier
```

### Total Emissions

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

### Reduction vs Current

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

### Reduction vs Current %

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

### Forecast Flag

```qlik
If(
    Only([Scenario Year]) <= Max(TOTAL [Current Year]),
    'Actual',
    'Forecast'
)
```
