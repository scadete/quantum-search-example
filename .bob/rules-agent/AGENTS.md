# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Coding Rules (Non-Obvious)

- **Domain**: The "real problem" is searching for a soy cultivar matching agronomic conditions from the Embrapa Centro-Sul 2013 catalogue. Variables `a`–`e` in `PhaseOracle` expressions map to boolean cultivar/condition attributes from that document.
- **Do not upgrade Qiskit** — uses `qiskit==0.43.0` / `qiskit-terra==0.24.0`. APIs `qiskit.algorithms.Grover`, `qiskit.algorithms.AmplificationProblem`, `qiskit.primitives.Sampler` were removed in Qiskit 1.x. Rewriting requires full migration.
- **conda env, not pip** — `requirements.txt` is conda `--file` format for `linux-64`. `pip install -r requirements.txt` will fail.
- **Phase-flip oracle required** — `Grover`/`AmplificationProblem` require phase-flip oracles (target state amplitude ×-1). New oracle examples must use the `PhaseOracle` boolean-expression pattern or the CZ-gate manual pattern, not bit-flip.
- **`PhaseOracle` depends on `tweedledum`** — cells wrap this in `try/except MissingOptionalLibraryError`. Don't remove `tweedledum` from env.
- **Variable naming**: early cells use Portuguese (`oraculo`, `estado_desejado`, `problema`, `expressao`); later cells use English. Match the surrounding cell when editing; use English for new cells.
- **IBM Runtime session pattern** — real hardware cells use `with Session(service=service, backend=backend):` context manager. Do not instantiate `Sampler` from `qiskit_ibm_runtime` outside the session block.
- **Result format difference** — local `Aer` simulator: `resultado_simulador.get_counts()` returns integer counts. IBM Runtime `Sampler`: `result.quasi_dists` returns quasi-probability distributions. Visualisation differs: `plot_histogram(quantidade)` vs `plot_histogram(result.quasi_dists)`.
- **`iterations` parameter** — the toy example uses `Grover(sampler=Sampler())` (auto-iterations). The real-problem simulation uses `iterations=1024`; real hardware uses `iterations=1`. These are intentionally different for pedagogical/hardware reasons.
