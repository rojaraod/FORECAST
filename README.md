# Supply Chain Emissions Forecasting - What-If Analysis

This repository contains a native Qlik Sense Enterprise implementation package
for a corporate ESG supply-chain emissions what-if dashboard.

## Contents

- `qlik/supply_chain_emissions_what_if_load_script.qvs`  
  Qlik load script for the supplied supplier emissions CSV.
- `docs/qlik_expression_catalog.md`  
  Native Qlik helper variables, KPIs, chart measures, and table expressions.
- `docs/qlik_dashboard_build_guide.md`  
  Step-by-step Qlik Sense UI build instructions.

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
expressions. The guide optionally references Qlik's own Variable input control
for a better what-if user experience; no third-party extensions are required.