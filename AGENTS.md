# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project Purpose

Educational demonstration of **Grover's quantum search algorithm** applied to a real agricultural search problem: finding the right **soy cultivar** for a given set of growing conditions, using data from the Embrapa catalogue:
> https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/976493/1/CATALOGOSojaCentrosul2013.pdf

The notebook is written in **Brazilian Portuguese** (comments and markdown cells). Variable names in early cells are Portuguese (`oraculo`, `estado_desejado`, `problema`); later cells switch to English (`oracle`, `problem`, `result`). Follow the surrounding cell's language when editing inline; use English for new cells.

## Notebook Structure (Pedagogical Progression)

The notebook teaches Grover's algorithm in three escalating steps:

1. **Toy oracle with `QuantumCircuit`** — 2-qubit CZ gate marks state `'11'` as the target. Uses manual oracle construction and validation via `teste_oraculo` (Hadamard + phase kickback verification pattern).
2. **Oracle from `Statevector`** — alternative oracle construction from a state vector label (e.g. `'01'`).
3. **Oracle from boolean expression (`PhaseOracle`)** — the "real problem" cell uses the expression `'(a | b | c | d | e) & (a & d & e)'` encoding soy cultivar search conditions mapped from the Embrapa catalogue. 5 qubits = 5 boolean attributes of the growing conditions/cultivar properties.
4. **Real quantum hardware execution** — same boolean-expression problem run on `ibmq_belem` (5-qubit IBM Quantum device) via `QiskitRuntimeService` + `Session`.

## Domain: Soy Cultivar Search

The boolean expression `'(a | b | c | d | e) & (a & d & e)'` encodes search conditions derived from the **Embrapa Centro-Sul 2013 soy catalogue**. Variables `a`–`e` represent attributes (growing region, maturity group, disease resistance, productivity class, or similar agronomic properties) that a cultivar must satisfy. The oracle marks cultivars that simultaneously satisfy conditions `a`, `d`, and `e` while also satisfying at least one of `a`, `b`, `c`, `d`, or `e`. Any extension of the soy search logic must maintain this boolean-expression oracle pattern.

## Environment Setup

`requirements.txt` is a **conda** format file (NOT pip). Create environment with:
```bash
conda create --name <env> --file requirements.txt
```
Pinned to `linux-64`. The notebook header incorrectly says `python install -r requirements.txt` — ignore it.

## Running

```bash
jupyter notebook quantum-search-example.ipynb
```
No automated tests exist. Cells are run top-to-bottom; kernel state is not preserved across restarts.

## Critical API Constraints

- Uses **Qiskit 0.43 / qiskit-terra 0.24** legacy APIs: `qiskit.algorithms.Grover`, `qiskit.algorithms.AmplificationProblem`, `qiskit.primitives.Sampler`. **Do not upgrade Qiskit** — these APIs were removed in Qiskit 1.x.
- `Aer.get_backend('qasm_simulator')` — local simulation; requires `qiskit-aer`.
- `PhaseOracle` requires `tweedledum` (pinned in conda env). Missing it raises `MissingOptionalLibraryError` (cells wrap this in `try/except`).
- All Grover oracles must be **phase-flip** (target amplitudes ×-1), not bit-flip.

## Real Quantum Hardware

Requires IBM Quantum credentials before running the `QiskitRuntimeService` cells:
```python
QiskitRuntimeService.save_account(channel="ibm_quantum", token="MY_IBM_QUANTUM_TOKEN")
```
The stored `SamplerResult` output in the last cells (with a WebSocket error traceback in stderr) is from a prior real hardware run — it is **not a code bug**.

Real-hardware `Sampler` returns `SamplerResult` with `quasi_dists` (quasi-probabilities), not raw counts like the local `Aer` simulator. Use `plot_histogram(result.quasi_dists)` for visualisation.
