# FORECAST

Qlik Sense artifacts for a Supply Chain Emissions Forecasting what-if dashboard.

## Contents

- `data/supply_chain_emissions_suppliers_50.csv` - 50 supplier records for emissions forecasting.
- `qlik/supply_chain_emissions_what_if_model.qvs` - Qlik Sense load script for the end-to-end supplier-year data model.
- `docs/qlik_sense_supply_chain_emissions_build_guide.md` - object-by-object dashboard dimensions, expressions, sliders, filters, colors, and options.
- `data/supply_chain_emissions_supplier_year_default_forecast.csv` - 1,650-row default scenario supplier-year CSV extract.
- `data/supply_chain_emissions_scope_breakdown_2025.csv` - 150-row Scope 1/2/3 emissions breakdown CSV.
- `docs/qlik_sense_dashboard_object_property_matrix.md` - detailed Qlik object configuration matrix.
- `docs/supply_chain_emissions_pdf_style_report.md` - PDF-style handoff documentation.
- `qlik/supply_chain_emissions_theme.json` - Qlik theme settings for the dashboard.

The sample data totals 619,700 tCO2e for 2025 current emissions and includes 30 supplier-target records plus 20 expert-judgement records.

## QVF development

The `qvf/` folder contains a Qlik Sense QVF source package and instructions. A valid `.qvf` binary must be exported by Qlik Sense Desktop/Enterprise/Cloud; use `scripts/create_qvf_local_engine.mjs` with a running Qlik Engine to create and save the app shell from the included load script and CSV.
