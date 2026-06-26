# QVF Development Package

Qlik Sense `.qvf` files are binary app files saved or exported by Qlik Sense Desktop, Qlik Sense Enterprise, or Qlik Cloud. This repository cannot safely hand-author that proprietary binary format, so this folder contains the source package needed to generate the QVF in a Qlik environment.

## Files

- `supply_chain_emissions_qvf_spec.json` - machine-readable Qlik app specification: app metadata, data model, variables, filters, measures, sheet layout, and dashboard objects.
- `../qlik/supply_chain_emissions_what_if_model.qvs` - Qlik load script used in the QVF.
- `../data/supply_chain_emissions_suppliers_50.csv` - source CSV data.
- `../scripts/create_qvf_local_engine.mjs` - Node.js script that connects to a local Qlik Engine, creates/opens the app, sets the load script, reloads, and saves the app/QVF shell.

## Generate the QVF with Qlik Sense Desktop

1. Install/open Qlik Sense Desktop and confirm the local engine is running.
2. Make the CSV available to Qlik using a folder data connection named `SupplyChainData`, or set `QLIK_DATA_CONNECTION` to an accessible `lib://...` connection.
3. From this repo, run:

```bash
node scripts/create_qvf_local_engine.mjs
```

4. Open the saved app in Qlik Sense Desktop.
5. Create the dashboard sheet objects from `supply_chain_emissions_qvf_spec.json` or `docs/qlik_sense_supply_chain_emissions_build_guide.md`.
6. Export/copy the finished app as:

```text
qvf/Supply_Chain_Emissions_Forecasting_What_If.qvf
```

## Generate the QVF with Qlik Sense Enterprise or Qlik Cloud

1. Create a folder/data-files connection named `SupplyChainData` and upload the CSV.
2. Create an app named `Supply Chain Emissions Forecasting - What-If Analysis`.
3. Paste `../qlik/supply_chain_emissions_what_if_model.qvs` into the Data Load Editor and reload.
4. Build sheet objects from `supply_chain_emissions_qvf_spec.json`.
5. Export the app from Hub/QMC as `Supply_Chain_Emissions_Forecasting_What_If.qvf`.

## Validation targets

- Supplier records: `50`.
- Generated supplier-year rows after reload: `1,650`.
- 2025 current emissions: `619,700 tCO2e`.
- Forecast method distribution: `30` Supplier Target, `20` Expert Judgement.


## Expanded package additions

The QVF source package now includes extra implementation and QA assets:

- `../data/supply_chain_emissions_supplier_year_default_forecast.csv` - 1,650-row default scenario extract for validating the forecast curve outside Qlik.
- `../data/supply_chain_emissions_scope_breakdown_2025.csv` - 150-row Scope 1/2/3 dataset for supplier-detail visuals.
- `../qlik/supply_chain_emissions_theme.json` - custom Qlik theme settings.
- `../docs/qlik_sense_dashboard_object_property_matrix.md` - detailed object configuration matrix.
- `../docs/supply_chain_emissions_pdf_style_report.md` - PDF-style documentation handoff.

## Detailed QVF build sequence

1. Create or confirm the `SupplyChainData` data connection.
2. Upload all CSV files from `../data/` if you want both the main dashboard and optional detail sheets.
3. Run `node scripts/create_qvf_local_engine.mjs` to create the app shell and reload the main model.
4. Open the app in Qlik Sense and verify the data model contains `FactSupplierYear` and `IndustrySort`.
5. Add the custom theme from `../qlik/supply_chain_emissions_theme.json` if your tenant permits custom themes.
6. Build the executive dashboard from `supply_chain_emissions_qvf_spec.json`.
7. Use the object property matrix for labels, colors, conditional formatting, selection behavior, and export settings.
8. Optionally add Supplier Detail and Industry Deep Dive sheets using the supplemental CSV extracts.
9. Save, reload, and export the final app as `Supply_Chain_Emissions_Forecasting_What_If.qvf`.

## Troubleshooting

| Issue | Resolution |
| --- | --- |
| Local engine connection fails | Confirm Qlik Sense Desktop is running and check `QLIK_ENGINE_URL`. |
| CSV cannot be found | Confirm the `SupplyChainData` connection points to the folder containing `supply_chain_emissions_suppliers_50.csv`. |
| Reload succeeds but visuals are blank | Confirm variables exist and match the names in the build guide. |
| Slider does not update measures | Use chart expressions from the guide so variables are evaluated at runtime. |
| Theme does not apply | Import the theme in QMC/tenant admin or manually apply the listed colors. |
| QVF export unavailable | Use Qlik Sense Desktop copy/export or Enterprise/QMC app export permissions. |
