# Regression reference regeneration

Date: 2026-07-25

The current `Passive VS Code.ipynb` formulas are the authoritative scientific
implementation. Two previously stored EnergyPlus cases were found to have been
generated using an older parameterization:

- `Wi005 = 2.600 W/m2-K` instead of the current `2.625 W/m2-K`.
- In the all-deteriorated case, `R005 = 1.6416 m2-K/W` and
  `F005 = 1.3959 m2-K/W` instead of the current `1.6074` and `1.3818`.

Those historical values exactly reproduced the old raw CSV files, confirming
that the differences were reference-data provenance issues rather than
numerical variation or refactoring errors.

The following reference cases were regenerated with EnergyPlus 24.2 from the
current notebook formulas:

- `W005_Wi005_R005_F005_S0`
- `W005_Wi005_R1_F1_S0`

The unaffected `W2_Wi2_R2_F2_S0` control already matched exactly and was not
replaced. Compact authoritative metrics are stored in
`tests/reference/representative_cases.json`. Generated raw outputs remain
outside Git.

The historical files were backed up locally under
`outputs/historical_reference_backup/`, which is ignored by Git.

