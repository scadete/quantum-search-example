# Qiskit Migration — Lessons Learned
# quantum-search-example project
# Last updated: 2026-10-21

This file records concrete discoveries made while migrating this notebook from
deprecated Qiskit APIs to clean Qiskit 2.5.x. Load it before any future
migration or upgrade work on this project to skip the discovery phase.

---

## 1. PhaseOracle → PhaseOracleGate

### What changed
`PhaseOracle` (deprecated since 2.2, removed in 3.0) was a `QuantumCircuit` subclass.
`PhaseOracleGate` (replacement) is a `Gate` — it cannot be passed directly to
`AmplificationProblem` or used as a standalone oracle circuit.

### Wrapping pattern required
```python
from qiskit.circuit.library import PhaseOracleGate
from qiskit import QuantumCircuit

gate = PhaseOracleGate(expression)
oracle = QuantumCircuit(gate.num_qubits)
oracle.append(gate, range(gate.num_qubits))
```

### evaluate_bitstring is gone
`PhaseOracle.evaluate_bitstring` does not exist on `PhaseOracleGate`.
Replace `is_good_state=oracle.evaluate_bitstring` with:
```python
from qiskit.circuit.classicalfunction import BooleanExpression
is_good_state=lambda bits: BooleanExpression(expression).simulate(bits)
```
`BooleanExpression.simulate(bitstring)` returns `True`/`False` — same semantics.

### BooleanExpression / classicalfunction — avoid entirely
`qiskit.circuit.classicalfunction` is an **optional C-extension** that is
frequently absent even when `qiskit[all]` is installed. Any import of it
raises `ModuleNotFoundError` in those environments.

**Do not use `BooleanExpression.simulate()` for oracle evaluation.**
The project already has `cultivar_matches(cultivar, query)` (Sub-Tarefa 5)
as the canonical classical oracle. Use it instead:
```python
oracle_eval = any(cultivar_matches(c, query) for c in CULTIVARES)
```
This is semantically equivalent and has zero extra dependencies.

### tweedledum is no longer needed
`PhaseOracle` required `tweedledum` for boolean synthesis.
`PhaseOracleGate` uses Qiskit's own internal synthesis — no external package needed.
Remove `tweedledum` from requirements and install cells entirely.

---

## 2. qiskit-algorithms (Grover + AmplificationProblem) → native grover_operator

### What changed
`qiskit_algorithms.Grover` and `AmplificationProblem` are a community package
wrapping removed `qiskit.algorithms.*`. Qiskit 2.x ships the full primitive
natively in `qiskit.circuit.library`.

### Replacement
```python
from qiskit.circuit.library import grover_operator   # function, not class
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

# Build oracle (QuantumCircuit) first, then:
grover_op = grover_operator(oracle)

n = oracle.num_qubits
circuit = QuantumCircuit(n)
circuit.h(range(n))                        # uniform superposition (state prep)
circuit.compose(grover_op, inplace=True)   # one Grover iteration
circuit.measure_all()

job = StatevectorSampler().run([circuit], shots=1024)
counts = job.result()[0].data.meas.get_counts()
top_measurement = max(counts, key=counts.get)
```

For multiple iterations (e.g. the cultivar search used 1024), loop:
```python
for _ in range(num_iterations):
    circuit.compose(grover_op, inplace=True)
```
Note: large iteration counts on 21-qubit circuits are very slow with
`StatevectorSampler`. Start with 1 iteration for debugging.

### Result fields that no longer exist
`GroverResult.top_measurement`, `.oracle_evaluation`, `.circuit_results[0]`
are gone with `qiskit-algorithms`. Manual equivalents:
```python
top_measurement  = max(counts, key=counts.get)
oracle_evaluation = BooleanExpression(expression).simulate(top_measurement)
histogram_data    = counts  # pass directly to plot_histogram()
```

---

## 3. grover_operator() vs GroverOperator class

Both exist in `qiskit.circuit.library`. The **function** `grover_operator()` is
the recommended API for Qiskit 2.x. The **class** `GroverOperator` also works
and exposes attributes like `.oracle` and `.state_preparation`. For drawing the
oracle only:
```python
grover_operator(oracle).decompose().draw(output='mpl')
# Replaces: problem.grover_operator.oracle.decompose().draw(output='mpl')
```

---

## 4. SamplerV2 / StatevectorSampler result shape

`StatevectorSampler.run([circuit], shots=N)` returns a `PrimitiveJob`.
Result access chain:
```python
result  = job.result()          # PrimitiveResult
pub_result = result[0]          # SamplerPubResult
bit_array  = pub_result.data.meas   # DataBin attribute name = creg name
counts     = bit_array.get_counts() # dict[str, int]
```
The `DataBin` attribute name matches the classical register name.
`measure_all()` creates a register named `meas` → `pub_result.data.meas`.
If a custom register name is used, access it by that name instead.

---

## 5. plot_state_qsphere requires Statevector, not QuantumCircuit

Passing a `QuantumCircuit` directly to `plot_state_qsphere` triggers implicit
conversion which may silently break or warn. Pass explicitly:
```python
from qiskit.quantum_info import Statevector
plot_state_qsphere(Statevector(circuit))
```

---

## 6. generate_preset_pass_manager import path

Canonical import in Qiskit 2.x (avoids submodule import warning):
```python
from qiskit.transpiler import generate_preset_pass_manager   # correct
# NOT: from qiskit.transpiler.preset_passmanagers import ...
```

---

## 7. qiskit-docs MCP tool — confirmed useful lookups

- `PhaseOracleGate` full API: `api/qiskit/qiskit.circuit.library.PhaseOracleGate`
- `grover_operator` function: `api/qiskit/qiskit.circuit.library.grover_operator`
- `GroverOperator` class: `api/qiskit/qiskit.circuit.library.GroverOperator`
- `StatevectorSampler`: `api/qiskit/qiskit.primitives.StatevectorSampler`
- `HAS_TWEEDLEDUM` status: `api/qiskit/utils#qiskitutilsoptionalshas_tweedledum`
- Qiskit 2.0 migration guide: `guides/qiskit-2.0`

Use `search_docs_tool` first, then `get_page_tool` on the returned URL for
full content. Scope `"api"` cuts noise significantly for API lookups.

---

## 8. Dependency reduction achieved

| Removed | Reason |
|---|---|
| `tweedledum~=1.1.1` | `PhaseOracleGate` uses built-in synthesis |
| `qiskit-algorithms~=0.3.1` | Replaced by native `grover_operator` |

Final install cell (as of 2026-10-21):
```
qiskit[all]~=2.5.2  qiskit-aer~=0.17.0  qiskit-ibm-runtime~=0.47.0  matplotlib~=3.9
```
