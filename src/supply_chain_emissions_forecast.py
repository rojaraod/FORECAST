"""
Supply Chain Emissions Forecasting Model

This script creates a supplier-level emissions forecasting framework that can be
implemented in Python, Excel, and Qlik Sense. It can either generate synthetic
sample data or read prepared CSV files, calculates total emissions using a
prioritized fallback hierarchy, selects a forecasting method, builds annual glide
paths, scores confidence, categorizes supplier risk, and exports CSV/XLSX
datasets for analytics and dashboarding.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd


INDUSTRIES = [
    "Electronics",
    "Logistics",
    "Chemicals",
    "Metals",
    "Packaging",
    "Professional Services",
    "Agriculture",
    "Textiles",
]


def safe_divide(numerator: float, denominator: float) -> float:
    """Return numerator / denominator, preserving NaN for invalid divisions."""
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return np.nan
    return numerator / denominator


def bounded(value: float, lower: float, upper: float) -> float:
    """Clamp a numeric value between lower and upper bounds."""
    return max(lower, min(upper, value))


def generate_industry_haircut_table(rng: np.random.Generator) -> pd.DataFrame:
    """Create industry fallback targets and emission factors."""
    rows = []
    for industry in INDUSTRIES:
        has_industry_pathway = industry not in {"Agriculture", "Professional Services"}
        rows.append(
            {
                "Supplier_Industry": industry,
                "Industry_Baseline_Year": int(rng.choice([2018, 2019, 2020])),
                "Industry_Target_Year": int(rng.choice([2030, 2035, 2040]))
                if has_industry_pathway
                else np.nan,
                "Industry_Reduction_Percentage": round(float(rng.uniform(0.18, 0.55)), 4)
                if has_industry_pathway
                else np.nan,
                "Industry_Emission_Factor": round(float(rng.uniform(120, 720)), 4),
                "Spend_Based_Emission_Factor": round(float(rng.uniform(0.00008, 0.0012)), 8),
                "Revenue_Based_Emission_Intensity": round(float(rng.uniform(0.00005, 0.0010)), 8),
            }
        )
    return pd.DataFrame(rows)


def generate_supplier_master(
    rng: np.random.Generator, supplier_count: int = 100
) -> pd.DataFrame:
    """Create supplier master records."""
    rows = []
    for supplier_number in range(1, supplier_count + 1):
        industry = str(rng.choice(INDUSTRIES))
        rows.append(
            {
                "Supplier_ID": f"SUP-{supplier_number:04d}",
                "Supplier_Name": f"{industry.split()[0]} Supplier {supplier_number:03d}",
                "Supplier_Industry": industry,
                "Supplier_Country": str(
                    rng.choice(["US", "DE", "IN", "CN", "BR", "MX", "UK", "JP"])
                ),
                "Preferred_Supplier_Flag": bool(rng.choice([True, False], p=[0.55, 0.45])),
                "Supplier_Status": str(rng.choice(["Active", "Strategic", "Watchlist"], p=[0.75, 0.18, 0.07])),
            }
        )
    return pd.DataFrame(rows)


def generate_supplier_targets(
    rng: np.random.Generator, supplier_master: pd.DataFrame
) -> pd.DataFrame:
    """Create supplier-specific targets for a subset of suppliers."""
    target_rows = []
    targeted_suppliers = supplier_master.sample(
        frac=0.62, random_state=int(rng.integers(1, 1_000_000))
    )
    for _, supplier in targeted_suppliers.iterrows():
        baseline_year = int(rng.choice([2018, 2019, 2020, 2021]))
        target_year = int(rng.choice([2030, 2035, 2040]))
        reduction = round(float(rng.uniform(0.20, 0.70)), 4)
        interim_reduction = round(float(reduction * rng.uniform(0.35, 0.65)), 4)
        target_rows.append(
            {
                "Supplier_ID": supplier["Supplier_ID"],
                "Supplier_Name": supplier["Supplier_Name"],
                "Supplier_Industry": supplier["Supplier_Industry"],
                "Baseline_Year": baseline_year,
                "Target_Year": target_year,
                "Target_Reduction_Percentage": reduction,
                "Interim_Target_Reduction_Percentage": interim_reduction,
                "Target_Type": str(rng.choice(["Absolute", "Intensity"], p=[0.72, 0.28])),
                "Target_Source": str(rng.choice(["SBTi", "CDP", "Supplier Survey", "Contractual Target"])),
            }
        )
    return pd.DataFrame(target_rows)


def generate_historical_emissions(
    rng: np.random.Generator,
    supplier_master: pd.DataFrame,
    supplier_targets: pd.DataFrame,
    industry_table: pd.DataFrame,
    start_year: int = 2015,
    end_year: int = 2024,
) -> pd.DataFrame:
    """Create 1,000 historical supplier-year records by default."""
    target_lookup = supplier_targets.set_index("Supplier_ID").to_dict("index")
    industry_lookup = industry_table.set_index("Supplier_Industry").to_dict("index")
    rows = []

    for _, supplier in supplier_master.iterrows():
        industry = supplier["Supplier_Industry"]
        industry_factors = industry_lookup[industry]
        supplier_base_spend = float(rng.uniform(150_000, 25_000_000))
        supplier_base_revenue = supplier_base_spend * float(rng.uniform(1.2, 8.0))
        supplier_emission_multiplier = float(rng.uniform(0.65, 1.45))
        annual_spend_growth = float(rng.uniform(-0.03, 0.09))
        decarb_rate = float(rng.uniform(-0.01, 0.055))

        for supplier_year in range(start_year, end_year + 1):
            years_from_start = supplier_year - start_year
            spend = supplier_base_spend * ((1 + annual_spend_growth) ** years_from_start)
            revenue = supplier_base_revenue * ((1 + annual_spend_growth + rng.normal(0.005, 0.018)) ** years_from_start)
            spend *= float(rng.normal(1.0, 0.08))
            revenue *= float(rng.normal(1.0, 0.10))

            model_emissions = (
                spend
                * industry_factors["Spend_Based_Emission_Factor"]
                * supplier_emission_multiplier
                * ((1 - decarb_rate) ** years_from_start)
                * float(rng.normal(1.0, 0.12))
            )
            model_emissions = max(model_emissions, 1.0)

            scope1_share = float(rng.uniform(0.08, 0.28))
            scope2_share = float(rng.uniform(0.06, 0.22))
            scope3_share = max(0.0, 1.0 - scope1_share - scope2_share)
            scope1 = model_emissions * scope1_share * float(rng.normal(1.0, 0.03))
            scope2 = model_emissions * scope2_share * float(rng.normal(1.0, 0.03))
            scope3 = model_emissions * scope3_share * float(rng.normal(1.0, 0.03))

            reported_emissions = model_emissions * float(rng.normal(1.0, 0.04))

            # Missingness is intentional so the fallback logic is exercised.
            if rng.random() < 0.28:
                reported_emissions = np.nan
            if rng.random() < 0.18:
                scope1 = np.nan
            if rng.random() < 0.20:
                scope2 = np.nan
            if rng.random() < 0.22:
                scope3 = np.nan
            if rng.random() < 0.07:
                spend = np.nan
            if rng.random() < 0.08:
                revenue = np.nan

            target = target_lookup.get(supplier["Supplier_ID"], {})
            rows.append(
                {
                    "Supplier_ID": supplier["Supplier_ID"],
                    "Supplier_Name": supplier["Supplier_Name"],
                    "Supplier_Industry": industry,
                    "Supplier_Year": supplier_year,
                    "Gross_Spend": round(float(spend), 2) if not pd.isna(spend) else np.nan,
                    "Revenue": round(float(revenue), 2) if not pd.isna(revenue) else np.nan,
                    "Reported_Emissions": round(float(reported_emissions), 4)
                    if not pd.isna(reported_emissions)
                    else np.nan,
                    "Scope1_Emission": round(float(scope1), 4) if not pd.isna(scope1) else np.nan,
                    "Scope2_Emission": round(float(scope2), 4) if not pd.isna(scope2) else np.nan,
                    "Scope3_Emission": round(float(scope3), 4) if not pd.isna(scope3) else np.nan,
                    "Baseline_Year": target.get("Baseline_Year", np.nan),
                    "Target_Year": target.get("Target_Year", np.nan),
                    "Target_Reduction_Percentage": target.get("Target_Reduction_Percentage", np.nan),
                    "Interim_Target_Reduction_Percentage": target.get(
                        "Interim_Target_Reduction_Percentage", np.nan
                    ),
                    "Industry_Baseline_Year": industry_factors["Industry_Baseline_Year"],
                    "Industry_Target_Year": industry_factors["Industry_Target_Year"],
                    "Industry_Reduction_Percentage": industry_factors["Industry_Reduction_Percentage"],
                    "Industry_Emission_Factor": industry_factors["Industry_Emission_Factor"],
                    "Spend_Based_Emission_Factor": industry_factors["Spend_Based_Emission_Factor"],
                    "Revenue_Based_Emission_Intensity": industry_factors[
                        "Revenue_Based_Emission_Intensity"
                    ],
                }
            )
    return pd.DataFrame(rows)


def create_sample_data(seed: int, supplier_count: int) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generate supplier master, historical emissions, supplier targets, and industry tables."""
    rng = np.random.default_rng(seed)
    industry_table = generate_industry_haircut_table(rng)
    supplier_master = generate_supplier_master(rng, supplier_count=supplier_count)
    supplier_targets = generate_supplier_targets(rng, supplier_master)
    historical_emissions = generate_historical_emissions(
        rng, supplier_master, supplier_targets, industry_table
    )
    return supplier_master, historical_emissions, supplier_targets, industry_table


def calculate_total_emission(row: pd.Series) -> pd.Series:
    """
    Calculate Total_Emission_Value using the required priority hierarchy.

    Priority 1: Supplier reported emissions.
    Priority 2: Scope 1 + Scope 2 + Scope 3.
    Priority 3: Spend x spend-based emission factor.
    Priority 4: Revenue x revenue-based emission intensity.
    Priority 5: Industry average or haircut estimate.
    Priority 6: Missing data.
    """
    missing_parameters = []
    total_emissions = np.nan
    emission_source = "Missing Data"
    fallback_applied = False
    data_quality = "Missing"
    confidence = 0.0

    reported = row.get("Reported_Emissions")
    scope_values = [row.get("Scope1_Emission"), row.get("Scope2_Emission"), row.get("Scope3_Emission")]
    spend = row.get("Gross_Spend")
    spend_factor = row.get("Spend_Based_Emission_Factor")
    revenue = row.get("Revenue")
    revenue_intensity = row.get("Revenue_Based_Emission_Intensity")
    industry_factor = row.get("Industry_Emission_Factor")

    if not pd.isna(reported) and reported >= 0:
        total_emissions = reported
        emission_source = "Supplier Reported Emissions"
        data_quality = "High"
        confidence = 0.95
    elif all(not pd.isna(value) for value in scope_values):
        total_emissions = sum(scope_values)
        emission_source = "Scope 1 + Scope 2 + Scope 3"
        fallback_applied = True
        data_quality = "High"
        confidence = 0.88
    elif not pd.isna(spend) and not pd.isna(spend_factor):
        total_emissions = spend * spend_factor
        emission_source = "Spend-Based Estimate"
        fallback_applied = True
        data_quality = "Medium"
        confidence = 0.70
    elif not pd.isna(revenue) and not pd.isna(revenue_intensity):
        total_emissions = revenue * revenue_intensity
        emission_source = "Revenue-Based Estimate"
        fallback_applied = True
        data_quality = "Medium-Low"
        confidence = 0.60
    elif not pd.isna(industry_factor):
        activity_proxy = spend if not pd.isna(spend) else revenue
        if not pd.isna(activity_proxy):
            scale_factor = 1_000_000
            total_emissions = industry_factor * (activity_proxy / scale_factor)
            emission_source = "Industry Haircut Estimate"
            fallback_applied = True
            data_quality = "Low"
            confidence = 0.45
        else:
            missing_parameters.extend(["Gross_Spend", "Revenue"])
    else:
        missing_parameters.append("Industry_Emission_Factor")

    if pd.isna(reported):
        missing_parameters.append("Reported_Emissions")
    if any(pd.isna(value) for value in scope_values):
        missing_parameters.append("Scope_Emissions")
    if pd.isna(spend):
        missing_parameters.append("Gross_Spend")
    if pd.isna(spend_factor):
        missing_parameters.append("Spend_Based_Emission_Factor")
    if pd.isna(revenue):
        missing_parameters.append("Revenue")
    if pd.isna(revenue_intensity):
        missing_parameters.append("Revenue_Based_Emission_Intensity")

    validation_flag = "Valid"
    if pd.isna(total_emissions):
        validation_flag = "Missing Emissions"
    elif total_emissions < 0:
        validation_flag = "Invalid Negative Emissions"
    elif total_emissions > 1_000_000:
        validation_flag = "Outlier Review"

    return pd.Series(
        {
            "Total_Emission_Value": round(float(total_emissions), 4) if not pd.isna(total_emissions) else np.nan,
            "Emission_Source_Flag": emission_source,
            "Fallback_Applied_Flag": bool(fallback_applied),
            "Data_Quality_Flag": data_quality,
            "Missing_Parameter_Flag": "; ".join(sorted(set(missing_parameters))) if missing_parameters else "None",
            "Base_Confidence_Score": round(float(confidence), 4),
            "Validation_Flag": validation_flag,
        }
    )


def add_total_emission_calculations(historical_emissions: pd.DataFrame) -> pd.DataFrame:
    """Apply total emission fallback logic to every supplier-year record."""
    calculated = historical_emissions.apply(calculate_total_emission, axis=1)
    return pd.concat([historical_emissions.copy(), calculated], axis=1)


def compute_supplier_metrics(enriched_history: pd.DataFrame) -> pd.DataFrame:
    """Calculate historical trend and baseline metrics at supplier level."""
    valid_history = enriched_history.dropna(subset=["Total_Emission_Value"]).copy()
    metrics = []

    for supplier_id, group in valid_history.groupby("Supplier_ID"):
        group = group.sort_values("Supplier_Year")
        latest = group.iloc[-1]
        earliest = group.iloc[0]
        baseline_year = latest.get("Baseline_Year")
        baseline_record = pd.DataFrame()

        if not pd.isna(baseline_year):
            baseline_record = group[group["Supplier_Year"] == int(baseline_year)]
        if baseline_record.empty:
            baseline_record = group[group["Supplier_Year"] == group["Supplier_Year"].min()]

        baseline_row = baseline_record.iloc[0]
        baseline_emission = float(baseline_row["Total_Emission_Value"])
        latest_emission = float(latest["Total_Emission_Value"])
        historical_years = max(int(latest["Supplier_Year"] - earliest["Supplier_Year"]), 1)
        historical_cagr = (latest_emission / float(earliest["Total_Emission_Value"])) ** (1 / historical_years) - 1

        spend_growth = np.nan
        spend_history = group.dropna(subset=["Gross_Spend"])
        if len(spend_history) >= 2:
            first_spend = float(spend_history.iloc[0]["Gross_Spend"])
            last_spend = float(spend_history.iloc[-1]["Gross_Spend"])
            spend_years = max(
                int(spend_history.iloc[-1]["Supplier_Year"] - spend_history.iloc[0]["Supplier_Year"]),
                1,
            )
            if first_spend > 0:
                spend_growth = (last_spend / first_spend) ** (1 / spend_years) - 1

        metrics.append(
            {
                "Supplier_ID": supplier_id,
                "Supplier_Name": latest["Supplier_Name"],
                "Supplier_Industry": latest["Supplier_Industry"],
                "Baseline_Year": int(baseline_row["Supplier_Year"]),
                "Baseline_Emission": round(baseline_emission, 4),
                "Latest_Historical_Year": int(latest["Supplier_Year"]),
                "Latest_Historical_Emission": round(latest_emission, 4),
                "Historical_Trend": round(float(historical_cagr), 6),
                "Supplier_Growth_Projection": round(float(spend_growth), 6)
                if not pd.isna(spend_growth)
                else 0.0,
                "Historical_Record_Count": int(len(group)),
                "Average_Base_Confidence": round(float(group["Base_Confidence_Score"].mean()), 4),
                "Latest_Gross_Spend": latest.get("Gross_Spend", np.nan),
                "Latest_Revenue": latest.get("Revenue", np.nan),
            }
        )
    return pd.DataFrame(metrics)


def select_forecast_method(row: pd.Series) -> str:
    """Select forecast method using supplier target, industry haircut, historical trend hierarchy."""
    if not pd.isna(row.get("Target_Reduction_Percentage")) and not pd.isna(row.get("Target_Year")):
        return "Supplier Target Pathway"
    if (
        not pd.isna(row.get("Industry_Reduction_Percentage"))
        and not pd.isna(row.get("Industry_Target_Year"))
    ):
        return "Industry Haircut Pathway"
    return "Historical Trend Pathway"


def calculate_forecast_row(
    supplier: pd.Series,
    forecast_year: int,
    target_reduction: float,
    target_year: int,
    forecast_method: str,
) -> Dict[str, object]:
    """Calculate one supplier-year forecast row."""
    baseline_year = int(supplier["Baseline_Year"])
    baseline_emission = float(supplier["Baseline_Emission"])
    latest_year = int(supplier["Latest_Historical_Year"])
    latest_emission = float(supplier["Latest_Historical_Emission"])
    target_year = int(target_year)
    target_reduction = bounded(float(target_reduction), 0.0, 0.99)
    target_emission = baseline_emission * (1 - target_reduction)

    full_target_span = max(target_year - baseline_year, 1)
    annual_reduction_required = (baseline_emission - target_emission) / full_target_span

    years_after_latest = max(forecast_year - latest_year, 0)
    years_after_baseline = max(forecast_year - baseline_year, 0)
    glide_path_emission = max(
        target_emission,
        baseline_emission - annual_reduction_required * years_after_baseline,
    )

    if forecast_method in {"Supplier Target Pathway", "Industry Haircut Pathway"}:
        forecast_emission = glide_path_emission
    else:
        growth_projection = float(supplier.get("Supplier_Growth_Projection", 0.0) or 0.0)
        trend = float(supplier.get("Historical_Trend", 0.0) or 0.0)
        combined_rate = bounded((0.65 * trend) + (0.35 * growth_projection), -0.20, 0.20)
        forecast_emission = latest_emission * ((1 + combined_rate) ** years_after_latest)

    absolute_reduction = baseline_emission - forecast_emission
    emission_intensity = safe_divide(forecast_emission, supplier.get("Latest_Gross_Spend"))
    baseline_intensity = safe_divide(baseline_emission, supplier.get("Latest_Gross_Spend"))
    intensity_reduction = safe_divide(baseline_intensity - emission_intensity, baseline_intensity)
    gap_to_target = forecast_emission - target_emission

    return {
        "Forecast_Year": forecast_year,
        "Forecast_Method_Flag": forecast_method,
        "Baseline_Emission": round(baseline_emission, 4),
        "Target_Emission": round(float(target_emission), 4),
        "Forecast_Emission": round(float(forecast_emission), 4),
        "Glide_Path_Emission": round(float(glide_path_emission), 4),
        "Absolute_Reduction": round(float(absolute_reduction), 4),
        "Emission_Intensity": round(float(emission_intensity), 8) if not pd.isna(emission_intensity) else np.nan,
        "Intensity_Reduction": round(float(intensity_reduction), 6)
        if not pd.isna(intensity_reduction)
        else np.nan,
        "Gap_to_Target": round(float(gap_to_target), 4),
        "Annual_Reduction_Required": round(float(annual_reduction_required), 4),
    }


def build_forecast_output(
    enriched_history: pd.DataFrame,
    supplier_targets: pd.DataFrame,
    industry_table: pd.DataFrame,
    forecast_start_year: int = 2025,
    forecast_end_year: int = 2040,
) -> pd.DataFrame:
    """Build supplier-year forecast records with glide path and risk outputs."""
    supplier_metrics = compute_supplier_metrics(enriched_history)
    target_cols = [
        "Supplier_ID",
        "Target_Year",
        "Target_Reduction_Percentage",
        "Interim_Target_Reduction_Percentage",
        "Target_Type",
    ]
    supplier_metrics = supplier_metrics.merge(
        supplier_targets[target_cols], on="Supplier_ID", how="left"
    )
    supplier_metrics = supplier_metrics.merge(industry_table, on="Supplier_Industry", how="left")

    latest_history = (
        enriched_history.sort_values("Supplier_Year")
        .groupby("Supplier_ID")
        .tail(1)
        .set_index("Supplier_ID")
    )

    forecast_rows = []
    for _, supplier in supplier_metrics.iterrows():
        method = select_forecast_method(supplier)
        if method == "Supplier Target Pathway":
            target_reduction = supplier["Target_Reduction_Percentage"]
            target_year = int(supplier["Target_Year"])
        elif method == "Industry Haircut Pathway":
            target_reduction = supplier["Industry_Reduction_Percentage"]
            target_year = int(supplier["Industry_Target_Year"])
        else:
            trend = float(supplier.get("Historical_Trend", 0.0) or 0.0)
            target_reduction = bounded(-trend * 10, 0.05, 0.35)
            target_year = forecast_end_year

        cumulative_emissions = 0.0
        for forecast_year in range(forecast_start_year, forecast_end_year + 1):
            calculated = calculate_forecast_row(
                supplier=supplier,
                forecast_year=forecast_year,
                target_reduction=target_reduction,
                target_year=target_year,
                forecast_method=method,
            )
            cumulative_emissions += float(calculated["Forecast_Emission"])
            target_emission = float(calculated["Target_Emission"])
            forecast_emission = float(calculated["Forecast_Emission"])
            target_budget = max(
                target_emission * max(target_year - forecast_start_year + 1, 1),
                0.0,
            )
            carbon_budget_remaining = target_budget - cumulative_emissions
            gap_ratio = safe_divide(forecast_emission - target_emission, target_emission)

            base_confidence = float(supplier["Average_Base_Confidence"])
            method_adjustment = {
                "Supplier Target Pathway": 0.05,
                "Industry Haircut Pathway": -0.05,
                "Historical Trend Pathway": -0.12,
            }[method]
            confidence_score = bounded(
                base_confidence + method_adjustment + min(supplier["Historical_Record_Count"], 10) * 0.005,
                0.10,
                0.99,
            )

            if pd.isna(gap_ratio):
                risk_category = "Unknown"
            elif gap_ratio <= 0:
                risk_category = "Low"
            elif gap_ratio <= 0.15:
                risk_category = "Medium"
            elif gap_ratio <= 0.35:
                risk_category = "High"
            else:
                risk_category = "Critical"

            target_status = "On Track" if forecast_emission <= target_emission else "Off Track"
            if forecast_year < target_year and forecast_emission <= float(calculated["Glide_Path_Emission"]):
                target_status = "On Track to Glide Path"

            latest = latest_history.loc[supplier["Supplier_ID"]]
            forecast_rows.append(
                {
                    "Supplier_ID": supplier["Supplier_ID"],
                    "Supplier_Name": supplier["Supplier_Name"],
                    "Supplier_Industry": supplier["Supplier_Industry"],
                    "Supplier_Year": int(latest["Supplier_Year"]),
                    "Baseline_Year": int(supplier["Baseline_Year"]),
                    "Target_Year": int(target_year),
                    "Reported_Emissions": latest.get("Reported_Emissions"),
                    "Scope1_Emission": latest.get("Scope1_Emission"),
                    "Scope2_Emission": latest.get("Scope2_Emission"),
                    "Scope3_Emission": latest.get("Scope3_Emission"),
                    "Gross_Spend": latest.get("Gross_Spend"),
                    "Revenue": latest.get("Revenue"),
                    "Total_Emission_Value": latest.get("Total_Emission_Value"),
                    "Emission_Source_Flag": latest.get("Emission_Source_Flag"),
                    "Fallback_Applied_Flag": latest.get("Fallback_Applied_Flag"),
                    "Data_Quality_Flag": latest.get("Data_Quality_Flag"),
                    "Missing_Parameter_Flag": latest.get("Missing_Parameter_Flag"),
                    "Validation_Flag": latest.get("Validation_Flag"),
                    **calculated,
                    "Carbon_Budget_Remaining": round(float(carbon_budget_remaining), 4),
                    "Cumulative_Emissions": round(float(cumulative_emissions), 4),
                    "Confidence_Score": round(float(confidence_score), 4),
                    "Supplier_Risk_Category": risk_category,
                    "Target_Achievement_Status": target_status,
                }
            )

    return pd.DataFrame(forecast_rows)


def create_data_dictionary() -> pd.DataFrame:
    """Create a data dictionary for source and output fields."""
    rows = [
        ("Supplier_ID", "Unique supplier key", "String", "ERP / Supplier master", "Mandatory", "Joins datasets", "Primary grouping key", "SUP-0001"),
        ("Supplier_Name", "Legal or reporting supplier name", "String", "ERP / Supplier master", "Mandatory", "Supplier reporting", "Dashboard label", "Electronics Supplier 001"),
        ("Supplier_Industry", "Supplier industry category", "String", "Supplier master / Taxonomy", "Mandatory", "Benchmarking and fallback targets", "Enables industry haircut pathway", "Electronics"),
        ("Supplier_Year", "Historical reporting year", "Integer", "ERP / ESG data lake", "Mandatory", "Time series analysis", "Trend and baseline selection", "2024"),
        ("Gross_Spend", "Annual procurement spend", "Decimal", "ERP / Procurement", "Optional", "Spend-based emissions estimate", "Fallback calculation and intensity", "2500000"),
        ("Revenue", "Supplier revenue attributable or total revenue", "Decimal", "Supplier survey / Finance", "Optional", "Revenue-based intensity estimate", "Fallback calculation", "12000000"),
        ("Reported_Emissions", "Supplier reported total emissions", "Decimal", "CDP / Supplier portal", "Optional", "Preferred emissions source", "Highest confidence total", "1850.75"),
        ("Scope1_Emission", "Direct emissions", "Decimal", "Supplier ESG report", "Optional", "Scope-level rollup", "Second priority fallback", "120.5"),
        ("Scope2_Emission", "Purchased energy emissions", "Decimal", "Supplier ESG report", "Optional", "Scope-level rollup", "Second priority fallback", "80.2"),
        ("Scope3_Emission", "Supplier value-chain emissions", "Decimal", "Supplier ESG report", "Optional", "Scope-level rollup", "Second priority fallback", "1650.1"),
        ("Baseline_Year", "Supplier target baseline year", "Integer", "Supplier target table", "Optional", "Target pathway anchor", "Defines baseline emission", "2020"),
        ("Target_Year", "Supplier target completion year", "Integer", "Supplier target table", "Optional", "Target pathway endpoint", "Forecast endpoint", "2030"),
        ("Target_Reduction_Percentage", "Supplier target reduction from baseline", "Decimal", "Supplier target table", "Optional", "Supplier-specific target", "Target emission formula", "0.42"),
        ("Interim_Target_Reduction_Percentage", "Interim reduction target", "Decimal", "Supplier target table", "Optional", "Midpoint governance", "Can support milestone dashboard", "0.21"),
        ("Industry_Baseline_Year", "Industry baseline year", "Integer", "Industry benchmark table", "Optional", "Fallback pathway anchor", "Industry pathway", "2019"),
        ("Industry_Target_Year", "Industry target year", "Integer", "Industry benchmark table", "Optional", "Fallback pathway endpoint", "Industry pathway", "2035"),
        ("Industry_Reduction_Percentage", "Industry reduction haircut", "Decimal", "Benchmark / ESG scenario", "Optional", "Fallback reduction target", "Industry pathway", "0.35"),
        ("Industry_Emission_Factor", "Average industry emissions factor", "Decimal", "LCA / EEIO factor database", "Optional", "Last-resort estimate", "Fallback source", "420.5"),
        ("Spend_Based_Emission_Factor", "Emissions per currency spend", "Decimal", "EEIO / Procurement factor table", "Optional", "Spend-based estimate", "Fallback source", "0.00045"),
        ("Revenue_Based_Emission_Intensity", "Emissions per currency revenue", "Decimal", "Benchmark / ESG data", "Optional", "Revenue-based estimate", "Fallback source", "0.00021"),
        ("Total_Emission_Value", "Best available calculated total emissions", "Decimal", "Calculated", "Mandatory output", "Core model input", "Drives all forecasts", "1500.42"),
        ("Forecast_Method_Flag", "Selected forecasting method", "String", "Calculated", "Mandatory output", "Governance transparency", "Explains forecast basis", "Supplier Target Pathway"),
        ("Confidence_Score", "0-1 confidence score", "Decimal", "Calculated", "Mandatory output", "Risk and audit context", "Weights data reliability", "0.86"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "Attribute_Name",
            "Description",
            "Data_Type",
            "Source_System",
            "Mandatory_or_Optional",
            "Business_Purpose",
            "Model_Impact",
            "Example_Value",
        ],
    )


def create_formula_dictionary() -> pd.DataFrame:
    """Create Excel-style formulas for calculated parameters."""
    rows = [
        ("Total_Emission_Value", '=IF([@[Reported_Emissions]]<>"",[@[Reported_Emissions]],IF(AND([@[Scope1_Emission]]<>"",[@[Scope2_Emission]]<>"",[@[Scope3_Emission]]<>""),[@[Scope1_Emission]]+[@[Scope2_Emission]]+[@[Scope3_Emission]],IF(AND([@[Gross_Spend]]<>"",[@[Spend_Based_Emission_Factor]]<>""),[@[Gross_Spend]]*[@[Spend_Based_Emission_Factor]],IF(AND([@[Revenue]]<>"",[@[Revenue_Based_Emission_Intensity]]<>""),[@[Revenue]]*[@[Revenue_Based_Emission_Intensity]],IF([@[Industry_Emission_Factor]]<>"",[@[Industry_Emission_Factor]],"Missing Data")))))'),
        ("Emission_Intensity", '=IFERROR([@[Forecast_Emission]]/[@[Gross_Spend]],"")'),
        ("Target_Emission", '=[@[Baseline_Emission]]*(1-[@[Target_Reduction_Percentage]])'),
        ("Annual_Reduction_Required", '=IFERROR(([@[Baseline_Emission]]-[@[Target_Emission]])/([@[Target_Year]]-[@[Baseline_Year]]),0)'),
        ("Forecast_Emission", '=IF([@[Forecast_Method_Flag]]="Historical Trend Pathway",[@[Total_Emission_Value]]*(1+[@[Historical_Trend]])^([@[Forecast_Year]]-[@[Supplier_Year]]),[@[Glide_Path_Emission]])'),
        ("Glide_Path_Emission", '=MAX([@[Target_Emission]],[@[Baseline_Emission]]-[@[Annual_Reduction_Required]]*([@[Forecast_Year]]-[@[Baseline_Year]]))'),
        ("Absolute_Reduction", '=[@[Baseline_Emission]]-[@[Forecast_Emission]]'),
        ("Intensity_Reduction", '=IFERROR(([@[Baseline_Intensity]]-[@[Emission_Intensity]])/[@[Baseline_Intensity]],"")'),
        ("Gap_to_Target", '=[@[Forecast_Emission]]-[@[Target_Emission]]'),
        ("YoY_Change", '=IFERROR(([@[Forecast_Emission]]-OFFSET([@[Forecast_Emission]],-1,0))/OFFSET([@[Forecast_Emission]],-1,0),"")'),
        ("CAGR", '=IFERROR(([@[Forecast_Emission]]/[@[Baseline_Emission]])^(1/([@[Forecast_Year]]-[@[Baseline_Year]]))-1,"")'),
        ("Supplier_Growth_Projection", '=IFERROR(([@[Current_Spend]]/[@[Baseline_Spend]])^(1/([@[Supplier_Year]]-[@[Baseline_Year]]))-1,"")'),
        ("Carbon_Budget_Remaining", '=[@[Target_Carbon_Budget]]-[@[Cumulative_Emissions]]'),
        ("Cumulative_Emissions", '=SUMIFS([Forecast_Emission],[Supplier_ID],[@[Supplier_ID]],[Forecast_Year],"<="&[@[Forecast_Year]])'),
        ("MAPE", '=AVERAGE(ABS((Actual_Range-Forecast_Range)/Actual_Range))'),
        ("RMSE", '=SQRT(AVERAGE((Actual_Range-Forecast_Range)^2))'),
        ("R2", '=1-(SUMXMY2(Actual_Range,Forecast_Range)/DEVSQ(Actual_Range))'),
    ]
    return pd.DataFrame(rows, columns=["Calculated_Parameter", "Excel_Structured_Formula"])


def read_or_generate_inputs(
    input_dir: Path | None, seed: int, supplier_count: int
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Read source CSVs from input_dir when supplied; otherwise generate sample data."""
    if input_dir is None:
        return create_sample_data(seed=seed, supplier_count=supplier_count)

    supplier_master_path = input_dir / "supplier_master.csv"
    historical_path = input_dir / "historical_emissions.csv"
    targets_path = input_dir / "supplier_targets.csv"
    industry_path = input_dir / "industry_haircut_pathway.csv"
    required_paths = [supplier_master_path, historical_path, targets_path, industry_path]
    if not all(path.exists() for path in required_paths):
        missing = ", ".join(str(path) for path in required_paths if not path.exists())
        raise FileNotFoundError(f"Missing required input files: {missing}")

    return (
        pd.read_csv(supplier_master_path),
        pd.read_csv(historical_path),
        pd.read_csv(targets_path),
        pd.read_csv(industry_path),
    )


def export_datasets(
    output_dir: Path,
    supplier_master: pd.DataFrame,
    historical_emissions: pd.DataFrame,
    supplier_targets: pd.DataFrame,
    industry_table: pd.DataFrame,
    enriched_history: pd.DataFrame,
    forecast_output: pd.DataFrame,
    data_dictionary: pd.DataFrame,
    formula_dictionary: pd.DataFrame,
) -> None:
    """Export datasets to CSV and a consolidated Excel workbook."""
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "supplier_master": supplier_master,
        "historical_emissions": historical_emissions,
        "supplier_targets": supplier_targets,
        "industry_haircut_pathway": industry_table,
        "historical_emissions_enriched": enriched_history,
        "forecast_output": forecast_output,
        "data_dictionary": data_dictionary,
        "formula_dictionary": formula_dictionary,
    }

    for name, data in datasets.items():
        data.to_csv(output_dir / f"{name}.csv", index=False)

    workbook_path = output_dir / "supply_chain_emissions_forecast_model.xlsx"
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        for name, data in datasets.items():
            sheet_name = name[:31]
            data.to_excel(writer, sheet_name=sheet_name, index=False)


def build_model(args: argparse.Namespace) -> None:
    """Run the full model pipeline."""
    input_dir = Path(args.input_dir) if args.input_dir else None
    output_dir = Path(args.output_dir)

    # Step 1: Read or generate source datasets.
    supplier_master, historical_emissions, supplier_targets, industry_table = read_or_generate_inputs(
        input_dir=input_dir,
        seed=args.seed,
        supplier_count=args.suppliers,
    )

    # Step 2: Calculate total emissions and audit flags using fallback logic.
    enriched_history = add_total_emission_calculations(historical_emissions)

    # Step 3: Build supplier-level forecasts and annual glide paths.
    forecast_output = build_forecast_output(
        enriched_history=enriched_history,
        supplier_targets=supplier_targets,
        industry_table=industry_table,
        forecast_start_year=args.forecast_start_year,
        forecast_end_year=args.forecast_end_year,
    )

    # Step 4: Build dictionaries for Excel/Qlik/dashboard implementation.
    data_dictionary = create_data_dictionary()
    formula_dictionary = create_formula_dictionary()

    # Step 5: Export all datasets for analysis and dashboarding.
    export_datasets(
        output_dir=output_dir,
        supplier_master=supplier_master,
        historical_emissions=historical_emissions,
        supplier_targets=supplier_targets,
        industry_table=industry_table,
        enriched_history=enriched_history,
        forecast_output=forecast_output,
        data_dictionary=data_dictionary,
        formula_dictionary=formula_dictionary,
    )

    print(f"Created {len(historical_emissions):,} historical records")
    print(f"Created {len(forecast_output):,} forecast records")
    print(f"Output written to: {output_dir.resolve()}")


def parse_args(args: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Build supply chain emissions forecast datasets.")
    parser.add_argument("--input-dir", default=None, help="Optional directory containing source CSV files.")
    parser.add_argument("--output-dir", default="data/output", help="Output directory for CSV/XLSX files.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for synthetic data generation.")
    parser.add_argument("--suppliers", type=int, default=100, help="Number of synthetic suppliers to generate.")
    parser.add_argument("--forecast-start-year", type=int, default=2025, help="First forecast year.")
    parser.add_argument("--forecast-end-year", type=int, default=2040, help="Final forecast year.")
    return parser.parse_args(args)


if __name__ == "__main__":
    build_model(parse_args())
