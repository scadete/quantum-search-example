# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architecture Constraints (Non-Obvious)

- **No modular structure** — all logic in a single `.ipynb`. Cells are the only units of organisation; there are no importable modules.
- **Domain mapping is implicit** — the Embrapa catalogue attributes mapped to variables `a`–`e` are not documented in the notebook code itself. The mapping exists only in the human mind of the author and the linked PDF. Any extension requires consulting the Embrapa PDF to correctly assign new boolean variables.
- **Qiskit version lock is hard** — the algorithm layer (`Grover`, `AmplificationProblem`, `Sampler` from `qiskit.primitives`) was completely replaced between Qiskit 0.x and 1.x. Migration is a full rewrite, not a find-replace.
- **Two independent oracle creation paths**: (1) manual `QuantumCircuit` (CZ gate), (2) `PhaseOracle` from boolean expressions (needs `tweedledum`). Both feed `AmplificationProblem`. The soy problem uses path 2. Any domain extension should use path 2 with a new boolean expression.
- **Two execution backends with incompatible result formats**: local `Aer` simulator returns `get_counts()` (integer counts); IBM Runtime `Sampler` returns `quasi_dists` (quasi-probabilities, floats summing to ~1). These are architecturally different and cannot be used interchangeably.
- **5-qubit problem space** — the soy search uses 5 boolean variables = 2^5 = 32 possible states. The selected real hardware (`ibmq_belem`) is exactly a 5-qubit device. Adding more boolean attributes would require a larger quantum computer.
- **`iterations` is not portable** — `iterations=1024` works on the local simulator but is impractical on real hardware (noise increases with circuit depth). Real hardware uses `iterations=1`. This is an architectural limitation of NISQ-era devices, not a bug.
- **No state is shared between kernel restarts** — imports and all variable definitions must be re-run top-to-bottom.
