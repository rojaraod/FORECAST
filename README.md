# Supply Chain Emissions Forecasting Model

This repository contains a complete supplier-level supply chain emissions
forecasting framework for ESG, Procurement, Sustainability, Data Science, and
Audit teams.

## What is included

- Mathematical forecasting methodology for supplier emissions.
- Direct historical/current emissions validation with source, quality, validation,
  and confidence flags.
- Supplier target, industry haircut, and historical trend forecasting pathways.
- Excel structured formula library.
- Qlik Sense dashboard design and expressions.
- End-to-end Python implementation that generates 1,000 sample historical
  supplier-year records and forecast outputs.

## Repository structure

```text
docs/
  supply_chain_emissions_forecasting_framework.md
src/
  supply_chain_emissions_forecast.py
requirements.txt
```

## Quick start

```bash
pip install -r requirements.txt
python3 src/supply_chain_emissions_forecast.py --output-dir data/output
```

The script exports:

- `supplier_master.csv`
- `historical_emissions.csv`
- `supplier_targets.csv`
- `industry_haircut_pathway.csv`
- `historical_emissions_enriched.csv`
- `forecast_output.csv`
- `data_dictionary.csv`
- `formula_dictionary.csv`
- `supply_chain_emissions_forecast_model.xlsx`

## Documentation

See
[`docs/supply_chain_emissions_forecasting_framework.md`](docs/supply_chain_emissions_forecasting_framework.md)
for the full business methodology, source data design, formulas, Python logic,
Excel formulas, Qlik dashboard scope, validation checks, assumptions, risks, and
future enhancements.

## PowerPoint deck

A 20-slide presentation is available at:

```text
docs/supply_chain_emissions_forecasting_20_slide_deck.pptx
```

To regenerate it:

```bash
python3 scripts/create_forecasting_presentation.py
```