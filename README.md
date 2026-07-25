# Building Retrofit Analysis

Reproducible Python refactoring of the `Passive VS Code.ipynb` reference
notebook. The package preserves the notebook's scenario ordering, EnergyPlus
object modifications, five-year checkpoint convention, economic formulas,
comfort calculations, emissions calculations, units, and scientific scenario
identifiers.

The reference notebook is intentionally not copied or modified. Generated
models, EnergyPlus results, tables, and figures belong under `outputs/` and are
ignored by Git.

## Requirements

- Python 3.11+
- EnergyPlus 24.2 for simulation
- The baseline `.epJSON` model and `.epw` weather file

Install for development:

```bash
python -m pip install -e ".[dev]"
```

Install the optional plotting stack with
`python -m pip install -e ".[visualization]"`.

Copy `config/example.toml` to `config/local.toml` and edit its paths.

## Workflows

Run a small, safe simulation subset (the default):

```bash
python scripts/run_simulations.py --config config/local.toml
```

Choose representative scenario numbers:

```bash
python scripts/run_simulations.py --config config/local.toml --indices 0 1 2688
```

Running all 18,421 scenario timelines requires an explicit flag:

```bash
python scripts/run_simulations.py --config config/local.toml --all
```

Analyze existing EnergyPlus results:

```bash
python scripts/analyze_results.py --config config/local.toml
```

Run the three-case reference regression:

```bash
python scripts/validate_reference.py --config config/local.toml
```

Reference provenance and the 2026 regeneration are documented in
`docs/REFERENCE_REGENERATION.md`. Compact version-controlled metrics live in
`tests/reference/representative_cases.json`; raw EnergyPlus outputs are not
committed.

Run tests:

```bash
python -m pytest
```

## Scientific conventions retained

- Component order: wall, window, roof, floor, shading.
- Time order: `Now`, `5_years`, `10_years`, `15_years`, `20_years`,
  `25_years`; `CC` means no retrofit.
- Wall and window baseline/upgrade status must match, and upgraded wall and
  window installation times are synchronized.
- Shading requires upgraded windows and may occur at or after window
  replacement.
- District heating is stored in GJ and converted with 277.778 kWh/GJ.
- Costs are NOK; emissions are kg CO2e.
- The 30-year analysis repeats checkpoints for `(5, 5, 5, 5, 5, 6)` years
  where the notebook does so, then uses the first 30 annual entries.

## Configuration

All machine-specific paths are in TOML configuration. Relative paths are
resolved from the configuration file's directory. The example file contains
the paths used by the reference notebook as documentation only.

## Package layout

- `scenarios.py`: exact scenario enumeration and checkpoint identifiers
- `measures.py`: retrofit properties and deterioration values
- `energyplus/`: model mutation, execution, and result parsing
- `economics.py`, `comfort.py`, `emissions.py`: calculations
- `results.py`: result-to-scenario mapping and final table assembly
- `workflow.py`: executable orchestration
- `tests/`: scenario, formula, model-mutation, parser, and regression tests
