# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Documentation Context (Non-Obvious)

- **Single-file project** — entire codebase is one Jupyter notebook (`quantum-search-example.ipynb`). No source modules, packages, or test files.
- **Domain source**: The real-world problem (soy cultivar search) is derived from the Embrapa Centro-Sul 2013 soy catalogue PDF. The notebook links to it but does not reproduce the catalogue data. Variables `a`–`e` in the oracle expression represent mapped boolean attributes from that document.
- **Pedagogical structure** — the notebook progresses from a trivial 2-qubit toy problem → `Statevector` oracle → `PhaseOracle` from boolean expression → real IBM Quantum hardware. Each section builds on the previous.
- **Markdown cells are in Brazilian Portuguese** — the canonical explanation text. English appears only in code and later cells.
- **`requirements.txt` is misleading** — looks like pip but is conda `--file` format. Header comment clarifies this.
- **The stored WebSocket error traceback** in the real-hardware cell output is from a prior run (network connectivity issue during result streaming), not a code bug. The result was still retrieved successfully (the `SamplerResult` print statement shows 32 quasi-distribution values for the 5-qubit problem).
- **`teste_oraculo` cells** (cells 3–5) are a verification pattern (Hadamard + phase kickback + measurement), not part of the Grover execution flow. They confirm the oracle marks the correct state before running the full algorithm.
- **The expression `'(a | b | c | d | e) & (a & d & e)'`** is the actual soy search query. With 5 qubits, the search space is 2^5 = 32 possible combinations of conditions. The real hardware output `quasi_dists` shows 32 probability values indexed 0–31.
