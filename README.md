# Supply Chain Emissions Forecasting - What-If Analysis

This repository contains a native Qlik Sense Enterprise implementation package
for a corporate ESG supply-chain emissions what-if dashboard.

## Contents

### Sheet 1 - portfolio what-if dashboard

- `qlik/supply_chain_emissions_what_if_load_script.qvs`
  Qlik load script for the supplied supplier emissions CSV.
- `docs/qlik_expression_catalog.md`
  Native Qlik helper variables, KPIs, chart measures, and table expressions.
- `docs/qlik_dashboard_build_guide.md`
  Step-by-step Qlik Sense UI build instructions.

### Sheet 2 - supplier scenario what-if dashboard

- `qlik/sheet2_supplier_specific_what_if_load_script.qvs`
  Separate Qlik app load script for multi-supplier and supplier-specific
  what-if analysis.
- `docs/qlik_sheet2_expression_catalog.md`
  Native Qlik helper variables, scenario measures, top-supplier adjustment
  expressions, and chart measures.
- `docs/qlik_sheet2_design_development_guide.md`
  End-to-end data model, design, and development instructions for Sheet 2.

## Source data

The dashboard expects the supplied CSV:

```text
supplier_emissions_source_100_records_c6ee.csv
```

Upload the file to a governed Qlik data connection such as:

```text
lib://ESG_Source_Data/
```

Then update `vSourceDataFile` in the Qlik script if your connection or file name
differs.

## Extension policy

The data model and analytics use only native Qlik load script and native Qlik
expressions. The guides optionally reference Qlik's own Variable input control
for a better what-if user experience; no third-party extensions are required.