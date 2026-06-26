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
