# Supply Chain Emissions Forecasting - What-If Analysis

**PDF-style dashboard documentation pack**
**Last updated:** 25 May 2025
**Prepared for:** Qlik Sense dashboard development and QVF export

---

## 1. Executive summary

This dashboard models supplier emissions from 2018 through 2050 and provides interactive what-if controls for reduction pathways, expert adjustments, growth assumptions, and net-zero timing.

Key baseline facts:

| Metric | Value |
| --- | ---: |
| Supplier records | 50 |
| 2025 current emissions | 619,700 tCO2e |
| Supplier Target records | 30 |
| Expert Judgement records | 20 |
| Generated supplier-year rows | 1,650 |
| Default forecast year | 2030 |
| Default net-zero target | 2050 |

---

## 2. Data inventory

| File | Rows | Description |
| --- | ---: | --- |
| `data/supply_chain_emissions_suppliers_50.csv` | 50 | Supplier-level source records used by the Qlik load script. |
| `data/supply_chain_emissions_supplier_year_default_forecast.csv` | 1,650 | Default scenario supplier-year extract for QA, external review, and offline validation. |
| `data/supply_chain_emissions_scope_breakdown_2025.csv` | 150 | Scope 1, Scope 2, and Scope 3 emissions split for each supplier in 2025. |

---

## 3. Dashboard pages

### Page 1 - Executive what-if dashboard

Purpose: show current emissions, selected forecast emissions, reduction achieved, supplier target coverage, and forecast pathways.

Primary visuals:

- KPI cards for current emissions, forecast emissions, reduction, reduction percent, supplier target count, and expert judgement count.
- Historical versus forecast line chart with baseline and net-zero pathway overlays.
- Forecast method donut chart.
- Forecast emissions by industry horizontal bar chart.
- Year-by-year forecast data table.

### Page 2 - Supplier detail recommended add-on

Purpose: validate one supplier at a time and review input quality.

Recommended visuals:

- Supplier profile card.
- 2025 Scope 1/2/3 stacked bar using `supply_chain_emissions_scope_breakdown_2025.csv`.
- Supplier-specific historical and forecast line.
- Supplier assumption table.

### Page 3 - Industry deep dive recommended add-on

Purpose: identify industries with the largest emissions and reduction opportunities.

Recommended visuals:

- Industry ranking bar chart.
- Forecast method mix by industry.
- Supplier table sorted by selected-year forecast emissions.
- Data quality by industry.

---

## 4. User controls

| Control | Default | Business meaning |
| --- | ---: | --- |
| Forecast Year | 2030 | Year used for selected forecast KPI and industry ranking. |
| Additional Reduction | 5% | Additional reduction ambition applied to each supplier. |
| Expert Judgement Adjustment | 3% | Additional adjustment applied only to Expert Judgement records. |
| Growth Adjustment | 2% | Annual growth factor before reduction effects. |
| Net Zero Target Year | 2050 | Year when net-zero pathway reaches zero. |

---

## 5. Qlik Sense development checklist

1. Load the 50-row supplier CSV through a `SupplyChainData` connection.
2. Paste and reload `qlik/supply_chain_emissions_what_if_model.qvs`.
3. Import/apply `qlik/supply_chain_emissions_theme.json` if custom themes are allowed.
4. Create variables and bind them to Variable input sliders.
5. Build sheet objects from `docs/qlik_sense_supply_chain_emissions_build_guide.md`.
6. Use `docs/qlik_sense_dashboard_object_property_matrix.md` for detailed object options.
7. Validate totals and supplier counts.
8. Export the app as `Supply_Chain_Emissions_Forecasting_What_If.qvf`.

---

## 6. Acceptance criteria

| Test | Expected result |
| --- | --- |
| Supplier count | 50 |
| 2025 total emissions | 619,700 tCO2e |
| Forecast method distribution | 60% Supplier Target / 40% Expert Judgement |
| Slider response | KPIs, line chart, industry bar, and table update immediately |
| Filter response | Supplier, Industry, and Forecast Method filters affect all visuals |
| Export readiness | QVF can be exported from Qlik Sense after reload and sheet build |

---

## 7. Print/PDF formatting notes

Recommended export settings:

- Page size: A4 landscape or 16:9 widescreen.
- Margins: 0.35 inch.
- Header/footer: include dashboard title, last updated date, and page number.
- Use page breaks before each numbered section.
- Keep code blocks in monospace at 9 pt.
- Use the generated dashboard image as the cover visual if a single-page handout is required.
