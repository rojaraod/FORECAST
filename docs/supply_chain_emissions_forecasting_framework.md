# Supply Chain Emissions Forecasting Framework

## 1. Business Objective

The objective is to forecast supplier-level greenhouse gas emissions from historical years to future target years using a transparent, auditable, and scalable mathematical model. The framework supports:

- Supplier-specific decarbonization targets when supplier target data exists.
- Industry-level target pathways when supplier-specific targets are unavailable.
- Historical trend forecasting when neither supplier nor industry targets are sufficient.
- Python execution, Excel implementation, and Qlik Sense dashboarding.

The model is designed for ESG, Procurement, Sustainability, Data Science, Finance, and Audit teams. Because historical and current emissions are available for all suppliers, the model uses supplied emissions directly and focuses on validation checks, confidence scores, and forecast-method transparency.

---

## 2. Data Architecture

### Core datasets

1. **Supplier Master**: one row per supplier with supplier identity and segmentation.
2. **Historical Emissions**: supplier-year emissions, activity, scope, and factor data.
3. **Supplier Targets**: supplier-specific baseline, target year, and target reduction details.
4. **Industry Haircut Pathway**: industry reduction assumptions and benchmark factors.
5. **Forecast Output**: supplier-year forecast results by forecast year.
6. **Data Dictionary**: source and output metadata for governance.
7. **Formula Dictionary**: Excel formula library for implementation.

### Recommended model flow

```text
Supplier Master
        |
Historical Emissions + Supplier Targets + Industry Haircut Pathway
        |
Direct Emissions Validation
        |
Forecast Method Selection
        |
Supplier Target / Industry Haircut / Historical Trend Forecast
        |
Glide Path, Gap-to-Target, Risk, Confidence
        |
CSV, Excel, Qlik Sense Dashboard
```

---

## 3. Source Data Design

| Attribute name | Description | Data type | Source system | Mandatory / optional | Business purpose | Model impact | Example value |
|---|---|---:|---|---|---|---|---|
| Supplier_ID | Unique supplier identifier | String | ERP / Supplier master | Mandatory | Stable join key | Groups supplier history and forecasts | SUP-0001 |
| Supplier_Name | Supplier legal or reporting name | String | ERP / Supplier master | Mandatory | Reporting label | Used in output and dashboards | Electronics Supplier 001 |
| Supplier_Industry | Industry classification | String | Supplier master / taxonomy | Mandatory | Benchmarking and industry targets | Drives industry haircut and factors | Electronics |
| Supplier_Country | Supplier primary country | String | Supplier master | Optional | Geographic segmentation | Dashboard filter and future regional factors | DE |
| Supplier_Status | Supplier relationship status | String | Procurement | Optional | Supplier governance | Risk segmentation | Strategic |
| Preferred_Supplier_Flag | Preferred supplier indicator | Boolean | Procurement | Optional | Procurement prioritization | Risk prioritization and filters | TRUE |
| Supplier_Year | Historical reporting year | Integer | ESG platform / data lake | Mandatory | Time-series anchor | Historical trend and latest-year selection | 2024 |
| Gross_Spend | Annual spend with supplier | Decimal | ERP / AP / Procurement | Optional | Emissions intensity and growth analysis | Denominator for intensity and growth | 2500000 |
| Revenue | Supplier revenue or attributable revenue | Decimal | Supplier survey / Finance | Optional | Financial context and intensity analysis | Optional denominator and dashboard filter | 12000000 |
| Reported_Emissions | Supplier reported total emissions | Decimal | CDP / supplier portal / ESG report | Mandatory | Historical/current emissions input | Core model input | 1850.75 |
| Total_Emission_Value | Validated supplier total emissions | Decimal | ESG data lake / supplier report | Mandatory | Forecast baseline and history | Drives all forecasts | 1850.75 |
| Scope1_Emission | Direct supplier emissions | Decimal | Supplier ESG report | Optional | Scope-level breakdown | Dashboard segmentation | 120.5 |
| Scope2_Emission | Purchased energy emissions | Decimal | Supplier ESG report | Optional | Scope-level breakdown | Dashboard segmentation | 80.2 |
| Scope3_Emission | Supplier value-chain emissions | Decimal | Supplier ESG report | Optional | Scope-level breakdown | Dashboard segmentation | 1650.1 |
| Baseline_Year | Supplier target baseline year | Integer | Supplier target table | Optional | Target pathway start | Defines baseline emission | 2020 |
| Target_Year | Supplier target endpoint year | Integer | Supplier target table | Optional | Target pathway endpoint | Defines target horizon | 2030 |
| Target_Reduction_Percentage | Supplier target reduction from baseline | Decimal | Supplier target table | Optional | Supplier-specific decarbonization goal | Target emission calculation | 0.42 |
| Interim_Target_Reduction_Percentage | Supplier interim reduction goal | Decimal | Supplier target table | Optional | Midpoint governance | Optional interim milestone tracking | 0.21 |
| Target_Type | Absolute or intensity target | String | Supplier target table | Optional | Target interpretation | Can switch formula basis | Absolute |
| Target_Source | Evidence source for supplier target | String | SBTi / CDP / survey / contract | Optional | Auditability | Confidence adjustment | SBTi |
| Industry_Baseline_Year | Industry baseline year | Integer | Industry benchmark table | Optional | Industry target pathway anchor | Industry haircut pathway | 2019 |
| Industry_Target_Year | Industry target year | Integer | Industry benchmark table | Optional | Industry target pathway endpoint | Industry haircut pathway | 2035 |
| Industry_Reduction_Percentage | Industry target reduction haircut | Decimal | Benchmark / pathway scenario | Optional | Industry decarbonization assumption | Used when supplier target missing | 0.35 |
| Industry_Emission_Factor | Average emissions factor for industry | Decimal | LCA / EEIO / benchmark | Optional | Benchmarking context | Not required for emissions calculation when actual emissions exist | 420.5 |
| Spend_Based_Emission_Factor | Emissions per currency unit of spend | Decimal | EEIO / factor database | Optional | Benchmarking context | Not required when actual emissions exist | 0.00045 |
| Revenue_Based_Emission_Intensity | Emissions per currency unit of revenue | Decimal | Industry benchmark / ESG data | Optional | Benchmarking context | Not required when actual emissions exist | 0.00021 |

### Supporting calculated attributes

| Attribute name | Description | Data type | Source system | Mandatory / optional | Business purpose | Model impact | Example value |
|---|---|---:|---|---|---|---|---|
| Total_Emission_Value | Validated total emissions value | Decimal | Source / validation step | Mandatory output | Forecast model input | Drives all emissions forecasts | 1500.42 |
| Emission_Source_Flag | Source used for total emissions | String | Calculated | Mandatory output | Audit trail | Confirms direct emissions input | Provided Total Emissions |
| Emissions_Data_Available_Flag | Confirms emissions are available | Boolean | Calculated | Mandatory output | Completeness control | Excludes incomplete records | TRUE |
| Data_Quality_Flag | High / Missing / Review | String | Calculated | Mandatory output | Governance and filtering | Risk and confidence | High |
| Missing_Parameter_Flag | Missing inputs that affected calculation | String | Calculated | Mandatory output | Data remediation | Data quality dashboard | None |
| Confidence_Score | Forecast confidence score from 0 to 1 | Decimal | Calculated | Mandatory output | Forecast reliability | Risk scoring | 0.82 |
| Validation_Flag | Validity result | String | Calculated | Mandatory output | Audit exception handling | Excludes or flags anomalies | Valid |
| Forecast_Method_Flag | Selected forecast method | String | Calculated | Mandatory output | Method transparency | Explains forecast pathway | Supplier Target Pathway |
| Supplier_Risk_Category | Low / Medium / High / Critical | String | Calculated | Mandatory output | Supplier intervention priority | Dashboard risk heatmap | High |
| Target_Achievement_Status | On track or off track | String | Calculated | Mandatory output | Performance management | Executive reporting | Off Track |

---

## 4. Total Emission Value Validation

### Why the 6-level waterfall is not required here

The 6-level data resolution waterfall is only required when supplier emissions are incomplete and the model must estimate missing values from scopes, spend, revenue, or industry averages. In this dataset, all suppliers already have historical and current emissions, so the model should not estimate emissions. It should use the supplied emissions directly and apply validation controls.

### Direct input logic

Let:

- `TE` = source-provided Total_Emission_Value
- `RE` = Reported_Emissions

```text
Total_Emission_Value =
    TE, if source total emissions are provided
    RE, if reported emissions are provided and TE is not separately provided
    Missing Emissions, only if both are blank
```

This is not a waterfall-estimation method. It is a validation rule that confirms the emissions value is present, non-negative, and reasonable before forecasting.

### Supplemental benchmark calculations

Because actual emissions are already available, spend-based and revenue-based emissions should be used as **benchmark and reasonableness checks**, not as replacements for actual supplier emissions.

| Benchmark | Formula | Purpose | Model treatment |
|---|---|---|---|
| Spend-Based Emissions | `Gross_Spend x Spend_Based_Emission_Factor` | Compare procurement-spend proxy to actual emissions | Supplemental benchmark only |
| Revenue-Based Emissions | `Revenue x Revenue_Based_Emission_Intensity` | Compare revenue-intensity proxy to actual emissions | Supplemental benchmark only |
| Spend-Based vs Actual | `Spend_Based_Emission - Total_Emission_Value` | Identify suppliers where spend proxy diverges from actual emissions | Data quality / reasonableness check |
| Revenue-Based vs Actual | `Revenue_Based_Emission - Total_Emission_Value` | Identify suppliers where revenue proxy diverges from actual emissions | Data quality / reasonableness check |

### Required validation flags

| Flag | Purpose | Example values |
|---|---|---|
| Emission_Source_Flag | Shows whether the model used the supplied total emissions or reported emissions field | Provided Total Emissions, Supplier Reported Emissions |
| Emissions_Data_Available_Flag | Confirms the supplier-year record has emissions available | TRUE / FALSE |
| Data_Quality_Flag | Summarizes quality tier for the supplied value | High, Missing, Review |
| Missing_Parameter_Flag | Lists missing mandatory inputs | None, Total_Emission_Value |
| Confidence_Score | Numeric reliability score for direct emissions input | 0.95 when emissions are available |
| Validation_Flag | Identifies validity issues | Valid, Missing Emissions, Invalid Negative Emissions, Outlier Review |

---

## 5. Forecasting Methodology

### Forecast selection hierarchy

```text
IF supplier target exists:
    Supplier Target Pathway
ELSE IF industry haircut exists:
    Industry Haircut Pathway
ELSE:
    Historical Trend Pathway
```

### 5.1 Supplier Target Pathway

| Category | Detail |
|---|---|
| When to use | Supplier has Baseline_Year, Target_Year, and Target_Reduction_Percentage. |
| Required inputs | Baseline_Emission, Baseline_Year, Target_Year, Target_Reduction_Percentage. |
| Mathematical formula | `Target_Emission = Baseline_Emission x (1 - Target_Reduction_Percentage)` and `Glide_Path = max(Target_Emission, Baseline_Emission - Annual_Reduction_Required x (Forecast_Year - Baseline_Year))`. |
| Excel formula | `=[@[Baseline_Emission]]*(1-[@[Target_Reduction_Percentage]])` |
| Python logic | `forecast_method = "Supplier Target Pathway"` when supplier target fields are populated; forecast follows the glide path. |
| Output columns | Forecast_Method_Flag, Target_Emission, Glide_Path_Emission, Forecast_Emission, Gap_to_Target, Target_Achievement_Status. |
| Business impact | Aligns supplier forecasts with supplier commitments and contractual targets. |
| Advantages | Highest business relevance, easy to audit, supports supplier engagement. |
| Drawbacks | Depends on accurate supplier target evidence and baseline data. |

### 5.2 Industry Haircut Pathway

| Category | Detail |
|---|---|
| When to use | Supplier-specific target is unavailable but industry baseline, target year, and reduction percentage exist. |
| Required inputs | Baseline_Emission, Industry_Target_Year, Industry_Reduction_Percentage. |
| Mathematical formula | `Industry_Target_Emission = Baseline_Emission x (1 - Industry_Reduction_Percentage)`. |
| Excel formula | `=[@[Baseline_Emission]]*(1-[@[Industry_Reduction_Percentage]])` |
| Python logic | Use industry pathway when supplier target fields are missing but industry pathway fields are available. |
| Output columns | Forecast_Method_Flag, Target_Emission, Glide_Path_Emission, Forecast_Emission, Gap_to_Target. |
| Business impact | Provides consistent sector-based assumptions for suppliers without disclosed targets. |
| Advantages | Scalable, consistent, suitable for incomplete supplier target coverage. |
| Drawbacks | Less supplier-specific; can understate or overstate actual supplier decarbonization. |

### 5.3 Historical Trend Pathway

| Category | Detail |
|---|---|
| When to use | Supplier target and industry haircut data are unavailable or insufficient. |
| Required inputs | Historical Total_Emission_Value by Supplier_ID and Supplier_Year. |
| Mathematical formula | `Forecast_Emission_y = Latest_Emission x (1 + Historical_CAGR)^(Forecast_Year - Latest_Year)`. |
| Excel formula | `=[@[Total_Emission_Value]]*(1+[@[Historical_Trend]])^([@[Forecast_Year]]-[@[Supplier_Year]])` |
| Python logic | Calculate supplier historical CAGR and extend the latest emissions value forward. |
| Output columns | Historical_Trend, Forecast_Method_Flag, Forecast_Emission, Gap_to_Target. |
| Business impact | Provides a data-driven estimate when formal target data is missing. |
| Advantages | Uses observed supplier behavior and can detect improving or worsening suppliers. |
| Drawbacks | Past performance may not predict future changes; sensitive to outliers and missing data. |

### 5.4 Spend-Based and Revenue-Based Emissions Benchmarks

| Category | Spend-based emissions | Revenue-based emissions |
|---|---|---|
| When to use | Use as a supplemental benchmark when gross spend and spend factor are available. | Use as a supplemental benchmark when revenue and revenue intensity are available. |
| Required inputs | Gross_Spend, Spend_Based_Emission_Factor, Total_Emission_Value. | Revenue, Revenue_Based_Emission_Intensity, Total_Emission_Value. |
| Mathematical formula | `Spend_Based_Emission = Gross_Spend x Spend_Based_Emission_Factor`. | `Revenue_Based_Emission = Revenue x Revenue_Based_Emission_Intensity`. |
| Excel formula | `=IFERROR([@[Gross_Spend]]*[@[Spend_Based_Emission_Factor]],"")` | `=IFERROR([@[Revenue]]*[@[Revenue_Based_Emission_Intensity]],"")` |
| Output columns | Spend_Based_Emission, Spend_Based_vs_Actual, Spend_Based_Variance_Percentage. | Revenue_Based_Emission, Revenue_Based_vs_Actual, Revenue_Based_Variance_Percentage. |
| Business impact | Helps Procurement test whether spend profile is directionally aligned with actual emissions. | Helps Finance and ESG test whether revenue intensity is directionally aligned with actual emissions. |
| Advantages | Easy to scale across procurement data and useful for reasonableness checks. | Useful when supplier revenue is a better activity proxy than spend. |
| Drawbacks | Spend can reflect inflation, price changes, or category mix rather than physical activity. | Revenue can be distorted by margins, pricing, or supplier business mix. |

Important: these benchmark calculations do not override `Total_Emission_Value`. They support validation, scenario analysis, and dashboard comparisons.

---

## 6. Required Forecast Parameters

| Parameter | Explanation | Business use |
|---|---|---|
| Historical Trend | Supplier emissions CAGR from historical records | Understand actual decarbonization or growth pattern |
| Supplier Target Pathway | Forecast based on supplier's own target | Supplier accountability |
| Industry Haircut Pathway | Forecast based on industry reduction benchmark | Used for suppliers without specific targets |
| Spend-Based Emissions | Gross spend multiplied by spend-based factor | Benchmark actual emissions against procurement-spend proxy |
| Revenue-Based Emissions | Revenue multiplied by revenue-based intensity | Benchmark actual emissions against revenue proxy |
| Spend/Revenue Variance to Actual | Proxy emissions minus actual emissions | Identify unusual differences for review |
| Absolute Emissions Reduction | Baseline emissions minus forecast emissions | Quantifies tonnes reduced |
| Emissions Intensity Reduction | Reduction in emissions per spend or revenue | Normalizes performance for growth |
| Supplier Growth Projection | Spend or revenue CAGR | Adjusts trend-based forecasts for supplier growth |
| Gap-to-Target Analysis | Forecast emissions minus target emissions | Identifies off-track suppliers |
| Glide Path / Year-by-Year Reduction Pathway | Annual emissions trajectory to target | Enables interim tracking |
| Target Emissions | Target endpoint emissions | Defines success threshold |
| Forecast Emissions | Forecast result for each future year | Main model output |
| Baseline Emissions | Emissions in baseline year | Starting point for reductions |
| Annual Reduction Required | Required annual absolute decrease | Annual execution target |
| CAGR | Compound annual growth or reduction rate | Long-run trend calculation |
| YoY Change | Year-over-year emissions change | Annual performance tracking |
| Carbon Budget Remaining | Target budget less cumulative forecast emissions | Budget governance |
| Cumulative Forecast Emissions | Sum of forecast emissions through current forecast year | Long-term climate impact |
| Target Achievement Status | On track / off track | Executive performance status |
| Supplier Risk Category | Low / Medium / High / Critical | Supplier engagement prioritization |
| Forecast Confidence Score | Reliability score based on source quality and method | Audit and data quality weighting |

---

## 7. Mathematical Formula Library

| Calculation | Formula |
|---|---|
| Total Emission Value | `TE` if source total emissions are supplied; otherwise `RE`; otherwise `Missing Emissions` |
| Spend-Based Emissions | `Spend_Based_Emission = Gross_Spend x Spend_Based_Emission_Factor` |
| Revenue-Based Emissions | `Revenue_Based_Emission = Revenue x Revenue_Based_Emission_Intensity` |
| Spend-Based Variance to Actual | `Spend_Based_vs_Actual = Spend_Based_Emission - Total_Emission_Value` |
| Revenue-Based Variance to Actual | `Revenue_Based_vs_Actual = Revenue_Based_Emission - Total_Emission_Value` |
| Spend-Based Variance % | `Spend_Based_Variance_Percentage = Spend_Based_vs_Actual / Total_Emission_Value` |
| Revenue-Based Variance % | `Revenue_Based_Variance_Percentage = Revenue_Based_vs_Actual / Total_Emission_Value` |
| Emission Intensity | `Emission_Intensity = Emissions / Activity`, where activity is spend or revenue |
| Target Emission | `Target_Emission = Baseline_Emission x (1 - Reduction_Percentage)` |
| Annual Reduction | `Annual_Reduction_Required = (Baseline_Emission - Target_Emission) / (Target_Year - Baseline_Year)` |
| Forecast Emission | Target pathways: `Forecast_Emission = Glide_Path_Emission`; trend pathway: `Latest_Emission x (1 + Historical_Trend)^n` |
| Glide Path Emission | `Glide_Path_Emission_y = max(Target_Emission, Baseline_Emission - Annual_Reduction_Required x (Forecast_Year - Baseline_Year))` |
| Absolute Reduction | `Absolute_Reduction = Baseline_Emission - Forecast_Emission` |
| Intensity Reduction | `Intensity_Reduction = (Baseline_Intensity - Forecast_Intensity) / Baseline_Intensity` |
| Gap to Target | `Gap_to_Target = Forecast_Emission - Target_Emission` |
| YoY Change | `YoY_Change = (Emission_y - Emission_y-1) / Emission_y-1` |
| CAGR | `CAGR = (Ending_Value / Beginning_Value)^(1 / Years) - 1` |
| Supplier Growth Projection | `Growth = (Current_Activity / Baseline_Activity)^(1 / Years) - 1` |
| Carbon Budget Remaining | `Carbon_Budget_Remaining = Target_Carbon_Budget - Cumulative_Emissions` |
| Cumulative Emissions | `Cumulative_Emissions_y = sum(Forecast_Emission from start year to y)` |
| Forecast Accuracy | `Accuracy = 1 - abs(Actual - Forecast) / Actual` |
| MAPE | `MAPE = average(abs((Actual - Forecast) / Actual))` |
| RMSE | `RMSE = sqrt(average((Actual - Forecast)^2))` |
| R2 | `R2 = 1 - sum((Actual - Forecast)^2) / sum((Actual - Average_Actual)^2)` |

---

## 8. Excel Formula Library

Assume the main Excel table is named `ForecastTable`.

| Parameter | Structured Excel formula |
|---|---|
| Total_Emission_Value | `=IF([@[Source_Total_Emission_Value]]<>"",[@[Source_Total_Emission_Value]],IF([@[Reported_Emissions]]<>"",[@[Reported_Emissions]],"Missing Emissions"))` |
| Emission_Source_Flag | `=IF([@[Source_Total_Emission_Value]]<>"","Provided Total Emissions",IF([@[Reported_Emissions]]<>"","Supplier Reported Emissions","Missing Emissions"))` |
| Emissions_Data_Available_Flag | `=IF([@[Total_Emission_Value]]<>"",TRUE,FALSE)` |
| Data_Quality_Flag | `=IF([@[Total_Emission_Value]]<>"","High","Missing")` |
| Confidence_Score | `=IF([@[Total_Emission_Value]]<>"",0.95,0)` |
| Spend_Based_Emission | `=IFERROR([@[Gross_Spend]]*[@[Spend_Based_Emission_Factor]],"")` |
| Revenue_Based_Emission | `=IFERROR([@[Revenue]]*[@[Revenue_Based_Emission_Intensity]],"")` |
| Spend_Based_vs_Actual | `=IFERROR([@[Spend_Based_Emission]]-[@[Total_Emission_Value]],"")` |
| Revenue_Based_vs_Actual | `=IFERROR([@[Revenue_Based_Emission]]-[@[Total_Emission_Value]],"")` |
| Spend_Based_Variance_Percentage | `=IFERROR([@[Spend_Based_vs_Actual]]/[@[Total_Emission_Value]],"")` |
| Revenue_Based_Variance_Percentage | `=IFERROR([@[Revenue_Based_vs_Actual]]/[@[Total_Emission_Value]],"")` |
| Forecast_Method_Flag | `=IF(AND([@[Target_Year]]<>"",[@[Target_Reduction_Percentage]]<>""),"Supplier Target Pathway",IF(AND([@[Industry_Target_Year]]<>"",[@[Industry_Reduction_Percentage]]<>""),"Industry Haircut Pathway","Historical Trend Pathway"))` |
| Baseline_Emission | `=SUMIFS(ForecastTable[Total_Emission_Value],ForecastTable[Supplier_ID],[@[Supplier_ID]],ForecastTable[Supplier_Year],[@[Baseline_Year]])` |
| Target_Emission | `=[@[Baseline_Emission]]*(1-[@[Target_Reduction_Percentage]])` |
| Annual_Reduction_Required | `=IFERROR(([@[Baseline_Emission]]-[@[Target_Emission]])/([@[Target_Year]]-[@[Baseline_Year]]),0)` |
| Glide_Path_Emission | `=MAX([@[Target_Emission]],[@[Baseline_Emission]]-[@[Annual_Reduction_Required]]*([@[Forecast_Year]]-[@[Baseline_Year]]))` |
| Forecast_Emission | `=IF([@[Forecast_Method_Flag]]="Historical Trend Pathway",[@[Total_Emission_Value]]*(1+[@[Historical_Trend]])^([@[Forecast_Year]]-[@[Supplier_Year]]),[@[Glide_Path_Emission]])` |
| Absolute_Reduction | `=[@[Baseline_Emission]]-[@[Forecast_Emission]]` |
| Emission_Intensity | `=IFERROR([@[Forecast_Emission]]/[@[Gross_Spend]],"")` |
| Intensity_Reduction | `=IFERROR(([@[Baseline_Intensity]]-[@[Emission_Intensity]])/[@[Baseline_Intensity]],"")` |
| Gap_to_Target | `=[@[Forecast_Emission]]-[@[Target_Emission]]` |
| YoY_Change | `=IFERROR(([@[Forecast_Emission]]-SUMIFS(ForecastTable[Forecast_Emission],ForecastTable[Supplier_ID],[@[Supplier_ID]],ForecastTable[Forecast_Year],[@[Forecast_Year]]-1))/SUMIFS(ForecastTable[Forecast_Emission],ForecastTable[Supplier_ID],[@[Supplier_ID]],ForecastTable[Forecast_Year],[@[Forecast_Year]]-1),"")` |
| CAGR | `=IFERROR(([@[Forecast_Emission]]/[@[Baseline_Emission]])^(1/([@[Forecast_Year]]-[@[Baseline_Year]]))-1,"")` |
| Carbon_Budget_Remaining | `=[@[Target_Carbon_Budget]]-[@[Cumulative_Emissions]]` |
| Cumulative_Emissions | `=SUMIFS(ForecastTable[Forecast_Emission],ForecastTable[Supplier_ID],[@[Supplier_ID]],ForecastTable[Forecast_Year],"<="&[@[Forecast_Year]])` |
| Target_Achievement_Status | `=IF([@[Forecast_Emission]]<=[@[Target_Emission]],"On Track","Off Track")` |
| Supplier_Risk_Category | `=IFS([@[Gap_to_Target]]<=0,"Low",[@[Gap_to_Target]]/[@[Target_Emission]]<=0.15,"Medium",[@[Gap_to_Target]]/[@[Target_Emission]]<=0.35,"High",TRUE,"Critical")` |
| MAPE | `=AVERAGE(ABS((Actual_Range-Forecast_Range)/Actual_Range))` |
| RMSE | `=SQRT(AVERAGE((Actual_Range-Forecast_Range)^2))` |
| R2 | `=1-(SUMXMY2(Actual_Range,Forecast_Range)/DEVSQ(Actual_Range))` |

---

## 9. Python Implementation

The script is available at:

```text
src/supply_chain_emissions_forecast.py
```

Run it with:

```bash
pip install -r requirements.txt
python src/supply_chain_emissions_forecast.py --output-dir data/output
```

It performs the following steps:

1. Generates or reads supplier source datasets.
2. Validates complete historical/current emissions inputs.
3. Confirms `Total_Emission_Value` for each supplier-year record.
4. Calculates spend-based and revenue-based benchmark emissions.
5. Creates source, availability, missing parameter, validation, and quality flags.
6. Applies supplier target pathway.
7. Applies industry haircut pathway.
8. Applies historical trend pathway.
9. Calculates year-by-year glide paths.
10. Calculates gap-to-target, absolute reduction, intensity reduction, carbon budget remaining, cumulative emissions, confidence score, supplier risk category, and target status.
11. Exports all output datasets to CSV and a consolidated Excel workbook.

---

## 10. Sample Data Design

The Python script generates:

- 100 suppliers.
- 1,000 historical supplier-year records by default.
- 8 industries.
- Multiple supplier years from 2015 to 2024.
- Multiple baseline years and target years.
- Gross spend and revenue.
- Reported emissions and scope emissions.
- Complete historical and current emissions for all suppliers.
- Industry haircut table.
- Supplier target table.
- Historical emissions table.

Generated output datasets:

| Dataset | File |
|---|---|
| Supplier Master | `data/output/supplier_master.csv` |
| Historical Emissions | `data/output/historical_emissions.csv` |
| Supplier Targets | `data/output/supplier_targets.csv` |
| Industry Haircut Pathway | `data/output/industry_haircut_pathway.csv` |
| Forecast Output | `data/output/forecast_output.csv` |
| Data Dictionary | `data/output/data_dictionary.csv` |
| Formula Dictionary | `data/output/formula_dictionary.csv` |
| Excel Workbook | `data/output/supply_chain_emissions_forecast_model.xlsx` |

---

## 11. Final Output Dataset

The final forecast output includes:

- Supplier_ID
- Supplier_Name
- Supplier_Industry
- Supplier_Year
- Baseline_Year
- Target_Year
- Forecast_Year
- Reported_Emissions
- Scope1_Emission
- Scope2_Emission
- Scope3_Emission
- Gross_Spend
- Revenue
- Total_Emission_Value
- Emission_Source_Flag
- Emissions_Data_Available_Flag
- Historical_Trend
- Supplier_Growth_Projection
- Spend_Based_Emission
- Revenue_Based_Emission
- Spend_Based_vs_Actual
- Revenue_Based_vs_Actual
- Spend_Based_Variance_Percentage
- Revenue_Based_Variance_Percentage
- Data_Quality_Flag
- Missing_Parameter_Flag
- Validation_Flag
- Forecast_Method_Flag
- Baseline_Emission
- Target_Emission
- Forecast_Emission
- Glide_Path_Emission
- Absolute_Reduction
- Emission_Intensity
- Intensity_Reduction
- Gap_to_Target
- Annual_Reduction_Required
- Carbon_Budget_Remaining
- Cumulative_Emissions
- Confidence_Score
- Supplier_Risk_Category
- Target_Achievement_Status

---

## 12. Qlik Sense Dashboard Scope

### 12.1 Landing Page

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| KPI: Total Forecast Emissions | Forecast_Year | Forecast emissions | `Sum(Forecast_Emission)` | Show total projected emissions | What is our forecast emissions exposure? |
| KPI: Suppliers Covered | Supplier_ID | Supplier count | `Count(DISTINCT Supplier_ID)` | Show model coverage | How many suppliers are included? |
| KPI: Target Coverage | Forecast_Method_Flag | Supplier count | `Count({<Forecast_Method_Flag={'Supplier Target Pathway'}>} DISTINCT Supplier_ID)` | Show supplier target coverage | How many suppliers have their own targets? |
| Navigation Tiles | Page name | N/A | N/A | User navigation | Where should users go for each analysis? |

### 12.2 Executive Summary

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Emissions by Forecast Year | Forecast_Year | Forecast emissions | `Sum(Forecast_Emission)` | Executive trend line | Are emissions increasing or decreasing? |
| Gap to Target KPI | Forecast_Year | Gap to target | `Sum(Gap_to_Target)` | Target performance | Are we above or below target? |
| Risk Category Split | Supplier_Risk_Category | Supplier count | `Count(DISTINCT Supplier_ID)` | Risk overview | How many suppliers are high risk? |
| Carbon Budget Remaining | Forecast_Year | Budget remaining | `Sum(Carbon_Budget_Remaining)` | Budget governance | How much carbon budget remains? |

### 12.3 Supplier Emissions Trend

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Supplier Forecast Trend | Forecast_Year, Supplier_Name | Forecast emissions | `Sum(Forecast_Emission)` | Supplier-level trajectory | Which suppliers drive future emissions? |
| Historical vs Forecast | Supplier_Year / Forecast_Year | Emissions | `Sum(Total_Emission_Value)` and `Sum(Forecast_Emission)` | Compare past and future | Is forecast consistent with history? |
| Top 20 Suppliers | Supplier_Name | Forecast emissions | `Sum(Forecast_Emission)` | Prioritize suppliers | Which suppliers require engagement? |

### 12.4 Industry Benchmark

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Emissions by Industry | Supplier_Industry | Forecast emissions | `Sum(Forecast_Emission)` | Sector concentration | Which industries dominate emissions? |
| Average Intensity by Industry | Supplier_Industry | Emission intensity | `Avg(Emission_Intensity)` | Benchmark intensity | Which industries are most emissions intensive? |
| Industry Pathway Coverage | Supplier_Industry, Forecast_Method_Flag | Supplier count | `Count(DISTINCT Supplier_ID)` | Method coverage by sector | Where are industry assumptions used most? |
| Spend Proxy Variance | Supplier_Industry | Spend variance % | `Avg(Spend_Based_Variance_Percentage)` | Compare spend proxy to actual emissions | Which industries diverge from spend-based estimates? |
| Revenue Proxy Variance | Supplier_Industry | Revenue variance % | `Avg(Revenue_Based_Variance_Percentage)` | Compare revenue proxy to actual emissions | Which industries diverge from revenue-based estimates? |

### 12.5 Gap-to-Target Analysis

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Gap by Supplier | Supplier_Name | Gap to target | `Sum(Gap_to_Target)` | Supplier target gap ranking | Which suppliers are furthest off target? |
| Gap by Year | Forecast_Year | Gap to target | `Sum(Gap_to_Target)` | Time-based gap tracking | When does the target gap peak? |
| Off-Track Supplier Count | Target_Achievement_Status | Supplier count | `Count(DISTINCT Supplier_ID)` | Status view | How many suppliers are off track? |

### 12.6 Glide Path Analysis

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Forecast vs Glide Path | Forecast_Year | Forecast and glide path emissions | `Sum(Forecast_Emission)` and `Sum(Glide_Path_Emission)` | Compare trajectory | Are forecasts aligned with required glide path? |
| Annual Reduction Requirement | Forecast_Year | Annual reduction | `Sum(Annual_Reduction_Required)` | Execution planning | How much reduction is required annually? |
| Target Endpoint View | Target_Year | Target emissions | `Sum(Target_Emission)` | Endpoint planning | What target emissions must be achieved? |

### 12.7 Forecast Method Coverage

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Method Coverage Donut | Forecast_Method_Flag | Supplier count | `Count(DISTINCT Supplier_ID)` | Method transparency | Which forecast methods are most used? |
| Emissions by Method | Forecast_Method_Flag | Forecast emissions | `Sum(Forecast_Emission)` | Exposure by method | How much emissions exposure is estimated vs target based? |
| Confidence by Method | Forecast_Method_Flag | Confidence | `Avg(Confidence_Score)` | Reliability view | Which methods have lower confidence? |

### 12.8 Data Quality Page

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Quality Flag Split | Data_Quality_Flag | Record count | `Count(Supplier_ID)` | Quality monitoring | How much data is high or low quality? |
| Emission Source Split | Emission_Source_Flag | Emissions | `Sum(Total_Emission_Value)` | Source transparency | Which direct emissions source is used? |
| Spend vs Actual Variance | Supplier_Name | Variance | `Sum(Spend_Based_vs_Actual)` | Reasonableness check | Which suppliers differ most from spend proxy? |
| Revenue vs Actual Variance | Supplier_Name | Variance | `Sum(Revenue_Based_vs_Actual)` | Reasonableness check | Which suppliers differ most from revenue proxy? |
| Missing Parameters | Missing_Parameter_Flag | Record count | `Count(Supplier_ID)` | Data remediation | Which inputs should be collected first? |
| Validation Exceptions | Validation_Flag | Record count | `Count(Supplier_ID)` | Audit controls | What records require review? |

### 12.9 Supplier Risk Heatmap

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Risk Heatmap | Supplier_Industry, Supplier_Risk_Category | Supplier count | `Count(DISTINCT Supplier_ID)` | Risk concentration | Which industries have critical suppliers? |
| Supplier Risk Table | Supplier_Name | Risk, gap, confidence | `Only(Supplier_Risk_Category)`, `Sum(Gap_to_Target)`, `Avg(Confidence_Score)` | Supplier action list | Which suppliers need immediate action? |
| Critical Emissions Exposure | Supplier_Risk_Category | Forecast emissions | `Sum({<Supplier_Risk_Category={'Critical'}>} Forecast_Emission)` | Critical exposure | What emissions are associated with critical suppliers? |

### 12.10 Scenario Analysis

| Chart name | Dimension | Measure | Qlik expression | Purpose | Business question answered |
|---|---|---|---|---|---|
| Scenario Reduction Slider | Variable reduction | Forecast emissions | `Sum(Forecast_Emission)*(1-vScenarioReduction)` | What-if modeling | What happens with stronger reductions? |
| Growth Scenario | Variable growth | Forecast emissions | `Sum(Forecast_Emission)*Pow(1+vGrowthRate,Forecast_Year-Min(TOTAL Forecast_Year))` | Growth sensitivity | How does supplier growth affect emissions? |
| Confidence Filter | Confidence band | Forecast emissions | `Sum({<Confidence_Score={">=0.7"}>} Forecast_Emission)` | Reliability filtering | What is the high-confidence emissions view? |

---

## 13. Validation Checks

Recommended validation rules:

| Check | Rule | Action |
|---|---|---|
| Negative emissions | Emissions must be >= 0 | Flag invalid |
| Missing total emissions | Total_Emission_Value is null | Exclude from forecast or remediate |
| Extreme outliers | Total emissions above threshold or z-score limit | Flag for review |
| Missing target year | Supplier target reduction exists but target year missing | Use industry pathway |
| Target year before baseline year | Target_Year <= Baseline_Year | Flag invalid target |
| Missing spend or revenue | Activity denominator missing | Intensity or growth metrics may be blank |
| Low confidence | Confidence_Score below threshold | Prioritize data improvement |

---

## 14. Advantages, Drawbacks, Assumptions, and Risks

### Advantages

- Direct use of actual historical/current supplier emissions.
- Avoids unnecessary estimates when emissions data is already complete.
- Supports supplier-specific and industry decarbonization pathways.
- Produces audit-friendly source, method, quality, and validation flags.
- Scales across Python, Excel, and Qlik Sense.
- Creates supplier risk and confidence views for procurement action.

### Drawbacks

- Industry haircuts may not represent individual supplier operations.
- Historical trend models can be distorted by one-time events, acquisitions, or reporting changes.
- Scope 3 supplier data may have inconsistent boundaries across suppliers.
- Carbon budget calculations depend on policy assumptions.

### Key assumptions

- Historical and current supplier emissions are available for every supplier.
- Supplied emissions are non-negative and aligned to the reporting period.
- Spend and revenue values are aligned to the same currency and period when used for intensity.
- Target reduction percentages are expressed as decimals, for example `0.42` for 42%.
- Linear glide paths are acceptable for annual planning unless a science-based nonlinear pathway is provided.
- Latest historical emissions are the starting point for forward forecasts.

### Risks

- Supplier-reported data may be unaudited or use inconsistent methods.
- Emission factors may become outdated.
- Procurement spend changes may reflect price inflation rather than real activity growth.
- Revenue-based intensity can be distorted by supplier margin changes.
- Missing supplier target coverage can increase reliance on lower-confidence methods.

---

## 15. Future Enhancements

1. Add region-specific emission factors and grid decarbonization curves.
2. Add nonlinear S-curve or science-based sectoral decarbonization pathways.
3. Add supplier-specific production volume denominators.
4. Add Monte Carlo confidence intervals for forecast uncertainty.
5. Add automated anomaly detection for emissions and spend.
6. Add scenario parameters for procurement growth, supplier switching, and renewable energy adoption.
7. Integrate external datasets such as CDP, SBTi, EcoVadis, or lifecycle assessment factors.
8. Add model backtesting using historical holdout years.
9. Add workflow controls for supplier engagement and data remediation.
10. Add auditable versioning for emission factors and target assumptions.
